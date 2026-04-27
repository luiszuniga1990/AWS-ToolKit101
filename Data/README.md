# Data

Module dedicated to samples and hands-on resources for AWS data services. It includes infrastructure templates, ETL scripts, and deployment guides for serverless data processing pipelines in the cloud.

## Contents

```
Data/
├── README.md
└── data-processing/
    ├── README.md
    ├── PLAYBOOK.md                     ← Step-by-step deployment guide
    ├── quick-setup.md                  ← Amazon QuickSight setup
    ├── data-processing-template.yaml   ← CloudFormation template
    ├── glue-job-script.py              ← ETL script (PySpark)
    ├── LICENSE
    └── sample-data/
        ├── sample-001.json
        ├── sample-002.json
        └── sample-003.json
```

## Target Audience

- Data engineers looking for serverless pipeline patterns on AWS
- Developers who want to learn about S3, Glue, Athena, and QuickSight
- Teams that need ready-to-use templates for JSON-to-Parquet data processing
