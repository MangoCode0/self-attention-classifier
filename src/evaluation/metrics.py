
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


def calculate_metrics(y_true, y_pred):
    """Calculate classification metrics."""

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_true, y_pred)
        ),
        "macro_f1": float(
            f1_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(
            y_true, y_pred, labels=[0, 1]
        ).tolist(),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=[
                "Other diagnoses",
                "Glioblastoma, IDH wildtype",
            ],
            output_dict=True,
            zero_division=0,
        ),
    }


def save_metrics(metrics, output_path):
    """Save evaluation metrics as a JSON file."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print(f"Metrics saved to: {output_path}")


def print_metrics(metrics, model_name="Model"):
    """Print the main metrics in a readable format."""

    print(f"\n--- {model_name} Evaluation ---")
    print(f"Accuracy:          {metrics['accuracy']:.4f}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"Macro F1:          {metrics['macro_f1']:.4f}")
    print("Confusion matrix:")
    print(np.array(metrics["confusion_matrix"]))
