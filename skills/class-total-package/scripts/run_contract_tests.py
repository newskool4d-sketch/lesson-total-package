"""Run the deterministic package contract suite and validate rubric structure."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.validate_package import validate_manifest
except ModuleNotFoundError:  # direct `py scripts/run_contract_tests.py` invocation
    from validate_package import validate_manifest


RUBRIC_HEADERS = {"ID", "Bucket", "Criterion", "PassRequires", "Critical", "Conditional"}
BUCKETS = {"P", "R", "O", "M", "S"}
EXPECTED_RUBRIC_COUNT = 24


def load_rubric(path: Path | str) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_rubric_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if len(rows) != EXPECTED_RUBRIC_COUNT:
        errors.append(f"rubric must contain {EXPECTED_RUBRIC_COUNT} criteria; got {len(rows)}")
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        missing = sorted(RUBRIC_HEADERS - set(row))
        if missing:
            errors.append(f"rubric row {index} missing headers: {', '.join(missing)}")
            continue
        criterion_id = row.get("ID", "").strip()
        if not criterion_id:
            errors.append(f"rubric row {index} has empty ID")
        elif criterion_id in seen:
            errors.append(f"duplicate rubric ID: {criterion_id}")
        seen.add(criterion_id)
        if row.get("Bucket") not in BUCKETS:
            errors.append(f"rubric {criterion_id} has invalid bucket {row.get('Bucket')!r}")
        if row.get("Critical") not in {"true", "false"}:
            errors.append(f"rubric {criterion_id} Critical must be true or false")
        for field in ("Criterion", "PassRequires"):
            if not row.get(field, "").strip():
                errors.append(f"rubric {criterion_id} requires {field}")
    if {row.get("Bucket") for row in rows} != BUCKETS:
        errors.append("rubric must cover P/R/O/M/S buckets")
    return errors


def _expected_exit(path: Path) -> int:
    return 1 if ".invalid." in path.name else 0


def run_fixture_suite(fixtures_dir: Path | str, rubric_rows: list[dict[str, str]]) -> list[str]:
    errors = validate_rubric_rows(rubric_rows)
    if errors:
        return errors
    fixture_dir = Path(fixtures_dir)
    manifests = sorted(fixture_dir.glob("package-manifest*.json"))
    if not manifests:
        return [f"no manifest fixtures found in {fixture_dir}"]
    for path in manifests:
        try:
            manifest: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}: cannot load JSON: {exc}")
            continue
        actual_exit = 0 if not validate_manifest(manifest, fixture_dir) else 1
        expected_exit = _expected_exit(path)
        if actual_exit != expected_exit:
            errors.append(
                f"{path.name}: expected exit {expected_exit}, got {actual_exit}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run package contract fixtures and rubric checks")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=Path("evals/fixtures"),
        help="directory containing valid and invalid manifest fixtures",
    )
    parser.add_argument(
        "--rubric",
        type=Path,
        default=Path("evals/rubrics/shared.csv"),
        help="shared P/R/O/M/S rubric CSV",
    )
    args = parser.parse_args(argv)
    try:
        rows = load_rubric(args.rubric)
    except OSError as exc:
        print(f"FAIL: cannot read rubric: {exc}")
        return 1
    errors = run_fixture_suite(args.fixtures_dir, rows)
    if errors:
        print(f"FAIL: {len(errors)} contract error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: rubric={len(rows)} criteria; fixtures={len(list(args.fixtures_dir.glob('package-manifest*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
