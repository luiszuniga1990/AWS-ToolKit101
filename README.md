# AWS ToolKit 101

## 1. Descripción del Repositorio

Repositorio de aprendizaje y recursos prácticos sobre servicios de AWS, organizado en tres pilares fundamentales: Data, Inteligencia Artificial y Seguridad. Cada módulo contiene guías, templates de infraestructura y playbooks paso a paso para implementaciones en la nube de AWS. Los deploys se realizan mediante templates YAML (CloudFormation) e incluyen playbooks step by step para tener una experiencia completa de deploy de principio a fin.

## 2. Público Objetivo

- Desarrolladores que inician su camino en AWS
- Ingenieros de datos, ML y seguridad que buscan referencias rápidas
- Equipos DevOps y arquitectos cloud que necesitan patrones base

## 3. Estructura del Repositorio

```
AWS-ToolKit101/
├── README.md
├── Data/
│   ├── README.md
│   └── data-processing/
│       ├── README.md
│       ├── PLAYBOOK.md                     ← Guía paso a paso de deploy
│       ├── quick-setup.md
│       ├── data-processing-template.yaml   ← CloudFormation template
│       ├── glue-job-script.py              ← Script ETL (PySpark)
│       ├── LICENSE
│       └── sample-data/
│           ├── sample-001.json
│           ├── sample-002.json
│           └── sample-003.json
├── IA/
│   └── README.md                           ← Próximamente
└── Secure/
    └── README.md                           ← Próximamente
```

---

> 🚧 **Módulos IA y Secure** están en proceso de desarrollo. Próximamente se subirá contenido con templates, playbooks y guías prácticas para cada uno.
