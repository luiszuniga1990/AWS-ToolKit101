# JSON Data Processing Pipeline

Serverless architecture on AWS to process JSON files and visualize them in Amazon Quick.

## Architecture

```
S3 (raw JSON) --> AWS Glue Job (manual) --> Parquet --> Athena --> Amazon Quick (2 dashboards)
```

```
                         JSON Data Pipeline - AWS
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                                                                             │
 │   ┌──────────────┐      ┌──────────────────┐      ┌──────────────────┐     │
 │   │              │      │                  │      │                  │     │
 │   │   S3 Bucket  │      │   AWS Glue Job   │      │  S3 Bucket       │     │
 │   │  (Raw JSON)  │─────>│   (Manual ETL)   │─────>│  (Parquet)       │     │
 │   │              │      │                  │      │                  │     │
 │   │ sample-001   │      │  - Read JSON     │      │ /processed/      │     │
 │   │ sample-002   │      │  - Clean data    │      │   /sales/        │     │
 │   │ sample-003   │      │  - Deduplicate   │      │   /returns/      │     │
 │   │   ...        │      │  - Partition     │      │                  │     │
 │   └──────────────┘      └──────────────────┘      └────────┬─────────┘     │
 │                                                            │               │
 │                          ┌─────────────────┐               │               │
 │                          │  Glue Catalog   │<──────────────┘               │
 │                          │  (Database +    │                               │
 │                          │   Table)        │                               │
 │                          └────────┬────────┘                               │
 │                                   │                                        │
 │                          ┌────────▼────────┐                               │
 │                          │                 │                               │
 │                          │  Amazon Athena  │                               │
 │                          │  (SQL Queries)  │                               │
 │                          │                 │                               │
 │                          └────────┬────────┘                               │
 │                                   │                                        │
 │                    ┌──────────────┴──────────────┐                         │
 │                    │                             │                         │
 │           ┌────────▼─────────┐         ┌────────▼─────────┐               │
 │           │  Amazon Quick    │         │  Amazon Quick    │               │
 │           │  Dashboard 1    │         │  Dashboard 2    │               │
 │           │                 │         │                 │               │
 │           │ General Summary │         │ Detail &        │               │
 │           │                 │         │ Trends          │               │
 │           └─────────────────┘         └─────────────────┘               │
 │                                                                             │
 └─────────────────────────────────────────────────────────────────────────────┘

 Prerequisite: Amazon Quick must be subscribed beforehand (user ARN is required)
```

## Prerequisites

- AWS CLI configured with valid credentials
- IAM permissions for CloudFormation, S3, Glue, Athena, and QuickSight
- **Amazon Quick (QuickSight) already subscribed and configured** in the AWS account
- Amazon Quick user ARN

```bash
# Get the Amazon Quick user ARN
aws quicksight list-users --aws-account-id ACCOUNT_ID --namespace default --region us-east-1
```

## Project Structure

```
.
├── data-processing-template.yaml   # CloudFormation template (full infrastructure)
├── glue-job-script.py              # PySpark script for the Glue Job (ETL)
├── sample-data/                    # Sample JSON files
│   ├── sample-001.json
│   ├── sample-002.json
│   └── sample-003.json
├── quick-setup.md                  # Amazon Quick setup guide
├── README.md                       # This file
└── .gitignore
```

## Resources Created by the Stack

| Resource | Type | Description |
|----------|------|-------------|
| RawDataBucket | S3 | Bucket for incoming JSON files |
| GlueScriptsBucket | S3 | Bucket for Glue Job scripts |
| AthenaResultsBucket | S3 | Bucket for Athena query results |
| GlueServiceRole | IAM Role | Permissions for the Glue Job |
| GlueDatabase | Glue Database | Data catalog |
| GlueJob | Glue Job | ETL: JSON to Parquet (manual execution) |
| AthenaWorkgroup | Athena | Workgroup for SQL queries |
| QuickDataSource | QuickSight | Connection to Athena |
| QuickDataSet | QuickSight | Dataset with processed data (SPICE) |
| QuickDashboard1 | QuickSight | Dashboard - General Summary |
| QuickDashboard2 | QuickSight | Dashboard - Detail & Trends |
| QuickAthenaPolicy | IAM Policy | Amazon Quick permissions for Athena/S3 |

## Deployment

### Step 1: Deploy the CloudFormation stack

```bash
aws cloudformation create-stack \
  --stack-name data-processing-stack \
  --template-body file://data-processing-template.yaml \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=data-processing \
    ParameterKey=QuickSightUserArn,ParameterValue=arn:aws:quicksight:us-east-1:ACCOUNT_ID:user/default/USERNAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 2: Verify stack status

```bash
aws cloudformation describe-stacks \
  --stack-name data-processing-stack \
  --query 'Stacks[0].StackStatus' \
  --region us-east-1
