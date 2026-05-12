# Copilot Instructions — Python Data Science Project

## Project Context

This is a data science project using Python, pandas, and scikit-learn. The main goal is to build a churn prediction model for a SaaS product.

## Coding Standards

### Python style

Follow PEP 8. Use Black for formatting (line length 88). Use isort for imports.

### Notebooks

Jupyter notebooks live in `notebooks/`. Each notebook should:
- Have a markdown cell at the top explaining the notebook's purpose
- Be runnable top-to-bottom without errors
- Output should be cleared before committing (use `jupyter nbconvert --clear-output`)

### Data files

Raw data lives in `data/raw/`. Never modify raw data. Processed data goes in `data/processed/`. Large files (>10MB) are tracked in `.gitignore` and documented in `data/README.md`.

### Modeling

Models are trained in `src/models/train.py` and saved to `models/`. Use MLflow for experiment tracking:

```python
import mlflow

with mlflow.start_run():
    mlflow.log_params({"n_estimators": 100, "max_depth": 5})
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(clf, "model")
```

### Feature engineering

All feature engineering is in `src/features/`. Each feature transformer should be a scikit-learn compatible transformer (implementing `fit` and `transform`).

## What Copilot Should Know

- The target variable is `churn` (binary: 0 or 1)
- The primary metric is ROC-AUC, not accuracy (class imbalance exists)
- We use stratified train/test splits always
- Customer ID columns must never be used as features
- Date columns should be converted to `days_since` relative features

## Forbidden Patterns

- Never use `df.fillna(0)` for missing values without domain justification
- Never look at test data during feature engineering or model selection
- Never commit API keys or database passwords — use `python-dotenv`
