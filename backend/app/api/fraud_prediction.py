from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

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


router = APIRouter()


@router.post(
    "/fraud/predict",
    response_model=FraudPredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict_fraud(
    request: FraudPredictionRequest,
    current_user: CurrentUser,
) -> FraudPredictionResponse:
    try:
        prediction_result = (
            fraud_ml_service.predict(
                request
            )
        )

        ai_explanation = (
            fraud_explanation_service
            .generate_explanation(
                request=request,
                prediction_result=(
                    prediction_result
                ),
            )
        )

        return FraudPredictionResponse(
            **prediction_result,
            ai_explanation=ai_explanation,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print(
            "Fraud prediction error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to calculate fraud "
                "prediction."
            ),
        ) from error


@router.get(
    "/fraud/model/metrics",
    response_model=FraudModelMetricsResponse,
    status_code=status.HTTP_200_OK,
)
def get_fraud_model_metrics(
    current_user: CurrentUser,
) -> FraudModelMetricsResponse:
    try:
        metrics = (
            fraud_ml_service.load_metrics()
        )

        return FraudModelMetricsResponse(
            model_name=metrics["model_name"],
            model_version=metrics[
                "model_version"
            ],
            accuracy=metrics["accuracy"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
            roc_auc=metrics["roc_auc"],
            training_rows=metrics[
                "training_rows"
            ],
            testing_rows=metrics[
                "testing_rows"
            ],
            fraud_records=metrics[
                "fraud_records"
            ],
            non_fraud_records=metrics[
                "non_fraud_records"
            ],
            fraud_rate=metrics[
                "fraud_rate"
            ],
            feature_count=metrics[
                "feature_count"
            ],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except Exception as error:
        print(
            "Model metrics error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to retrieve model metrics."
            ),
        ) from error