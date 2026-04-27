import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, to_timestamp, when, lit

# Obtener argumentos del Job
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'SOURCE_BUCKET', 'DATABASE_NAME'])

# Inicializar contextos
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

source_bucket = args['SOURCE_BUCKET']
database_name = args['DATABASE_NAME']

# ============================================
# PASO 1: Leer archivos JSON raw desde S3
# ============================================
source_path = f"s3://{source_bucket}/"

datasource = glueContext.create_dynamic_frame.from_options(
    format_options={"multiline": False},
    connection_type="s3",
    format="json",
    connection_options={
        "paths": [source_path],
        "recurse": True
    },
    transformation_ctx="datasource"
)

print(f"Registros leidos: {datasource.count()}")

# Convertir a DataFrame para transformaciones
df = datasource.toDF()

if df.count() == 0:
    print("No se encontraron registros. Finalizando job.")
    job.commit()
    sys.exit(0)

# ============================================
# PASO 2: Transformaciones y limpieza
# ============================================

# Castear tipos de datos
df_transformed = df \
    .withColumn("timestamp", to_timestamp(col("timestamp"))) \
    .withColumn("amount", col("amount").cast("double")) \
    .withColumn("category", when(col("category").isNull(), lit("sin_categoria")).otherwise(col("category"))) \
    .withColumn("status", when(col("status").isNull(), lit("unknown")).otherwise(col("status")))

# Eliminar duplicados por id
df_clean = df_transformed.dropDuplicates(["id"])

print(f"Registros despues de limpieza: {df_clean.count()}")
print("Schema:")
df_clean.printSchema()

# ============================================
# PASO 3: Escribir datos en formato Parquet
# ============================================
output_path = f"s3://{source_bucket}/processed/"

df_clean.write \
    .mode("overwrite") \
    .partitionBy("category") \
    .parquet(output_path)

print(f"Datos escritos en: {output_path}")

# ============================================
# PASO 4: Crear/actualizar tabla en Glue Catalog
# ============================================
df_clean.createOrReplaceTempView("processed_view")

spark.sql(f"DROP TABLE IF EXISTS {database_name}.processed_data")

spark.sql(f"""
    CREATE TABLE {database_name}.processed_data
    USING parquet
    PARTITIONED BY (category)
    LOCATION '{output_path}'
    AS SELECT id, data, timestamp, amount, region, status, category
    FROM processed_view
""")

# Reparar particiones para que Athena las detecte
spark.sql(f"MSCK REPAIR TABLE {database_name}.processed_data")

print(f"Tabla {database_name}.processed_data creada/actualizada exitosamente")

job.commit()
print("Job completado exitosamente")
