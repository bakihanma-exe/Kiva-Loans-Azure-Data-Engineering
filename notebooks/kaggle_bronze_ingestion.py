# Databricks notebook source
# Kiva Kaggle CSV -> Bronze Delta
# Configure these widget paths for your ADLS Gen2 workspace.
dbutils.widgets.text("raw_root", "abfss://<container>@<storage-account>.dfs.core.windows.net/kiva/raw")
dbutils.widgets.text("bronze_root", "abfss://<container>@<storage-account>.dfs.core.windows.net/kiva/bronze")
raw_root = dbutils.widgets.get("raw_root").rstrip("/")
bronze_root = dbutils.widgets.get("bronze_root").rstrip("/")
from pyspark.sql import functions as F
FILES = ["kiva_loans", "kiva_mpi_region_locations", "loan_theme_ids", "loan_themes_by_region"]
# Keep raw fields as strings: do not guess source types during ingestion.
for table_name in FILES:
    source_path = f"{raw_root}/{table_name}.csv"
    target_path = f"{bronze_root}/{table_name}"
    df = (spark.read.option("header", "true").option("inferSchema", "false").option("mode", "FAILFAST").csv(source_path))
    if not df.columns:
        raise ValueError(f"No header detected in {source_path}")
    bronze_df = df.withColumn("_source_file", F.input_file_name()).withColumn("_ingested_at_utc", F.current_timestamp())
    (bronze_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(target_path))
    print(f"Bronze loaded: {table_name}; rows={bronze_df.count()}; path={target_path}")
