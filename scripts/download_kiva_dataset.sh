#!/usr/bin/env bash
set -euo pipefail

DATASET="kiva/data-science-for-good-kiva-crowdfunding"
OUTPUT_DIR="data"

if ! command -v kaggle >/dev/null 2>&1; then
  echo "Kaggle CLI not found. Install it with: python -m pip install kaggle" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
kaggle datasets download -d "$DATASET" --unzip -p "$OUTPUT_DIR"

required=(
  "kiva_loans.csv"
  "kiva_mpi_region_locations.csv"
  "loan_theme_ids.csv"
  "loan_themes_by_region.csv"
)

for file in "${required[@]}"; do
  if [[ ! -s "$OUTPUT_DIR/$file" ]]; then
    echo "Expected dataset file missing or empty: $OUTPUT_DIR/$file" >&2
    exit 1
  fi
done

echo "Downloaded the official Kiva Crowdfunding dataset to $OUTPUT_DIR/"
echo "Run: python scripts/validate_kiva_dataset.py"
