#!/bin/bash
set -e

PROJECT_NAME="${PROJECT_NAME:-asmmv2}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_PREFIX="${PROJECT_NAME}-${ENVIRONMENT}"

echo "========================================="
echo " ASMMv2 - Deploy"
echo " Project: ${PROJECT_NAME}"
echo " Environment: ${ENVIRONMENT}"
echo " Region: ${REGION}"
echo "========================================="

# Stack 1: Auth
echo ""
echo ">>> Deploying Stack 1: Auth (Cognito)..."
aws cloudformation deploy \
  --template-file stack-1-auth.yaml \
  --stack-name "${STACK_PREFIX}-auth" \
  --parameter-overrides ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT} \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ${REGION}

# Stack 2: Frontend
echo ""
echo ">>> Deploying Stack 2: Frontend (S3 + CloudFront)..."
aws cloudformation deploy \
  --template-file stack-2-frontend.yaml \
  --stack-name "${STACK_PREFIX}-frontend" \
  --parameter-overrides ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT} \
  --region ${REGION}

# Stack 3: Validation
echo ""
echo ">>> Deploying Stack 3: Validation Lambdas..."
aws cloudformation package \
  --template-file stack-3-validation.yaml \
  --s3-bucket "${STACK_PREFIX}-deploy-artifacts" \
  --output-template-file stack-3-validation-packaged.yaml \
  --region ${REGION}

aws cloudformation deploy \
  --template-file stack-3-validation-packaged.yaml \
  --stack-name "${STACK_PREFIX}-validation" \
  --parameter-overrides ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT} \
  --capabilities CAPABILITY_IAM \
  --region ${REGION}

# Stack 4: Assessment
echo ""
echo ">>> Deploying Stack 4: Assessment Lambdas..."
aws cloudformation package \
  --template-file stack-4-assessment.yaml \
  --s3-bucket "${STACK_PREFIX}-deploy-artifacts" \
  --output-template-file stack-4-assessment-packaged.yaml \
  --region ${REGION}

aws cloudformation deploy \
  --template-file stack-4-assessment-packaged.yaml \
  --stack-name "${STACK_PREFIX}-assessment" \
  --parameter-overrides ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT} \
  --capabilities CAPABILITY_IAM \
  --region ${REGION}

# Stack 5: Agent
echo ""
echo ">>> Deploying Stack 5: Agent (Bedrock)..."
aws cloudformation package \
  --template-file stack-5-agent.yaml \
  --s3-bucket "${STACK_PREFIX}-deploy-artifacts" \
  --output-template-file stack-5-agent-packaged.yaml \
  --region ${REGION}

aws cloudformation deploy \
  --template-file stack-5-agent-packaged.yaml \
  --stack-name "${STACK_PREFIX}-agent" \
  --parameter-overrides ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT} \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ${REGION}

# Upload frontend
echo ""
echo ">>> Uploading frontend..."
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_PREFIX}-frontend" \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
  --output text --region ${REGION})

aws s3 sync frontend/ "s3://${BUCKET}/" --delete --region ${REGION}

echo ""
echo "========================================="
echo " ✅ Deploy completo!"
echo ""
echo " Outputs:"
aws cloudformation describe-stacks --stack-name "${STACK_PREFIX}-frontend" \
  --query "Stacks[0].Outputs" --output table --region ${REGION}
echo "========================================="
