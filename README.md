# Kiva Loans — On-Prem SQL Server to Azure

This project folder documents and reconstructs the Kiva loan analytics pipeline described in the supplied 23-page walkthrough.

## Source-documented architecture
On-premises SQL Server → Azure Data Factory + Self-Hosted Integration Runtime → ADLS Gen2 (Bronze / Silver / Gold) → Azure Databricks notebooks → Azure Synapse Serverless SQL views → Power BI.

Azure Key Vault stores the SQL Server credentials used by the ADF linked service. The walkthrough uses a system-assigned managed identity for ADF access to Key Vault and Synapse access to the lake.

## Source-documented processing
- ADF Lookup queries SQL Server metadata for tables in the `dbo` schema.
- ForEach iterates over the Lookup output and runs a parameterized Copy Activity.
- Bronze stores source tables as CSV in separate table folders.
- Databricks Bronze-to-Silver notebook converts columns containing date/time in their names to `yyyy-MM-dd`.
- Databricks Silver-to-Gold notebook converts column names to lowercase.
- Synapse Serverless SQL creates views over Gold CSV folders using OPENROWSET and a stored procedure.
- ADF Get Metadata + ForEach calls the stored procedure for each Gold table.
- Power BI connects to Synapse views and presents loan, funded amount, sector, borrower gender, repayment interval, country, and monthly trends.

## Repository contents
- `docs/source-walkthrough.md`: page-by-page implementation notes and caveats
- `sql/metadata_tables.sql`: metadata query for dynamic ADF ingestion
- `notebooks/bronze_to_silver.py`: generic date/time normalization
- `notebooks/silver_to_gold.py`: lowercase column naming
- `synapse/create_serverless_view.sql`: parameterized view procedure template
- `adf/pipeline-design.md`: orchestration and expressions
- `powerbi/dashboard-design.md`: dashboard layout and KPI definitions
- `schemas/kiva_dataset_schema.json`: exact raw CSV header contract for the four official Kaggle files
- `data/README.md`: official dataset source and download instructions
- `scripts/download_kiva_dataset.sh`: downloads only the named Kaggle dataset using the Kaggle CLI
- `scripts/validate_kiva_dataset.py`: checks all four files and their exact headers
- `tests/`: local source-contract and dataset validation tests

## Dataset setup and validation
1. Install the Kaggle CLI: `python -m pip install kaggle`.
2. Configure your own Kaggle API credentials locally (never commit them).
3. Run `bash scripts/download_kiva_dataset.sh` from the repository root.
4. Run `python scripts/validate_kiva_dataset.py` to check the four official CSV headers.

The source CSVs are not committed here because Kaggle requires account authorization to download the official archive. The repository contains the official dataset identifier, exact source-file names, header schema, and reproducible download script. No substitute dataset is used.

## Important implementation notes
The walkthrough's sample source and storage names are environment-specific. Replace all placeholders with your own. Never copy credentials, access tokens, account keys, or secrets from screenshots or notebooks into Git. Prefer managed identity / workload identity and Key Vault. The old Databricks DBFS mount / credential-passthrough pattern shown in the walkthrough is legacy; use a currently supported secure storage access pattern in a new workspace.

The walkthrough describes a daily full refresh / overwrite in Bronze, not a robust incremental CDC implementation. Its final testing section adds 10 rows per day and refreshes Power BI, but the ingestion section says the Bronze folder is overwritten on each run. Reconcile this design before claiming true incremental preservation.

## KPI note
The PDF dashboard reports approximately 671K loans, $565.4M total loan amount, and $527.6M funded amount. Your resume rounds the loan amount to $565M. Use the exact values only after reproducing them from the dataset and documenting the filters.
