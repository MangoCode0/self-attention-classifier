
# Brain Tumor Classification Using Gene Expression Data

### Custom Self-Attention vs Logistic Regression

## 1. Project Overview

This project explores binary brain tumor classification using gene-expression data from the GSE272042 dataset.

Two machine learning approaches are implemented and compared:

1. **Custom Self-Attention Classifier:** A PyTorch-based neural network using scaled dot-product self-attention.
2. **Logistic Regression:** A classical machine learning baseline.

The project includes data preprocessing, model training, evaluation, model saving, sample prediction, and an interactive Streamlit interface.

## 2. Dataset

- Dataset: GSE272042
- Expression matrix: 40,232 genes and 153 samples
- Selected features: 500 genes
- Metadata: Supplementary Excel file

### Classification Labels

| Label | Diagnosis |
|---|---|
| 0 | Other diagnoses |
| 1 | Glioblastoma, IDH wildtype |

Class 0 contains multiple heterogeneous diagnoses.

## 3. Project Architecture

```text
brain-tumor-attention/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── self_attention_classifier.ipynb
│
├── src/
│   ├── attention/
│   ├── data/
│   ├── evaluation/
│   ├── inference/
│   └── models/
│
├── models/
│   └── saved/
│
├── reports/
│   ├── figures/
│   └── results/
│
├── tests/
│
├── app.py
├── train.py
├── README.md
├── requirements.txt
└── .gitignore
```

## 4. Methodology

1. Load gene-expression data and supplementary metadata.
2. Match sample identifiers and diagnosis labels.
3. Create stratified training, validation, and test splits.
4. Perform gene selection using training data only.
5. Apply log transformation and standardization.
6. Train the Self-Attention classifier.
7. Train Logistic Regression as a baseline.
8. Evaluate both models on the held-out test set.
9. Save models, preprocessing objects, metrics, and visualizations.

### Data Split

| Dataset | Samples |
|---|---:|
| Training | 97 |
| Validation | 25 |
| Testing | 31 |
| Total | 153 |

## 5. Self-Attention Architecture

- Input: 500 gene-expression features
- Embedding dimension: 32
- Attention: Scaled dot-product self-attention
- Pooling: Mean pooling
- Classifier: MLP with hidden dimension 32
- Output: 2 classes
- Dropout: 0.3

## 6. Experimental Results

| Metric | Self-Attention | Logistic Regression |
|---|---:|---:|
| Accuracy | 67.74% | 87.10% |
| Balanced Accuracy | 66.03% | 79.08% |
| Macro F1 | 63.10% | 81.55% |

Logistic Regression achieved better test performance in this experiment.

## 7. Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd brain-tumor-attention
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Place the required dataset files inside `data/raw/`.

## 8. Run the Project

### Run preprocessing tests

```bash
python -m tests.test_preprocessing_pipeline
```

### Train models

```bash
python train.py
```

### Predict using the saved model

```bash
python -m src.inference.predict
```

### Launch the web application

```bash
streamlit run app.py
```

## 9. Saved Outputs

### Models

- `self_attention_model.pt`
- `logistic_regression.joblib`
- `preprocessing.joblib`

### Results

- Test metrics in JSON format
- Model comparison CSV
- Test predictions CSV
- Sample prediction demonstration JSON

### Figures

- Training and validation loss
- Test confusion matrices

## 10. Technologies Used

- Python
- NumPy
- Pandas
- Scikit-learn
- PyTorch
- Matplotlib
- Streamlit
- Jupyter Notebook

## 11. Limitations

- The dataset contains only 153 samples.
- The classification task is binary.
- The Other diagnoses class is heterogeneous.
- The Self-Attention model did not outperform Logistic Regression in this experiment.
- Results require further validation on independent datasets.

**This project is an educational research prototype and is not a clinically validated diagnostic system.**
