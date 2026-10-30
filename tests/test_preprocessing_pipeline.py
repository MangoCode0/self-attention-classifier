
from src.data.load_data import load_expression_data, load_metadata
from src.data.preprocessing import (
    prepare_dataset,
    create_splits,
    select_genes_and_scale,
)


def main():
    print("\n[1/4] Loading dataset...")
    expression = load_expression_data()
    metadata = load_metadata()

    print("\n[2/4] Matching samples and labels...")
    X, y, diagnoses = prepare_dataset(expression, metadata)

    print("Matched expression shape:", X.shape)
    print("Class counts:")
    print(y.value_counts().sort_index())

    print("\n[3/4] Creating data splits...")
    splits = create_splits(X, y)

    print("Training samples:", len(splits["X_train"]))
    print("Validation samples:", len(splits["X_val"]))
    print("Test samples:", len(splits["X_test"]))

    print("\n[4/4] Selecting genes and scaling...")
    processed = select_genes_and_scale(splits)

    print("Processed training shape:", processed["X_train_scaled"].shape)
    print("Processed validation shape:", processed["X_val_scaled"].shape)
    print("Processed test shape:", processed["X_test_scaled"].shape)
    print("Selected genes:", len(processed["selected_genes"]))

    print("\nPreprocessing pipeline completed successfully.")


if __name__ == "__main__":
    main()
