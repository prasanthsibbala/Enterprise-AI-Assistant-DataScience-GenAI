from fastapi import APIRouter, HTTPException, status

from app.dependencies.auth import CurrentUser
from app.schemas.fraud import (
    FraudModelMetricsResponse,
    FraudPredictionRequest,
    FraudPredictionResponse,
)
from app.services.fraud_explanation_service import (
    fraud_explanation_service,
)
from app.services.fraud_ml_service import (
    fraud_ml_service,
)

router = APIRouter(
    prefix="/fraud",
    tags=["Fraud Analytics"],
)


@router.post(
    "/predict",
    response_model=FraudPredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict_fraud(
    request: FraudPredictionRequest,
    current_user: CurrentUser,
) -> FraudPredictionResponse:
    try:
        prediction = fraud_ml_service.predict(
            request
        )

        explanation = (
            fraud_explanation_service.generate_explanation(
                request=request,
                prediction_result=prediction,
            )
        )

        prediction["ai_explanation"] = explanation

        return FraudPredictionResponse(
            **prediction
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Fraud prediction failed: "
                f"{type(error).__name__}"
            ),
        ) from error


@router.get(
    "/model/metrics",
    response_model=FraudModelMetricsResponse,
    status_code=status.HTTP_200_OK,
)
def get_model_metrics(
    current_user: CurrentUser,
) -> FraudModelMetricsResponse:
    try:
        metrics = fraud_ml_service.load_metrics()

        return FraudModelMetricsResponse(
            **metrics
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.post(
    "/model/train",
    response_model=FraudModelMetricsResponse,
    status_code=status.HTTP_200_OK,
)
def train_model(
    current_user: CurrentUser,
) -> FraudModelMetricsResponse:

    if current_user.role not in {
        "admin",
        "analyst",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )

    try:
        metrics = fraud_ml_service.train(
            force=True
        )

        return FraudModelMetricsResponse(
            **metrics
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error