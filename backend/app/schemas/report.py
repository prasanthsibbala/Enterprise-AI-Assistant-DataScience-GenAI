from pydantic import BaseModel, Field


class FraudReportRequest(BaseModel):
    prediction: str = Field(..., min_length=2, max_length=100)
    fraud_probability: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., min_length=2, max_length=50)

    top_features: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    ai_explanation: str = Field(
        ...,
        min_length=10,
        max_length=5000,
    )

    recommendation: str = Field(
        ...,
        min_length=5,
        max_length=2000,
    )