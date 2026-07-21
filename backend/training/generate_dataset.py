from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
DEFAULT_ROWS = 10_000

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATASET_PATH = DATA_DIR / "healthcare_claims.csv"


def generate_healthcare_claims(
    rows: int = DEFAULT_ROWS,
    random_seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate a synthetic healthcare claims dataset.

    This dataset is intended for learning, development and demonstration.
    It must not be treated as real patient or production insurance data.
    """
    if rows < 100:
        raise ValueError("rows must be at least 100.")

    rng = np.random.default_rng(random_seed)

    provider_specialties = np.array(
        [
            "Primary Care",
            "Cardiology",
            "Orthopedics",
            "Radiology",
            "Oncology",
            "Neurology",
            "Emergency Medicine",
        ]
    )

    claim_types = np.array(
        [
            "Outpatient",
            "Inpatient",
            "Emergency",
            "Pharmacy",
        ]
    )

    insurance_plans = np.array(
        [
            "Commercial",
            "Medicare",
            "Medicaid",
            "Marketplace",
        ]
    )

    data = pd.DataFrame(
        {
            "claim_id": [
                f"CLM-{index:08d}"
                for index in range(1, rows + 1)
            ],
            "claim_amount": rng.lognormal(
                mean=7.5,
                sigma=1.05,
                size=rows,
            ).clip(50, 250_000),
            "patient_age": rng.integers(
                low=1,
                high=96,
                size=rows,
            ),
            "previous_claims": rng.poisson(
                lam=4,
                size=rows,
            ).clip(0, 60),
            "inpatient_days": rng.poisson(
                lam=2,
                size=rows,
            ).clip(0, 45),
            "diagnosis_count": rng.poisson(
                lam=3,
                size=rows,
            ).clip(1, 25),
            "procedure_count": rng.poisson(
                lam=2,
                size=rows,
            ).clip(0, 20),
            "provider_claims_30d": rng.lognormal(
                mean=4.2,
                sigma=0.8,
                size=rows,
            ).astype(int).clip(1, 2_500),
            "duplicate_claim": rng.binomial(
                n=1,
                p=0.08,
                size=rows,
            ),
            "out_of_network": rng.binomial(
                n=1,
                p=0.20,
                size=rows,
            ),
            "emergency_claim": rng.binomial(
                n=1,
                p=0.15,
                size=rows,
            ),
            "provider_specialty": rng.choice(
                provider_specialties,
                size=rows,
            ),
            "claim_type": rng.choice(
                claim_types,
                size=rows,
                p=[0.48, 0.22, 0.15, 0.15],
            ),
            "insurance_plan": rng.choice(
                insurance_plans,
                size=rows,
                p=[0.36, 0.24, 0.25, 0.15],
            ),
        }
    )

    # Create a realistic synthetic fraud relationship.
    risk_score = (
        -4.5
        + 0.000020 * data["claim_amount"]
        + 0.060 * data["previous_claims"]
        + 0.035 * data["inpatient_days"]
        + 0.006 * data["provider_claims_30d"]
        + 2.10 * data["duplicate_claim"]
        + 0.90 * data["out_of_network"]
        + 0.45 * data["emergency_claim"]
        + 0.55
        * (
            data["procedure_count"]
            > data["diagnosis_count"] + 2
        ).astype(int)
        + 0.40
        * (
            data["claim_amount"] > 30_000
        ).astype(int)
        + 0.35
        * (
            data["provider_specialty"] == "Radiology"
        ).astype(int)
        + rng.normal(
            loc=0,
            scale=0.75,
            size=rows,
        )
    )

    fraud_probability = (
        1 / (1 + np.exp(-risk_score))
    ).clip(0.01, 0.98)

    data["is_fraud"] = rng.binomial(
        n=1,
        p=fraud_probability,
    )

    # Add a small amount of missing data so preprocessing is realistic.
    for column in [
        "claim_amount",
        "patient_age",
        "provider_specialty",
        "insurance_plan",
    ]:
        missing_indices = rng.choice(
            data.index,
            size=max(1, int(rows * 0.01)),
            replace=False,
        )
        data.loc[missing_indices, column] = np.nan

    return data


def save_dataset(
    rows: int = DEFAULT_ROWS,
    output_path: Path = DATASET_PATH,
) -> Path:
    dataset = generate_healthcare_claims(
        rows=rows
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset.to_csv(
        output_path,
        index=False,
    )

    return output_path


if __name__ == "__main__":
    saved_path = save_dataset()

    print(
        "Synthetic healthcare claims dataset "
        f"created successfully: {saved_path}"
    )