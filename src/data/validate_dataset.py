"""Validate RNA-seq sample identifiers and labels against Supplementary Table S1 and GEO."""

from __future__ import annotations

import csv
import gzip
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPRESSION_PATH = PROJECT_ROOT / "data" / "raw" / "GSE272042_tpmALL.csv.gz"
METADATA_PATH = PROJECT_ROOT / "data" / "raw" / "41597_2025_4597_MOESM1_ESM.xlsx"
REPORT_PATH = PROJECT_ROOT / "reports" / "results" / "dataset_validation.md"
GEO_MATRIX_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE272nnn/GSE272042/"
    "matrix/GSE272042_series_matrix.txt.gz"
)
REQUIRED_COLUMNS = {"Sample", "RNA-seq", "Diagnosis"}
PATIENT_COLUMN_TERMS = ("patient", "donor", "subject", "case", "individual")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sample_number(value: object) -> str | None:
    match = re.fullmatch(r"Sample\s+(\d+)", str(value).strip())
    return match.group(1) if match else None


def normalize_label(value: object) -> str | None:
    if pd.isna(value):
        return None
    return " ".join(str(value).replace("\xa0", " ").split())


def find_metadata_table(path: Path) -> tuple[str, int, pd.DataFrame]:
    workbook = pd.ExcelFile(path)
    candidates: list[tuple[str, int, pd.DataFrame]] = []
    for sheet_name in workbook.sheet_names:
        raw = pd.read_excel(workbook, sheet_name=sheet_name, header=None)
        for row_index, row in raw.iterrows():
            headers = {str(value).strip() for value in row.dropna()}
            if REQUIRED_COLUMNS.issubset(headers):
                frame = pd.read_excel(
                    workbook, sheet_name=sheet_name, header=int(row_index)
                ).dropna(how="all")
                candidates.append((sheet_name, int(row_index), frame))
    if len(candidates) != 1:
        raise ValueError(
            "Expected exactly one worksheet header containing "
            f"{sorted(REQUIRED_COLUMNS)}; found {len(candidates)}."
        )
    sheet_name, header_row, frame = candidates[0]
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Metadata worksheet is missing columns: {sorted(missing)}")
    return sheet_name, header_row, frame


def fetch_geo_records() -> tuple[dict[str, dict[str, str]], str]:
    request = Request(GEO_MATRIX_URL, headers={"User-Agent": "RNA-Transformer-validation/1.0"})
    with urlopen(request, timeout=30) as response:
        compressed = response.read()
    text = gzip.decompress(compressed).decode("utf-8")
    rows: dict[str, list[str]] = {}
    series_accession_found = False
    for line in text.splitlines():
        if line.startswith("!Series_geo_accession\t"):
            fields = next(csv.reader([line], delimiter="\t", quotechar='"'))
            if len(fields) < 2 or fields[1] != "GSE272042":
                raise ValueError("GEO matrix does not identify itself as GSE272042.")
            series_accession_found = True
        if line.startswith(("!Sample_geo_accession\t", "!Sample_title\t", "!Sample_description\t")):
            fields = next(csv.reader([line], delimiter="\t", quotechar='"'))
            rows[fields[0]] = fields[1:]

    required = (
        "!Sample_geo_accession",
        "!Sample_title",
        "!Sample_description",
    )
    if not series_accession_found:
        raise ValueError("GEO matrix is missing its GSE272042 series accession.")
    if any(key not in rows for key in required):
        raise ValueError("GEO matrix is missing required sample metadata rows.")
    if len({len(rows[key]) for key in required}) != 1:
        raise ValueError("GEO sample metadata rows have inconsistent lengths.")

    accessions, titles, descriptions = (rows[key] for key in required)
    if len(accessions) != len(set(accessions)):
        raise ValueError("GEO matrix contains duplicate sample accessions.")
    records = {
        accession: {"title": title, "description": description}
        for accession, title, description in zip(
            accessions, titles, descriptions, strict=True
        )
    }
    return records, hashlib.sha256(compressed).hexdigest()


def format_values(values: list[object]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "None"


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |"
        for row in rows
    )
    return "\n".join(lines)


