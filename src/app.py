import os

from fastapi import FastAPI
from pydantic import BaseModel

from src.inference import build_feature_frame, load_feature_columns, load_model

app = FastAPI()

MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_MODEL_KEY = os.getenv("S3_MODEL_KEY", "data/models/model.pkl")
FEATURE_COLUMNS_PATH = os.getenv("FEATURE_COLUMNS_PATH", "models/feature_columns.json")

model = load_model(MODEL_PATH, s3_bucket=S3_BUCKET, s3_key=S3_MODEL_KEY)
feature_columns = load_feature_columns(FEATURE_COLUMNS_PATH)


class CustomerFeatures(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

@app.get("/")
def home():
    return {"message": "Telco Churn API is running"}

@app.post("/predict")
def predict(features: CustomerFeatures):
    payload = features.model_dump() if hasattr(features, "model_dump") else features.dict()
    feature_frame = build_feature_frame(payload, feature_columns)
    prediction = model.predict(feature_frame)[0]
    probability = model.predict_proba(feature_frame)[0][1]

    return {
        "prediction": int(prediction),
        "churn_probability": float(probability)
    }
