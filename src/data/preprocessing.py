
import re

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
TOP_K_GENES = 500
POSITIVE_DIAGNOSIS = "Glioblastoma, IDH wildtype"


def normalize_sample_id(value):
    """Normalize numeric IDs and values such as 'Sample 126'."""
    text = str(value).strip()

    match = re.fullmatch(
        r"(?:Sample\s*)?(\d+)",
        text,
        flags=re.IGNORECASE,
    )

    return match.group(1) if match else None


def prepare_dataset(expression, metadata):
    """Match metadata Sample IDs with expression column IDs."""

    required = {"Sample", "Diagnosis"}
    missing = required - set(metadata.columns)

    if missing:
        raise ValueError(f"Missing metadata columns: {sorted(missing)}")

    # Normalize expression columns, for example '126' -> '126'.
    expression_id_to_column = {}

    for column in expression.columns:
        sample_id = normalize_sample_id(column)

        if sample_id is not None:
            if sample_id in expression_id_to_column:
                raise ValueError(
                    f"Duplicate normalized expression ID: {sample_id}"
                )
            expression_id_to_column[sample_id] = column

    metadata = metadata.copy()
    metadata["sample_id"] = metadata["Sample"].apply(
        normalize_sample_id
    )

    metadata["Diagnosis"] = (
        metadata["Diagnosis"]
        .astype("string")
        .str.replace("\u00a0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    metadata = metadata.dropna(
        subset=["sample_id", "Diagnosis"]
    )
    metadata = metadata.drop_duplicates(
        subset=["sample_id"],
        keep="first",
    )

    matched = metadata[
        metadata["sample_id"].isin(expression_id_to_column)
    ].copy()

    if matched.empty:
        raise ValueError(
            "No sample IDs matched. Check expression columns and "
            "metadata Sample values."
        )

    # Preserve metadata order when matching samples.
    expression_columns = [
        expression_id_to_column[sample_id]
        for sample_id in matched["sample_id"]
    ]

    X = expression.loc[:, expression_columns].T.copy()
    X.index = matched["sample_id"].tolist()
    X.index.name = "sample_id"

    diagnosis = matched["Diagnosis"].astype(str).tolist()

    y = pd.Series(
        [
            int(label.casefold() == POSITIVE_DIAGNOSIS.casefold())
            for label in diagnosis
        ],
        index=X.index,
        name="label",
        dtype="int64",
    )

    X = X.apply(pd.to_numeric, errors="coerce")

    if X.isna().any().any():
        raise ValueError("Expression data contains missing values.")

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("Expression data contains infinite values.")

    if y.nunique() != 2:
        raise ValueError("Both binary classes are required.")

    print("Matched samples:", len(X))
    print("Genes:", X.shape[1])
    print("Class counts:")
    print(y.value_counts().sort_index())

    return X, y, pd.Series(diagnosis, index=X.index, name="Diagnosis")


def create_splits(X, y):
    """Create stratified train, validation, and test splits."""

    indices = np.arange(len(X))

    train_val_idx, test_idx = train_test_split(
        indices,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    train_idx, val_idx = train_test_split(
        train_val_idx,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y.iloc[train_val_idx],
    )

    return {
        "X_train": X.iloc[train_idx].copy(),
        "X_val": X.iloc[val_idx].copy(),
        "X_test": X.iloc[test_idx].copy(),
        "y_train": y.iloc[train_idx].to_numpy(),
        "y_val": y.iloc[val_idx].to_numpy(),
        "y_test": y.iloc[test_idx].to_numpy(),
    }


def select_genes_and_scale(splits):
    """Select top genes and fit the scaler on training data only."""

    X_train = splits["X_train"]
    X_val = splits["X_val"]
    X_test = splits["X_test"]

    variable_genes = X_train.columns[X_train.var(axis=0) > 0]

    train_log = np.log1p(X_train[variable_genes])
    val_log = np.log1p(X_val[variable_genes])
    test_log = np.log1p(X_test[variable_genes])

    gene_variance = train_log.var(axis=0)
    selected_genes = gene_variance.nlargest(
        min(TOP_K_GENES, len(gene_variance))
    ).index

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(train_log[selected_genes])
    X_val_scaled = scaler.transform(val_log[selected_genes])
    X_test_scaled = scaler.transform(test_log[selected_genes])

    return {
        **splits,
        "X_train_scaled": X_train_scaled,
        "X_val_scaled": X_val_scaled,
        "X_test_scaled": X_test_scaled,
        "selected_genes": selected_genes.tolist(),
        "variable_genes": variable_genes.tolist(),
        "scaler": scaler,
    }
