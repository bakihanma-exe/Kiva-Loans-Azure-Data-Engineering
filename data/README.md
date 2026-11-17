# Kiva source dataset

This project uses only the dataset named in the supplied project walkthrough:

**Kaggle — Data Science for Good: Kiva Crowdfunding**

Source: https://www.kaggle.com/datasets/kiva/data-science-for-good-kiva-crowdfunding

Download the original four CSV files into this directory:

- `kiva_loans.csv`
- `kiva_mpi_region_locations.csv`
- `loan_theme_ids.csv`
- `loan_themes_by_region.csv`

## Download

1. Accept Kaggle's dataset terms and create a Kaggle API token in your Kaggle account.
2. Install the Kaggle CLI: `python -m pip install kaggle`.
3. Configure the Kaggle API token using Kaggle's documented credentials setup. Never commit `kaggle.json`.
4. From the repository root run: `bash scripts/download_kiva_dataset.sh`.

The source data files are not checked into Git in this commit because downloading the official archive requires Kaggle account authorization. The script fetches the named dataset itself; it does not substitute or transform it.

## Expected source shape

The walkthrough identifies the loan records as loans issued from January 2014 through July 2017 and reports 671K loan records in its dashboard. The full source column lists are in [schemas/kiva_dataset_schema.json](../schemas/kiva_dataset_schema.json).

The walkthrough does not publish SQL Server DDL or authoritative per-column SQL types. Do not treat inferred types as source-provided schema. The validator checks exact CSV headers and non-empty files; it does not assert unverified row counts.

## Data handling

Keep the four original CSVs under `data/` locally. They are ignored by Git to avoid accidentally committing large raw files. Do not add credentials, tokens, or other secrets.
