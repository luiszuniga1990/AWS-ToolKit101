# Stack 4: Assessment Lambdas

## Overview
Serverless stack with 3 Lambda functions that perform the AWS account security analysis. Each Lambda covers a sector of the AWS Security Maturity Model v2: Identity, Logging, and Detection.

## Components

| Resource | Type | Description |
|---|---|---|
| AssessmentApi | API Gateway HTTP | Assessment endpoint |
| AssessIamFunction | Lambda | Analyzes IAM: MFA, access keys, root, password policy |
| AssessLoggingFunction | Lambda | Analyzes CloudTrail, Config, CloudWatch |
| AssessDetectionFunction | Lambda | Analyzes GuardDuty, Security Hub |

## Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                  Stack 4: Assessment                           │
│                                                                │
│  ┌──────────┐     ┌────────────────────────────────────────┐   │
│  │ Frontend │────▶│          API Gateway HTTP              │   │
│  └──────────┘     └──────┬───────────┬───────────┬─────────┘   │
│                          │           │           │             │
│               POST /assess-iam  /assess-logging  /assess-detection
│                          │           │           │             │
│                          ▼           ▼           ▼             │
│                   ┌──────────┐┌──────────┐┌──────────────┐     │
│                   │ Lambda 1 ││ Lambda 2 ││   Lambda 3   │     │
│                   │   IAM    ││ Logging  ││  Detection   │     │
│                   └────┬─────┘└────┬─────┘└──────┬───────┘     │
│                        │           │             │              │
│                        ▼           ▼             ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          User's AWS Account (read-only)                 │   │
│  │  IAM │ CloudTrail │ Config │ CloudWatch │ GuardDuty │ SH│   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  Output: AssessmentApiUrl                                      │
└────────────────────────────────────────────────────────────────┘
```

## Deployment

```bash
# 1. Set variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Package Lambdas
aws cloudformation package \
  --template-file stack-4-assessment.yaml \
  --s3-bucket "${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" \
  --output-template-file stack-4-assessment-packaged.yaml \
  --region $REGION

# 3. Deploy
aws cloudformation deploy \
  --template-file stack-4-assessment-packaged.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-assessment" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# 4. Get API URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-assessment" \
  --query "Stacks[0].Outputs[?OutputKey=='AssessmentApiUrl'].OutputValue" \
  --output text --region $REGION
```
