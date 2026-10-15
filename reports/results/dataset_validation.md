# RNA-seq Dataset Validation

- **Status:** IDENTIFIERS VERIFIED; MODELING BLOCKED
- **Generated (UTC):** 2026-10-14T23:23:47+00:00
- **Model training:** Not performed.
- **Supplementary workbook:** `data\raw\41597_2025_4597_MOESM1_ESM.xlsx`
- **Expression file:** `data\raw\GSE272042_tpmALL.csv.gz`
- **Workbook SHA-256:** `d06d321f349a178b9ad52838556c529f7ebf976b13697b805110df195955f3a1`
- **Expression SHA-256:** `512aa69b2820e10207e48962cf14372bbb28dffbd61246b390eb4e9e08c857d2`
- **GEO source:** [https://ftp.ncbi.nlm.nih.gov/geo/series/GSE272nnn/GSE272042/matrix/GSE272042_series_matrix.txt.gz](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE272nnn/GSE272042/matrix/GSE272042_series_matrix.txt.gz)
- **GEO compressed-file SHA-256:** `7b7ce2da3bd28f621fa85da1334ca72e5cec9bdcbc9b708f7a7c4b7331352aaf`

## Workbook structure

- Sheet: `Hoja1`; header row: 3 (1-based).
- Data rows: 185.
- Columns: `Sample`, `RNA-seq`, `Methylation beadchips`, `Diagnosis`.
- Rows with RNA-seq GSM: 153; without RNA-seq GSM: 32.
- Patient/group identifier columns detected: None.

## Sample alignment

| Check | Count |
| --- | --- |
| Expression sample columns | 153 |
| Metadata sample rows | 185 |
| Metadata rows with RNA-seq accession | 153 |
| Expression samples matched to one unique metadata sample | 153 |
| Expression samples unmatched | 0 |
| Metadata rows with RNA-seq but absent from expression | 0 |
| Metadata rows with no RNA-seq accession | 32 |
| Expression sample names matched to GEO titles | 153 |

- Expression sample IDs: `126`, `134`, `140`, `156`, `157`, `159`, `160`, `161`, `171`, `219`, `232`, `274`, `280`, `294`, `322`, `138`, `228`, `286`, `287`, `293`, `299`, `320`, `351`, `361`, `362`, `364`, `365`, `366`, `367`, `372`, `300`, `327`, `344`, `360`, `411`, `414`, `415`, `417`, `426`, `442`, `443`, `444`, `445`, `448`, `461`, `117`, `144`, `152`, `193`, `209`, `216`, `225`, `276`, `279`, `306`, `313`, `316`, `428`, `430`, `453`, `465`, `104`, `132`, `141`, `190`, `192`, `198`, `203`, `205`, `218`, `256`, `272`, `278`, `328`, `330`, `343`, `120`, `133`, `136`, `151`, `183`, `197`, `233`, `238`, `337`, `410`, `413`, `75`, `83`, `84`, `88`, `98`, `31`, `32`, `42`, `73`, `81`, `95`, `158`, `166`, `199`, `208`, `214`, `236`, `249`, `253`, `416`, `466`, `105`, `110`, `12`, `128`, `16`, `184`, `19`, `227`, `29`, `3`, `46`, `58`, `61`, `91`, `102`, `254`, `255`, `346`, `36`, `363`, `41`, `438`, `439`, `440`, `458`, `460`, `66`, `67`, `92`, `100`, `106`, `109`, `121`, `122`, `2`, `24`, `35`, `54`, `68`, `76`, `77`, `79`, `8`, `89`, `90`
- Metadata sample IDs and RNA-seq accessions (185 rows): Sample 100 → GSM8391697; Sample 102 → GSM8391676; Sample 104 → GSM8391763; Sample 105 → GSM8391666; Sample 106 → GSM8391698; Sample 109 → GSM8391699; Sample 110 → GSM8391667; Sample 117 → GSM8391747; Sample 12 → GSM8391658; Sample 120 → GSM8391783; Sample 121 → GSM8391700; Sample 122 → GSM8391701; Sample 126 → GSM8391702; Sample 128 → GSM8391668; Sample 132 → GSM8391764; Sample 133 → GSM8391784; Sample 134 → GSM8391703; Sample 136 → GSM8391785; Sample 138 → GSM8391717; Sample 140 → GSM8391704; Sample 141 → GSM8391765; Sample 144 → GSM8391748; Sample 151 → GSM8391786; Sample 152 → GSM8391749; Sample 156 → GSM8391705; Sample 157 → GSM8391706; Sample 158 → GSM8391647; Sample 159 → GSM8391707; Sample 16 → GSM8391659; Sample 160 → GSM8391708; Sample 161 → GSM8391709; Sample 162 → no RNA-seq GSM; Sample 166 → GSM8391648; Sample 171 → GSM8391710; Sample 183 → GSM8391787; Sample 184 → GSM8391669; Sample 19 → GSM8391660; Sample 190 → GSM8391766; Sample 192 → GSM8391767; Sample 193 → GSM8391750; Sample 197 → GSM8391788; Sample 198 → GSM8391768; Sample 199 → GSM8391649; Sample 2 → GSM8391686; Sample 203 → GSM8391769; Sample 205 → GSM8391770; Sample 208 → GSM8391650; Sample 209 → GSM8391751; Sample 214 → GSM8391651; Sample 216 → GSM8391752; Sample 218 → GSM8391771; Sample 219 → GSM8391711; Sample 225 → GSM8391753; Sample 227 → GSM8391670; Sample 228 → GSM8391718; Sample 230 → no RNA-seq GSM; Sample 232 → GSM8391712; Sample 233 → GSM8391789; Sample 236 → GSM8391652; Sample 238 → GSM8391790; Sample 24 → GSM8391688; Sample 242 → no RNA-seq GSM; Sample 246 → no RNA-seq GSM; Sample 249 → GSM8391653; Sample 253 → GSM8391654; Sample 254 → GSM8391677; Sample 255 → GSM8391678; Sample 256 → GSM8391772; Sample 260 → no RNA-seq GSM; Sample 272 → GSM8391773; Sample 273 → no RNA-seq GSM; Sample 274 → GSM8391713; Sample 276 → GSM8391754; Sample 278 → GSM8391774; Sample 279 → GSM8391755; Sample 280 → GSM8391714; Sample 282 → no RNA-seq GSM; Sample 286 → GSM8391719; Sample 287 → GSM8391720; Sample 29 → GSM8391661; Sample 293 → GSM8391721; Sample 294 → GSM8391715; Sample 299 → GSM8391722; Sample 3 → GSM8391657; Sample 300 → GSM8391732; Sample 301 → no RNA-seq GSM; Sample 305 → no RNA-seq GSM; Sample 306 → GSM8391756; Sample 31 → GSM8391641; Sample 313 → GSM8391757; Sample 316 → GSM8391758; Sample 32 → GSM8391642; Sample 320 → GSM8391723; Sample 322 → GSM8391716; Sample 326 → no RNA-seq GSM; Sample 327 → GSM8391733; Sample 328 → GSM8391775; Sample 330 → GSM8391776; Sample 331 → no RNA-seq GSM; Sample 333 → no RNA-seq GSM; Sample 336 → no RNA-seq GSM; Sample 337 → GSM8391791; Sample 340 → no RNA-seq GSM; Sample 342 → no RNA-seq GSM; Sample 343 → GSM8391777; Sample 344 → GSM8391734; Sample 346 → GSM8391679; Sample 347 → no RNA-seq GSM; Sample 35 → GSM8391689; Sample 351 → GSM8391724; Sample 36 → GSM8391671; Sample 360 → GSM8391735; Sample 361 → GSM8391725; Sample 362 → GSM8391726; Sample 363 → GSM8391680; Sample 364 → GSM8391727; Sample 365 → GSM8391728; Sample 366 → GSM8391729; Sample 367 → GSM8391730; Sample 369 → no RNA-seq GSM; Sample 372 → GSM8391731; Sample 397 → no RNA-seq GSM; Sample 399 → no RNA-seq GSM; Sample 4 → no RNA-seq GSM; Sample 400 → no RNA-seq GSM; Sample 406 → no RNA-seq GSM; Sample 408 → no RNA-seq GSM; Sample 41 → GSM8391672; Sample 410 → GSM8391792; Sample 411 → GSM8391736; Sample 413 → GSM8391793; Sample 414 → GSM8391737; Sample 415 → GSM8391738; Sample 416 → GSM8391655; Sample 417 → GSM8391739; Sample 42 → GSM8391643; Sample 421 → no RNA-seq GSM; Sample 422 → no RNA-seq GSM; Sample 423 → no RNA-seq GSM; Sample 426 → GSM8391740; Sample 428 → GSM8391759; Sample 430 → GSM8391760; Sample 436 → no RNA-seq GSM; Sample 438 → GSM8391681; Sample 439 → GSM8391682; Sample 440 → GSM8391683; Sample 442 → GSM8391741; Sample 443 → GSM8391742; Sample 444 → GSM8391743; Sample 445 → GSM8391744; Sample 448 → GSM8391745; Sample 450 → no RNA-seq GSM; Sample 451 → no RNA-seq GSM; Sample 453 → GSM8391761; Sample 456 → no RNA-seq GSM; Sample 457 → no RNA-seq GSM; Sample 458 → GSM8391684; Sample 46 → GSM8391662; Sample 460 → GSM8391685; Sample 461 → GSM8391746; Sample 465 → GSM8391762; Sample 466 → GSM8391656; Sample 54 → GSM8391690; Sample 58 → GSM8391663; Sample 6 → no RNA-seq GSM; Sample 61 → GSM8391664; Sample 66 → GSM8391673; Sample 67 → GSM8391674; Sample 68 → GSM8391691; Sample 73 → GSM8391644; Sample 75 → GSM8391778; Sample 76 → GSM8391692; Sample 77 → GSM8391693; Sample 79 → GSM8391694; Sample 8 → GSM8391687; Sample 81 → GSM8391645; Sample 83 → GSM8391779; Sample 84 → GSM8391780; Sample 88 → GSM8391781; Sample 89 → GSM8391695; Sample 90 → GSM8391696; Sample 91 → GSM8391665; Sample 92 → GSM8391675; Sample 95 → GSM8391646; Sample 98 → GSM8391782
- Expression sample IDs without a unique metadata match: None
- Metadata sample IDs with RNA-seq but absent from expression: None
- Metadata sample IDs without RNA-seq accessions: `Sample 162`, `Sample 230`, `Sample 242`, `Sample 246`, `Sample 260`, `Sample 273`, `Sample 282`, `Sample 301`, `Sample 305`, `Sample 326`, `Sample 331`, `Sample 333`, `Sample 336`, `Sample 340`, `Sample 342`, `Sample 347`, `Sample 369`, `Sample 397`, `Sample 399`, `Sample 4`, `Sample 400`, `Sample 406`, `Sample 408`, `Sample 421`, `Sample 422`, `Sample 423`, `Sample 436`, `Sample 450`, `Sample 451`, `Sample 456`, `Sample 457`, `Sample 6`

## Diagnostic class counts

Counts below use the Supplementary Table S1 diagnosis labels; whitespace including non-breaking spaces is normalized for display only.

| Supplementary Table S1 diagnosis | Matched expression samples |
| --- | --- |
| Glioblastoma, IDH wildtype | 113 |
| Oligodendroglioma, IDH-mutant and 1p/19q-codeleted, grade 2 | 9 |
| Astrocytoma, IDH-mutant, grade 2 | 7 |
| Supratentorial ependymoma | 7 |
| Pilocytic astrocytoma | 6 |
| Astrocytoma, IDH-mutant, grade 3 | 5 |
| Ganglioglioma | 3 |
| Oligodendroglioma, IDH-mutant and 1p/19q-codeleted, grade 3 | 3 |

| Supplementary Table S1 diagnosis | All metadata rows |
| --- | --- |
| Glioblastoma, IDH wildtype | 139 |
| Oligodendroglioma, IDH-mutant and 1p/19q-codeleted, grade 2 | 10 |
| Supratentorial ependymoma | 9 |
| Astrocytoma, IDH-mutant, grade 2 | 8 |
| Pilocytic astrocytoma | 7 |
| Astrocytoma, IDH-mutant, grade 3 | 5 |
| Oligodendroglioma, IDH-mutant and 1p/19q-codeleted, grade 3 | 4 |
| Ganglioglioma | 3 |

## Missing values, duplicates, and expression validity

| Check | Result |
| --- | --- |
| Missing metadata sample IDs | 0 |
| Duplicate metadata sample IDs | 0 |
| Missing RNA-seq GSM accessions | 32 |
| Duplicate RNA-seq GSM accessions | 0 |
| Missing diagnosis labels | 0 |
| Duplicate expression sample headers | 0 |
| Non-numeric expression sample headers | 0 |
| Missing expression/gene cells | 0 |
| Missing gene identifiers | 0 |
| Duplicate gene identifiers | 0 |
| Non-numeric expression values | 0 |
| Non-finite expression values | 0 |
| Negative expression values | 0 |

- Duplicate metadata sample IDs: None
- Duplicate expression headers: None

## Official GEO cross-check

- GEO records retrieved: 153; sample-name/accession matches: 153/153.
- Diagnosis labels matching GEO descriptions after whitespace-only normalization: 146/153.
| Sample | GEO accession | Supplementary Table S1 diagnosis | GEO sample description |
| --- | --- | --- | --- |
| Sample 216 | GSM8391752 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |
| Sample 430 | GSM8391760 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |
| Sample 12 | GSM8391658 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |
| Sample 91 | GSM8391665 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |
| Sample 102 | GSM8391676 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |
| Sample 254 | GSM8391677 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |
| Sample 346 | GSM8391679 | Supratentorial ependymoma | Supratentorial ependymoma, NOS |

- Other GEO mapping issues: None

## Patient-grouped splitting

The inspected metadata has no patient, donor, subject, case, or individual identifier. Whether multiple samples belong to one patient cannot be determined; patient-grouped splitting is not supported by these files.

## Gate / next action

Sample identity mapping is verified, but modeling remains blocked until the seven diagnosis discrepancies with GEO are resolved by the dataset owner and a patient-level group identifier (or confirmation that samples are independent) is obtained. No diagnosis was inferred, rewritten, or dropped.

The validator does not discard unmatched samples and does not train models.
