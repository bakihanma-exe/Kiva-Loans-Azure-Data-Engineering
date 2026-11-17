"""Unit tests for the Kiva raw dataset header validator."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts.validate_kiva_dataset import load_schema, validate_dataset


class KivaDatasetValidationTests(unittest.TestCase):
    def test_all_four_expected_headers_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for filename, columns in load_schema()["files"].items():
                with (root / filename).open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(columns)
                    writer.writerow([""] * len(columns))
            self.assertEqual([], validate_dataset(root))

    def test_missing_file_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(4, len(validate_dataset(Path(temp_dir))))

    def test_header_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for filename, columns in load_schema()["files"].items():
                actual = list(columns)
                if filename == "kiva_loans.csv":
                    actual[0] = "wrong_id"
                with (root / filename).open("w", encoding="utf-8", newline="") as handle:
                    csv.writer(handle).writerow(actual)
            errors = validate_dataset(root)
            self.assertEqual(1, len(errors))
            self.assertIn("kiva_loans.csv", errors[0])


if __name__ == "__main__":
    unittest.main()
