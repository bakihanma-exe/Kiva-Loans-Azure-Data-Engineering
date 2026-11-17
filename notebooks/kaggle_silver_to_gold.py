# Databricks notebook source
# Kiva Silver -> Gold business aggregates. No unvalidated many-to-many joins.
dbutils.widgets.text("silver_root", "abfss://<container>@<storage-account>.dfs.core.windows.net/kiva/silver")
dbutils.widgets.text("gold_root", "abfss://<container>@<storage-account>.dfs.core.windows.net/kiva/gold")
silver_root = dbutils.widgets.get("silver_root").rstrip("/")
gold_root = dbutils.widgets.get("gold_root").rstrip("/")
from pyspark.sql import functions as F
loans = spark.read.format("delta").load(f"{silver_root}/kiva_loans")

def save_gold(df, name):
    path = f"{gold_root}/{name}"
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)
    print(f"Gold written: {name}; rows={df.count()}")

kpi = loans.agg(
    F.count("*").alias("total_loan_count"),
    F.sum("loan_amount").alias("total_loan_amount"),
    F.sum("funded_amount").alias("total_funded_amount"),
    F.avg("loan_amount").alias("average_loan_amount"),
    F.countDistinct("country").alias("country_count"),
    F.sum(F.when(F.col("funded_amount") >= F.col("loan_amount"), 1).otherwise(0)).alias("fully_funded_loan_count"))
save_gold(kpi, "gold_kpi_summary")

monthly = (loans.where(F.col("posted_time").isNotNull())
    .withColumn("posted_month", F.date_trunc("month", "posted_time").cast("date"))
    .groupBy("posted_month")
    .agg(F.count("*").alias("loan_count"), F.sum("loan_amount").alias("loan_amount"), F.sum("funded_amount").alias("funded_amount"))
    .orderBy("posted_month"))
save_gold(monthly, "gold_monthly_trend")

for grouping, name in [("sector", "gold_sector_summary"), ("country", "gold_country_summary"), ("repayment_interval", "gold_repayment_summary"), ("borrower_genders", "gold_borrower_gender_summary")]:
    dims = [grouping]
    if grouping == "country": dims.append("country_code")
    result = loans.groupBy(*dims).agg(F.count("*").alias("loan_count"), F.sum("loan_amount").alias("loan_amount"), F.sum("funded_amount").alias("funded_amount"), F.avg("loan_amount").alias("average_loan_amount"))
    save_gold(result, name)
