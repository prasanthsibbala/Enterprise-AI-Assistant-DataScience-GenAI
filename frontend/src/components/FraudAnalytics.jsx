import {
  useEffect,
  useState,
} from "react";

import {
  downloadFraudReport,
  getFraudModelMetrics,
  predictFraud,
  trainFraudModel,
} from "../services/api";

const initialForm = {
  claim_amount: 12500,
  patient_age: 48,
  previous_claims: 6,
  inpatient_days: 2,
  diagnosis_count: 3,
  procedure_count: 2,
  provider_claims_30d: 90,
  duplicate_claim: false,
  out_of_network: false,
  emergency_claim: false,
  provider_specialty: "Radiology",
  claim_type: "Outpatient",
  insurance_plan: "Commercial",
};

const numericFields = [
  ["claim_amount", "Claim Amount"],
  ["patient_age", "Patient Age"],
  [
    "previous_claims",
    "Previous Claims",
  ],
  [
    "inpatient_days",
    "Inpatient Days",
  ],
  [
    "diagnosis_count",
    "Diagnosis Count",
  ],
  [
    "procedure_count",
    "Procedure Count",
  ],
  [
    "provider_claims_30d",
    "Provider Claims (30d)",
  ],
];

const checkboxFields = [
  [
    "duplicate_claim",
    "Duplicate claim",
  ],
  [
    "out_of_network",
    "Out of network",
  ],
  [
    "emergency_claim",
    "Emergency claim",
  ],
];

