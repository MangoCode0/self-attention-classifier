
from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw/GSE272042_tpmALL.csv.gz")

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH.resolve()}"
    )

df = pd.read_csv(DATA_PATH, compression="gzip", nrows=5)

print("\n--- First 5 rows ---")
print(df.to_string(max_cols=8))

print("\n--- File overview ---")
print("Columns:", len(df.columns))
print("Preview shape:", df.shape)
print("Column names:")
print(df.columns.tolist()[:15])

print("\n--- Data types ---")
print(df.dtypes.value_counts())

print("\nDataset loaded successfully for initial inspection.")
