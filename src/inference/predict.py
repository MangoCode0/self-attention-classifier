
from pathlib import Path

import pandas as pd
import joblib
import numpy as np
import torch

from src.data.load_data import load_expression_data
from src.data.preprocessing import normalize_sample_id
from src.models.attention_classifier import (
    GeneExpressionAttentionClassifier,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "models" / "saved"

LABELS = {
    0: "Other diagnoses",
    1: "Glioblastoma, IDH wildtype",
}


def load_saved_model():
    """Load trained model and preprocessing objects."""

    preprocessing = joblib.load(
        MODEL_DIR / "preprocessing.joblib"
    )

    checkpoint = torch.load(
        MODEL_DIR / "self_attention_model.pt",
        map_location="cpu",
        weights_only=True,
    )

    model = GeneExpressionAttentionClassifier(
        num_genes=checkpoint["num_genes"],
        embed_dim=checkpoint["embed_dim"],
        hidden_dim=checkpoint["hidden_dim"],
        num_classes=checkpoint["num_classes"],
        dropout=checkpoint["dropout"],
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model, preprocessing


def predict_sample(sample_id):
    """Predict the class of an existing expression-dataset sample."""

    expression = load_expression_data()

    target_id = normalize_sample_id(sample_id)

    if target_id is None:
        raise ValueError("Invalid sample ID.")

    matching_columns = [
        column
        for column in expression.columns
        if normalize_sample_id(column) == target_id
    ]

    if not matching_columns:
        raise ValueError(f"Sample {sample_id} not found.")

    model, preprocessing = load_saved_model()

    selected_genes = preprocessing["selected_genes"]
    scaler = preprocessing["scaler"]

    missing_genes = [
        gene for gene in selected_genes
        if gene not in expression.index
    ]

    if missing_genes:
        raise ValueError(
            f"{len(missing_genes)} selected genes are missing."
        )

    # Extract the sample's selected gene-expression values.
    sample = expression.loc[
        selected_genes, matching_columns[0]
    ].astype(float)

    sample = np.log1p(sample.to_numpy()).reshape(1, -1)

    # Use the scaler fitted during training.
    sample_df = pd.DataFrame(
        sample,
        columns=selected_genes,
    )

    sample_scaled = scaler.transform(sample_df)

    input_tensor = torch.tensor(
        sample_scaled,
        dtype=torch.float32,
    )

    with torch.no_grad():
        logits, attention_weights = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)[0].numpy()

    predicted_class = int(np.argmax(probabilities))

    result = {
        "sample_id": target_id,
        "predicted_class": predicted_class,
        "prediction": LABELS[predicted_class],
        "probabilities": {
            LABELS[0]: float(probabilities[0]),
            LABELS[1]: float(probabilities[1]),
        },
        "attention_shape": list(attention_weights.shape),
    }

    return result


if __name__ == "__main__":
    sample_id = input("Enter sample ID (e.g. 126): ")

    result = predict_sample(sample_id)

    print("\nPrediction result")
    print("-----------------")
    print("Sample:", result["sample_id"])
    print("Prediction:", result["prediction"])
    print("\nClass probabilities:")

    for label, probability in result["probabilities"].items():
        print(f"{label}: {probability * 100:.2f}%")

    print("\nNote: Research prototype only, not a clinical diagnosis.")
