from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FraudPredictionRequest(BaseModel):
    claim_amount: float = Field(
        ...,
        ge=0,
        le=1_000_000,
        examples=[12500],
    )

    patient_age: int = Field(
        ...,
        ge=0,
        le=120,
        examples=[54],
    )

    previous_claims: int = Field(
        ...,
        ge=0,
        le=500,
        examples=[8],
    )

    inpatient_days: int = Field(
        ...,
        ge=0,
        le=365,
        examples=[3],
    )

    diagnosis_count: int = Field(
        ...,
        ge=1,
        le=100,
        examples=[2],
    )

    procedure_count: int = Field(
        ...,
        ge=0,
        le=100,
        examples=[4],
    )

    provider_claims_30d: int = Field(
        ...,
        ge=0,
        le=100_000,
        examples=[125],
    )

    duplicate_claim: bool = Field(
        default=False
    )

    out_of_network: bool = Field(
        default=False
    )

    emergency_claim: bool = Field(
        default=False
    )

    provider_specialty: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Radiology"],
    )

    claim_type: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Outpatient"],
    )

    insurance_plan: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Commercial"],
    )


class FraudFeatureContribution(BaseModel):
    feature: str
    importance: float
    direction: Literal[
        "increases_risk",
        "decreases_risk",
        "neutral",
    ]


class FraudPredictionResponse(BaseModel):
    prediction: Literal[
        "Fraud",
        "Not Fraud",
    ]

    fraud_probability: float
    confidence_score: float

    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical",
    ]

    model_name: str
    model_version: str

    primary_risk_factors: list[
        FraudFeatureContribution
    ]

    ai_explanation: str


class FraudModelMetricsResponse(BaseModel):
    model_name: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    training_rows: int
    testing_rows: int
    fraud_records: int
    non_fraud_records: int
    fraud_rate: float
    feature_count: int