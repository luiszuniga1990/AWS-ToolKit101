# Playbook: Deploy de Data Processing Pipeline

Guía paso a paso para desplegar el pipeline serverless de procesamiento de datos JSON en AWS.

## Arquitectura

```
S3 (raw JSON) → AWS Glue Job → Parquet → Athena → Amazon QuickSight (2 dashboards)
```

---

## Pre-requisitos

- [ ] AWS CLI instalado y configurado con credenciales válidas
- [ ] Permisos IAM para CloudFormation, S3, Glue, Athena y QuickSight
- [ ] Amazon QuickSight suscrito y configurado (ver `data-processing/quick-setup.md`)
- [ ] Obtener tu QuickSight User ARN:

```bash
aws quicksight list-users \
  --aws-account-id TU_ACCOUNT_ID \
  --namespace default \
  --region us-east-1
```

---

## Paso 1: Clonar el repositorio

```bash
git clone https://github.com/luiszuniga1990/AWS-ToolKit101.git
cd AWS-ToolKit101/Data/data-processing
```

## Paso 2: Desplegar el stack de CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name data-processing-stack \
  --template-body file://data-processing-template.yaml \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=data-processing \
    ParameterKey=QuickSightUserArn,ParameterValue=arn:aws:quicksight:us-east-1:TU_ACCOUNT_ID:user/default/TU_USUARIO \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

## Paso 3: Verificar que el stack se creó correctamente

```bash
aws cloudformation describe-stacks \
  --stack-name data-processing-stack \
  --query 'Stacks[0].StackStatus' \
  --region us-east-1
```

Esperar hasta que el estado sea `CREATE_COMPLETE`.

## Paso 4: Subir el script de Glue al bucket

```bash
aws s3 cp glue-job-script.py \
  s3://data-processing-glue-scripts-TU_ACCOUNT_ID/glue-job-script.py \
  --region us-east-1
```

## Paso 5: Subir los datos de ejemplo a S3

```bash
aws s3 cp sample-data/ \
  s3://data-processing-raw-data-TU_ACCOUNT_ID/ \
  --recursive --region us-east-1
```

## Paso 6: Ejecutar el Glue Job

```bash
aws glue start-job-run \
  --job-name data-processing-json-processor \
  --region us-east-1
```

## Paso 7: Verificar la ejecución del Job

```bash
aws glue get-job-run \
  --job-name data-processing-json-processor \
  --run-id TU_RUN_ID \
  --region us-east-1
```

Esperar hasta que el estado sea `SUCCEEDED`.

## Paso 8: Consultar datos en Athena

```sql
-- Ver registros procesados
SELECT * FROM data_processing_database.processed_data LIMIT 20;

-- Resumen por categoría
SELECT category, COUNT(*) as total, SUM(amount) as total_amount
FROM data_processing_database.processed_data
GROUP BY category;
```

## Paso 9: Verificar dashboards en QuickSight

1. Ir a la consola de Amazon QuickSight en `us-east-1`
2. Verificar que existan los 2 dashboards:
   - **General Summary** — Vista consolidada
   - **Detail & Trends** — Análisis detallado con tendencias

---

## Limpieza (cuando ya no se necesite)

```bash
# Vaciar buckets
aws s3 rm s3://data-processing-raw-data-TU_ACCOUNT_ID --recursive --region us-east-1
aws s3 rm s3://data-processing-glue-scripts-TU_ACCOUNT_ID --recursive --region us-east-1
aws s3 rm s3://data-processing-athena-results-TU_ACCOUNT_ID --recursive --region us-east-1

# Eliminar el stack
aws cloudformation delete-stack \
  --stack-name data-processing-stack \
  --region us-east-1
```

---

> 💡 **Nota:** Reemplaza `TU_ACCOUNT_ID` y `TU_USUARIO` con tus valores reales de AWS en todos los comandos.
