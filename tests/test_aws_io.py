import importlib
import unittest
from unittest.mock import Mock


class AwsIoTests(unittest.TestCase):
    def test_s3_uri_formats_bucket_and_key(self) -> None:
        aws_io = importlib.import_module("src.aws_io")

        self.assertEqual(
            aws_io.s3_uri("telco-churn-aws", "models/model.pkl"),
            "s3://telco-churn-aws/models/model.pkl",
        )

    def test_upload_file_uses_provided_s3_client(self) -> None:
        aws_io = importlib.import_module("src.aws_io")
        client = Mock()

        aws_io.upload_file(
            "models/model.pkl",
            "telco-churn-aws",
            "models/model.pkl",
            s3_client=client,
        )

        client.upload_file.assert_called_once_with(
            "models/model.pkl",
            "telco-churn-aws",
            "models/model.pkl",
        )


if __name__ == "__main__":
    unittest.main()
