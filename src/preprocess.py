import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


RAW_PATH = Path("data/raw/telco_customer_churn.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_PATH = PROCESSED_DIR / "telco_churn_processed.csv"


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


FEATURE_COLUMNS_PATH = Path("models/feature_columns.json")


def clean_data(df: pd.DataFrame, training: bool = True) -> pd.DataFrame:
    df = df.copy()

    # Drop customer ID because it is not useful for prediction
    df = df.drop(columns=["customerID"], errors="ignore")

    # Convert TotalCharges from object to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Drop rows with missing TotalCharges during training; prediction requires a value.
    if training:
        df = df.dropna()

    # Convert target variable
    if "Churn" in df.columns:
        df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    categorical_cols = df.select_dtypes(include=["object"]).columns

    df_encoded = pd.get_dummies(
        df,
        columns=categorical_cols,
        drop_first=True
    )

    return df_encoded



def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FEATURE_COLUMNS_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = load_data(RAW_PATH)
    df = clean_data(df)
    df = encode_features(df)

    df.to_csv(PROCESSED_PATH, index=False)

    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    X_train.to_csv(PROCESSED_DIR / "X_train.csv", index=False)
    X_test.to_csv(PROCESSED_DIR / "X_test.csv", index=False)
    y_train.to_csv(PROCESSED_DIR / "y_train.csv", index=False)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=False)
    FEATURE_COLUMNS_PATH.write_text(json.dumps(X.columns.tolist(), indent=2))

    print(f"Processed data saved to {PROCESSED_PATH}")
    print(f"Processed shape: {df.shape}")
    print("Train/test files saved to data/processed/")


if __name__ == "__main__":
    main()
