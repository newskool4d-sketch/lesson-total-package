"""Validate the prototype lesson-differentiation contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .validation_common import (
        ValidationInputError, audience_content_errors, contains_pii, manifest_safety_errors,
        read_artifact, read_utf8_bounded, safety_views,
    )
else:  # direct CLI invocation
    from validation_common import (
        ValidationInputError, audience_content_errors, contains_pii, manifest_safety_errors,
        read_artifact, read_utf8_bounded, safety_views,
    )


TIERS = {"support", "core", "extension"}
AUDIENCES = {"teacher", "student", "shared"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_differentiation(manifest: dict[str, Any], base_dir: Path | str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    safety_errors = manifest_safety_errors(manifest)
    if safety_errors:
        return safety_errors
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
    elif not isinstance(standard.get("status"), str) or standard["status"] not in {"verified", "user-provided", "pending"}:
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
    if any(not _nonempty(tier_id) for tier_id in tier_ids) or set(tier_ids) != TIERS or len(tier_ids) != len(TIERS):
        errors.append("tiers must contain exactly support, core, and extension")

    allowed_tasks = {tier_id: set() for tier_id in TIERS}
    required_tasks = {tier_id: set(core_task_ids) for tier_id in TIERS}
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
            extensions = []
        if tier_id == "support" and not scaffolds:
            errors.append("support tier requires at least one scaffold")
        if tier_id == "extension" and not extensions:
            errors.append("extension tier requires at least one extension task")
        if _nonempty(tier_id) and tier_id in TIERS:
            allowed_tasks[tier_id] = set(task_ids) | set(extensions)
            required_tasks[tier_id].update(extensions)

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
    student_tiers: set[str] = set()
    student_tasks = {tier_id: set() for tier_id in TIERS}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            errors.append("artifact must be an object")
            continue
        artifact_id = artifact.get("artifact_id", "<unknown>")
        tier_id = artifact.get("tier_id")
        valid_tier_id = _nonempty(tier_id) and tier_id in TIERS
        if not valid_tier_id:
            errors.append(f"artifact {artifact_id} has unknown tier_id")
        audience = artifact.get("audience")
        if not _nonempty(audience) or audience not in AUDIENCES:
            errors.append(f"artifact {artifact_id} has invalid audience")
        task_ids = artifact.get("task_ids")
        if not isinstance(task_ids, list) or not all(_nonempty(item) for item in task_ids):
            errors.append(f"artifact {artifact_id} task_ids must be a string list")
            task_ids = []
        if valid_tier_id:
            unknown_tasks = set(task_ids) - allowed_tasks[tier_id]
            if unknown_tasks:
                errors.append(f"artifact {artifact_id} has unknown task_ids for tier {tier_id}: {', '.join(sorted(unknown_tasks))}")
            if audience == "student":
                student_tiers.add(tier_id)
                student_tasks[tier_id].update(task_ids)
        path_value = artifact.get("path")
        if not _nonempty(path_value):
            errors.append(f"artifact {artifact_id} requires path")
            continue
        if base_dir is not None:
            try:
                content = read_artifact(path_value, base_dir)
                has_pii = contains_pii(content)
                views = safety_views(content)
            except ValidationInputError as exc:
                errors.append(str(exc))
                continue
            errors.extend(audience_content_errors(audience, views, path_value))
            if has_pii:
                errors.append(f"PII detected in artifact {path_value}")

    for tier_id in sorted(TIERS):
        if tier_id not in student_tiers:
            errors.append(f"tier {tier_id} requires at least one student artifact")
        missing_tasks = required_tasks[tier_id] - student_tasks[tier_id]
        if missing_tasks:
            errors.append(f"tier {tier_id} student artifacts missing required task_ids: {', '.join(sorted(missing_tasks))}")

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
        manifest = json.loads(read_utf8_bounded(args.manifest))
    except (OSError, ValueError, RecursionError) as exc:
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
