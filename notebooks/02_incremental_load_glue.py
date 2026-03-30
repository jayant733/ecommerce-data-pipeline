import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max

BUCKET_NAME = "ecommerce-data-pipeline-jayant"
STAGING_PATH = f"s3://{BUCKET_NAME}/staging/sales/"
CURATED_PREFIX = "curated/sales/"
CURATED_PATH = f"s3://{BUCKET_NAME}/{CURATED_PREFIX}"


def curated_has_data(bucket, prefix):
    s3_client = boto3.client("s3")
    resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=5)
    contents = resp.get("Contents", [])
    return any(obj["Key"].endswith(".parquet") for obj in contents)


spark = SparkSession.builder.appName("IncrementalLoad").getOrCreate()
df_staging = spark.read.parquet(STAGING_PATH)

if curated_has_data(BUCKET_NAME, CURATED_PREFIX):
    existing_df = spark.read.parquet(CURATED_PATH)
    max_date = existing_df.select(spark_max("Order_Date")).collect()[0][0]

    if max_date is None:
        df_incremental = df_staging
    else:
        print(f"Last processed Order_Date: {max_date}")
        df_incremental = df_staging.filter(col("Order_Date") > max_date)

    new_count = df_incremental.count()
    if new_count > 0:
        df_incremental.write.mode("append").parquet(CURATED_PATH)
        print(f"Appended {new_count} new records to curated zone.")
    else:
        print("No new records to load.")
else:
    print("No curated parquet files found; running initial full load.")
    df_staging.write.mode("overwrite").parquet(CURATED_PATH)
    print("Full load completed.")
