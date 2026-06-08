# Telco Churn AWS Handoff Checklist

This file is a short handoff note for teammates and for final project assembly.

## What is already done

- Dataset preprocessing is implemented in `src/preprocess.py`.
- Model training is implemented in `src/train.py`.
- Feature-column metadata is generated alongside the trained model for inference compatibility.
- The trained model artifact exists in S3 at `s3://telco-churn-aws/data/models/model.pkl`.
- EC2 instance deployment has been completed in `us-east-2`.
- FastAPI is live on the EC2 instance at `http://3.143.205.27:8000/docs`.
- `/predict` has been tested successfully with a valid payload and returned:

```json
{
  "prediction": 0,
  "churn_probability": 0.1
}
```

- The API is running as a persistent Linux service:
  - service name: `telco-churn-api`
- Deployment assets are now tracked in the repo:
  - `deploy/setup_ec2.sh`
  - `deploy/telco-churn-api.service`
- The README contains the validated EC2 deployment steps.

## What is still required for final submission

- Architecture deliverable
  - final architecture diagram image
  - preferably the editable `drawio` source file too

- Cost / planning deliverables
  - AWS Pricing Calculator estimate
  - project timeline or milestone breakdown

- Cloud evidence
  - S3 screenshot showing `model.pkl`
  - EC2 screenshot showing running instance
  - FastAPI `/docs` screenshot
  - successful `/predict` screenshot
  - `systemctl status telco-churn-api` screenshot
  - CloudWatch screenshot while the instance/service is active

- Final written materials
  - final report or summary document
  - presentation slides / PDF

## Optional but recommended cleanup

- Attach an IAM role to the EC2 instance with `s3:GetObject` access to `s3://telco-churn-aws/data/models/model.pkl`
  - This removes the need for manual model copy from a local machine.

- Update the live EC2 server to the latest pushed branch:
  - branch: `codex/day1-reproducibility`

- If the team wants a cleaner demo later:
  - verify the full deploy flow from `deploy/setup_ec2.sh`
  - add CloudWatch log or alarm evidence

## Quick project facts

- AWS region: `us-east-2`
- S3 bucket: `telco-churn-aws`
- S3 model path: `s3://telco-churn-aws/data/models/model.pkl`
- EC2 endpoint: `http://3.143.205.27:8000/docs`
- systemd service: `telco-churn-api`
