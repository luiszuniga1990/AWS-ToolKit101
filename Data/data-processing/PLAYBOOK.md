# Playbook: Data Processing Pipeline Deployment

Step-by-step guide to deploy the serverless JSON data processing pipeline on AWS.

## Architecture

```
S3 (raw JSON) → AWS Glue Job → Parquet → Athena → Amazon QuickSight (2 dashboards)
```

---

## Prerequisites

- [ ] AWS CLI installed and configured with valid credentials
- [ ] IAM permissions for CloudFormation, S3, Glue, Athena, and QuickSight
- [ ] Amazon QuickSight subscribed and configured (see `quick-setup.md`)
- [ ] Obtain your QuickSight User ARN:

```bash
aws quicksight list-users \
  --aws-account-id YOUR_ACCOUNT_ID \
  --namespace default \
  --region us-east-1
```

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/luiszuniga1990/AWS-ToolKit101.git
cd AWS-ToolKit101/Data/data-processing
```

## Step 2: Deploy the CloudFormation Stack

```bash
aws cloudformation create-stack \
  --stack-name data-processing-stack \
  --template-body file://data-processing-template.yaml \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=data-processing \
    ParameterKey=QuickSightUserArn,ParameterValue=arn:aws:quicksight:us-east-1:YOUR_ACCOUNT_ID:user/default/YOUR_USERNAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

## Step 3: Verify Stack Creation

```bash
aws cloudformation describe-stacks \
  --stack-name data-processing-stack \
  --query 'Stacks[0].StackStatus' \
  --region us-east-1
```

Wait until the status is `CREATE_COMPLETE`.

## Step 4: Upload the Glue Script

```bash
aws s3 cp glue-job-script.py \
  s3://data-processing-glue-scripts-YOUR_ACCOUNT_ID/glue-job-script.py \
  --region us-east-1
```

## Step 5: Upload Sample Data to S3

```bash
aws s3 cp sample-data/ \
  s3://data-processing-raw-data-YOUR_ACCOUNT_ID/ \
  --recursive --region us-east-1
```

## Step 6: Run the Glue Job

```bash
aws glue start-job-run \
  --job-name data-processing-json-processor \
  --region us-east-1
```

## Step 7: Verify Job Execution

```bash
aws glue get-job-run \
  --job-name data-processing-json-processor \
  --run-id YOUR_RUN_ID \
  --region us-east-1
```

Wait until the status is `SUCCEEDED`.

## Step 8: Query Data with Athena

```sql
-- View processed records
SELECT * FROM data_processing_database.processed_data LIMIT 20;

-- Summary by category
SELECT category, COUNT(*) as total, SUM(amount) as total_amount
FROM data_processing_database.processed_data
GROUP BY category;
```

## Step 9: Verify QuickSight Dashboards

1. Navigate to the Amazon QuickSight console in `us-east-1`
2. Confirm that both dashboards are available:
   - **General Summary** — Consolidated overview
   - **Detail & Trends** — Detailed analysis with time-based trends

---

## Cleanup (When No Longer Needed)

```bash
# Empty buckets
aws s3 rm s3://data-processing-raw-data-YOUR_ACCOUNT_ID --recursive --region us-east-1
aws s3 rm s3://data-processing-glue-scripts-YOUR_ACCOUNT_ID --recursive --region us-east-1
aws s3 rm s3://data-processing-athena-results-YOUR_ACCOUNT_ID --recursive --region us-east-1

# Delete the stack
aws cloudformation delete-stack \
  --stack-name data-processing-stack \
  --region us-east-1
```

---

> 💡 **Note:** Replace `YOUR_ACCOUNT_ID` and `YOUR_USERNAME` with your actual AWS values in all commands.
