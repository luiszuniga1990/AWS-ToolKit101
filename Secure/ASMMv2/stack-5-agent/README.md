# Stack 5: Agent (Bedrock AgentCore)

## Resumen
Stack del agente de IA que recibe los resultados del assessment, los evalúa contra el AWS Security Maturity Model v2, y genera recomendaciones en formato chat interactivo con links al modelo oficial.

## Componentes

| Recurso | Tipo | Descripción |
|---|---|---|
| KnowledgeBaseBucket | S3 Bucket | Documentos del Security Maturity Model v2 |
| AgentRole | IAM Role | Rol del agente con permisos a Bedrock y S3 |
| AgentOrchestratorFunction | Lambda | Orquesta el agente, invoca Bedrock |
| AgentApi | API Gateway HTTP | Endpoint /chat para el frontend |

## Diagrama

```
┌──────────────────────────────────────────────────────────────┐
│                   Stack 5: Agent                             │
│                                                              │
│  ┌──────────┐     ┌──────────────────┐     ┌─────────────┐  │
│  │ Frontend │────▶│ API Gateway HTTP │────▶│   Lambda    │  │
│  └──────────┘     └──────────────────┘     │Orchestrator │  │
│                          POST /chat         └──────┬──────┘  │
│                                                    │         │
│                                    ┌───────────────┼───────┐ │
│                                    │               ▼       │ │
│                                    │  ┌─────────────────┐  │ │
│                                    │  │ Bedrock Model   │  │ │
│                                    │  │ (Nova Pro)      │  │ │
│                                    │  └─────────────────┘  │ │
│                                    │               │       │ │
│                                    │               ▼       │ │
│                                    │  ┌─────────────────┐  │ │
│                                    │  │  S3 KB Bucket   │  │ │
│                                    │  │ (Maturity Model)│  │ │
│                                    │  └─────────────────┘  │ │
│                                    │    Bedrock AgentCore   │ │
│                                    └───────────────────────┘ │
│                                                              │
│  Output: AgentApiUrl, KBBucket                               │
└──────────────────────────────────────────────────────────────┘
```

## Deploy Step by Step

```bash
# 1. Configurar variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Empaquetar Lambda
aws cloudformation package \
  --template-file stack-5-agent.yaml \
  --s3-bucket "${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" \
  --output-template-file stack-5-agent-packaged.yaml \
  --region $REGION

# 3. Desplegar
aws cloudformation deploy \
  --template-file stack-5-agent-packaged.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-agent" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# 4. Subir documentos del Maturity Model al KB bucket
KB_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-agent" \
  --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseBucketName'].OutputValue" \
  --output text --region $REGION)

# aws s3 cp maturity-model-docs/ "s3://${KB_BUCKET}/" --recursive

# 5. Obtener API URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-agent" \
  --query "Stacks[0].Outputs[?OutputKey=='AgentApiUrl'].OutputValue" \
  --output text --region $REGION
```
