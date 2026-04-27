# Data

Módulo dedicado a samples y recursos prácticos sobre servicios de datos en AWS. Contiene templates de infraestructura, scripts ETL y guías de deploy para pipelines de procesamiento de datos en la nube.

## Contenido

```
Data/
├── README.md
└── data-processing/
    ├── README.md
    ├── PLAYBOOK.md                     ← Guía paso a paso de deploy
    ├── quick-setup.md                  ← Setup de Amazon QuickSight
    ├── data-processing-template.yaml   ← CloudFormation template
    ├── glue-job-script.py              ← Script ETL (PySpark)
    ├── LICENSE
    └── sample-data/
        ├── sample-001.json
        ├── sample-002.json
        └── sample-003.json
```

## Público Objetivo

- Ingenieros de datos que buscan patrones de pipelines serverless en AWS
- Desarrolladores que quieren aprender sobre S3, Glue, Athena y QuickSight
- Equipos que necesitan templates listos para procesamiento de datos JSON a Parquet
