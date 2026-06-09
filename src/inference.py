import json
import os
from pathlib import Path
from typing import List

import joblib
import pandas as pd

from src.aws_io import download_file
from src.preprocess import clean_data


DEFAULT_MODEL_PATH = Path("models/model.pkl")
DEFAULT_FEATURE_COLUMNS_PATH = Path("models/feature_columns.json")
DEFAULT_FALLBACK_TRAINING_DATA = Path("data/processed/X_train.csv")


def ensure_model_artifact(
    model_path: Path = DEFAULT_MODEL_PATH,
    s3_bucket: str = None,
    s3_key: str = None,
) -> Path:
    resolved_path = Path(model_path)
    if resolved_path.exists():
        return resolved_path

    bucket = s3_bucket or os.getenv("S3_BUCKET")
    key = s3_key or os.getenv("S3_MODEL_KEY")
    if not bucket or not key:
        raise FileNotFoundError(
            f"Model file not found at {resolved_path} and no S3 fallback configured."
        )

    return download_file(bucket, key, resolved_path)


def load_feature_columns(
    feature_columns_path: Path = DEFAULT_FEATURE_COLUMNS_PATH,
    fallback_training_data: Path = DEFAULT_FALLBACK_TRAINING_DATA,
) -> List[str]:
    resolved_columns_path = Path(feature_columns_path)
    if resolved_columns_path.exists():
        return json.loads(resolved_columns_path.read_text())

    fallback_path = Path(fallback_training_data)
    if fallback_path.exists():
        return pd.read_csv(fallback_path).columns.tolist()

    raise FileNotFoundError(
        "No feature column metadata found. Expected models/feature_columns.json or data/processed/X_train.csv."
    )


def build_feature_frame(payload: dict, feature_columns: List[str]) -> pd.DataFrame:
    raw_frame = pd.DataFrame([payload])
    cleaned_frame = clean_data(raw_frame, training=False)
    feature_frame = pd.DataFrame(0.0, index=[0], columns=feature_columns)

    for numeric_column in ("SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"):
        if numeric_column in feature_frame.columns:
            feature_frame.at[0, numeric_column] = cleaned_frame.iloc[0][numeric_column]

    for column in feature_columns:
        if "_" not in column:
            continue

        source_column, encoded_value = column.split("_", 1)
        raw_value = str(cleaned_frame.iloc[0][source_column])
        feature_frame.at[0, column] = int(raw_value == encoded_value)

    return feature_frame


def load_model(
    model_path: Path = DEFAULT_MODEL_PATH,
    s3_bucket: str = None,
    s3_key: str = None,
):
    resolved_model_path = ensure_model_artifact(model_path, s3_bucket=s3_bucket, s3_key=s3_key)
    return joblib.load(resolved_model_path)
