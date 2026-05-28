# Stack 2: Frontend (S3 + CloudFront)

## Overview
Serverless hosting stack for the SPA (Single Page Application). Uses S3 as origin and CloudFront as CDN with HTTPS.

## Components

| Resource | Type | Description |
|---|---|---|
| FrontendBucket | S3 Bucket | Stores static files (HTML/CSS/JS) |
| FrontendBucketPolicy | S3 Bucket Policy | Allows access only from CloudFront |
| OriginAccessControl | CloudFront OAC | Origin access control for S3 |
| CloudFrontDistribution | CloudFront | CDN with HTTPS and SPA routing |

## Diagram

```
┌──────────────────────────────────────────────────┐
│              Stack 2: Frontend                    │
│                                                  │
│  ┌────────────┐       ┌───────────────────────┐  │
│  │    User    │──────▶│  CloudFront (HTTPS)   │  │
│  └────────────┘       └───────────┬───────────┘  │
│                                   │ OAC          │
│                                   ▼              │
│                       ┌───────────────────────┐  │
│                       │   S3 Bucket (private)  │  │
│                       │   index.html, assets  │  │
│                       └───────────────────────┘  │
│                                                  │
│  Outputs: BucketName, CloudFrontDomain, DistId   │
└──────────────────────────────────────────────────┘
```

## Deployment

```bash
# 1. Set variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Deploy stack
aws cloudformation deploy \
  --template-file stack-2-frontend.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-frontend" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --region $REGION

# 3. Upload frontend to bucket
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-frontend" \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
  --output text --region $REGION)

aws s3 sync frontend/ "s3://${BUCKET}/" --delete --region $REGION

# 4. Get URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-frontend" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" \
  --output text --region $REGION
```
