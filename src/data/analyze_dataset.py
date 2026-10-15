
from pathlib import Path
import pandas as pd

path = Path("data/raw/GSE272042_tpmALL.csv.gz")
df = pd.read_csv(path, compression="gzip")

print("Full dataset shape:", df.shape)
print("\nFirst 10 gene identifiers:")
print(df.iloc[:10, 0].to_list())

print("\nFirst 10 sample columns:")
print(df.columns[1:11].to_list())

print("\nFirst 10 rows, selected columns:")
print(df.iloc[:10, :6].to_string())

print("\nMissing values:", int(df.isna().sum().sum()))
print("Duplicate gene identifiers:", int(df.iloc[:, 0].duplicated().sum()))

print("\nSample column names:")
for col in df.columns[1:]:
    print(col)
