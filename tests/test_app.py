import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd


class InferenceTests(unittest.TestCase):
    def test_build_feature_frame_matches_training_columns(self) -> None:
        from src import inference

        payload = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "Yes",
            "tenure": 65,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "Yes",
            "DeviceProtection": "Yes",
            "TechSupport": "Yes",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Two year",
            "PaperlessBilling": "No",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 94.55,
            "TotalCharges": 6078.75,
        }
        feature_columns = pd.read_csv("data/processed/X_train.csv").columns.tolist()

        feature_frame = inference.build_feature_frame(payload, feature_columns)

        self.assertEqual(feature_columns, feature_frame.columns.tolist())
        self.assertEqual(float(feature_frame.iloc[0]["TotalCharges"]), 6078.75)
        self.assertTrue(bool(feature_frame.iloc[0]["gender_Male"]))
        self.assertTrue(bool(feature_frame.iloc[0]["Contract_Two year"]))

    def test_ensure_model_artifact_downloads_from_s3_when_missing(self) -> None:
        from src import inference

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "models" / "model.pkl"
            def fake_download(bucket, key, local_path):
                destination = Path(local_path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"model")
                return destination

            download = Mock(side_effect=fake_download)

            with patch.object(inference, "download_file", download):
                resolved = inference.ensure_model_artifact(
                    model_path=model_path,
                    s3_bucket="telco-churn-aws",
                    s3_key="data/models/model.pkl",
                )

            self.assertEqual(resolved, model_path)
            self.assertTrue(model_path.exists())
            download.assert_called_once_with(
                "telco-churn-aws",
                "data/models/model.pkl",
                model_path,
            )

    def test_load_feature_columns_from_json(self) -> None:
        from src import inference

        with tempfile.TemporaryDirectory() as temp_dir:
            feature_columns_path = Path(temp_dir) / "feature_columns.json"
            feature_columns_path.write_text(json.dumps(["tenure", "MonthlyCharges"]))

            columns = inference.load_feature_columns(feature_columns_path)

        self.assertEqual(columns, ["tenure", "MonthlyCharges"])


if __name__ == "__main__":
    unittest.main()
