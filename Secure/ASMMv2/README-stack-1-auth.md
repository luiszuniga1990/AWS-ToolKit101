# Stack 1: Auth (Cognito)

## Resumen
Stack de autenticación que provisiona Amazon Cognito para gestionar el login de usuarios en la interfaz web de ASMMv2.

## Componentes

| Recurso | Tipo | Descripción |
|---|---|---|
| UserPool | Cognito User Pool | Pool de usuarios con verificación por email |
| UserPoolClient | Cognito App Client | Cliente web (SRP auth, sin secret) |
| IdentityPool | Cognito Identity Pool | Federación de identidades |

## Diagrama

```
┌─────────────────────────────────────────────┐
│              Stack 1: Auth                   │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │         Cognito User Pool             │  │
│  │  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │  App Client │  │ Password Policy│  │  │
│  │  └─────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────┘  │
│                    │                         │
│                    ▼                         │
│  ┌───────────────────────────────────────┐  │
│  │       Cognito Identity Pool           │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Outputs: UserPoolId, ClientId, IdentityId  │
└─────────────────────────────────────────────┘
```

## Deploy Step by Step

```bash
# 1. Configurar variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Desplegar stack
aws cloudformation deploy \
  --template-file stack-1-auth.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-auth" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# 3. Obtener outputs
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-auth" \
  --query "Stacks[0].Outputs" --output table --region $REGION
```
