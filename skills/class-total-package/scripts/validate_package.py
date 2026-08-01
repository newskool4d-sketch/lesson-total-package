"""Validate the class-total-package manifest contract.

The validator intentionally uses only the Python standard library.  It validates
package-level relationships and safety gates without replacing any linked module's
native renderer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


OUTPUT_MODES = {"간단형", "수업형", "패키지형"}
STATUSES = {"verified", "user-provided", "pending"}
SOURCE_VERIFICATION_STATUSES = {"verified", "user-provided", "pending"}
COPYRIGHT_STATUSES = {"cleared", "attribution_required", "unknown"}
AUDIENCES = {"teacher", "student", "shared"}
STUDENT_TEACHER_ONLY_TERMS = re.compile(r"교사용|교사 메모|학생 관찰 기록|정답 및 해설")
STUDENT_ABILITY_LABELS = re.compile(r"하위 수준|낮은 수준|보충반|기초반|상위 수준|심화반|Below|Above|Group A|Group C")
PII_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    re.compile(r"(?<!\d)(?:01[016789]|02|0[3-9]\d)[-\s.]?\d{3,4}[-\s.]?\d{4}(?!\d)"),
    re.compile(r"(?<!\d)\d{6}[-\s.]?[1-4]\d{6}(?!\d)"),
)


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _unique_ids(items: list[Any], key: str, label: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for item in items:
        value = item.get(key) if isinstance(item, dict) else None
        if not _is_nonempty(value):
            errors.append(f"{label} requires non-empty {key}")
            continue
        if value in seen:
            errors.append(f"duplicate {label} {value}")
        seen.add(value)
    return seen


def _validate_paths_and_content(
    manifest: dict[str, Any], base_dir: Path, errors: list[str]
) -> None:
    for artifact in _as_list(manifest.get("artifacts")):
        if not isinstance(artifact, dict):
            continue
        path_value = artifact.get("path")
        if not _is_nonempty(path_value):
            errors.append("artifact requires path")
            continue
        path = Path(path_value)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"artifact path escapes package root: {path_value}")
            continue
        resolved = base_dir / path
        if not resolved.is_file():
            errors.append(f"artifact file not found: {path_value}")
            continue
        try:
            content = resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"artifact is not UTF-8 text: {path_value}")
            continue
        for pattern in PII_PATTERNS:
            if pattern.search(content):
                errors.append(f"PII detected in artifact {path_value}")
                break
        if artifact.get("audience") == "student":
            if STUDENT_TEACHER_ONLY_TERMS.search(content):
                errors.append(f"teacher-only content in student artifact {path_value}")
            if STUDENT_ABILITY_LABELS.search(content):
                errors.append(f"student ability label in student artifact {path_value}")


def validate_manifest(manifest: dict[str, Any], base_dir: Path | str | None = None) -> list[str]:
    """Return human-readable validation errors for one package manifest.

    ``base_dir`` is the directory against which artifact paths are resolved.  When
    omitted, file-path checks are skipped so callers can validate an in-memory
    manifest independently of the filesystem.
    """

    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]

    required_top_level = {
        "schema_version",
        "package_id",
        "output_mode",
        "context",
        "standard",
        "anchor",
        "learner_profile",
        "pedagogy_profile",
        "modules",
        "tasks",
        "sources",
        "artifacts",
        "criteria",
        "safety",
    }
    missing = sorted(required_top_level - set(manifest))
    errors.extend(f"missing top-level field: {field}" for field in missing)
    if missing:
        return errors

    if not _is_nonempty(manifest.get("schema_version")):
        errors.append("schema_version must be non-empty")
    if not _is_nonempty(manifest.get("package_id")):
        errors.append("package_id must be non-empty")
    if manifest.get("output_mode") not in OUTPUT_MODES:
        errors.append(f"output_mode must be one of {sorted(OUTPUT_MODES)}")

    context = manifest.get("context")
    if not isinstance(context, dict):
        errors.append("context must be an object")
        context = {}
    duration = context.get("duration_minutes")
    if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
        errors.append("context.duration_minutes must be a positive integer")
    for field in ("topic", "subject", "school_level", "grade_band"):
        if not _is_nonempty(context.get(field)):
            errors.append(f"context.{field} must be non-empty")

    standard = manifest.get("standard")
    if not isinstance(standard, dict):
        errors.append("standard must be an object")
        standard = {}
    status = standard.get("status")
    if status not in STATUSES:
        errors.append(f"standard.status must be one of {sorted(STATUSES)}")
    if status == "verified":
        for field in ("code", "text", "source"):
            if not _is_nonempty(standard.get(field)):
                errors.append(f"verified standard requires {field}")
    elif status in {"pending", "user-provided"}:
        marker = f"{standard.get('code', '')} {standard.get('text', '')}".lower()
        if status == "pending" and "확인 필요" not in marker and not standard.get("confirmation_required"):
            errors.append("standard confirmation required for pending status")

    anchor = manifest.get("anchor")
    if not isinstance(anchor, dict):
        errors.append("anchor must be an object")
        anchor = {}
    for field in (
        "topic",
        "grade_band",
        "subject",
        "objective",
        "essential_question",
        "final_artifact",
    ):
        if not _is_nonempty(anchor.get(field)):
            errors.append(f"anchor.{field} must be non-empty")
    for field in ("key_concepts", "student_actions", "evaluation_points"):
        values = anchor.get(field)
        if not isinstance(values, list) or not values or not all(_is_nonempty(item) for item in values):
            errors.append(f"anchor.{field} must be a non-empty string list")

    learner_profile = manifest.get("learner_profile")
    if not isinstance(learner_profile, dict):
        errors.append("learner_profile must be an object")
        learner_profile = {}
    if learner_profile.get("mode") not in {"default", "provided"}:
        errors.append("learner_profile.mode must be default or provided")
    for field in ("reading_access", "grouping_basis", "regrouping_rule"):
        if not _is_nonempty(learner_profile.get(field)):
            errors.append(f"learner_profile.{field} must be non-empty")
    supports = learner_profile.get("supports")
    if not isinstance(supports, list) or not all(_is_nonempty(item) for item in supports):
        errors.append("learner_profile.supports must be a string list")
    udl_defaults = learner_profile.get("udl_defaults")
    if not isinstance(udl_defaults, list) or len(udl_defaults) < 2 or not all(
        _is_nonempty(item) for item in udl_defaults
    ):
        errors.append("learner_profile.udl_defaults must contain at least two strings")
    for field in ("no_ability_labels", "cognitive_demand_preserved", "scaffold_fade"):
        if learner_profile.get(field) is not True:
            errors.append(f"learner_profile.{field} must be true")

    pedagogy_profile = manifest.get("pedagogy_profile")
    if not isinstance(pedagogy_profile, dict):
        errors.append("pedagogy_profile must be an object")
        pedagogy_profile = {}
    if pedagogy_profile.get("subject") != context.get("subject"):
        errors.append("pedagogy_profile.subject must match context.subject")
    for field in ("non_negotiables", "selected_checks"):
        values = pedagogy_profile.get(field)
        if not isinstance(values, list) or not values or not all(_is_nonempty(item) for item in values):
            errors.append(f"pedagogy_profile.{field} must be a non-empty string list")

    modules = _as_list(manifest.get("modules"))
    module_ids = _unique_ids(modules, "module_id", "module", errors)
    active_modules = {
        item.get("module_id")
        for item in modules
        if isinstance(item, dict) and item.get("active") is True
    }
    if not active_modules:
        errors.append("at least one active module is required")

    tasks = _as_list(manifest.get("tasks"))
    task_ids = _unique_ids(tasks, "task_id", "task", errors)
    total_minutes = 0
    for task in tasks:
        if not isinstance(task, dict):
            errors.append("task must be an object")
            continue
        minutes = task.get("minutes")
        if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes <= 0:
            errors.append(f"task {task.get('task_id', '<unknown>')} duration must be positive")
        else:
            total_minutes += minutes
        for field in ("phase", "student_action", "evidence"):
            if not _is_nonempty(task.get(field)):
                errors.append(f"task {task.get('task_id', '<unknown>')} requires {field}")
        owners = _as_list(task.get("module_owners"))
        for owner in owners:
            if owner not in module_ids:
                errors.append(f"task {task.get('task_id', '<unknown>')} references unknown module {owner}")
            elif owner not in active_modules:
                errors.append(f"task {task.get('task_id', '<unknown>')} module {owner} is not active")
    if isinstance(duration, int) and total_minutes != duration:
        errors.append(f"task duration total {total_minutes} does not match context duration {duration}")

    sources = _as_list(manifest.get("sources"))
    source_ids = _unique_ids(sources, "source_id", "source", errors)
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source must be an object")
            continue
        verification = source.get("verification_status")
        copyright_status = source.get("copyright_status")
        if verification not in SOURCE_VERIFICATION_STATUSES:
            errors.append(f"source {source.get('source_id', '<unknown>')} has invalid verification_status")
        if copyright_status not in COPYRIGHT_STATUSES:
            errors.append(f"source {source.get('source_id', '<unknown>')} has invalid copyright_status")
        if copyright_status == "unknown":
            errors.append(f"source {source.get('source_id', '<unknown>')} copyright status unknown")
        if copyright_status == "attribution_required" and not _is_nonempty(source.get("attribution")):
            errors.append(f"source {source.get('source_id', '<unknown>')} requires attribution")
        if not _is_nonempty(source.get("location")):
            errors.append(f"source {source.get('source_id', '<unknown>')} requires location")

    artifacts = _as_list(manifest.get("artifacts"))
    artifact_ids = _unique_ids(artifacts, "artifact_id", "artifact", errors)
    referenced_task_ids: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            errors.append("artifact must be an object")
            continue
        module_id = artifact.get("module_id")
        if module_id not in module_ids:
            errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} references unknown module {module_id}")
        elif module_id not in active_modules:
            errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} module {module_id} is not active")
        if artifact.get("audience") not in AUDIENCES:
            errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} has invalid audience")
        for task_id in _as_list(artifact.get("task_ids")):
            if task_id not in task_ids:
                errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} references unknown task {task_id}")
            referenced_task_ids.add(task_id)
        for source_id in _as_list(artifact.get("source_ids")):
            if source_id not in source_ids:
                errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} references unknown source {source_id}")
    for task_id in sorted(task_ids - referenced_task_ids):
        errors.append(f"task {task_id} is not referenced by any artifact")

    criteria = _as_list(manifest.get("criteria"))
    _unique_ids(criteria, "criterion_id", "criterion", errors)
    for criterion in criteria:
        if not isinstance(criterion, dict):
            errors.append("criterion must be an object")
            continue
        for task_id in _as_list(criterion.get("task_ids")):
            if task_id not in task_ids:
                errors.append(f"criterion {criterion.get('criterion_id', '<unknown>')} references unknown task {task_id}")
        for field in ("evidence_required", "feedback_use"):
            if not _is_nonempty(criterion.get(field)):
                errors.append(f"criterion {criterion.get('criterion_id', '<unknown>')} requires {field}")

    safety = manifest.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be an object")
    else:
        if safety.get("pii_check") != "passed":
            errors.append("safety.pii_check must be passed")
        for field in ("ai_verification_required", "license_notice_required"):
            if not isinstance(safety.get(field), bool):
                errors.append(f"safety.{field} must be boolean")

    if base_dir is not None:
        _validate_paths_and_content(manifest, Path(base_dir), errors)
    return errors


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a class-total-package manifest")
    parser.add_argument("manifest", type=Path, help="manifest JSON path")
    parser.add_argument("--base-dir", type=Path, help="artifact root; defaults to manifest parent")
    args = parser.parse_args(argv)
    try:
        manifest = _load_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    base_dir = args.base_dir or args.manifest.parent
    errors = validate_manifest(manifest, base_dir)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {args.manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
