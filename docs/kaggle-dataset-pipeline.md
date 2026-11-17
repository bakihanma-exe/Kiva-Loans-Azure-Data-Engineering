# Kiva Kaggle dataset pipeline (reproducible path)

This path processes the four original CSV files from Kaggle's Data Science for Good: Kiva Crowdfunding dataset. It is a dataset-driven companion to the SQL Server architecture in the supplied walkthrough, not a claim that Kaggle CSVs were extracted from that SQL Server.

## Data layout

The download script places the four files in the repository's data folder. Upload those files to the equivalent ADLS Gen2 raw folder:
- kiva_loans.csv — loan-level records; use this as the grain for dashboard measures.
- kiva_mpi_region_locations.csv — regional MPI and geography attributes.
- loan_theme_ids.csv — loan-to-theme/partner mapping.
- loan_themes_by_region.csv — partner/theme regional attributes.

Expected raw headers are in schemas/kiva_dataset_schema.json. Keep raw headers unchanged in Bronze.

## Databricks execution order

1. Download and validate the official CSVs using the repository scripts.
2. Upload the four CSVs to the ADLS Gen2 raw folder.
3. Run notebooks/kaggle_bronze_ingestion.py with raw_root and bronze_root widgets.
4. Run notebooks/kaggle_bronze_to_silver.py with bronze_root and silver_root.
5. Run notebooks/kaggle_silver_to_gold.py with silver_root and gold_root.
6. Run sql/kiva_data_quality_checks.sql.
7. Register Gold Delta outputs as tables or expose them through a supported Synapse/Fabric serving pattern before connecting Power BI.

All notebook paths are placeholders. Replace the storage account, container, and folder values. Configure access using a supported managed identity / credential mechanism; never paste keys or tokens into notebooks.

## Transformation decisions

- Bronze reads fields as strings and adds ingestion metadata; source CSVs are not modified.
- Silver casts loan IDs, amounts, partner IDs, term, lender count and the loan date/time fields. Unparseable values become null and should be measured by quality checks.
- Supporting files remain separate tables. Their column names are normalized to snake_case in Silver only.
- Gold aggregates use the loan-level table. No theme/geography join is applied by default because mismatched geographic or partner/theme grains can multiply rows or create misleading coverage. Validate join keys and cardinality before adding enrichment.
- Monthly trend is based on posted_time, the loan-posting timestamp.

## Limitations

- The Kaggle source is a historical snapshot, not a continuously arriving feed. Re-runs overwrite Delta outputs: this is a full refresh, not incremental CDC.
- The dataset does not establish actual repayment outcomes. Do not label the dashboard as repayment performance or credit-default analysis.
- KPI values in the source walkthrough are reference figures. Recompute them from the downloaded files and document filters/data version.
- These notebooks have not been executed against the full Kaggle archive or an Azure workspace. Run them in Databricks and review row counts and quality exceptions before describing the pipeline as end-to-end tested.
