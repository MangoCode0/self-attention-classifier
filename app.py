
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.inference.predict import predict_sample


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "reports" / "results"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Brain Tumor Classification",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Brain Tumor Classification")
st.subheader("Gene Expression Analysis Using Self-Attention")

st.markdown(
    """
    This research prototype compares a custom PyTorch Self-Attention
    classifier with a Logistic Regression baseline using gene-expression
    data from GSE272042.
    """
)

st.divider()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("Project Information")

st.sidebar.markdown(
    """
    **Dataset:** GSE272042

    **Input features:** 500 selected genes

    **Classes:**
    - 0: Other diagnoses
    - 1: Glioblastoma, IDH wildtype

    **Models:**
    - Custom Self-Attention
    - Logistic Regression
    """
)

st.sidebar.info(
    "Educational research prototype only. "
    "Not intended for clinical diagnosis."
)


# --------------------------------------------------
# Load saved results
# --------------------------------------------------

@st.cache_data
def load_metrics():
    path = RESULTS_DIR / "test_metrics.json"

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data
def load_comparison():
    path = RESULTS_DIR / "test_model_comparison.csv"

    if not path.exists():
        return None

    return pd.read_csv(path)


metrics = load_metrics()
comparison = load_comparison()


# --------------------------------------------------
# Model performance
# --------------------------------------------------

st.header("1. Model Performance")

if comparison is not None:
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    col1, col2 = st.columns(2)

    for column, model_name in zip(
        [col1, col2],
        ["Custom Self-Attention", "Logistic Regression"],
    ):
        row = comparison[comparison["Model"] == model_name]

        if not row.empty:
            with column:
                st.metric(
                    "Accuracy",
                    f"{row.iloc[0]['Accuracy'] * 100:.2f}%",
                )
                st.metric(
                    "Macro F1",
                    f"{row.iloc[0]['Macro F1'] * 100:.2f}%",
                )
else:
    st.warning("Model comparison results not found. Run train.py first.")


# --------------------------------------------------
# Confusion matrices
# --------------------------------------------------

st.header("2. Confusion Matrices")

confusion_path = FIGURES_DIR / "test_confusion_matrices.png"

if confusion_path.exists():
    st.image(
        str(confusion_path),
        caption="Test-set confusion matrices",
        use_container_width=True,
    )
else:
    st.info("Confusion matrix image is not available.")


# --------------------------------------------------
# Sample prediction
# --------------------------------------------------

st.divider()
st.header("3. Sample Prediction")

st.write(
    "Enter an existing sample ID from the expression dataset "
    "to generate a prediction using the saved Self-Attention model."
)

sample_id = st.text_input(
    "Enter Sample ID",
    placeholder="Example: 122",
)

if st.button("Predict", type="primary"):
    if not sample_id.strip():
        st.warning("Please enter a sample ID.")

    else:
        try:
            with st.spinner("Generating prediction..."):
                result = predict_sample(sample_id)

            st.success("Prediction generated successfully.")

            st.subheader(
                f"Sample ID: {result['sample_id']}"
            )

            st.metric(
                "Predicted Class",
                result["prediction"],
            )

            st.write("Class Probabilities")

            probability_data = pd.DataFrame({
                "Class": list(result["probabilities"].keys()),
                "Probability": [
                    value * 100
                    for value in result["probabilities"].values()
                ],
            })

            st.bar_chart(
                probability_data.set_index("Class")
            )

            st.dataframe(
                probability_data,
                use_container_width=True,
                hide_index=True,
            )

        except FileNotFoundError:
            st.error(
                "Saved model or preprocessing file not found. "
                "Please run train.py first."
            )

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(f"Prediction failed: {error}")


# --------------------------------------------------
# Training history
# --------------------------------------------------

st.divider()
st.header("4. Training History")

history_path = RESULTS_DIR / "training_history.json"

if history_path.exists():
    with open(history_path, "r", encoding="utf-8") as file:
        history = json.load(file)

    history_df = pd.DataFrame({
        "Training Loss": history["train_loss"],
        "Validation Loss": history["val_loss"],
    })

    st.line_chart(history_df)

    st.write(
        "Best epoch:",
        history.get("best_epoch", "Not available"),
    )
else:
    st.info("Training history is not available.")


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Brain Tumor Classification Research Project | "
    "GSE272042 | Custom Self-Attention and Logistic Regression"
)

st.warning(
    "This system is an educational research prototype. "
    "Its predictions must not be used for medical decisions."
)
