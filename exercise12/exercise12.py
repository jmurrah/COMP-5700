"""
COMP-5700 Exercise 12: ML for Vulnerability Analysis
Author: Jacob Murrah
Date: 11/10/2025
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
)
from sklearn.model_selection import RepeatedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


RANDOM_SEED = 2025


def load_dataset(path: str) -> pd.DataFrame:
    # Item 1) Loading the dataset into a data structure
    return pd.read_csv(path)


def bucket_server_vendor(server_col: pd.Series) -> pd.Series:
    s = server_col.astype(str).str.lower()

    vendor_map = [  # pattern, choice
        ("nginx", "nginx"),
        ("apache|coyote", "apache"),
        ("microsoft|iis", "microsoft"),
        ("openresty", "openresty"),
        ("cloudflare", "cloudflare"),
        ("litespeed", "litespeed"),
        ("lighttpd", "lighttpd"),
        ("gse|youtube", "google"),
        ("ats", "ats"),
        ("varnish", "varnish"),
        ("codfw", "codfw"),
        ("nxfps", "nxfps"),
        ("oracle", "oracle"),
        ("pagely", "pagely"),
        ("pizza", "pizza"),
        ("pepyaka", "pepyaka"),
    ]

    conditions = [s.str.contains(pattern) for pattern, _ in vendor_map]
    choices = [choice for _, choice in vendor_map]

    return np.select(conditions, choices, default="other")


def prepare_xy(df: pd.DataFrame):
    COLUMNS_TO_DROP = ["URL", "WHOIS_STATEPRO", "WHOIS_REGDATE", "WHOIS_UPDATED_DATE"]
    y = df["Type"].astype(int)  # Always 0 or 1
    X = df.drop(columns=["Type"])

    for col in COLUMNS_TO_DROP:
        if col in X.columns:
            X = X.drop(columns=[col])

    X["SERVER_VENDOR"] = bucket_server_vendor(X["SERVER"])
    X = X.drop(columns=["SERVER"])

    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = X.columns.difference(cat_cols).tolist()
    return X, y, cat_cols, num_cols


def build_pipeline(cat_cols, num_cols) -> Pipeline:
    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            ),
        ]
    )

    # Item 2) Using the Decision Tree implementation in scikit-learn
    # Item 5) Use entropy to determine the quality of a split
    clf = DecisionTreeClassifier(criterion="entropy", random_state=RANDOM_SEED)
    return Pipeline([("preprocess", pre), ("clf", clf)])


def run_cv(pipe: Pipeline, X: pd.DataFrame, y: pd.Series):
    # Item 3) Reporting accuracy, precision, recall, and F-measure for the predicted classes using 10x10-fold cross validation
    cv = RepeatedKFold(n_splits=10, n_repeats=10, random_state=RANDOM_SEED)
    scoring = {
        "accuracy": make_scorer(accuracy_score),
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "f1": make_scorer(f1_score, zero_division=0),
    }
    return cross_validate(pipe, X, y, scoring=scoring, cv=cv)


def aggregate_importances(
    pipe: Pipeline, X: pd.DataFrame, y: pd.Series
) -> pd.DataFrame:
    # Item 4) Reporting the importance of each feature using the constructed decision tree
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
        agg[key] = agg.get(key, 0.0) + float(v)

    out = pd.DataFrame({"feature": list(agg.keys()), "importance": list(agg.values())})
    out = out.sort_values("importance", ascending=False).reset_index(drop=True)
    return out


if __name__ == "__main__":
    np.random.seed(RANDOM_SEED)

    df = load_dataset("DATASET.csv")  # Item 1
    X, y, cat_cols, num_cols = prepare_xy(df)

    pipe = build_pipeline(cat_cols, num_cols)  # Item 2 and Item 5

    cv_results = run_cv(pipe, X, y)  # Item 3

    imps = aggregate_importances(pipe, X, y)  # Item 4

    output_path = "results.txt"
    with open(output_path, "w") as out:
        out.write("----- 10×10-Fold Cross-Validation Summary: -----\n")
        for m in ["accuracy", "precision", "recall", "f1"]:
            s = cv_results[f"test_{m}"]
            out.write(f"{m.title():<10}: {np.mean(s):.4f} ± {np.std(s, ddof=1):.4f}\n")

        out.write("\n----- Feature Importances (aggregated): -----\n")
        out.write(imps.to_string(index=False))
        out.write("\n")

    print(f"Results written to {output_path}")
