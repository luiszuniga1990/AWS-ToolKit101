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
    └── README.md                           ← Coming soon
```

---

> 🚧 **IA and Secure modules** are currently under development. Templates, playbooks, and practical guides for each module will be released soon.
