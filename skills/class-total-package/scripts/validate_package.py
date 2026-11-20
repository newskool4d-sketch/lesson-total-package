"""Validate the class-total-package manifest contract.

The validator intentionally uses only the Python standard library.  It validates
package-level relationships and safety gates without replacing any linked module's
native renderer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

if __package__:
    from .artifact_contract import artifact_anchor_signature, artifact_contract_errors
    from .validation_common import (
        ValidationInputError, contains_pii as _contains_pii, manifest_safety_errors,
        audience_content_errors, read_utf8_bounded, resolve_package_file, safety_views,
    )
else:  # direct CLI invocation
    from artifact_contract import artifact_anchor_signature, artifact_contract_errors
    from validation_common import (
        ValidationInputError, contains_pii as _contains_pii, manifest_safety_errors,
        audience_content_errors, read_utf8_bounded, resolve_package_file, safety_views,
    )


OUTPUT_MODES = {"간단형", "수업형", "패키지형"}
STATUSES = {"verified", "user-provided", "pending"}
SOURCE_VERIFICATION_STATUSES = {"verified", "user-provided", "pending"}
COPYRIGHT_STATUSES = {"cleared", "attribution_required", "unknown"}
AUDIENCES = {"teacher", "student", "shared"}


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _as_list(value: Any, field: str, errors: list[str]) -> list[Any]:
    if isinstance(value, list):
        return value
    errors.append(f"{field} must be a list")
    return []


def _id_references(value: Any, field: str, errors: list[str]) -> list[str]:
    if isinstance(value, list) and all(_is_nonempty(item) for item in value):
        return value
    errors.append(f"{field} must be a list of non-empty strings")
    return []


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


def _check_source_location(source: dict, base_dir: Path | str | None, errors: list[str]) -> None:
    label = f"source {source.get('source_id', '<unknown>')}"
    location = source.get("location")
    if not _is_nonempty(location):
        errors.append(f"{label} requires location")
        return
    # Older packages recorded URLs or relative filenames in a single field.
    is_url = location.lower().startswith(("https://", "http://"))
    kind = source.get("location_kind", "external" if is_url else "packaged")
    if kind == "external":
        try:
            url = urlsplit(location)
            valid_url = url.scheme in ("http", "https") and bool(url.hostname)
        except ValueError:
            valid_url = False
        if not valid_url or any(ch.isspace() for ch in location):
            errors.append(f"{label} requires an HTTP(S) source URL")
    elif kind == "packaged":
        if is_url:
            errors.append(f"{label} requires a package-relative file")
        elif base_dir is not None:
            try:
                path = resolve_package_file(location, base_dir, label="source")
                with path.open("rb") as stream:
                    if not stream.read(1):
                        errors.append(f"{label} references an empty packaged file")
            except ValidationInputError as exc:
                errors.append(str(exc))
            except OSError:
                errors.append(f"{label} file cannot be read")
    elif kind != "teacher-held":
        errors.append(f"{label} location_kind must be packaged, external, or teacher-held")


def _validate_paths_and_content(
    manifest: dict, artifacts: list[Any], base_dir: Path, errors: list[str],
    *, generated: bool, check_anchor: bool, skills_roots: list[Path] | None,
) -> None:
    primary_paths: dict[tuple[int, int] | Path, str] = {}
    common_anchor = None
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        path_value = artifact.get("path")
        if not _is_nonempty(path_value):
            errors.append("artifact requires path")
            continue
        try:
            path = resolve_package_file(path_value, base_dir)
            content = read_utf8_bounded(path)
            has_pii = _contains_pii(content)
            views = safety_views(content)
        except ValidationInputError as exc:
            errors.append(str(exc))
            continue
        except UnicodeDecodeError:
            errors.append(f"artifact is not UTF-8 text: {path_value}")
            continue
        except OSError:
            errors.append(f"artifact cannot be read: {path_value}")
            continue
        errors.extend(audience_content_errors(artifact.get("audience"), views, path_value))
        if has_pii:
            errors.append(f"PII detected in artifact {path_value}")
            continue
        if not content.strip():
            errors.append(f"artifact file has no content: {path_value}")
            continue
        primary = artifact.get("artifact_role", "primary") == "primary"
        if generated and primary:
            try:
                info = path.stat()
            except OSError:
                errors.append(f"artifact cannot be read: {path_value}")
                continue
            identity = (info.st_dev, info.st_ino) if info.st_ino else path
            if identity in primary_paths:
                errors.append(f"duplicate primary artifact file: {path_value} and {primary_paths[identity]}")
            else:
                primary_paths[identity] = path_value
        contract_errors = artifact_contract_errors(
            manifest, artifact, path, content, base_dir,
            check_anchor=check_anchor, check_native=generated and primary,
            expected_anchor=common_anchor, skills_roots=skills_roots,
        )
        errors.extend(f"{path_value}: {message}" for message in contract_errors)
        if check_anchor and common_anchor is None and not contract_errors:
            common_anchor = artifact_anchor_signature(path, content)


def validate_manifest(manifest: dict[str, Any], base_dir: Path | str | None = None,
                      *, expected_stage: str = "generated", skills_roots: list[Path] | None = None) -> list[str]:
    """Return human-readable validation errors for one package manifest.

    ``base_dir`` is the directory against which artifact paths are resolved.  When
    omitted, file-path checks are skipped so callers can validate an in-memory
    manifest independently of the filesystem.
    """

    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    safety_errors = manifest_safety_errors(manifest)
    if safety_errors:
        return safety_errors
    stage = manifest.get("deliverable_stage", "generated")
    if expected_stage not in ("generated", "design") or stage != expected_stage:
        return ["deliverable_stage must match the requested stage (generated or design)"]

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
    if not isinstance(manifest.get("output_mode"), str) or manifest["output_mode"] not in OUTPUT_MODES:
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
    if not isinstance(status, str) or status not in STATUSES:
        errors.append(f"standard.status must be one of {sorted(STATUSES)}")
    if status in ("verified", "user-provided"):
        for field in ("code", "text", "source"):
            if not _is_nonempty(standard.get(field)):
                errors.append(f"{status} standard requires {field}")
        if any("확인 필요" in str(standard.get(field, "")) for field in ("code", "text")):
            errors.append("confirmed standard cannot contain a pending marker")
    elif status == "pending":
        markers = (standard.get("code"), standard.get("text"))
        if standard.get("confirmation_required") is not True or not any(
            isinstance(value, str) and "확인 필요" in value for value in markers
        ):
            errors.append("pending standard requires confirmation_required=true and visible 확인 필요")

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
    for field in ("topic", "subject", "grade_band"):
        if anchor.get(field) != context.get(field):
            errors.append(f"anchor.{field} must match context.{field}")

    learner_profile = manifest.get("learner_profile")
    if not isinstance(learner_profile, dict):
        errors.append("learner_profile must be an object")
        learner_profile = {}
    if not isinstance(learner_profile.get("mode"), str) or learner_profile["mode"] not in {"default", "provided"}:
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

    modules = _as_list(manifest.get("modules"), "modules", errors)
    module_ids = _unique_ids(modules, "module_id", "module", errors)
    for module in modules:
        if isinstance(module, dict) and not isinstance(module.get("required", False), bool):
            errors.append("module.required must be boolean")
    active_modules = {
        item.get("module_id")
        for item in modules
        if isinstance(item, dict) and item.get("active") is True and _is_nonempty(item.get("module_id"))
    }
    if not active_modules:
        errors.append("at least one active module is required")
    required_modules = {
        item["module_id"] for item in modules
        if isinstance(item, dict) and item.get("required") is True and _is_nonempty(item.get("module_id"))
    }
    for module_id in sorted(required_modules - active_modules):
        errors.append(f"required module {module_id} must be active")

    tasks = _as_list(manifest.get("tasks"), "tasks", errors)
    task_ids = _unique_ids(tasks, "task_id", "task", errors)
    task_owners: dict[str, set[str]] = {}
    oral_tasks: set[str] = set()
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
        owners = _id_references(
            task.get("module_owners", []), f"task {task.get('task_id', '<unknown>')} module_owners", errors
        )
        if not owners:
            errors.append(f"task {task.get('task_id', '<unknown>')} requires module_owners")
        delivery = task.get("delivery", "student-artifact")
        if delivery not in ("student-artifact", "teacher-oral"):
            errors.append(f"task {task.get('task_id', '<unknown>')} has invalid delivery")
        if _is_nonempty(task.get("task_id")):
            task_owners[task["task_id"]] = set(owners)
            if delivery == "teacher-oral":
                oral_tasks.add(task["task_id"])
                if not _is_nonempty(task.get("oral_prompt")):
                    errors.append(f"teacher-oral task {task['task_id']} requires oral_prompt")
        for owner in owners:
            if owner not in module_ids:
                errors.append(f"task {task.get('task_id', '<unknown>')} references unknown module {owner}")
            elif owner not in active_modules:
                errors.append(f"task {task.get('task_id', '<unknown>')} module {owner} is not active")
    if isinstance(duration, int) and total_minutes != duration:
        errors.append(f"task duration total {total_minutes} does not match context duration {duration}")

    sources = _as_list(manifest.get("sources"), "sources", errors)
    source_ids = _unique_ids(sources, "source_id", "source", errors)
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source must be an object")
            continue
        verification = source.get("verification_status")
        copyright_status = source.get("copyright_status")
        if not isinstance(verification, str) or verification not in SOURCE_VERIFICATION_STATUSES:
            errors.append(f"source {source.get('source_id', '<unknown>')} has invalid verification_status")
        if not isinstance(copyright_status, str) or copyright_status not in COPYRIGHT_STATUSES:
            errors.append(f"source {source.get('source_id', '<unknown>')} has invalid copyright_status")
        if copyright_status == "unknown":
            errors.append(f"source {source.get('source_id', '<unknown>')} copyright status unknown")
        if copyright_status == "attribution_required" and not _is_nonempty(source.get("attribution")):
            errors.append(f"source {source.get('source_id', '<unknown>')} requires attribution")
        _check_source_location(source, base_dir, errors)

    artifacts = _as_list(manifest.get("artifacts"), "artifacts", errors)
    _unique_ids(artifacts, "artifact_id", "artifact", errors)
    referenced_task_ids: set[str] = set()
    delivered_tasks: set[str] = set()
    artifact_modules: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            errors.append("artifact must be an object")
            continue
        artifact_label = f"artifact {artifact.get('artifact_id', '<unknown>')}"
        module_id = artifact.get("module_id")
        if not _is_nonempty(module_id) or module_id not in module_ids:
            errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} references unknown module {module_id}")
        elif module_id not in active_modules:
            errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} module {module_id} is not active")
        elif artifact.get("artifact_role", "primary") == "primary":
            artifact_modules.add(module_id)
        if artifact.get("artifact_role", "primary") not in ("primary", "supplement"):
            errors.append(f"{artifact_label} has invalid artifact_role")
        if not isinstance(artifact.get("audience"), str) or artifact["audience"] not in AUDIENCES:
            errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} has invalid audience")
        for task_id in _id_references(artifact.get("task_ids", []), f"{artifact_label} task_ids", errors):
            if task_id not in task_ids:
                errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} references unknown task {task_id}")
            elif not _is_nonempty(module_id) or module_id not in task_owners.get(task_id, set()):
                errors.append(f"{artifact_label} module does not own task {task_id}")
            elif artifact.get("audience") in (
                ("teacher", "shared") if task_id in oral_tasks else ("student", "shared")
            ):
                delivered_tasks.add(task_id)
            referenced_task_ids.add(task_id)
        for source_id in _id_references(artifact.get("source_ids", []), f"{artifact_label} source_ids", errors):
            if source_id not in source_ids:
                errors.append(f"artifact {artifact.get('artifact_id', '<unknown>')} references unknown source {source_id}")
    for task_id in sorted(task_ids - referenced_task_ids):
        errors.append(f"task {task_id} is not referenced by any artifact")
    for task_id in sorted(task_ids - delivered_tasks):
        required_audience = "teacher/shared" if task_id in oral_tasks else "student/shared"
        errors.append(f"task {task_id} requires a {required_audience} artifact from an owning module")
    for module_id in sorted(required_modules - artifact_modules):
        errors.append(f"required module {module_id} requires at least one primary artifact")

    criteria = _as_list(manifest.get("criteria"), "criteria", errors)
    _unique_ids(criteria, "criterion_id", "criterion", errors)
    for criterion in criteria:
        if not isinstance(criterion, dict):
            errors.append("criterion must be an object")
            continue
        criterion_label = f"criterion {criterion.get('criterion_id', '<unknown>')}"
        for task_id in _id_references(criterion.get("task_ids", []), f"{criterion_label} task_ids", errors):
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
        _validate_paths_and_content(
            manifest, artifacts, Path(base_dir), errors, generated=stage == "generated",
            check_anchor=stage == "generated" and len(active_modules) >= 2, skills_roots=skills_roots,
        )
    return errors


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        return json.loads(read_utf8_bounded(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a class-total-package manifest")
    parser.add_argument("manifest", type=Path, help="manifest JSON path")
    parser.add_argument("--base-dir", type=Path, help="artifact root; defaults to manifest parent")
    parser.add_argument("--stage", choices=("generated", "design"), default="generated",
                        help="requested deliverable stage; use design for an explicit plan-only request")
    parser.add_argument("--skills-root", type=Path, action="append",
                        help="trusted installed skills directory; repeat for multiple locations")
    args = parser.parse_args(argv)
    try:
        manifest = _load_manifest(args.manifest)
    except (OSError, ValueError, RecursionError) as exc:
        print(f"FAIL: {exc}")
        return 1
    base_dir = args.base_dir or args.manifest.parent
    errors = validate_manifest(manifest, base_dir, expected_stage=args.stage, skills_roots=args.skills_root)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {args.stage} package {args.manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
