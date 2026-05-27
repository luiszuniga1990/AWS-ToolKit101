# Stack 3: Validation Lambdas

## Resumen
Stack serverless con 3 funciones Lambda que validan las credenciales AWS del usuario: verifican conexión, confirman que solo tienen permisos de lectura, y bloquean si detectan permisos de escritura.

## Componentes

| Recurso | Tipo | Descripción |
|---|---|---|
| ValidationApi | API Gateway HTTP | Endpoint para validaciones |
| ValidateCredentialsFunction | Lambda | Valida credenciales via STS GetCallerIdentity |
| ValidateReadOnlyFunction | Lambda | Verifica que solo tiene políticas ReadOnly |
| ValidateConnectionFunction | Lambda | Orquesta validación completa |

## Diagrama

```
┌────────────────────────────────────────────────────────────┐
│                 Stack 3: Validation                         │
│                                                            │
│  ┌──────────┐     ┌──────────────────────────────────────┐ │
│  │ Frontend │────▶│        API Gateway HTTP              │ │
│  └──────────┘     └──────┬──────────┬──────────┬─────────┘ │
│                          │          │          │           │
│              POST /validate-credentials       │           │
│                          │    POST /validate-readonly     │
│                          │          │    POST /validate   │
│                          ▼          ▼          ▼           │
│                   ┌──────────┐┌──────────┐┌──────────┐    │
│                   │ Lambda 1 ││ Lambda 2 ││ Lambda 3 │    │
│                   │Credentials││ ReadOnly ││Connection│    │
│                   └─────┬────┘└─────┬────┘└─────┬────┘    │
│                         │           │           │          │
│                         ▼           ▼           ▼          │
│                   ┌─────────────────────────────────┐      │
│                   │  AWS STS / IAM (cuenta target)  │      │
│                   └─────────────────────────────────┘      │
│                                                            │
│  Output: ValidationApiUrl                                  │
└────────────────────────────────────────────────────────────┘
```

## Deploy Step by Step

```bash
# 1. Configurar variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Crear bucket de artifacts (si no existe)
aws s3 mb "s3://${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" --region $REGION

# 3. Empaquetar Lambdas
aws cloudformation package \
  --template-file stack-3-validation.yaml \
  --s3-bucket "${PROJECT_NAME}-${ENVIRONMENT}-deploy-artifacts" \
  --output-template-file stack-3-validation-packaged.yaml \
  --region $REGION

# 4. Desplegar
aws cloudformation deploy \
  --template-file stack-3-validation-packaged.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-validation" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# 5. Obtener API URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-validation" \
  --query "Stacks[0].Outputs[?OutputKey=='ValidationApiUrl'].OutputValue" \
  --output text --region $REGION
```
