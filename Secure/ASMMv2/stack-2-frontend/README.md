# Stack 2: Frontend (S3 + CloudFront)

## Resumen
Stack de hosting serverless para la SPA (Single Page Application). Usa S3 como origen y CloudFront como CDN con HTTPS.

## Componentes

| Recurso | Tipo | Descripción |
|---|---|---|
| FrontendBucket | S3 Bucket | Almacena archivos estáticos (HTML/CSS/JS) |
| FrontendBucketPolicy | S3 Bucket Policy | Permite acceso solo desde CloudFront |
| OriginAccessControl | CloudFront OAC | Control de acceso al origen S3 |
| CloudFrontDistribution | CloudFront | CDN con HTTPS y SPA routing |

## Diagrama

```
┌──────────────────────────────────────────────────┐
│              Stack 2: Frontend                    │
│                                                  │
│  ┌────────────┐       ┌───────────────────────┐  │
│  │  Usuario   │──────▶│  CloudFront (HTTPS)   │  │
│  └────────────┘       └───────────┬───────────┘  │
│                                   │ OAC          │
│                                   ▼              │
│                       ┌───────────────────────┐  │
│                       │   S3 Bucket (privado) │  │
│                       │   index.html, assets  │  │
│                       └───────────────────────┘  │
│                                                  │
│  Outputs: BucketName, CloudFrontDomain, DistId   │
└──────────────────────────────────────────────────┘
```

## Deploy Step by Step

```bash
# 1. Configurar variables
export PROJECT_NAME=asmmv2
export ENVIRONMENT=dev
export REGION=us-east-1

# 2. Desplegar stack
aws cloudformation deploy \
  --template-file stack-2-frontend.yaml \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-frontend" \
  --parameter-overrides ProjectName=$PROJECT_NAME Environment=$ENVIRONMENT \
  --region $REGION

# 3. Subir frontend al bucket
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-frontend" \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
  --output text --region $REGION)

aws s3 sync frontend/ "s3://${BUCKET}/" --delete --region $REGION

# 4. Obtener URL
aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-frontend" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" \
  --output text --region $REGION
```
