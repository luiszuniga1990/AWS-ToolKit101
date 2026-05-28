# Secure

Security module of the AWS-ToolKit101 repository. Contains tools, templates, and agents to assess and improve the security posture of AWS accounts.

## Projects

| Project | Description | Status |
|---|---|---|
| [ASMMv2](./ASMMv2/) | AI agent that assesses AWS security against the Security Maturity Model v2 | ✅ Active |

## ASMMv2 — AWS Security Maturity Model v2 Agent

Serverless agent with an interactive web interface that analyzes the security posture of an AWS account and generates recommendations based on the [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/).

**Tech Stack**: Cognito · Lambda · API Gateway · Bedrock AgentCore · S3 · CloudFront

**Features**:
- Cognito authentication
- Read-only credential validation (blocks write access)
- Automated assessment: IAM, Logging, Detection
- Interactive chat with recommendations by maturity phase
- 5 CloudFormation stacks, 100% serverless

→ [View full documentation](./ASMMv2/README.md)
