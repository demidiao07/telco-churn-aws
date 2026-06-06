import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X_train = pd.read_csv("data/processed/X_train.csv")
X_test = pd.read_csv("data/processed/X_test.csv")
y_train = pd.read_csv("data/processed/y_train.csv")
y_test = pd.read_csv("data/processed/y_test.csv")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train.values.ravel())

preds = model.predict(X_test)

acc = accuracy_score(y_test, preds)

print(f"Accuracy: {acc:.4f}")

joblib.dump(model, "models/model.pkl")

print("Model saved to models/model.pkl")