```

### Step 3: Upload the Glue script

```bash
aws s3 cp glue-job-script.py \
  s3://data-processing-glue-scripts-ACCOUNT_ID/glue-job-script.py \
  --region us-east-1
```

### Step 4: Upload sample data

```bash
aws s3 cp sample-data/ \
  s3://data-processing-raw-data-ACCOUNT_ID/ \
  --recursive --region us-east-1
```

### Step 5: Run the Glue Job (manual)

```bash
aws glue start-job-run \
  --job-name data-processing-json-processor \
  --region us-east-1
```

### Step 6: Verify execution

```bash
# Get the run-id from the previous step output
aws glue get-job-run \
  --job-name data-processing-json-processor \
  --run-id RUN_ID \
  --region us-east-1
```

## Query Data with Athena

```sql
-- View all processed records
SELECT * FROM data_processing_database.processed_data LIMIT 20;

-- Summary by category
SELECT category, COUNT(*) as total, SUM(amount) as total_amount
FROM data_processing_database.processed_data
GROUP BY category;

-- Summary by region
SELECT region, COUNT(*) as total, SUM(amount) as total_amount
FROM data_processing_database.processed_data
GROUP BY region
ORDER BY total_amount DESC;
```

## Amazon Quick Dashboards

The stack automatically creates 2 dashboards:

1. **General Summary** - Consolidated view of all processed data
2. **Detail & Trends** - Detailed analysis with time-based trends

Access them from the Amazon Quick console in us-east-1.

## Data Schema

Input JSON files must follow this schema:

```json
{
  "id": "string - Unique transaction identifier",
  "data": "string - Transaction description",
  "timestamp": "string - Date/time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)",
  "category": "string - Category (sales, returns, etc.)",
  "amount": "number - Transaction amount",
  "region": "string - Geographic region",
  "status": "string - Status (completed, pending, processed)"
}
```

## ETL Pipeline (Glue Job)

The `glue-job-script.py` script performs the following transformations:

1. Reads all JSON files from the raw bucket
2. Casts data types (timestamp, amount)
3. Cleans null values in category and status
4. Removes duplicate records by id
5. Writes in Parquet format partitioned by category
6. Creates/updates the table in the Glue Catalog for Athena

## Cleanup

```bash
# Empty buckets
aws s3 rm s3://data-processing-raw-data-ACCOUNT_ID --recursive --region us-east-1
aws s3 rm s3://data-processing-glue-scripts-ACCOUNT_ID --recursive --region us-east-1
aws s3 rm s3://data-processing-athena-results-ACCOUNT_ID --recursive --region us-east-1

# Delete the stack
aws cloudformation delete-stack --stack-name data-processing-stack --region us-east-1
```

## Estimated Costs

Based on official AWS pricing for us-east-1 (April 2026).

| Service | Detail | Minimum Usage | Medium Usage |
|---------|--------|--------------|-------------|
| S3 Standard | $0.023/GB/month | ~$0.23/month (10 GB) | ~$2.30/month (100 GB) |
| Glue Job | $0.44/DPU-hour, 2 DPU (G.1X) | ~$0.73/month (10 runs x 5 min) | ~$14.67/month (100 runs x 10 min) |
| Athena | $5.00/TB scanned | ~$0.05/month (10 GB scan) | ~$5.00/month (1 TB scan) |
| Glue Catalog | First 1M objects free | $0.00 | $0.00 |
| Amazon Quick - Author (1) | $24/user/month | $24.00/month | $24.00/month |
| Amazon Quick - Reader (1) | $3/user/month | $3.00/month | $3.00/month |
| Amazon Quick - SPICE | $0.38/GB/month (10 GB included per Author) | $0.00 (included) | $0.00 (included) |
| **Estimated Total** | | **~$28.01/month** | **~$48.97/month** |

**Amazon Quick Sight Pricing ([official reference](https://aws.amazon.com/quick/quicksight/pricing/)):**

| Type | Monthly Price | Annual Price |
|------|--------------|-------------|
| Author | $24/user/month | $18/user/month (annual commitment) |
| Author Pro | $40/user/month | - |
| Reader | $3/user/month | - |
| Reader Pro | $20/user/month | - |
| SPICE | $0.38/GB/month (10 GB included per Author) | - |

**Important notes:**
- If Author Pro is used or Q&A with Topics is enabled, an additional $250/month per account fee applies
- SPICE includes 10 GB free per provisioned Author, sufficient for this project
- The table assumes 1 Author + 1 Reader as minimum
- Glue Job uses 2 G.1X workers (= 2 DPU), billed per second with 1-minute minimum
- Athena charges per TB scanned; using Parquet reduces costs ~90% vs JSON
- Prices may vary by region

*Prices checked April 2026, subject to changes by AWS*

## License

MIT License
