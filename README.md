# AWS ToolKit 101

## 1. Repository Description

A hands-on learning repository covering core AWS services, organized around three fundamental pillars: Data, Artificial Intelligence, and Security. Each module provides guides, infrastructure templates, and step-by-step playbooks for cloud deployments on AWS. All deployments are driven by YAML templates (CloudFormation) and include detailed playbooks to deliver a complete end-to-end deployment experience.

## 2. Target Audience

- Developers beginning their journey with AWS
- Data, ML, and security engineers looking for quick-reference patterns
- DevOps teams and cloud architects seeking reusable baseline templates

## 3. Repository Structure

```
AWS-ToolKit101/
├── README.md
├── Data/
│   ├── README.md
│   └── data-processing/
│       ├── README.md
│       ├── PLAYBOOK.md                     ← Step-by-step deployment guide
│       ├── quick-setup.md
│       ├── data-processing-template.yaml   ← CloudFormation template
│       ├── glue-job-script.py              ← ETL script (PySpark)
│       ├── LICENSE
│       └── sample-data/
│           ├── sample-001.json
│           ├── sample-002.json
│           └── sample-003.json
├── IA/
│   └── README.md                           ← Coming soon
└── Secure/
    └── ASMMv2/                             ← AWS Security Maturity Model v2 Agent
        ├── README.md
        ├── deploy.sh
        ├── frontend/
        │   └── index.html
        ├── lambdas/
        │   ├── validation/
        │   ├── assessment/
        │   └── agent/
        ├── stack-1-auth/
        ├── stack-2-frontend/
        ├── stack-3-validation/
        ├── stack-4-assessment/
        └── stack-5-agent/
```

---

## 4. Modules

### Data — Data Processing
ETL pipeline using AWS Glue, S3, and CloudFormation. Processes JSON data with PySpark.

### Secure — ASMMv2 (AWS Security Maturity Model v2 Agent)
Serverless AI agent with interactive web UI that assesses AWS account security posture against the [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/). Features:
- Cognito authentication
- Read-only credential validation (blocks write access)
- Automated security assessment (IAM, Logging, Detection)
- AI-powered recommendations via Bedrock AgentCore
- Interactive chat showing maturity phase + critical recommendations with links to the official model
- 5 CloudFormation stacks, 100% serverless

---

> 🚧 **IA module** is currently under development. Templates, playbooks, and practical guides will be released soon.