function FraudAnalytics({ user }) {
  const [form, setForm] =
    useState(initialForm);

  const [result, setResult] =
    useState(null);

  const [metrics, setMetrics] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [training, setTraining] =
    useState(false);

  const [downloading, setDownloading] =
    useState(false);

  const [error, setError] =
    useState("");

  const loadMetrics = async () => {
    try {
      const modelMetrics =
        await getFraudModelMetrics();

      setMetrics(modelMetrics);
    } catch (metricsError) {
      setError(metricsError.message);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  const updateField = (event) => {
    const {
      name,
      type,
      checked,
      value,
    } = event.target;

    setForm((current) => ({
      ...current,
      [name]:
        type === "checkbox"
          ? checked
          : type === "number"
            ? Number(value)
            : value,
    }));
  };

  const handlePredict = async (
    event
  ) => {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const prediction =
        await predictFraud(form);

      setResult(prediction);
    } catch (predictionError) {
      setError(
        predictionError.message
      );
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    setError("");

    try {
      const updatedMetrics =
        await trainFraudModel();

      setMetrics(updatedMetrics);
      setResult(null);
    } catch (trainingError) {
      setError(trainingError.message);
    } finally {
      setTraining(false);
    }
  };

  const handleDownload = async () => {
    if (!result) {
      return;
    }

    setDownloading(true);
    setError("");

    const riskFactors =
      result.primary_risk_factors ?? [];

    const recommendation =
      result.recommendation ||
      (
        result.risk_level === "Critical" ||
        result.risk_level === "High"
          ? "Route this claim for manual fraud investigation before final adjudication."
          : "Continue normal claim review while retaining the model result for audit purposes."
      );

    try {
      await downloadFraudReport({
        prediction:
          result.prediction,
        fraud_probability:
          result.fraud_probability,
        risk_level:
          result.risk_level,
        top_features:
          riskFactors.map(
            (item) => item.feature
          ),
        ai_explanation:
          result.ai_explanation,
        recommendation,
      });
    } catch (downloadError) {
      setError(downloadError.message);
    } finally {
      setDownloading(false);
    }
  };

  const riskFactors =
    result?.primary_risk_factors ??
    [];

  return (
    <section className="fraud-workspace">
      <div className="fraud-heading">
        <div>
          <span className="hero-badge">
            Data Science + GenAI
          </span>

          <h2>
            Healthcare Fraud Risk
            Prediction
          </h2>

          <p>
            Random Forest
            classification, feature
            importance, model metrics,
            GenAI explanation, and a
            downloadable audit report.
          </p>
        </div>

        {(
          user?.role === "admin" ||
          user?.role === "analyst"
        ) && (
          <button
            type="button"
            className="secondary-button"
            onClick={handleTrain}
            disabled={training}
          >
            {training
              ? "Training..."
              : "Retrain Model"}
          </button>
        )}
      </div>

      {error && (
        <div className="status-box error-box">
          {error}
        </div>
      )}

      {metrics && (
        <div className="metric-grid">
          <div>
            <span>Accuracy</span>
            <strong>
              {(
                metrics.accuracy * 100
              ).toFixed(1)}
              %
            </strong>
          </div>

          <div>
            <span>Precision</span>
            <strong>
              {(
                metrics.precision * 100
              ).toFixed(1)}
              %
            </strong>
          </div>

          <div>
            <span>Recall</span>
            <strong>
              {(
                metrics.recall * 100
              ).toFixed(1)}
              %
            </strong>
          </div>

          <div>
            <span>F1 Score</span>
            <strong>
              {(
                metrics.f1_score * 100
              ).toFixed(1)}
              %
            </strong>
          </div>

          <div>
            <span>ROC-AUC</span>
            <strong>
              {(
                metrics.roc_auc * 100
              ).toFixed(1)}
              %
            </strong>
          </div>
        </div>
      )}

      <div className="fraud-grid">
        <form
          className="card fraud-form"
          onSubmit={handlePredict}
        >
          <h3>Claim Features</h3>

          <div className="form-grid">
            {numericFields.map(
              ([name, label]) => (
                <label key={name}>
                  <span>{label}</span>

                  <input
                    name={name}
                    type="number"
                    value={form[name]}
                    min="0"
                    step={
                      name ===
                      "claim_amount"
                        ? "0.01"
                        : "1"
                    }
                    onChange={
                      updateField
                    }
                    required
                  />
                </label>
              )
            )}

            <label>
              <span>
                Provider Specialty
              </span>

              <select
                name="provider_specialty"
                value={
                  form.provider_specialty
                }
                onChange={updateField}
              >
                <option value="Radiology">
                  Radiology
                </option>
                <option value="Cardiology">
                  Cardiology
                </option>
                <option value="Orthopedics">
                  Orthopedics
                </option>
                <option value="Neurology">
                  Neurology
                </option>
                <option value="General Medicine">
                  General Medicine
                </option>
              </select>
            </label>

            <label>
              <span>Claim Type</span>

              <select
                name="claim_type"
                value={form.claim_type}
                onChange={updateField}
              >
                <option value="Outpatient">
                  Outpatient
                </option>
                <option value="Inpatient">
                  Inpatient
                </option>
                <option value="Emergency">
                  Emergency
                </option>
              </select>
            </label>

            <label>
              <span>
                Insurance Plan
              </span>

              <select
                name="insurance_plan"
                value={
                  form.insurance_plan
                }
                onChange={updateField}
              >
                <option value="Commercial">
                  Commercial
                </option>
                <option value="Medicare">
                  Medicare
                </option>
                <option value="Medicaid">
                  Medicaid
                </option>
              </select>
            </label>
          </div>

          <div className="checkbox-grid">
            {checkboxFields.map(
              ([name, label]) => (
                <label key={name}>
                  <input
                    name={name}
                    type="checkbox"
                    checked={form[name]}
                    onChange={
                      updateField
                    }
                  />

                  {label}
                </label>
              )
            )}
          </div>

          <button
            className="primary-button full-width"
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Predict Fraud Risk"}
          </button>
        </form>

        <section className="card prediction-panel">
          <h3>
            Prediction &
            Explainability
          </h3>

          {!result ? (
            <div className="empty-state">
              <h3>No prediction yet</h3>

              <p>
                Enter claim details and
                run the ML model.
              </p>
            </div>
          ) : (
            <>
              <div
                className={
                  `risk-banner risk-${result.risk_level.toLowerCase()}`
                }
              >
                <span>
                  {result.prediction}
                </span>

                <strong>
                  {
                    result.fraud_probability
                  }
                  %
                </strong>

                <small>
                  {result.risk_level} risk
                </small>
              </div>

              <div className="prediction-summary">
                <div>
                  <span>
                    Confidence
                  </span>

                  <strong>
                    {
                      result.confidence_score
                    }
                    %
                  </strong>
                </div>

                <div>
                  <span>
                    Model Version
                  </span>

                  <strong>
                    {
                      result.model_version
                    }
                  </strong>
                </div>
              </div>

              <h4>
                Primary risk factors
              </h4>

              <div className="feature-list">
                {riskFactors.map(
                  (item) => (
                    <div
                      key={item.feature}
                    >
                      <span>
                        {item.feature}
                      </span>

                      <strong>
                        {Number(
                          item.importance
                        ).toFixed(4)}
                      </strong>

                      <small>
                        {item.direction
                          .replaceAll(
                            "_",
                            " "
                          )}
                      </small>
                    </div>
                  )
                )}
              </div>

              <h4>
                GenAI explanation
              </h4>

              <p className="explanation-text">
                {
                  result.ai_explanation
                }
              </p>

              <button
                type="button"
                className="secondary-button"
                onClick={
                  handleDownload
                }
                disabled={downloading}
              >
                {downloading
                  ? "Preparing Report..."
                  : "Download Fraud Report"}
              </button>
            </>
          )}
        </section>
      </div>
    </section>
  );
}

export default FraudAnalytics;