import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_date

BUCKET_NAME = "ecommerce-data-pipeline-jayant"
RAW_PATH = f"s3://{BUCKET_NAME}/raw/sales_data.csv"
STAGING_PATH = f"s3://{BUCKET_NAME}/staging/sales/"

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

df_raw = spark.read.option("header", "true").csv(RAW_PATH)

df_clean = (
    df_raw
    .withColumn("Order_Date", to_date(col("Order Date"), "MM/dd/yyyy"))
    .withColumn("Ship_Date", to_date(col("Ship Date"), "MM/dd/yyyy"))
    .withColumn("Sales", col("Sales").cast("double"))
    .withColumn("Profit", col("Profit").cast("double"))
    .dropna(subset=["Order ID", "Sales", "Profit"])
)

df_clean.write.mode("overwrite").parquet(STAGING_PATH)
job.commit()
