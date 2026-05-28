# Stack 1: Auth (Cognito)

## Overview
Authentication stack that provisions Amazon Cognito to manage user login for the ASMMv2 web interface.

## Components

| Resource | Type | Description |
|---|---|---|
| UserPool | Cognito User Pool | User pool with email verification |
| UserPoolClient | Cognito App Client | Web client (SRP auth, no secret) |
| IdentityPool | Cognito Identity Pool | Identity federation |

## Diagram

```
┌─────────────────────────────────────────────┐
│              Stack 1: Auth                   │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │         Cognito User Pool             │  │
│  │  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │  App Client │  │ Password Policy│  │  │
│  │  └─────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────┘  │
│                    │                         │
│                    ▼                         │
│  ┌───────────────────────────────────────┐  │
│  │       Cognito Identity Pool           │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Outputs: UserPoolId, ClientId, IdentityId  │
└─────────────────────────────────────────────┘
```

## Deployment

```bash
# 1. Set variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Deploy stack
aws cloudformation deploy \
  --template-file stack-1-auth.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-auth" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# 3. Get outputs
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-auth" \
  --query "Stacks[0].Outputs" --output table --region $REGION
```
