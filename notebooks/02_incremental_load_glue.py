from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max

BUCKET_NAME = "ecommerce-data-pipeline-jayant"
STAGING_PATH = f"s3://{BUCKET_NAME}/staging/sales/"
CURATED_PATH = f"s3://{BUCKET_NAME}/curated/sales/"

spark = SparkSession.builder.appName("IncrementalLoad").getOrCreate()

df_staging = spark.read.parquet(STAGING_PATH)

try:
    existing_df = spark.read.parquet(CURATED_PATH)
    max_date = existing_df.select(spark_max("Order_Date")).collect()[0][0]
    print(f"Last processed Order_Date: {max_date}")

    df_incremental = df_staging.filter(col("Order_Date") > max_date)
    new_count = df_incremental.count()

    if new_count > 0:
        df_incremental.write.mode("append").parquet(CURATED_PATH)
        print(f"Appended {new_count} new records to curated zone.")
    else:
        print("No new records to load.")
except Exception:
    print("Curated zone empty; running initial full load.")
    df_staging.write.mode("overwrite").parquet(CURATED_PATH)
    print("Full load completed.")
