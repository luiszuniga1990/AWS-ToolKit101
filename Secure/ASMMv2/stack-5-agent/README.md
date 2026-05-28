# Stack 5: Agent (Bedrock AgentCore)

## Overview
AI agent stack that receives assessment results, evaluates them against the AWS Security Maturity Model v2, and generates recommendations in an interactive chat format with links to the official model.

## Components

| Resource | Type | Description |
|---|---|---|
| KnowledgeBaseBucket | S3 Bucket | Security Maturity Model v2 documents |
| AgentRole | IAM Role | Agent role with Bedrock and S3 permissions |
| AgentOrchestratorFunction | Lambda | Orchestrates the agent, invokes Bedrock |
| AgentApi | API Gateway HTTP | /chat endpoint for the frontend |

## Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   Stack 5: Agent                             │
│                                                              │
│  ┌──────────┐     ┌──────────────────┐     ┌─────────────┐  │
│  │ Frontend │────▶│ API Gateway HTTP │────▶│   Lambda    │  │
│  └──────────┘     └──────────────────┘     │Orchestrator │  │
│                          POST /chat         └──────┬──────┘  │
│                                                    │         │
│                                    ┌───────────────┼───────┐ │
│                                    │               ▼       │ │
│                                    │  ┌─────────────────┐  │ │
│                                    │  │ Bedrock Model   │  │ │
│                                    │  │ (Nova Pro)      │  │ │
│                                    │  └─────────────────┘  │ │
│                                    │               │       │ │
│                                    │               ▼       │ │
│                                    │  ┌─────────────────┐  │ │
│                                    │  │  S3 KB Bucket   │  │ │
│                                    │  │ (Maturity Model)│  │ │
│                                    │  └─────────────────┘  │ │
│                                    │    Bedrock AgentCore   │ │
│                                    └───────────────────────┘ │
│                                                              │
│  Output: AgentApiUrl, KBBucket                               │
└──────────────────────────────────────────────────────────────┘
```

## Deployment

```bash
# 1. Set variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Package Lambda
aws cloudformation package \
  --template-file stack-5-agent.yaml \
  --s3-bucket "${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" \
  --output-template-file stack-5-agent-packaged.yaml \
  --region $REGION

# 3. Deploy
aws cloudformation deploy \
  --template-file stack-5-agent-packaged.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-agent" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# 4. Upload Maturity Model documents to KB bucket
KB_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-agent" \
  --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseBucketName'].OutputValue" \
  --output text --region $REGION)

# aws s3 cp maturity-model-docs/ "s3://${KB_BUCKET}/" --recursive

# 5. Get API URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-agent" \
  --query "Stacks[0].Outputs[?OutputKey=='AgentApiUrl'].OutputValue" \
  --output text --region $REGION
```
