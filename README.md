# Telco Churn AWS

This project builds and deploys a customer churn prediction workflow on AWS using the IBM Telco Customer Churn dataset. The current architecture keeps the machine learning stack intentionally simple so the focus stays on cloud engineering: data is prepared in Python, model artifacts are stored in Amazon S3, training and inference run on Amazon EC2, and infrastructure health is monitored through Amazon CloudWatch.

## Project overview

The goal is to predict whether a telecom customer will churn using a Random Forest classifier trained on customer account, service, and billing features. For the course project, the more important objective is not model novelty but showing a clean end-to-end AWS workflow that covers:

- data collection and preprocessing
- model training and artifact storage
- inference deployment on EC2 with FastAPI
- cloud storage through S3
- monitoring through CloudWatch

## Dataset

- Dataset: IBM Telco Customer Churn
- Local raw file: `data/raw/telco_customer_churn.csv`
- Shape: 7,043 rows and 21 columns
- Target column: `Churn`

The preprocessing script removes `customerID`, converts `TotalCharges` to numeric, drops rows with missing values, maps `Churn` to `0/1`, and one-hot encodes categorical features.

## AWS resources

- Region: `us-east-2`
- S3 bucket: `telco-churn-aws`
- Current AWS evidence is stored in `docs/`

Relevant screenshots already included:

- `docs/architecture-diagram.png`
- `docs/ec2-instance.png`
- `docs/s3-artifacts.png`
- `docs/cloudwatch-monitoring.png`
- `docs/fastapi-endpoint.png`

## Repository structure

```text
.
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── notebooks/
│   └── eda.ipynb
├── src/
│   ├── app.py
│   ├── aws_io.py
│   ├── preprocess.py
│   └── train.py
├── tests/
├── .env.example
└── requirements.txt
```

## Local setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional environment configuration:

```bash
cp .env.example .env
```

The `.env.example` file contains the default AWS bucket and path settings used for this project:

- `AWS_REGION=us-east-2`
- `S3_BUCKET=telco-churn-aws`
- `S3_MODEL_KEY=data/models/model.pkl`
- `S3_RAW_PREFIX=raw/`
- `S3_PROCESSED_PREFIX=processed/`
- `S3_MODEL_PREFIX=models/`

## Run the preprocessing pipeline

From the repository root:

```bash
python3 src/preprocess.py
```

Outputs written to `data/processed/`:

- `telco_churn_processed.csv`
- `X_train.csv`
- `X_test.csv`
- `y_train.csv`
- `y_test.csv`

## Train the model

Run:

```bash
python3 src/train.py
```

Expected result:

- model metrics printed to the console
- trained artifact saved to `models/model.pkl`

## Run the API locally

After training completes, start the FastAPI app:

```bash
uvicorn src.app:app --reload
```

Then open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI spec: `http://127.0.0.1:8000/openapi.json`

## Deploy on EC2 with the S3 model

This is the working deployment path used for the AWS project demo.

### AWS resources used

- EC2 instance name: `telco-churn-api`
- EC2 public endpoint: `http://3.143.205.27:8000/docs`
- S3 model path: `s3://telco-churn-aws/data/models/model.pkl`
- Service name on EC2: `telco-churn-api`

### 1. SSH into the EC2 instance

From a local machine:

```bash
chmod 400 ~/Downloads/telco-churn-key.pem
ssh -i ~/Downloads/telco-churn-key.pem ec2-user@ec2-3-143-205-27.us-east-2.compute.amazonaws.com
```

### 2. Install the project on EC2

Run on the EC2 instance:

```bash
sudo dnf update -y
sudo dnf install -y git python3 python3-pip
git clone https://github.com/demidiao07/telco-churn-aws.git
cd telco-churn-aws
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install fastapi uvicorn
```

### 3. Copy the trained model onto EC2

Recommended approach: attach an IAM role to the EC2 instance with at least `s3:GetObject` permission for `s3://telco-churn-aws/data/models/model.pkl`, then let the app or setup script fetch the model directly from S3.

If the EC2 instance does not yet have an IAM role with S3 access, download `model.pkl` from the S3 console to the local machine and then copy it to EC2:

```bash
scp -i ~/Downloads/telco-churn-key.pem ~/Downloads/model.pkl ec2-user@3.143.205.27:~/telco-churn-aws/models/model.pkl
```

Verify on EC2:

```bash
ls -lh ~/telco-churn-aws/models/model.pkl
```

IAM-role-based pull on EC2:

```bash
aws s3 cp s3://telco-churn-aws/data/models/model.pkl ~/telco-churn-aws/models/model.pkl
```

### 4. Run the API manually

For a manual session-based start:

```bash
cd ~/telco-churn-aws
source .venv/bin/activate
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

### 5. Run the API as a persistent Linux service

Create the systemd unit:

```bash
sudo tee /etc/systemd/system/telco-churn-api.service > /dev/null <<'EOF'
[Unit]
Description=Telco Churn FastAPI
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/telco-churn-aws
Environment="PATH=/home/ec2-user/telco-churn-aws/.venv/bin"
ExecStart=/home/ec2-user/telco-churn-aws/.venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telco-churn-api
sudo systemctl start telco-churn-api
sudo systemctl status telco-churn-api
```

Useful service commands:

```bash
sudo systemctl status telco-churn-api
sudo systemctl restart telco-churn-api
sudo systemctl stop telco-churn-api
```

### 6. Validate the deployment

Open:

- `http://3.143.205.27:8000/docs`

Confirmed test payload used for the live demo:

```json
{
  "SeniorCitizen": 0,
  "tenure": 65,
  "MonthlyCharges": 94.55,
  "TotalCharges": 6078.75,
  "gender_Male": true,
  "Partner_Yes": true,
  "Dependents_Yes": true,
  "PhoneService_Yes": true,
  "MultipleLines_No phone service": false,
  "MultipleLines_Yes": true,
  "InternetService_Fiber optic": true,
  "InternetService_No": false,
  "OnlineSecurity_No internet service": false,
  "OnlineSecurity_Yes": true,
  "OnlineBackup_No internet service": false,
  "OnlineBackup_Yes": true,
  "DeviceProtection_No internet service": false,
  "DeviceProtection_Yes": true,
  "TechSupport_No internet service": false,
  "TechSupport_Yes": true,
  "StreamingTV_No internet service": false,
  "StreamingTV_Yes": false,
  "StreamingMovies_No internet service": false,
  "StreamingMovies_Yes": false,
  "Contract_One year": false,
  "Contract_Two year": true,
  "PaperlessBilling_Yes": false,
  "PaymentMethod_Credit card (automatic)": true,
  "PaymentMethod_Electronic check": false,
  "PaymentMethod_Mailed check": false
}
```

Expected response from the live deployment:

```json
{
  "prediction": 0,
  "churn_probability": 0.1
}
```

## Current API limitation

The current `/predict` endpoint expects already engineered feature columns that match the trained model input. Supporting raw customer-style JSON input is planned for the next implementation phase.

## S3 helper foundation

Day 1 includes a small S3 utility scaffold in `src/aws_io.py`. It provides helper functions to:

- build S3 URIs
- upload local files to S3
- download S3 objects to local paths

This foundation will be wired into preprocessing, training, and deployment in the next phase.

## Monitoring and deployment evidence

The repository currently includes screenshots showing:

- EC2 instance deployment
- model artifact storage in S3
- CloudWatch EC2 monitoring
- FastAPI endpoint exposure

The next implementation phase will convert more of that process from manual steps into explicit deployment and artifact-management code.
