# Stack 4: Assessment Lambdas

## Resumen
Stack serverless con 3 funciones Lambda que ejecutan el análisis de seguridad de la cuenta AWS. Cada Lambda cubre un sector del AWS Security Maturity Model v2: Identity, Logging y Detection.

## Componentes

| Recurso | Tipo | Descripción |
|---|---|---|
| AssessmentApi | API Gateway HTTP | Endpoint para análisis |
| AssessIamFunction | Lambda | Analiza IAM: MFA, access keys, root, password policy |
| AssessLoggingFunction | Lambda | Analiza CloudTrail, Config, CloudWatch |
| AssessDetectionFunction | Lambda | Analiza GuardDuty, Security Hub |

## Diagrama

```
┌────────────────────────────────────────────────────────────────┐
│                  Stack 4: Assessment                           │
│                                                                │
│  ┌──────────┐     ┌────────────────────────────────────────┐   │
│  │ Frontend │────▶│          API Gateway HTTP              │   │
│  └──────────┘     └──────┬───────────┬───────────┬─────────┘   │
│                          │           │           │             │
│               POST /assess-iam  /assess-logging  /assess-detection
│                          │           │           │             │
│                          ▼           ▼           ▼             │
│                   ┌──────────┐┌──────────┐┌──────────────┐     │
│                   │ Lambda 1 ││ Lambda 2 ││   Lambda 3   │     │
│                   │   IAM    ││ Logging  ││  Detection   │     │
│                   └────┬─────┘└────┬─────┘└──────┬───────┘     │
│                        │           │             │              │
│                        ▼           ▼             ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Cuenta AWS del usuario (read-only)           │   │
│  │  IAM │ CloudTrail │ Config │ CloudWatch │ GuardDuty │ SH│   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  Output: AssessmentApiUrl                                      │
└────────────────────────────────────────────────────────────────┘
```

## Deploy Step by Step

```bash
# 1. Configurar variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Empaquetar Lambdas
aws cloudformation package \
  --template-file stack-4-assessment.yaml \
  --s3-bucket "${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" \
  --output-template-file stack-4-assessment-packaged.yaml \
  --region $REGION

# 3. Desplegar
aws cloudformation deploy \
  --template-file stack-4-assessment-packaged.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-assessment" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# 4. Obtener API URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-assessment" \
  --query "Stacks[0].Outputs[?OutputKey=='AssessmentApiUrl'].OutputValue" \
  --output text --region $REGION
```
