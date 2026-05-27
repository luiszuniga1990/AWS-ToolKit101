# ASMMv2 — AWS Security Maturity Model v2 Agent

## Business Case

Las organizaciones que operan en AWS enfrentan un desafío creciente: evaluar y mejorar su postura de seguridad de forma continua sin depender de consultorías externas costosas ni auditorías manuales que consumen semanas.

**ASMMv2** resuelve esto proporcionando un assessment automatizado e inteligente basado en el framework oficial [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/), entregando en minutos lo que tradicionalmente toma días:

| Problema | Solución ASMMv2 |
|---|---|
| Auditorías manuales costosas ($5K-$50K) | Assessment automatizado por ~$7-32/mes |
| Semanas de espera por resultados | Resultados en minutos |
| Recomendaciones genéricas | Recomendaciones específicas a tu cuenta, priorizadas por criticidad |
| Sin visibilidad de madurez | Clasificación clara por fase del modelo oficial AWS |
| Requiere expertise en seguridad | Agente IA que explica en lenguaje claro con links de referencia |

**Público objetivo**: Equipos de DevOps, Cloud Engineers, CISOs y startups que necesitan visibilidad inmediata de su postura de seguridad AWS sin inversión en herramientas enterprise.

**Diferenciador**: 100% serverless, zero-trust (solo lectura), basado en el framework oficial de AWS, y con interfaz conversacional que guía al usuario paso a paso.

---

## Resumen Técnico

Agente de IA serverless con interfaz web interactiva que analiza la postura de seguridad de una cuenta AWS y genera recomendaciones basadas en el [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/).

El usuario se autentica, sube credenciales de solo lectura, el sistema valida que no tengan permisos de escritura, ejecuta un assessment de seguridad, y presenta resultados en un chat interactivo indicando la fase de madurez y recomendaciones críticas con links al modelo oficial.

## Componentes

| Componente | Servicio AWS | Descripción |
|---|---|---|
| Autenticación | Amazon Cognito | Login de usuarios web |
| Frontend | S3 + CloudFront | SPA interactiva con chat |
| Validación | Lambda + API Gateway | Verifica credenciales y permisos read-only |
| Assessment | Lambda + API Gateway | Análisis de IAM, Logging, Detection |
| Agente IA | Bedrock + Lambda | Genera recomendaciones con IA |
| Knowledge Base | S3 | Documentos del Security Maturity Model v2 |

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASMMv2 - Arquitectura                             │
│                                                                             │
│  ┌──────────┐    ┌───────────┐    ┌────────────────────────────────────┐    │
│  │ Usuario  │───▶│  Cognito  │───▶│         CloudFront + S3            │    │
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
│                          ┌────────────────────────┐    │  (Claude)   │     │
│                          │  Cuenta AWS Target     │    └──────┬──────┘     │
│                          │  (Read-Only Access)    │           │            │
│                          └────────────────────────┘    ┌──────┴──────┐     │
│                                                        │  S3 KB Docs │     │
│                                                        │(Maturity M.)│     │
│                                                        └─────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Estructura del Proyecto (Árbol CloudFormation)

```
Secure/ASMMv2/
├── stack-1-auth.yaml              ← Cognito (User Pool, Client, Identity Pool)
├── README-stack-1-auth.md
├── stack-2-frontend.yaml          ← S3 + CloudFront
├── README-stack-2-frontend.md
├── stack-3-validation.yaml        ← 3 Lambdas validación + API Gateway
├── README-stack-3-validation.md
├── stack-4-assessment.yaml        ← 3 Lambdas assessment + API Gateway
├── README-stack-4-assessment.md
├── stack-5-agent.yaml             ← Bedrock AgentCore + KB + API Gateway
├── README-stack-5-agent.md
├── deploy.sh                      ← Script de despliegue completo
├── frontend/
│   └── index.html                 ← SPA (interfaz web)
└── lambdas/
    ├── validation/
    │   ├── validate_credentials.py
    │   ├── validate_readonly.py
    │   └── validate_connection.py
    ├── assessment/
    │   ├── assess_iam.py
    │   ├── assess_logging.py
    │   └── assess_detection.py
    └── agent/
        └── agent_orchestrator.py
```

## Orden de Despliegue

```
Stack 1 (Auth) → Stack 2 (Frontend) → Stack 3 (Validation) → Stack 4 (Assessment) → Stack 5 (Agent)
```

Los stacks exportan outputs que los siguientes pueden consumir via `Fn::ImportValue`.

## Deploy Step by Step (Completo)

```bash
# Prerrequisitos
# - AWS CLI configurado
# - Permisos para crear: Cognito, S3, CloudFront, Lambda, API Gateway, IAM, Bedrock

# 1. Configurar variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export AWS_REGION=us-east-1

# 2. Crear bucket de artifacts
aws s3 mb "s3://${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" --region $AWS_REGION

# 3. Ejecutar deploy completo
cd Secure/ASMMv2
./deploy.sh

# O desplegar stack por stack (ver README de cada stack)
```

## Tabla de Costos Promedio (Mensual - USD)

| Servicio | Recurso | Costo Estimado | Notas |
|---|---|---|---|
| Cognito | User Pool | ~$0.00 | Gratis hasta 50,000 MAU |
| S3 | Frontend Bucket | ~$0.50 | Hosting estático < 1GB |
| CloudFront | Distribución | ~$1.00 | 1M requests/mes tier gratuito |
| API Gateway | 3 APIs HTTP | ~$1.00 | $1/millón de requests |
| Lambda | 7 funciones | ~$0.00 | 1M requests gratis/mes |
| Bedrock | Claude invocaciones | ~$5.00 - $30.00 | Depende del uso (~1000 assessments) |
| S3 | KB Bucket | ~$0.02 | Documentos del modelo < 100MB |
| **TOTAL** | | **~$7.52 - $32.52** | **Uso moderado** |

> **Nota**: Los costos de Bedrock varían según el modelo y volumen. Claude Sonnet: ~$3/1M input tokens, ~$15/1M output tokens. Para uso bajo (< 100 assessments/mes) el costo de Bedrock será ~$5. El free tier de AWS cubre la mayoría de los otros servicios durante los primeros 12 meses.

## Referencias

- [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon Cognito](https://aws.amazon.com/cognito/)
- [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
