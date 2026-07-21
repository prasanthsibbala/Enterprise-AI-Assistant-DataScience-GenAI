# Enterprise AI Assistant — Data Science + Generative AI

This project combines a healthcare fraud machine-learning workflow with a secured Generative AI document assistant.

## Main capabilities

- Healthcare fraud prediction using a Random Forest classifier
- Synthetic reproducible training dataset for local development
- Accuracy, precision, recall, F1 and ROC-AUC model metrics
- Feature-importance based explainability
- Gemini-generated business explanation with safe fallback text
- Downloadable fraud analysis PDF
- PDF ingestion, chunking, embeddings and ChromaDB RAG
- Gemini document question answering
- JWT registration, login and protected APIs
- React dashboard for ML prediction and document assistant

## Run backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Gemini API key and a strong JWT secret to .env
python -m uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

The first metrics or prediction request automatically trains and saves the fraud model. To train manually:

```bash
cd backend
python training/train_fraud_model.py
```

## Run frontend

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## New fraud endpoints

- `POST /api/v1/fraud/predict`
- `GET /api/v1/fraud/model/metrics`
- `POST /api/v1/fraud/model/train`

All fraud endpoints require a valid JWT bearer token.

## Resume-ready project summary

Designed and developed a healthcare fraud analytics and Generative AI platform using Python, Pandas, Scikit-learn, FastAPI, Gemini, ChromaDB, LangChain text splitting and React. Built an end-to-end classification pipeline with feature engineering, model evaluation, explainability, JWT-secured APIs, RAG-based document intelligence and automated PDF reporting.

## Important

The bundled training data is synthetic and intended for portfolio/demo use. A production implementation should use governed claims data, bias testing, model monitoring, calibration and human review.
