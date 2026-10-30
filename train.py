
import copy
import json
import random
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    ConfusionMatrixDisplay,
)

from src.data.load_data import load_expression_data, load_metadata
from src.data.preprocessing import (
    normalize_sample_id,
    prepare_dataset,
    create_splits,
    select_genes_and_scale,
)
from src.models.attention_classifier import (
    GeneExpressionAttentionClassifier,
)


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

SEED = 42
EPOCHS = 50
PATIENCE = 8
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-3

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_ROOT / "models" / "saved"
RESULTS_DIR = PROJECT_ROOT / "reports" / "results"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

for directory in (MODEL_DIR, RESULTS_DIR, FIGURES_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def calculate_metrics(y_true, y_pred):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_true, y_pred)
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
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


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# --------------------------------------------------
# 2. Load and align the dataset
# --------------------------------------------------

def main():
    set_seed()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    print("\n[1/7] Loading dataset...")
    expression = load_expression_data()
    metadata = load_metadata()

    X, y, diagnosis_labels = prepare_dataset(expression, metadata)

    # Preserve the original expression-column order used by the notebook.
    sample_order = [
        normalize_sample_id(column)
        for column in expression.columns
    ]

    if len(sample_order) != len(set(sample_order)):
        raise ValueError("Expression sample IDs are not unique.")

    X = X.loc[sample_order]
    y = y.loc[sample_order]
    diagnosis_labels = diagnosis_labels.loc[
        diagnosis_labels.index.isin(sample_order)
    ]

    # Re-align diagnosis labels directly to the ordered sample IDs.
    diagnosis_map = metadata.copy()
    diagnosis_map["sample_id"] = diagnosis_map["Sample"].apply(
        normalize_sample_id
    )
    diagnosis_map["Diagnosis"] = (
        diagnosis_map["Diagnosis"]
        .astype("string")
        .str.replace("\u00a0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    diagnosis_map = diagnosis_map.dropna(
        subset=["sample_id", "Diagnosis"]
    ).drop_duplicates("sample_id")

    diagnosis_by_id = diagnosis_map.set_index("sample_id")["Diagnosis"]
    diagnosis_labels = diagnosis_by_id.loc[sample_order]

    # Re-create the binary labels using the notebook's exact target.
    diagnosis_clean = (
        diagnosis_labels.astype(str)
        .str.replace("\u00a0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    y = (
        diagnosis_clean == "Glioblastoma, IDH wildtype"
    ).astype("int64")
    y.index = X.index

    if len(X) != 153 or int(y.sum()) != 113 or y.nunique() != 2:
        raise ValueError(
            "Dataset checks did not match the notebook expectations. "
            f"Samples={len(X)}, positive labels={int(y.sum())}, "
            f"classes={y.nunique()}. Stop and verify sample alignment."
        )

    print("Samples:", len(X))
    print("Genes:", X.shape[1])
    print("Class counts:")
    print(y.value_counts().sort_index().rename({
        0: "Other diagnoses",
        1: "Glioblastoma, IDH wildtype",
    }))

    # --------------------------------------------------
    # 3. Stratified train/validation/test split
    # --------------------------------------------------

    print("\n[2/7] Creating train/validation/test splits...")
    splits = create_splits(X, y)

    print("Train:", splits["X_train"].shape)
    print("Validation:", splits["X_val"].shape)
    print("Test:", splits["X_test"].shape)

    if (
        len(splits["X_train"]) != 97
        or len(splits["X_val"]) != 25
        or len(splits["X_test"]) != 31
    ):
        raise ValueError(
            "Split sizes differ from the notebook: expected 97/25/31."
        )

    # --------------------------------------------------
    # 4. Training-only gene selection and scaling
    # --------------------------------------------------

    print("\n[3/7] Selecting genes and scaling features...")
    processed = select_genes_and_scale(splits)

    X_train = processed["X_train_scaled"]
    X_val = processed["X_val_scaled"]
    X_test = processed["X_test_scaled"]

    y_train = processed["y_train"]
    y_val = processed["y_val"]
    y_test = processed["y_test"]

    print("Processed train:", X_train.shape)
    print("Processed validation:", X_val.shape)
    print("Processed test:", X_test.shape)

    if X_train.shape[1] != 500:
        raise ValueError("Expected 500 selected genes.")

    # Save preprocessing information for future inference.
    joblib.dump(
        {
            "selected_genes": processed["selected_genes"],
            "variable_genes": processed["variable_genes"],
            "scaler": processed["scaler"],
            "label_names": {
                0: "Other diagnoses",
                1: "Glioblastoma, IDH wildtype",
            },
        },
        MODEL_DIR / "preprocessing.joblib",
    )

    # --------------------------------------------------
    # 5. Train Self-Attention classifier
    # --------------------------------------------------

    print("\n[4/7] Training Self-Attention classifier...")

    X_train_tensor = torch.tensor(
        X_train, dtype=torch.float32, device=device
    )
    X_val_tensor = torch.tensor(
        X_val, dtype=torch.float32, device=device
    )
    X_test_tensor = torch.tensor(
        X_test, dtype=torch.float32, device=device
    )

    y_train_tensor = torch.tensor(
        y_train, dtype=torch.long, device=device
    )
    y_val_tensor = torch.tensor(
        y_val, dtype=torch.long, device=device
    )
    y_test_tensor = torch.tensor(
        y_test, dtype=torch.long, device=device
    )

    class_counts = torch.bincount(y_train_tensor, minlength=2)
    class_weights = len(y_train_tensor) / (
        2 * class_counts.float()
    )

    set_seed()
    model = GeneExpressionAttentionClassifier(
        num_genes=500,
        embed_dim=32,
        hidden_dim=32,
        num_classes=2,
        dropout=0.3,
    ).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    best_val_loss = float("inf")
    best_state = None
    best_epoch = 0
    patience_counter = 0

    history = {
        "train_loss": [],
        "val_loss": [],
        "train_accuracy": [],
        "val_accuracy": [],
    }

    for epoch in range(EPOCHS):
        model.train()
        optimizer.zero_grad()

        train_logits, _ = model(X_train_tensor)
        train_loss = criterion(train_logits, y_train_tensor)
        train_loss.backward()
        optimizer.step()

        train_accuracy = (
            train_logits.argmax(dim=1) == y_train_tensor
        ).float().mean().item()

        model.eval()
        with torch.no_grad():
            val_logits, _ = model(X_val_tensor)
            val_loss = criterion(val_logits, y_val_tensor)
            val_accuracy = (
                val_logits.argmax(dim=1) == y_val_tensor
            ).float().mean().item()

        train_loss_value = float(train_loss.item())
        val_loss_value = float(val_loss.item())

        history["train_loss"].append(train_loss_value)
        history["val_loss"].append(val_loss_value)
        history["train_accuracy"].append(train_accuracy)
        history["val_accuracy"].append(val_accuracy)

        if val_loss_value < best_val_loss:
            best_val_loss = val_loss_value
            best_epoch = epoch + 1
            best_state = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(
                f"Epoch {epoch + 1:02d}/{EPOCHS} | "
                f"Train loss: {train_loss_value:.4f} | "
                f"Val loss: {val_loss_value:.4f} | "
                f"Train acc: {train_accuracy:.3f} | "
                f"Val acc: {val_accuracy:.3f}"
            )

        if patience_counter >= PATIENCE:
            print(f"Early stopping at epoch {epoch + 1}.")
            break

    if best_state is None:
        raise RuntimeError("Training did not produce a valid checkpoint.")

    model.load_state_dict(best_state)
    model.eval()

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "num_genes": 500,
            "embed_dim": 32,
            "hidden_dim": 32,
            "num_classes": 2,
            "dropout": 0.3,
            "best_epoch": best_epoch,
            "best_validation_loss": best_val_loss,
            "seed": SEED,
        },
        MODEL_DIR / "self_attention_model.pt",
    )

    save_json(
        {
            **history,
            "best_epoch": best_epoch,
            "best_validation_loss": best_val_loss,
        },
        RESULTS_DIR / "training_history.json",
    )

    print("Best epoch:", best_epoch)
    print("Best validation loss:", round(best_val_loss, 4))

    # Save the training curve.
    plt.figure(figsize=(8, 5))
    plt.plot(history["train_loss"], label="Training loss")
    plt.plot(history["val_loss"], label="Validation loss")
    plt.xlabel("Epoch")
    plt.ylabel("Cross-entropy loss")
    plt.title("Self-Attention Training History")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "training_loss.png", dpi=150)
    plt.close()

    # --------------------------------------------------
    # 6. Train Logistic Regression baseline
    # --------------------------------------------------

    print("\n[5/7] Training Logistic Regression baseline...")

    baseline = LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=SEED,
    )
    baseline.fit(X_train, y_train)

    joblib.dump(
        baseline,
        MODEL_DIR / "logistic_regression.joblib",
    )

    # --------------------------------------------------
    # 7. Evaluate on the untouched test set
    # --------------------------------------------------

    print("\n[6/7] Evaluating models on the final test set...")

    with torch.no_grad():
        test_logits, _ = model(X_test_tensor)
        attention_predictions = (
            test_logits.argmax(dim=1).cpu().numpy()
        )
        y_test_true = y_test_tensor.cpu().numpy()

    logistic_predictions = baseline.predict(X_test)

    all_results = {}
    comparison_rows = []

    for name, predictions in [
        ("Custom Self-Attention", attention_predictions),
        ("Logistic Regression", logistic_predictions),
    ]:
        metrics = calculate_metrics(y_test_true, predictions)
        all_results[name] = metrics

        comparison_rows.append({
            "Model": name,
            "Accuracy": metrics["accuracy"],
            "Balanced Accuracy": metrics["balanced_accuracy"],
            "Macro F1": metrics["macro_f1"],
        })

        print(f"\n{name}")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}")
        print(f"Macro F1: {metrics['macro_f1']:.4f}")
        print("Confusion matrix:")
        print(np.array(metrics["confusion_matrix"]))
        print(
            classification_report(
                y_test_true,
                predictions,
                labels=[0, 1],
                target_names=[
                    "Other diagnoses",
                    "Glioblastoma, IDH wildtype",
                ],
                zero_division=0,
            )
        )

    save_json(all_results, RESULTS_DIR / "test_metrics.json")

    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(
        RESULTS_DIR / "test_model_comparison.csv",
        index=False,
    )

    predictions_df = pd.DataFrame({
        "sample_id": splits["X_test"].index.astype(str),
        "actual_label": y_test_true,
        "attention_prediction": attention_predictions,
        "logistic_prediction": logistic_predictions,
    })
    predictions_df.to_csv(
        RESULTS_DIR / "test_predictions.csv",
        index=False,
    )

    # Confusion-matrix figure.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    for ax, name, predictions in [
        (axes[0], "Self-Attention", attention_predictions),
        (axes[1], "Logistic Regression", logistic_predictions),
    ]:
        ConfusionMatrixDisplay.from_predictions(
            y_test_true,
            predictions,
            labels=[0, 1],
            display_labels=["Other", "Glioblastoma"],
            ax=ax,
            colorbar=False,
        )
        ax.set_title(name)

    fig.tight_layout()
    fig.savefig(
        FIGURES_DIR / "test_confusion_matrices.png",
        dpi=150,
    )
    plt.close(fig)

    # --------------------------------------------------
    # 8. Save a sample prediction demonstration
    # --------------------------------------------------

    print("\n[7/7] Saving a sample prediction demo...")

    sample_position = 0
    sample_tensor = X_test_tensor[
        sample_position:sample_position + 1
    ]

    with torch.no_grad():
        sample_logits, sample_attention = model(sample_tensor)
        sample_probabilities = torch.softmax(
            sample_logits, dim=1
        )[0].cpu().numpy()

    logistic_probabilities = baseline.predict_proba(
        X_test[sample_position:sample_position + 1]
    )[0]

    label_names = {
        0: "Other diagnoses",
        1: "Glioblastoma, IDH wildtype",
    }

    demo_result = {
        "sample_id": str(splits["X_test"].index[sample_position]),
        "actual_label": label_names[int(y_test_true[sample_position])],
        "self_attention_prediction": label_names[
            int(np.argmax(sample_probabilities))
        ],
        "self_attention_probabilities": {
            label_names[0]: float(sample_probabilities[0]),
            label_names[1]: float(sample_probabilities[1]),
        },
        "logistic_regression_prediction": label_names[
            int(np.argmax(logistic_probabilities))
        ],
        "logistic_regression_probabilities": {
            label_names[0]: float(logistic_probabilities[0]),
            label_names[1]: float(logistic_probabilities[1]),
        },
        "attention_matrix_shape": list(sample_attention.shape),
        "note": (
            "Educational research prototype only; "
            "not a clinically validated diagnostic tool."
        ),
    }

    save_json(demo_result, RESULTS_DIR / "sample_prediction_demo.json")

    print("\nModel comparison:")
    print(comparison.round(4).to_string(index=False))

    print("\nSaved artifacts:")
    for path in [
        MODEL_DIR / "self_attention_model.pt",
        MODEL_DIR / "logistic_regression.joblib",
        MODEL_DIR / "preprocessing.joblib",
        RESULTS_DIR / "training_history.json",
        RESULTS_DIR / "test_metrics.json",
        RESULTS_DIR / "test_model_comparison.csv",
        RESULTS_DIR / "test_predictions.csv",
        RESULTS_DIR / "sample_prediction_demo.json",
        FIGURES_DIR / "training_loss.png",
        FIGURES_DIR / "test_confusion_matrices.png",
    ]:
        print("-", path.relative_to(PROJECT_ROOT))

    print("\nTraining and evaluation completed.")


if __name__ == "__main__":
    main()