def create_report() -> tuple[str, bool]:
    if not EXPRESSION_PATH.is_file():
        raise FileNotFoundError(f"Expression file not found: {EXPRESSION_PATH}")
    if not METADATA_PATH.is_file():
        raise FileNotFoundError(f"Supplementary workbook not found: {METADATA_PATH}")

    sheet_name, header_row, metadata = find_metadata_table(METADATA_PATH)
    expression = pd.read_csv(EXPRESSION_PATH, compression="gzip")
    if expression.shape[1] < 2:
        raise ValueError("Expression table must contain a gene column and sample columns.")

    with gzip.open(EXPRESSION_PATH, "rt", encoding="utf-8-sig", newline="") as source:
        raw_expression_headers = next(csv.reader(source))
    expression_ids = [str(value).strip() for value in raw_expression_headers[1:]]
    if len(expression_ids) != len(expression.columns) - 1:
        raise ValueError("Raw expression headers do not match parsed expression columns.")
    gene_ids = expression.iloc[:, 0].astype("string").str.strip()
    metadata_ids = metadata["Sample"].astype("string").str.strip()
    metadata_gsm = metadata["RNA-seq"].astype("string").str.strip()
    metadata_gsm_present = metadata_gsm.notna() & metadata_gsm.ne("")
    metadata_gsm_missing = int((~metadata_gsm_present).sum())
    duplicate_gsm_ids = int(metadata_gsm[metadata_gsm_present].duplicated().sum())
    metadata_numbers = metadata_ids.map(parse_sample_number)
    metadata_with_numbers = metadata.loc[metadata_numbers.notna()].copy()
    metadata_with_numbers["_sample_number"] = metadata_numbers[metadata_numbers.notna()]
    metadata_number_counts = metadata_with_numbers["_sample_number"].value_counts()
    metadata_duplicates = metadata_number_counts[metadata_number_counts > 1].index.tolist()
    metadata_by_number = {
        str(row["_sample_number"]): row
        for _, row in metadata_with_numbers.iterrows()
        if metadata_number_counts[str(row["_sample_number"])] == 1
    }

    expression_numbers = [parse_sample_number(f"Sample {value}") for value in expression_ids]
    expression_numbers = [
        value if value is not None else sample_id
        for sample_id, value in zip(expression_ids, expression_numbers, strict=True)
    ]
    expression_duplicates = pd.Series(expression_ids).duplicated(keep=False)
    expression_duplicate_ids = sorted(
        set(pd.Series(expression_ids)[expression_duplicates].tolist())
    )
    invalid_expression_ids = [
        value for value in expression_ids if not re.fullmatch(r"\d+", value)
    ]

    matched_numbers = [
        number for number in expression_numbers if number in metadata_by_number
    ]
    expression_unmatched = [
        sample_id
        for sample_id, number in zip(expression_ids, expression_numbers, strict=True)
        if number not in metadata_by_number
    ]
    metadata_with_rnaseq_numbers = {
        str(number)
        for number in metadata_with_numbers.loc[
            metadata_gsm_present, "_sample_number"
        ]
    }
    metadata_only_numbers = sorted(
        metadata_with_rnaseq_numbers.difference(expression_numbers), key=int
    )
    metadata_without_rnaseq = metadata.loc[~metadata_gsm_present]

    numeric_values = expression.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    raw_values = expression.iloc[:, 1:]
    missing_values = int(expression.isna().sum().sum())
    nonnumeric_values = int(
        (numeric_values.isna() & raw_values.notna()).sum().sum()
    )
    values_array = numeric_values.to_numpy(dtype=float)
    nonfinite_values = int((~np.isfinite(values_array)).sum())
    negative_values = int((values_array < 0).sum())
    missing_gene_ids = int(gene_ids.isna().sum() + gene_ids.eq("").sum())
    duplicate_gene_ids = int(gene_ids.dropna().duplicated().sum())

    metadata_sample_missing = int(metadata_ids.isna().sum() + metadata_ids.eq("").sum())
    missing_diagnoses = int(
        metadata["Diagnosis"].isna().sum()
        + metadata["Diagnosis"].astype("string").str.strip().eq("").sum()
    )
    patient_columns = [
        str(column)
        for column in metadata.columns
        if any(term in str(column).casefold() for term in PATIENT_COLUMN_TERMS)
    ]

    geo_records: dict[str, dict[str, str]] = {}
    geo_hash: str | None = None
    geo_error: str | None = None
    try:
        geo_records, geo_hash = fetch_geo_records()
    except (OSError, URLError, gzip.BadGzipFile, UnicodeDecodeError, ValueError) as error:
        geo_error = f"{type(error).__name__}: {error}"

    geo_title_matches = 0
    geo_label_matches = 0
    geo_label_differences: list[list[object]] = []
    geo_mapping_problems: list[str] = []
    for sample_id, number in zip(expression_ids, expression_numbers, strict=True):
        if number not in metadata_by_number:
            continue
        row = metadata_by_number[number]
        accession = normalize_label(row["RNA-seq"])
        if not accession:
            geo_mapping_problems.append(
                f"Sample {number}: Supplementary Table S1 has no RNA-seq accession."
            )
            continue
        geo_record = geo_records.get(accession)
        if geo_error is not None:
            continue
        if geo_record is None:
            geo_mapping_problems.append(
                f"Sample {number} ({accession}): accession absent from GEO matrix."
            )
            continue
        if str(row["Sample"]).strip() == geo_record["title"].strip():
            geo_title_matches += 1
        else:
            geo_mapping_problems.append(
                f"Sample {number} ({accession}): metadata sample name "
                f"{row['Sample']!r} differs from GEO title {geo_record['title']!r}."
            )
        supplementary_label = normalize_label(row["Diagnosis"])
        geo_label = normalize_label(geo_record["description"])
        if supplementary_label == geo_label:
            geo_label_matches += 1
        else:
            geo_label_differences.append(
                [f"Sample {number}", accession, supplementary_label, geo_label]
            )

    matched_rows = [
        metadata_by_number[number]
        for number in expression_numbers
        if number in metadata_by_number
    ]
    matched_label_counts = pd.Series(
        [normalize_label(row["Diagnosis"]) for row in matched_rows], dtype="string"
    ).value_counts(dropna=False)
    all_metadata_label_counts = pd.Series(
        [normalize_label(value) for value in metadata["Diagnosis"]], dtype="string"
    ).value_counts(dropna=False)

    identifier_mapping_verified = (
        len(expression_ids) == len(matched_numbers)
        and not expression_unmatched
        and not metadata_duplicates
        and not expression_duplicate_ids
        and not duplicate_gsm_ids
        and not invalid_expression_ids
        and geo_error is None
        and not geo_mapping_problems
        and geo_title_matches == len(expression_ids)
    )
    labels_agree_with_geo = (
        geo_error is None
        and not geo_label_differences
        and geo_label_matches == len(expression_ids)
    )
    model_ready = (
        identifier_mapping_verified
        and labels_agree_with_geo
        and not missing_diagnoses
        and not missing_values
        and not nonnumeric_values
        and not nonfinite_values
        and not negative_values
        and not missing_gene_ids
        and not duplicate_gene_ids
        and bool(patient_columns)
    )
    status = "PASS" if model_ready else (
        "IDENTIFIERS VERIFIED; MODELING BLOCKED"
        if identifier_mapping_verified
        else "VALIDATION INCOMPLETE"
    )

    metadata_sample_list = [
        f"{str(row['Sample']).strip()} → {normalize_label(row['RNA-seq']) or 'no RNA-seq GSM'}"
        for _, row in metadata.iterrows()
    ]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# RNA-seq Dataset Validation",
        "",
        f"- **Status:** {status}",
        f"- **Generated (UTC):** {now}",
        "- **Model training:** Not performed.",
        f"- **Supplementary workbook:** `{METADATA_PATH.relative_to(PROJECT_ROOT)}`",
        f"- **Expression file:** `{EXPRESSION_PATH.relative_to(PROJECT_ROOT)}`",
        f"- **Workbook SHA-256:** `{sha256_file(METADATA_PATH)}`",
        f"- **Expression SHA-256:** `{sha256_file(EXPRESSION_PATH)}`",
        f"- **GEO source:** [{GEO_MATRIX_URL}]({GEO_MATRIX_URL})",
        f"- **GEO compressed-file SHA-256:** `{geo_hash or 'unavailable'}`",
        "",
        "## Workbook structure",
        "",
        f"- Sheet: `{sheet_name}`; header row: {header_row + 1} (1-based).",
        f"- Data rows: {len(metadata)}.",
        f"- Columns: {', '.join(f'`{column}`' for column in metadata.columns)}.",
        f"- Rows with RNA-seq GSM: {int(metadata_gsm.notna().sum())}; without RNA-seq GSM: {metadata_gsm_missing}.",
        f"- Patient/group identifier columns detected: {format_values(patient_columns)}.",
        "",
        "## Sample alignment",
        "",
        markdown_table(
            ["Check", "Count"],
            [
                ["Expression sample columns", len(expression_ids)],
                ["Metadata sample rows", len(metadata)],
                ["Metadata rows with RNA-seq accession", int(metadata_gsm_present.sum())],
                ["Expression samples matched to one unique metadata sample", len(matched_numbers)],
                ["Expression samples unmatched", len(expression_unmatched)],
                ["Metadata rows with RNA-seq but absent from expression", len(metadata_only_numbers)],
                ["Metadata rows with no RNA-seq accession", metadata_gsm_missing],
                ["Expression sample names matched to GEO titles", geo_title_matches],
            ],
        ),
        "",
        f"- Expression sample IDs: {format_values(expression_ids)}",
        f"- Metadata sample IDs and RNA-seq accessions ({len(metadata_sample_list)} rows): "
        f"{'; '.join(metadata_sample_list)}",
        f"- Expression sample IDs without a unique metadata match: {format_values(expression_unmatched)}",
        f"- Metadata sample IDs with RNA-seq but absent from expression: "
        f"{format_values([metadata_by_number[n]['Sample'] for n in metadata_only_numbers])}",
        f"- Metadata sample IDs without RNA-seq accessions: "
        f"{format_values(metadata_without_rnaseq['Sample'].astype(str).tolist())}",
        "",
        "## Diagnostic class counts",
        "",
        "Counts below use the Supplementary Table S1 diagnosis labels; whitespace "
        "including non-breaking spaces is normalized for display only.",
        "",
        markdown_table(
            ["Supplementary Table S1 diagnosis", "Matched expression samples"],
            [[str(label), int(count)] for label, count in matched_label_counts.items()],
        ),
        "",
        markdown_table(
            ["Supplementary Table S1 diagnosis", "All metadata rows"],
            [[str(label), int(count)] for label, count in all_metadata_label_counts.items()],
        ),
        "",
        "## Missing values, duplicates, and expression validity",
        "",
        markdown_table(
            ["Check", "Result"],
            [
                ["Missing metadata sample IDs", metadata_sample_missing],
                ["Duplicate metadata sample IDs", len(metadata_duplicates)],
                ["Missing RNA-seq GSM accessions", metadata_gsm_missing],
                ["Duplicate RNA-seq GSM accessions", duplicate_gsm_ids],
                ["Missing diagnosis labels", missing_diagnoses],
                ["Duplicate expression sample headers", len(expression_duplicate_ids)],
                ["Non-numeric expression sample headers", len(invalid_expression_ids)],
                ["Missing expression/gene cells", missing_values],
                ["Missing gene identifiers", missing_gene_ids],
                ["Duplicate gene identifiers", duplicate_gene_ids],
                ["Non-numeric expression values", nonnumeric_values],
                ["Non-finite expression values", nonfinite_values],
                ["Negative expression values", negative_values],
            ],
        ),
        "",
        f"- Duplicate metadata sample IDs: {format_values(metadata_duplicates)}",
        f"- Duplicate expression headers: {format_values(expression_duplicate_ids)}",
        "",
        "## Official GEO cross-check",
        "",
        (
            f"- GEO records retrieved: {len(geo_records)}; sample-name/accession "
            f"matches: {geo_title_matches}/{len(expression_ids)}."
            if geo_error is None
            else f"- GEO retrieval failed: `{geo_error}`."
        ),
        f"- Diagnosis labels matching GEO descriptions after whitespace-only normalization: "
        f"{geo_label_matches}/{len(expression_ids)}.",
        (
            markdown_table(
                [
                    "Sample",
                    "GEO accession",
                    "Supplementary Table S1 diagnosis",
                    "GEO sample description",
                ],
                geo_label_differences,
            )
            if geo_label_differences
            else "No diagnosis-text discrepancies found."
        ),
        "",
        f"- Other GEO mapping issues: {format_values(geo_mapping_problems)}",
        "",
        "## Patient-grouped splitting",
        "",
        (
            f"Candidate patient/group columns: {format_values(patient_columns)}."
            if patient_columns
            else "The inspected metadata has no patient, donor, subject, case, or individual identifier. "
            "Whether multiple samples belong to one patient cannot be determined; patient-grouped "
            "splitting is not supported by these files."
        ),
        "",
        "## Gate / next action",
        "",
        (
            "Sample identity mapping is verified, but modeling remains blocked until the seven "
            "diagnosis discrepancies with GEO are resolved by the dataset owner and a patient-level "
            "group identifier (or confirmation that samples are independent) is obtained. No "
            "diagnosis was inferred, rewritten, or dropped."
            if identifier_mapping_verified and (not labels_agree_with_geo or not patient_columns)
            else (
                "Resolve all listed missing, duplicate, invalid, and GEO mapping issues before "
                "using the dataset for modeling."
                if not identifier_mapping_verified
                else "All validation checks passed."
            )
        ),
        "",
        "The validator does not discard unmatched samples and does not train models.",
        "",
    ]
    return "\n".join(lines), model_ready


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        report, model_ready = create_report()
    except (FileNotFoundError, ImportError, OSError, ValueError) as error:
        report = (
            "# RNA-seq Dataset Validation\n\n"
            "**Status: VALIDATION INCOMPLETE**\n\n"
            f"Validation stopped explicitly: `{type(error).__name__}: {error}`\n\n"
            "No samples were matched or discarded and no models were trained.\n"
        )
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Validation incomplete; report written to {REPORT_PATH}")
        print(error, file=sys.stderr)
        return 2

    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Validation report written to {REPORT_PATH}")
    print(report.splitlines()[2])
    return 0 if model_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
