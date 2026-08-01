"""Validate the prototype lesson-differentiation contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


TIERS = {"support", "core", "extension"}
AUDIENCES = {"teacher", "student", "shared"}
ABILITY_LABELS = re.compile(r"하위 수준|낮은 수준|보충반|기초반|상위 수준|심화반|Below|Above|Group A|Group C")
PII_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    re.compile(r"(?<!\d)(?:01[016789]|02|0[3-9]\d)[-\s.]?\d{3,4}[-\s.]?\d{4}(?!\d)"),
)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_differentiation(manifest: dict[str, Any], base_dir: Path | str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    required = {
        "schema_version",
        "differentiation_id",
        "source_package_id",
        "subject",
        "grade_band",
        "standard",
        "shared_context",
        "shared_objective",
        "core_task_ids",
        "tiers",
        "grouping",
        "artifacts",
        "safety",
    }
    missing = sorted(required - set(manifest))
    errors.extend(f"missing top-level field: {field}" for field in missing)
    if missing:
        return errors

    for field in ("schema_version", "differentiation_id", "source_package_id", "subject", "grade_band", "shared_context", "shared_objective"):
        if not _nonempty(manifest.get(field)):
            errors.append(f"{field} must be non-empty")

    standard = manifest["standard"]
    if not isinstance(standard, dict):
        errors.append("standard must be an object")
    elif standard.get("status") not in {"verified", "user-provided", "pending"}:
        errors.append("standard.status must be verified, user-provided, or pending")

    core_task_ids = manifest["core_task_ids"]
    if not isinstance(core_task_ids, list) or not core_task_ids or not all(_nonempty(item) for item in core_task_ids):
        errors.append("core_task_ids must be a non-empty string list")
        core_task_ids = []
    else:
        if len(set(core_task_ids)) != len(core_task_ids):
            errors.append("core_task_ids must be unique")
        core_task_ids = list(core_task_ids)

    tiers = manifest["tiers"]
    if not isinstance(tiers, list):
        errors.append("tiers must be a list")
        tiers = []
    tier_ids = [tier.get("tier_id") for tier in tiers if isinstance(tier, dict)]
    if set(tier_ids) != TIERS or len(tier_ids) != len(TIERS):
        errors.append("tiers must contain exactly support, core, and extension")

    for tier in tiers:
        if not isinstance(tier, dict):
            errors.append("tier must be an object")
            continue
        tier_id = tier.get("tier_id", "<unknown>")
        for field in ("teacher_label", "student_label"):
            if not _nonempty(tier.get(field)):
                errors.append(f"tier {tier_id} requires {field}")
        task_ids = tier.get("task_ids")
        if not isinstance(task_ids, list) or not all(_nonempty(item) for item in task_ids):
            errors.append(f"tier {tier_id} task_ids must be a string list")
            task_ids = []
        if set(core_task_ids) - set(task_ids):
            errors.append(f"tier {tier_id} task_ids must include every core_task_id")
        if tier.get("shared_context") and tier.get("shared_context") != manifest.get("shared_context"):
            errors.append(f"tier {tier_id} shared_context differs from shared_context")
        scaffolds = tier.get("scaffolds")
        if not isinstance(scaffolds, list) or not all(_nonempty(item) for item in scaffolds):
            errors.append(f"tier {tier_id} scaffolds must be a string list")
        if tier.get("scaffold_fade") is not True:
            errors.append(f"tier {tier_id} scaffold_fade must be true")
        extensions = tier.get("extension_task_ids")
        if not isinstance(extensions, list) or not all(_nonempty(item) for item in extensions):
            errors.append(f"tier {tier_id} extension_task_ids must be a string list")
        if tier_id == "support" and not scaffolds:
            errors.append("support tier requires at least one scaffold")
        if tier_id == "extension" and not extensions:
            errors.append("extension tier requires at least one extension task")

    grouping = manifest["grouping"]
    if not isinstance(grouping, dict):
        errors.append("grouping must be an object")
    else:
        if not _nonempty(grouping.get("basis")):
            errors.append("grouping.basis must be non-empty")
        if grouping.get("revisable") is not True:
            errors.append("grouping.revisable must be true")

    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty list")
        artifacts = []
    tier_ids_set = set(TIERS)
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            errors.append("artifact must be an object")
            continue
        artifact_id = artifact.get("artifact_id", "<unknown>")
        tier_id = artifact.get("tier_id")
        if tier_id not in tier_ids_set:
            errors.append(f"artifact {artifact_id} has unknown tier_id")
        if artifact.get("audience") not in AUDIENCES:
            errors.append(f"artifact {artifact_id} has invalid audience")
        task_ids = artifact.get("task_ids")
        if not isinstance(task_ids, list):
            errors.append(f"artifact {artifact_id} task_ids must be a list")
        path_value = artifact.get("path")
        if not _nonempty(path_value):
            errors.append(f"artifact {artifact_id} requires path")
            continue
        if base_dir is not None:
            path = Path(path_value)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"artifact path escapes package root: {path_value}")
                continue
            resolved = Path(base_dir) / path
            if not resolved.is_file():
                errors.append(f"artifact file not found: {path_value}")
                continue
            try:
                content = resolved.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"artifact is not UTF-8 text: {path_value}")
                continue
            if artifact.get("audience") == "student" and ABILITY_LABELS.search(content):
                errors.append(f"student ability label in artifact {path_value}")
            if PII_PATTERNS[0].search(content) or PII_PATTERNS[1].search(content):
                errors.append(f"PII detected in artifact {path_value}")

    safety = manifest["safety"]
    if not isinstance(safety, dict):
        errors.append("safety must be an object")
    else:
        if safety.get("pii_check") != "passed":
            errors.append("safety.pii_check must be passed")
        if safety.get("no_ability_labels") is not True:
            errors.append("safety.no_ability_labels must be true")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a lesson-differentiation manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--base-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    errors = validate_differentiation(manifest, args.base_dir or args.manifest.parent)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {args.manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
