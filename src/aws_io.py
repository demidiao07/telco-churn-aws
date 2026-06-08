from pathlib import Path


def get_s3_client():
    import boto3

    return boto3.client("s3")


def s3_uri(bucket: str, key: str) -> str:
    normalized_key = key.lstrip("/")
    return f"s3://{bucket}/{normalized_key}"


def upload_file(local_path, bucket: str, key: str, s3_client=None) -> str:
    client = s3_client or get_s3_client()
    normalized_key = key.lstrip("/")
    client.upload_file(str(local_path), bucket, normalized_key)
    return s3_uri(bucket, normalized_key)


def download_file(bucket: str, key: str, local_path, s3_client=None) -> Path:
    client = s3_client or get_s3_client()
    destination = Path(local_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, key.lstrip("/"), str(destination))
    return destination
