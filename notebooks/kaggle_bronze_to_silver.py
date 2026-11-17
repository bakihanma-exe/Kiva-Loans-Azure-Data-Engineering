# Databricks notebook source
# Kiva Bronze -> Silver Delta. Curated typing is applied to loan-level fields.
dbutils.widgets.text("bronze_root", "abfss://<container>@<storage-account>.dfs.core.windows.net/kiva/bronze")
dbutils.widgets.text("silver_root", "abfss://<container>@<storage-account>.dfs.core.windows.net/kiva/silver")
bronze_root = dbutils.widgets.get("bronze_root").rstrip("/")
silver_root = dbutils.widgets.get("silver_root").rstrip("/")
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType, IntegerType, LongType

def write_delta(df, name):
    path = f"{silver_root}/{name}"
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)
    print(f"Silver written: {name}; rows={df.count()}")

loans = spark.read.format("delta").load(f"{bronze_root}/kiva_loans")
loans_silver = (loans
    .withColumn("id", F.col("id").cast(LongType()))
    .withColumn("funded_amount", F.col("funded_amount").cast(DecimalType(18, 2)))
    .withColumn("loan_amount", F.col("loan_amount").cast(DecimalType(18, 2)))
    .withColumn("partner_id", F.col("partner_id").cast(IntegerType()))
    .withColumn("term_in_months", F.col("term_in_months").cast(IntegerType()))
    .withColumn("lender_count", F.col("lender_count").cast(IntegerType()))
    .withColumn("posted_time", F.to_timestamp("posted_time"))
    .withColumn("disbursed_time", F.to_timestamp("disbursed_time"))
    .withColumn("funded_time", F.to_timestamp("funded_time"))
    .withColumn("date", F.to_date("date")))
write_delta(loans_silver, "kiva_loans")

# Keep supporting entities separate. Normalize names only in Silver.
def snake_case_columns(df):
    import re
    for old_name in df.columns:
        new_name = re.sub(r"[^A-Za-z0-9]+", "_", old_name.strip()).strip("_").lower()
        if old_name != new_name:
            df = df.withColumnRenamed(old_name, new_name)
    return df

for name in ["kiva_mpi_region_locations", "loan_theme_ids", "loan_themes_by_region"]:
    source = spark.read.format("delta").load(f"{bronze_root}/{name}")
    write_delta(snake_case_columns(source), name)
