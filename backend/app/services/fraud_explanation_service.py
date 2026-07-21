from __future__ import annotations

from app.schemas.fraud import FraudPredictionRequest
from app.services.gemini_service import gemini_service


class FraudExplanationService:
    @staticmethod
    def build_fallback_explanation(
        prediction_result: dict,
    ) -> str:
        prediction = prediction_result["prediction"]
        probability = prediction_result["fraud_probability"]
        risk_level = prediction_result["risk_level"]

        risk_factors = prediction_result["primary_risk_factors"]

        factor_names = [
            factor.feature
            for factor in risk_factors[:3]
        ]

        formatted_factors = (
            ", ".join(factor_names)
            if factor_names
            else "the submitted claim attributes"
        )

        return (
            f"The model classified this claim as {prediction} "
            f"with a fraud probability of {probability}%. "
            f"The assigned risk level is {risk_level}. "
            f"The most influential factors were {formatted_factors}. "
            f"This result supports fraud analysts and should not "
            f"be the sole basis for approving or denying a claim."
        )

    def generate_explanation(
        self,
        request: FraudPredictionRequest,
        prediction_result: dict,
    ) -> str:
        fallback = self.build_fallback_explanation(
            prediction_result
        )

        risk_factors = "\n".join(
            (
                f"- {factor.feature}: "
                f"{factor.importance} "
                f"({factor.direction})"
            )
            for factor in prediction_result[
                "primary_risk_factors"
            ]
        )

        prompt = f"""
You are a healthcare fraud analytics assistant.

Prediction: {prediction_result["prediction"]}
Fraud probability: {prediction_result["fraud_probability"]}%
Confidence: {prediction_result["confidence_score"]}%
Risk level: {prediction_result["risk_level"]}

Claim amount: {request.claim_amount}
Patient age: {request.patient_age}
Previous claims: {request.previous_claims}

Risk factors:
{risk_factors}

Explain this prediction in under 150 words.
"""

        try:
            response = gemini_service.generate_response(
                prompt
            )

            return (
                response.strip()
                if response.strip()
                else fallback
            )

        except Exception:
            return fallback


fraud_explanation_service = FraudExplanationService()