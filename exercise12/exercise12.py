"""
Minimal decision-tree classification (malicious vs benign) using
10×10-fold cross validation and feature importances.

Assumptions:
- Single CSV with stable dtypes.
- Target column is 'Type'.
- Column 'URL' is excluded from features.
- Entropy criterion for splits.
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


RANDOM_SEED = 42


def load_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare_xy(df: pd.DataFrame):
    y = df["Type"].astype(int)
    X = df.drop(columns=["Type"])  # exclude label
    if "URL" in X.columns:
        X = X.drop(columns=["URL"])  # exclude URL from features
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = X.columns.difference(cat_cols).tolist()
    return X, y, cat_cols, num_cols


def build_pipeline(cat_cols, num_cols) -> Pipeline:
    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse=False), cat_cols),
        ]
    )
    clf = DecisionTreeClassifier(criterion="entropy", random_state=RANDOM_SEED)
    return Pipeline([("preprocess", pre), ("clf", clf)])


def run_cv(pipe: Pipeline, X: pd.DataFrame, y: pd.Series):
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=10, random_state=RANDOM_SEED)
    scoring = {
        "accuracy": make_scorer(accuracy_score),
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "f1": make_scorer(f1_score, zero_division=0),
    }
    return cross_validate(pipe, X, y, scoring=scoring, cv=cv)


def aggregate_importances(pipe: Pipeline, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    fitted = pipe.fit(X, y)
    clf = fitted.named_steps["clf"]
    pre = fitted.named_steps["preprocess"]
    names = list(pre.get_feature_names_out())
    imps = clf.feature_importances_
    agg = {}
    for n, v in zip(names, imps):
        if n.startswith("num__"):
            key = n.split("__", 1)[1]
        elif n.startswith("cat__"):
            key = n.split("__", 1)[1].split("_", 1)[0]
        else:
            parts = n.split("__", 1)
            key = parts[1] if len(parts) == 2 else n
        agg[key] = agg.get(key, 0.0) + float(v)
    out = pd.DataFrame({"feature": list(agg.keys()), "importance": list(agg.values())})
    out = out.sort_values("importance", ascending=False).reset_index(drop=True)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default="exercise12/DATASET.csv")
    args = parser.parse_args()

    np.random.seed(RANDOM_SEED)

    df = load_dataset(args.data_path)
    X, y, cat_cols, num_cols = prepare_xy(df)
    pipe = build_pipeline(cat_cols, num_cols)

    cv_results = run_cv(pipe, X, y)
    print("\n=== 10×10-Fold Cross-Validation Summary ===")
    for m in ["accuracy", "precision", "recall", "f1"]:
        s = cv_results[f"test_{m}"]
        print(f"{m.title():<10}: {np.mean(s):.4f} ± {np.std(s, ddof=1):.4f}")

    imps = aggregate_importances(pipe, X, y)
    print("\n=== Feature Importances (aggregated) ===")
    print(imps.to_string(index=False))


if __name__ == "__main__":
    main()
