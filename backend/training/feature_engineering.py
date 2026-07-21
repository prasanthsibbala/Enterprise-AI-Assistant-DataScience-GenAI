from __future__ import annotations

import numpy as np
import pandas as pd


TARGET_COLUMN = "is_fraud"

NUMERIC_FEATURES = [
    "claim_amount",
    "patient_age",
    "previous_claims",
    "inpatient_days",
    "diagnosis_count",
    "procedure_count",
    "provider_claims_30d",
    "duplicate_claim",
    "out_of_network",
    "emergency_claim",
    "claim_amount_log",
    "procedures_per_diagnosis",
    "claim_amount_per_procedure",
    "provider_claim_intensity",
    "high_value_claim",
    "procedure_diagnosis_mismatch",
]

CATEGORICAL_FEATURES = [
    "provider_specialty",
    "claim_type",
    "insurance_plan",
]

MODEL_FEATURES = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)


def create_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create model-ready fraud-detection features.
    """
    required_columns = {
        "claim_amount",
        "patient_age",
        "previous_claims",
        "inpatient_days",
        "diagnosis_count",
        "procedure_count",
        "provider_claims_30d",
        "duplicate_claim",
        "out_of_network",
        "emergency_claim",
        "provider_specialty",
        "claim_type",
        "insurance_plan",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        formatted_columns = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "Dataset is missing required columns: "
            f"{formatted_columns}"
        )

    result = dataframe.copy()

    claim_amount = pd.to_numeric(
        result["claim_amount"],
        errors="coerce",
    ).clip(lower=0)

    diagnosis_count = pd.to_numeric(
        result["diagnosis_count"],
        errors="coerce",
    )

    procedure_count = pd.to_numeric(
        result["procedure_count"],
        errors="coerce",
    )

    provider_claims = pd.to_numeric(
        result["provider_claims_30d"],
        errors="coerce",
    ).clip(lower=0)

    result["claim_amount_log"] = np.log1p(
        claim_amount
    )

    result["procedures_per_diagnosis"] = (
        procedure_count
        / diagnosis_count.replace(0, np.nan)
    )

    result["claim_amount_per_procedure"] = (
        claim_amount
        / procedure_count.replace(0, np.nan)
    )

    result["provider_claim_intensity"] = np.log1p(
        provider_claims
    )

    result["high_value_claim"] = (
        claim_amount >= 25_000
    ).astype(int)

    result["procedure_diagnosis_mismatch"] = (
        procedure_count
        > diagnosis_count + 2
    ).astype(int)

    result.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True,
    )

    columns_to_return = MODEL_FEATURES.copy()

    if TARGET_COLUMN in result.columns:
        columns_to_return.append(
            TARGET_COLUMN
        )

    return result[columns_to_return]


def split_features_and_target(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    if TARGET_COLUMN not in dataframe.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' "
            "was not found."
        )

    engineered_data = create_features(
        dataframe
    )

    features = engineered_data[
        MODEL_FEATURES
    ]

    target = pd.to_numeric(
        engineered_data[TARGET_COLUMN],
        errors="raise",
    ).astype(int)

    invalid_values = (
        set(target.unique()) - {0, 1}
    )

    if invalid_values:
        raise ValueError(
            "Target column must contain only "
            "binary values 0 and 1."
        )

    return features, target