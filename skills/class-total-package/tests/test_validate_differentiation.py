import tempfile
import unittest
import json
from pathlib import Path

from scripts.validate_differentiation import validate_differentiation


def make_manifest():
    return {
        "schema_version": "1.0",
        "differentiation_id": "diff-fixture-001",
        "source_package_id": "fixture-science-001",
        "subject": "과학",
        "grade_band": "중학교 1-3학년군",
        "standard": {"code": "[9과03-01]", "status": "verified"},
        "shared_context": "연못 생태계의 상호작용",
        "shared_objective": "생태계 구성 요소의 상호작용을 근거와 함께 설명한다.",
        "core_task_ids": ["task-observe", "task-exit"],
        "tiers": [
            {
                "tier_id": "support",
                "teacher_label": "지원 프로필",
                "student_label": "활동지 1",
                "task_ids": ["task-observe", "task-exit"],
                "scaffolds": ["관찰 기록표", "설명 문장 틀"],
                "scaffold_fade": True,
                "extension_task_ids": [],
            },
            {
                "tier_id": "core",
                "teacher_label": "기본 프로필",
                "student_label": "활동지 2",
                "task_ids": ["task-observe", "task-exit"],
                "scaffolds": ["핵심 용어 풀이"],
                "scaffold_fade": True,
                "extension_task_ids": [],
            },
            {
                "tier_id": "extension",
                "teacher_label": "확장 프로필",
                "student_label": "활동지 3",
                "task_ids": ["task-observe", "task-exit"],
                "scaffolds": ["핵심 용어 풀이"],
                "scaffold_fade": True,
                "extension_task_ids": ["task-transfer"],
            },
        ],
        "grouping": {
            "basis": "이번 수업의 관찰 기록과 출구 ticket",
            "revisable": True,
        },
        "artifacts": [
            {"artifact_id": "support-sheet", "tier_id": "support", "audience": "student", "path": "artifacts/support.md", "task_ids": ["task-observe", "task-exit"]},
            {"artifact_id": "core-sheet", "tier_id": "core", "audience": "student", "path": "artifacts/core.md", "task_ids": ["task-observe", "task-exit"]},
            {"artifact_id": "extension-sheet", "tier_id": "extension", "audience": "student", "path": "artifacts/extension.md", "task_ids": ["task-observe", "task-exit", "task-transfer"]},
        ],
        "safety": {"pii_check": "passed", "no_ability_labels": True},
    }


class ValidateDifferentiationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        (self.base_dir / "artifacts").mkdir()
        for name in ("support", "core", "extension"):
            (self.base_dir / f"artifacts/{name}.md").write_text("학생 활동지", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_differentiation_manifest(self):
        self.assertEqual(validate_differentiation(make_manifest(), self.base_dir), [])

    def test_core_context_and_tasks_must_be_shared(self):
        manifest = make_manifest()
        manifest["tiers"][1]["task_ids"] = ["task-observe"]
        manifest["tiers"][2]["shared_context"] = "다른 맥락"
        errors = validate_differentiation(manifest, self.base_dir)
        self.assertTrue(any("task_ids" in error for error in errors))

    def test_grouping_and_scaffold_fade_are_required(self):
        manifest = make_manifest()
        manifest["grouping"]["revisable"] = False
        manifest["tiers"][0]["scaffold_fade"] = False
        errors = validate_differentiation(manifest, self.base_dir)
        self.assertTrue(any("revisable" in error for error in errors))
        self.assertTrue(any("scaffold_fade" in error for error in errors))

    def test_student_level_labels_are_rejected(self):
        manifest = make_manifest()
        (self.base_dir / "artifacts/support.md").write_text("보충반 활동지", encoding="utf-8")
        errors = validate_differentiation(manifest, self.base_dir)
        self.assertTrue(any("ability label" in error for error in errors))

    def test_every_tier_requires_a_student_artifact(self):
        for tier_id in ("support", "core", "extension"):
            with self.subTest(tier_id=tier_id):
                manifest = make_manifest()
                manifest["artifacts"] = [artifact for artifact in manifest["artifacts"] if artifact["tier_id"] != tier_id]
                errors = validate_differentiation(manifest, self.base_dir)
                self.assertIn(f"tier {tier_id} requires at least one student artifact", errors)

    def test_teacher_and_shared_artifacts_do_not_replace_student_artifacts(self):
        for audience in ("teacher", "shared"):
            with self.subTest(audience=audience):
                manifest = make_manifest()
                manifest["artifacts"][0]["audience"] = audience
                errors = validate_differentiation(manifest, self.base_dir)
                self.assertIn("tier support requires at least one student artifact", errors)
                self.assertTrue(any("tier support student artifacts missing required task_ids" in error for error in errors))

    def test_student_artifacts_must_cover_core_tasks(self):
        for index in range(3):
            for task_ids in ([], ["task-observe"]):
                with self.subTest(tier=index, task_ids=task_ids):
                    manifest = make_manifest()
                    artifact = manifest["artifacts"][index]
                    artifact["task_ids"] = task_ids
                    errors = validate_differentiation(manifest, self.base_dir)
                    self.assertTrue(any(f"tier {artifact['tier_id']} student artifacts missing required task_ids" in error and "task-exit" in error for error in errors))

    def test_student_artifacts_must_cover_extension_tasks(self):
        manifest = make_manifest()
        manifest["artifacts"][2]["task_ids"] = ["task-observe", "task-exit"]
        errors = validate_differentiation(manifest, self.base_dir)
        self.assertIn("tier extension student artifacts missing required task_ids: task-transfer", errors)

    def test_student_task_coverage_can_span_multiple_artifacts(self):
        manifest = make_manifest()
        manifest["artifacts"][2]["task_ids"] = ["task-observe", "task-exit"]
        manifest["artifacts"].append({
            "artifact_id": "extension-transfer-sheet",
            "tier_id": "extension",
            "audience": "student",
            "path": "artifacts/extension-transfer.md",
            "task_ids": ["task-transfer"],
        })
        (self.base_dir / "artifacts/extension-transfer.md").write_text("학생 확장 활동지", encoding="utf-8")
        self.assertEqual(validate_differentiation(manifest, self.base_dir), [])
        for audience in ("teacher", "shared"):
            with self.subTest(audience=audience):
                manifest["artifacts"][-1]["audience"] = audience
                errors = validate_differentiation(manifest, self.base_dir)
                self.assertIn("tier extension student artifacts missing required task_ids: task-transfer", errors)

    def test_artifact_tasks_must_belong_to_their_tier(self):
        for task_id in ("unknown-task", "task-transfer"):
            for audience in ("student", "teacher", "shared"):
                with self.subTest(task_id=task_id, audience=audience):
                    manifest = make_manifest()
                    manifest["artifacts"][0]["task_ids"].append(task_id)
                    manifest["artifacts"][0]["audience"] = audience
                    errors = validate_differentiation(manifest, self.base_dir)
                    self.assertIn(f"artifact support-sheet has unknown task_ids for tier support: {task_id}", errors)

    def test_invalid_tier_and_task_id_types_return_errors(self):
        for value in (None, {}, [], 7, ""):
            for collection in ("tiers", "artifacts"):
                with self.subTest(field="tier_id", collection=collection, value=value):
                    manifest = make_manifest()
                    manifest[collection][0]["tier_id"] = value
                    self.assertTrue(validate_differentiation(manifest, self.base_dir))
        for value in (None, {}, "task-observe", [None], [{}], [[]], [7], [""]):
            for collection, field in (("tiers", "task_ids"), ("tiers", "extension_task_ids"), ("artifacts", "task_ids")):
                with self.subTest(field=field, collection=collection, value=value):
                    manifest = make_manifest()
                    manifest[collection][0][field] = value
                    errors = validate_differentiation(manifest, self.base_dir)
                    self.assertTrue(any(f"{field} must be a string list" in error for error in errors))

    def test_repository_fixtures_match_expected_outcomes(self):
        fixture_dir = Path(__file__).parents[1] / "evals" / "fixtures"
        for name, expected_empty in (("differentiation.valid.json", True), ("differentiation.invalid.json", False)):
            path = fixture_dir / name
            manifest = json.loads(path.read_text(encoding="utf-8"))
            errors = validate_differentiation(manifest, fixture_dir)
            self.assertEqual(errors == [], expected_empty, name)


if __name__ == "__main__":
    unittest.main()
