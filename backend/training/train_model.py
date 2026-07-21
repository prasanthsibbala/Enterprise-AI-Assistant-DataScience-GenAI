from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from training.feature_engineering import (
    split_features_and_target,
)
from training.generate_dataset import (
    DATASET_PATH,
    save_dataset,
)
from training.preprocess import (
    build_preprocessor,
)


RANDOM_SEED = 42

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models_artifacts"

MODEL_PATH = MODEL_DIR / "fraud_model.joblib"
METRICS_PATH = MODEL_DIR / "fraud_metrics.json"
FEATURES_PATH = MODEL_DIR / "feature_names.json"


def load_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        print(
            "Training dataset does not exist. "
            "Generating synthetic dataset..."
        )

        save_dataset()

    dataset = pd.read_csv(
        DATASET_PATH
    )

    if dataset.empty:
        raise ValueError(
            "Training dataset is empty."
        )

    return dataset


def build_model_pipeline() -> Pipeline:
    preprocessor = build_preprocessor()

    classifier = RandomForestClassifier(
        n_estimators=350,
        max_depth=14,
        min_samples_split=6,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "classifier",
                classifier,
            ),
        ]
    )


def calculate_metrics(
    y_test: pd.Series,
    predictions: Any,
    probabilities: Any,
) -> dict[str, Any]:
    return {
        "model_name": (
            "Random Forest Healthcare "
            "Fraud Classifier"
        ),
        "model_version": "1.0.0",
        "accuracy": round(
            float(
                accuracy_score(
                    y_test,
                    predictions,
                )
            ),
            4,
        ),
        "precision": round(
            float(
                precision_score(
                    y_test,
                    predictions,
                    zero_division=0,
                )
            ),
            4,
        ),
        "recall": round(
            float(
                recall_score(
                    y_test,
                    predictions,
                    zero_division=0,
                )
            ),
            4,
        ),
        "f1_score": round(
            float(
                f1_score(
                    y_test,
                    predictions,
                    zero_division=0,
                )
            ),
            4,
        ),
        "roc_auc": round(
            float(
                roc_auc_score(
                    y_test,
                    probabilities,
                )
            ),
            4,
        ),
        "confusion_matrix": (
            confusion_matrix(
                y_test,
                predictions,
            ).tolist()
        ),
        "classification_report": (
            classification_report(
                y_test,
                predictions,
                output_dict=True,
                zero_division=0,
            )
        ),
    }


def save_feature_names(
    model_pipeline: Pipeline,
) -> list[str]:
    preprocessor = model_pipeline.named_steps[
        "preprocessor"
    ]

    feature_names = (
        preprocessor.get_feature_names_out()
        .tolist()
    )

    FEATURES_PATH.write_text(
        json.dumps(
            feature_names,
            indent=2,
        ),
        encoding="utf-8",
    )

    return feature_names


def train_model() -> dict[str, Any]:
    dataset = load_dataset()

    features, target = (
        split_features_and_target(
            dataset
        )
    )

    (
        x_train,
        x_test,
        y_train,
        y_test,
    ) = train_test_split(
        features,
        target,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=target,
    )

    model_pipeline = (
        build_model_pipeline()
    )

    print(
        "Training healthcare fraud "
        "classification model..."
    )

    model_pipeline.fit(
        x_train,
        y_train,
    )

    predictions = (
        model_pipeline.predict(
            x_test
        )
    )

    probabilities = (
        model_pipeline.predict_proba(
            x_test
        )[:, 1]
    )

    metrics = calculate_metrics(
        y_test=y_test,
        predictions=predictions,
        probabilities=probabilities,
    )

    metrics.update(
        {
            "training_rows": int(
                len(x_train)
            ),
            "testing_rows": int(
                len(x_test)
            ),
            "fraud_records": int(
                target.sum()
            ),
            "non_fraud_records": int(
                len(target) - target.sum()
            ),
            "fraud_rate": round(
                float(target.mean()),
                4,
            ),
        }
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model_pipeline,
        MODEL_PATH,
    )

    feature_names = save_feature_names(
        model_pipeline
    )

    metrics["feature_count"] = len(
        feature_names
    )

    METRICS_PATH.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "\nModel training completed successfully."
    )
    print(f"Model saved at: {MODEL_PATH}")
    print(f"Metrics saved at: {METRICS_PATH}")

    print("\nModel performance:")
    print(
        f"Accuracy : {metrics['accuracy']}"
    )
    print(
        f"Precision: {metrics['precision']}"
    )
    print(
        f"Recall   : {metrics['recall']}"
    )
    print(
        f"F1 Score : {metrics['f1_score']}"
    )
    print(
        f"ROC-AUC  : {metrics['roc_auc']}"
    )

    return metrics


if __name__ == "__main__":
    train_model()