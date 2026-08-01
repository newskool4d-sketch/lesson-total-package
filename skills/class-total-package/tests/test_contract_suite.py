import unittest
from pathlib import Path

from scripts.run_contract_tests import load_rubric, run_fixture_suite, validate_rubric_rows


ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "evals" / "rubrics" / "shared.csv"
FIXTURES = ROOT / "evals" / "fixtures"


class ContractSuiteTests(unittest.TestCase):
    def test_shared_rubric_has_24_valid_criteria(self):
        rows = load_rubric(RUBRIC)
        self.assertEqual(validate_rubric_rows(rows), [])
        self.assertEqual(len(rows), 24)
        self.assertEqual({row["Bucket"] for row in rows}, {"P", "R", "O", "M", "S"})

    def test_fixture_suite_matches_expected_exit_codes(self):
        rows = load_rubric(RUBRIC)
        self.assertEqual(run_fixture_suite(FIXTURES, rows), [])


if __name__ == "__main__":
    unittest.main()
