"""Validate the original Kiva Kaggle CSV files against their published headers.

This checks file presence, non-empty content, and exact header names/order.
It intentionally does not invent source SQL types or hard-code row counts.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "kiva_dataset_schema.json"
DATA_DIR = ROOT / "data"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_dataset(data_dir: Path = DATA_DIR) -> list[str]:
    schema = load_schema()
    errors: list[str] = []

    for filename, expected_columns in schema["files"].items():
        path = data_dir / filename
        if not path.is_file():
            errors.append(f"Missing file: {path}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"Empty file: {path}")
            continue

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            try:
                actual_columns = next(reader)
            except StopIteration:
                errors.append(f"CSV has no header: {path}")
                continue

        if actual_columns != expected_columns:
            missing = [c for c in expected_columns if c not in actual_columns]
            extra = [c for c in actual_columns if c not in expected_columns]
            errors.append(
                f"Header mismatch in {filename}; missing={missing}; extra={extra}; "
                f"expected_order={expected_columns == actual_columns}"
            )

    return errors


if __name__ == "__main__":
    problems = validate_dataset()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)
    print("Kiva dataset validation passed: all four official CSV headers match.")
