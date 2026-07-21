from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from app.schemas.fraud import (
    FraudFeatureContribution,
    FraudPredictionRequest,
)
from training.feature_engineering import create_features
from training.train_model import train_model as run_training_pipeline


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIRECTORY = BASE_DIR / "models_artifacts"
MODEL_PATH = MODEL_DIRECTORY / "fraud_model.joblib"
METRICS_PATH = MODEL_DIRECTORY / "fraud_metrics.json"
FEATURE_NAMES_PATH = MODEL_DIRECTORY / "feature_names.json"


class FraudMLService:
    def __init__(self) -> None:
        self._model: Pipeline | None = None
        self._metrics: dict[str, Any] | None = None
        self._feature_names: list[str] | None = None
        self._model_lock = Lock()

    def _ensure_model_exists(self) -> None:
        if not MODEL_PATH.exists():
            raise ValueError(
                "Fraud model was not found. Run "
                "`python -m training.train_model` first."
            )

    def clear_cache(self) -> None:
        """
        Clear cached model artifacts after model retraining.
        """
        self._model = None
        self._metrics = None
        self._feature_names = None

    def load_model(self) -> Pipeline:
        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is not None:
                return self._model

            self._ensure_model_exists()

            loaded_model = joblib.load(MODEL_PATH)

            if not isinstance(loaded_model, Pipeline):
                raise TypeError(
                    "Saved fraud model is not a valid "
                    "scikit-learn Pipeline."
                )

            self._model = loaded_model

        return self._model

    def load_metrics(self) -> dict[str, Any]:
        if self._metrics is not None:
            return self._metrics

        if not METRICS_PATH.exists():
            raise ValueError(
                "Model metrics were not found. "
                "Train the model first."
            )

        metrics = json.loads(
            METRICS_PATH.read_text(
                encoding="utf-8",
            )
        )

        if not isinstance(metrics, dict):
            raise ValueError(
                "Stored model metrics are invalid."
            )

        self._metrics = metrics
        return metrics

    def get_metrics(self) -> dict[str, Any]:
        """
        Alias used by API endpoints.
        """
        return self.load_metrics()

    def load_feature_names(self) -> list[str]:
        if self._feature_names is not None:
            return self._feature_names

        if not FEATURE_NAMES_PATH.exists():
            raise ValueError(
                "Model feature names were not found. "
                "Train the model first."
            )

        loaded_names = json.loads(
            FEATURE_NAMES_PATH.read_text(
                encoding="utf-8",
            )
        )

        if not isinstance(loaded_names, list):
            raise ValueError(
                "Stored model feature names are invalid."
            )

        self._feature_names = [
            str(feature_name)
            for feature_name in loaded_names
        ]

        return self._feature_names

    def train(
        self,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Train or retrain the healthcare fraud model.

        When force=False, existing metrics are returned when
        a trained model already exists.
        """
        if MODEL_PATH.exists() and not force:
            return self.load_metrics()

        with self._model_lock:
            if MODEL_PATH.exists() and not force:
                return self.load_metrics()

            self.clear_cache()

            training_metrics = run_training_pipeline()

            self.clear_cache()

            if isinstance(training_metrics, dict):
                return training_metrics

            return self.load_metrics()

    @staticmethod
    def request_to_dataframe(
        request: FraudPredictionRequest,
    ) -> pd.DataFrame:
        raw_record = {
            "claim_amount": request.claim_amount,
            "patient_age": request.patient_age,
            "previous_claims": request.previous_claims,
            "inpatient_days": request.inpatient_days,
            "diagnosis_count": request.diagnosis_count,
            "procedure_count": request.procedure_count,
            "provider_claims_30d": (
                request.provider_claims_30d
            ),
            "duplicate_claim": int(
                request.duplicate_claim
            ),
            "out_of_network": int(
                request.out_of_network
            ),
            "emergency_claim": int(
                request.emergency_claim
            ),
            "provider_specialty": (
                request.provider_specialty
            ),
            "claim_type": request.claim_type,
            "insurance_plan": request.insurance_plan,
        }

        dataframe = pd.DataFrame([raw_record])

        return create_features(dataframe)

    @staticmethod
    def get_risk_level(
        fraud_probability: float,
    ) -> str:
        if fraud_probability >= 0.85:
            return "Critical"

        if fraud_probability >= 0.65:
            return "High"

        if fraud_probability >= 0.35:
            return "Medium"

        return "Low"

    def get_feature_contributions(
        self,
        model: Pipeline,
        engineered_record: pd.DataFrame,
        limit: int = 6,
    ) -> list[FraudFeatureContribution]:
        preprocessor = model.named_steps[
            "preprocessor"
        ]

        classifier = model.named_steps[
            "classifier"
        ]

        transformed_record = preprocessor.transform(
            engineered_record
        )

        transformed_array = np.asarray(
            transformed_record
        ).reshape(-1)

        feature_names = (
            preprocessor
            .get_feature_names_out()
            .tolist()
        )

        importances = np.asarray(
            classifier.feature_importances_
        )

        if len(feature_names) != len(importances):
            raise ValueError(
                "Feature names and model importances "
                "do not match."
            )

        contributions: list[
            FraudFeatureContribution
        ] = []

        for (
            feature_name,
            feature_value,
            global_importance,
        ) in zip(
            feature_names,
            transformed_array,
            importances,
            strict=True,
        ):
            contribution_value = float(
                global_importance
                * abs(float(feature_value))
            )

            if contribution_value < 0.000001:
                direction = "neutral"
            elif feature_value > 0:
                direction = "increases_risk"
            else:
                direction = "decreases_risk"

            contributions.append(
                FraudFeatureContribution(
                    feature=self._clean_feature_name(
                        feature_name
                    ),
                    importance=round(
                        contribution_value,
                        6,
                    ),
                    direction=direction,
                )
            )

        contributions.sort(
            key=lambda item: item.importance,
            reverse=True,
        )

        return contributions[:limit]

    @staticmethod
    def _clean_feature_name(
        feature_name: str,
    ) -> str:
        cleaned_name = (
            feature_name
            .replace("numeric__", "")
            .replace("categorical__", "")
            .replace("_", " ")
            .strip()
        )

        return cleaned_name.title()

    def predict(
        self,
        request: FraudPredictionRequest,
    ) -> dict[str, Any]:
        model = self.load_model()

        engineered_record = (
            self.request_to_dataframe(request)
        )

        probabilities = model.predict_proba(
            engineered_record
        )

        if probabilities.shape[1] < 2:
            raise ValueError(
                "Fraud model did not return binary "
                "classification probabilities."
            )

        fraud_probability = float(
            probabilities[0][1]
        )

        predicted_class = int(
            fraud_probability >= 0.50
        )

        prediction = (
            "Fraud"
            if predicted_class == 1
            else "Not Fraud"
        )

        confidence_score = (
            fraud_probability
            if predicted_class == 1
            else 1 - fraud_probability
        )

        risk_level = self.get_risk_level(
            fraud_probability
        )

        contributions = (
            self.get_feature_contributions(
                model=model,
                engineered_record=engineered_record,
            )
        )

        metrics = self.load_metrics()

        return {
            "prediction": prediction,
            "fraud_probability": round(
                fraud_probability * 100,
                2,
            ),
            "confidence_score": round(
                confidence_score * 100,
                2,
            ),
            "risk_level": risk_level,
            "model_name": metrics.get(
                "model_name",
                (
                    "Random Forest Healthcare "
                    "Fraud Classifier"
                ),
            ),
            "model_version": metrics.get(
                "model_version",
                "1.0.0",
            ),
            "primary_risk_factors": contributions,
        }


fraud_ml_service = FraudMLService()