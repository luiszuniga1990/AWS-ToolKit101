# Stack 3: Validation Lambdas

## Overview
Serverless stack with 3 Lambda functions that validate the user's AWS credentials: verify connectivity, confirm read-only permissions, and block if write permissions are detected.

## Components

| Resource | Type | Description |
|---|---|---|
| ValidationApi | API Gateway HTTP | Validation endpoint |
| ValidateCredentialsFunction | Lambda | Validates credentials via STS GetCallerIdentity |
| ValidateReadOnlyFunction | Lambda | Verifies only ReadOnly policies are attached |
| ValidateConnectionFunction | Lambda | Orchestrates full validation |

## Diagram

```
┌────────────────────────────────────────────────────────────┐
│                 Stack 3: Validation                         │
│                                                            │
│  ┌──────────┐     ┌──────────────────────────────────────┐ │
│  │ Frontend │────▶│        API Gateway HTTP              │ │
│  └──────────┘     └──────┬──────────┬──────────┬─────────┘ │
│                          │          │          │           │
│              POST /validate-credentials       │           │
│                          │    POST /validate-readonly     │
│                          │          │    POST /validate   │
│                          ▼          ▼          ▼           │
│                   ┌──────────┐┌──────────┐┌──────────┐    │
│                   │ Lambda 1 ││ Lambda 2 ││ Lambda 3 │    │
│                   │Credentials││ ReadOnly ││Connection│    │
│                   └─────┬────┘└─────┬────┘└─────┬────┘    │
│                         │           │           │          │
│                         ▼           ▼           ▼          │
│                   ┌─────────────────────────────────┐      │
│                   │  AWS STS / IAM (target account)  │      │
│                   └─────────────────────────────────┘      │
│                                                            │
│  Output: ValidationApiUrl                                  │
└────────────────────────────────────────────────────────────┘
```

## Deployment

```bash
# 1. Set variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Create artifacts bucket (if it doesn't exist)
aws s3 mb "s3://${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" --region $REGION

# 3. Package Lambdas
aws cloudformation package \
  --template-file stack-3-validation.yaml \
  --s3-bucket "${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" \
  --output-template-file stack-3-validation-packaged.yaml \
  --region $REGION

# 4. Deploy
aws cloudformation deploy \
  --template-file stack-3-validation-packaged.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-validation" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# 5. Get API URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-validation" \
  --query "Stacks[0].Outputs[?OutputKey=='ValidationApiUrl'].OutputValue" \
  --output text --region $REGION
```
