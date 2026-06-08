#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/demidiao07/telco-churn-aws.git}"
APP_DIR="${APP_DIR:-/home/ec2-user/telco-churn-aws}"
S3_BUCKET="${S3_BUCKET:-telco-churn-aws}"
S3_MODEL_KEY="${S3_MODEL_KEY:-data/models/model.pkl}"

sudo dnf update -y
sudo dnf install -y git python3 python3-pip

if [ ! -d "${APP_DIR}" ]; then
  git clone "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p models
aws s3 cp "s3://${S3_BUCKET}/${S3_MODEL_KEY}" models/model.pkl

sudo cp deploy/telco-churn-api.service /etc/systemd/system/telco-churn-api.service
sudo systemctl daemon-reload
sudo systemctl enable telco-churn-api
sudo systemctl restart telco-churn-api
