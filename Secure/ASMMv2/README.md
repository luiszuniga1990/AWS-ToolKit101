# ASMMv2 — AWS Security Maturity Model v2 Agent

## Business Case

Organizations operating on AWS face a growing challenge: continuously assessing and improving their security posture without relying on expensive external consultancies or manual audits that take weeks.

**ASMMv2** solves this by providing an automated, intelligent assessment based on the official [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/) framework, delivering in minutes what traditionally takes days:

| Problem | ASMMv2 Solution |
|---|---|
| Expensive manual audits ($5K–$50K) | Automated assessment for ~$7–32/month |
| Weeks waiting for results | Results in minutes |
| Generic recommendations | Account-specific recommendations prioritized by criticality |
| No maturity visibility | Clear classification by phase from the official AWS model |
| Requires security expertise | AI agent that explains in plain language with reference links |

**Target Audience**: DevOps teams, Cloud Engineers, CISOs, and startups that need immediate visibility into their AWS security posture without investing in enterprise tools.

**Differentiator**: 100% serverless, zero-trust (read-only), based on the official AWS framework, and with a conversational interface that guides the user step by step.

---

## Technical Overview

Serverless AI agent with an interactive web interface that analyzes the security posture of an AWS account and generates recommendations based on the [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/).

The user authenticates, submits read-only credentials, the system validates they have no write permissions, runs a security assessment, and presents results in an interactive chat indicating the maturity phase and critical recommendations with links to the official model.

## Components

| Component | AWS Service | Description |
|---|---|---|
| Authentication | Amazon Cognito | Web user login |
| Frontend | S3 + CloudFront | Interactive SPA with chat |
| Validation | Lambda + API Gateway | Verifies credentials and read-only permissions |
| Assessment | Lambda + API Gateway | IAM, Logging, Detection analysis |
| AI Agent | Bedrock + Lambda | Generates AI-powered recommendations |
| Knowledge Base | S3 | Security Maturity Model v2 documents |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASMMv2 - Architecture                              │
│                                                                             │
│  ┌──────────┐    ┌───────────┐    ┌────────────────────────────────────┐    │
│  │   User   │───▶│  Cognito  │───▶│         CloudFront + S3            │    │
│  └──────────┘    │  (Auth)   │    │         (Frontend SPA)             │    │
│                  └───────────┘    └──────────────┬─────────────────────┘    │
│                                                  │                          │
│                                    ┌─────────────┼─────────────┐            │
│                                    │             │             │            │
│                                    ▼             ▼             ▼            │
│                          ┌──────────────┐┌─────────────┐┌───────────┐      │
│                          │  Validation  ││  Assessment ││   Agent   │      │
│                          │  API Gateway ││ API Gateway ││API Gateway│      │
│                          └──────┬───────┘└──────┬──────┘└─────┬─────┘      │
│                                 │               │             │             │
│                          ┌──────┴───────┐┌──────┴──────┐┌─────┴─────┐      │
│                          │  3 Lambdas   ││  3 Lambdas  ││  Lambda   │      │
│                          │ •Credentials ││ •IAM        ││Orchestrator│     │
│                          │ •ReadOnly    ││ •Logging    │└─────┬─────┘      │
│                          │ •Connection  ││ •Detection  │      │            │
│                          └──────┬───────┘└──────┬──────┘      ▼            │
│                                 │               │      ┌─────────────┐     │
│                                 ▼               ▼      │   Bedrock   │     │
│                          ┌────────────────────────┐    │ (Nova Pro)  │     │
│                          │  Target AWS Account    │    └──────┬──────┘     │
│                          │  (Read-Only Access)    │           │            │
│                          └────────────────────────┘    ┌──────┴──────┐     │
│                                                        │  S3 KB Docs │     │
│                                                        │(Maturity M.)│     │
│                                                        └─────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure (CloudFormation Tree)

```
Secure/ASMMv2/
├── stack-1-auth/
│   ├── stack-1-auth.yaml          ← Cognito (User Pool, Client, Identity Pool)
│   └── README.md
├── stack-2-frontend/
│   ├── stack-2-frontend.yaml      ← S3 + CloudFront
│   └── README.md
├── stack-3-validation/
│   ├── stack-3-validation.yaml    ← 3 validation Lambdas + API Gateway
│   └── README.md
├── stack-4-assessment/
│   ├── stack-4-assessment.yaml    ← 3 assessment Lambdas + API Gateway
│   └── README.md
├── stack-5-agent/
│   ├── stack-5-agent.yaml         ← Bedrock AgentCore + KB + API Gateway
│   └── README.md
├── frontend/
│   └── index.html                 ← SPA (web interface)
├── lambdas/
│   ├── validation/
│   │   ├── validate_credentials.py
│   │   ├── validate_readonly.py
│   │   └── validate_connection.py
│   ├── assessment/
│   │   ├── assess_iam.py
│   │   ├── assess_logging.py
│   │   └── assess_detection.py
│   └── agent/
│       └── agent_orchestrator.py
├── deploy.sh                      ← Full deployment script
└── README.md                      ← This file
```

## Deployment Order

```
Stack 1 (Auth) → Stack 2 (Frontend) → Stack 3 (Validation) → Stack 4 (Assessment) → Stack 5 (Agent)
```

Stacks export outputs that subsequent stacks consume via `Fn::ImportValue`.

## Full Deployment

```bash
# Prerequisites
# - AWS CLI configured
# - Permissions to create: Cognito, S3, CloudFront, Lambda, API Gateway, IAM, Bedrock

# 1. Set variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export AWS_REGION=us-east-1

# 2. Create artifacts bucket
aws s3 mb "s3://${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" --region $AWS_REGION

# 3. Run full deployment
cd Secure/ASMMv2
./deploy.sh

# Or deploy stack by stack (see each stack's README)
```

## Estimated Monthly Cost (USD)

| Service | Resource | Estimated Cost | Notes |
|---|---|---|---|
| Cognito | User Pool | ~$0.00 | Free up to 50,000 MAU |
| S3 | Frontend Bucket | ~$0.50 | Static hosting < 1GB |
| CloudFront | Distribution | ~$1.00 | 1M requests/month free tier |
| API Gateway | 3 HTTP APIs | ~$1.00 | $1/million requests |
| Lambda | 7 functions | ~$0.00 | 1M requests free/month |
| Bedrock | Nova Pro invocations | ~$3.00 - $20.00 | Depends on usage (~1000 assessments) |
| S3 | KB Bucket | ~$0.02 | Model documents < 100MB |
| **TOTAL** | | **~$7.52 - $32.52** | **Moderate usage** |

> **Note**: Bedrock costs vary by model and volume. Nova Pro: ~$0.80/1M input tokens, ~$3.20/1M output tokens. For low usage (< 100 assessments/month) the Bedrock cost will be ~$3. The AWS free tier covers most other services during the first 12 months.

## References

- [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon Cognito](https://aws.amazon.com/cognito/)
- [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
