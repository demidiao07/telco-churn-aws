from pathlib import Path
import json
import logging

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
MODEL_PATH = Path("models/model.pkl")
FEATURE_COLUMNS_PATH = Path("models/feature_columns.json")


def load_training_data(processed_dir: Path = PROCESSED_DIR) -> tuple:
    x_train = pd.read_csv(processed_dir / "X_train.csv")
    x_test = pd.read_csv(processed_dir / "X_test.csv")
    y_train = pd.read_csv(processed_dir / "y_train.csv")
    y_test = pd.read_csv(processed_dir / "y_test.csv")
    return x_train, x_test, y_train, y_test


def build_model() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )


def save_model(model: RandomForestClassifier, model_path: Path = MODEL_PATH) -> Path:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    return model_path


def save_feature_columns(
    feature_columns, feature_columns_path: Path = FEATURE_COLUMNS_PATH
) -> Path:
    feature_columns_path.parent.mkdir(parents=True, exist_ok=True)
    feature_columns_path.write_text(json.dumps(list(feature_columns), indent=2))
    return feature_columns_path


def main() -> None:
    logger.info("Starting model training pipeline")
    logger.info("Loading data from S3")
    x_train, x_test, y_train, y_test = load_training_data()
    model = build_model()
    logger.info("Training RandomForest model")
    model.fit(x_train, y_train.values.ravel())

    preds = model.predict(x_test)
    acc = accuracy_score(y_test, preds)
    saved_model_path = save_model(model)
    saved_feature_columns_path = save_feature_columns(x_train.columns)
    logger.info("Model training complete. Saving artifacts to models/")

    print(f"Accuracy: {acc:.4f}")
    print(f"Model saved to {saved_model_path}")
    print(f"Feature columns saved to {saved_feature_columns_path}")


if __name__ == "__main__":
    main()
