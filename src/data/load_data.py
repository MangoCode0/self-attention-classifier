
from pathlib import Path

import pandas as pd


# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

EXPRESSION_FILE = DATA_DIR / "GSE272042_tpmALL.csv.gz"
METADATA_FILE = DATA_DIR / "41597_2025_4597_MOESM1_ESM.xlsx"


def load_expression_data():
    """Load gene-expression data."""

    if not EXPRESSION_FILE.exists():
        raise FileNotFoundError(
            f"Expression dataset not found: {EXPRESSION_FILE}"
        )

    expression = pd.read_csv(
        EXPRESSION_FILE,
        compression="gzip",
        index_col=0,
    )

    expression.index = expression.index.astype(str)
    expression.columns = expression.columns.astype(str)

    print("Expression data loaded successfully.")
    print("Expression shape:", expression.shape)

    return expression


def load_metadata():
    """Load sample metadata from the supplementary Excel file."""

    if not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_FILE}"
        )

    # The notebook's metadata sheet has introductory rows.
    metadata = pd.read_excel(
        METADATA_FILE,
        header=2,
    )

    metadata.columns = (
        metadata.columns.astype(str).str.strip()
    )

    metadata = metadata.dropna(how="all").reset_index(drop=True)

    required_columns = {"Sample", "Diagnosis"}
    missing = required_columns - set(metadata.columns)

    if missing:
        raise ValueError(
            f"Expected metadata columns are missing: {sorted(missing)}. "
            f"Available columns: {metadata.columns.tolist()}"
        )

    print("Metadata loaded successfully.")
    print("Metadata shape:", metadata.shape)
    print("Metadata columns:", metadata.columns.tolist())

    return metadata


if __name__ == "__main__":
    expression = load_expression_data()
    metadata = load_metadata()

    print("\nExpression preview:")
    print(expression.iloc[:5, :5])

    print("\nMetadata preview:")
    print(metadata.head().to_string(index=False))
