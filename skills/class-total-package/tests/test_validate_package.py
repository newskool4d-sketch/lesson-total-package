import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_package import validate_manifest


def make_manifest():
    return {
        "schema_version": "1.0",
        "package_id": "fixture-science-001",
        "output_mode": "수업형",
        "context": {
            "topic": "생태계의 상호작용",
            "subject": "과학",
            "school_level": "중학교",
            "grade_band": "중학교 1-3학년군",
            "duration_minutes": 45,
        },
        "standard": {
            "code": "[9과03-01]",
            "text": "생태계 구성 요소의 상호작용을 설명한다.",
            "status": "verified",
            "source": "https://ncic.re.kr/example",
        },
        "anchor": {
            "topic": "생태계의 상호작용",
            "grade_band": "중학교 1-3학년군",
            "subject": "과학",
            "objective": "생태계 구성 요소의 상호작용을 근거와 함께 설명한다.",
            "essential_question": "생태계 구성 요소는 어떻게 서로 영향을 주는가?",
            "key_concepts": ["생태계", "상호작용"],
            "student_actions": ["관찰한다", "비교한다", "설명한다"],
            "final_artifact": "근거 기반 설명문",
            "evaluation_points": ["관찰 근거", "상호작용 설명"],
        },
        "learner_profile": {
            "mode": "default",
            "supports": [],
            "reading_access": "학년 수준의 짧은 문장과 용어 풀이",
            "udl_defaults": ["핵심 용어 풀이", "관찰 기록표", "설명 문장 틀"],
            "grouping_basis": "이번 수업의 관찰 기록과 출구 ticket",
            "regrouping_rule": "출구 ticket 근거로 다음 차시에 재편성한다.",
            "no_ability_labels": True,
            "cognitive_demand_preserved": True,
            "scaffold_fade": True,
        },
        "pedagogy_profile": {
            "subject": "과학",
            "non_negotiables": ["관찰·조사 후 설명", "증거 기반 모델 수정"],
            "selected_checks": ["관찰 증거", "상호작용 설명"],
        },
        "modules": [
            {"module_id": "board-writing-generator", "active": True, "required": True},
            {"module_id": "html-worksheet-generator", "active": True, "required": True},
            {"module_id": "pbl-lesson-designer", "active": False, "required": False},
        ],
        "tasks": [
            {
                "task_id": "task-observe",
                "phase": "탐구",
                "student_action": "관찰 결과를 비교한다.",
                "evidence": "관찰 기록표",
                "minutes": 20,
                "module_owners": ["board-writing-generator", "html-worksheet-generator"],
            },
            {
                "task_id": "task-exit",
                "phase": "정리",
                "student_action": "상호작용을 근거와 함께 설명한다.",
                "evidence": "출구 ticket",
                "minutes": 25,
                "module_owners": ["html-worksheet-generator"],
            },
        ],
        "sources": [
            {
                "source_id": "source-textbook",
                "type": "textbook",
                "location": "fixture-source.pdf",
                "verification_status": "verified",
                "copyright_status": "cleared",
            }
        ],
        "artifacts": [
            {
                "artifact_id": "artifact-board",
                "module_id": "board-writing-generator",
                "audience": "teacher",
                "required": True,
                "path": "artifacts/01_board.md",
                "task_ids": ["task-observe"],
                "source_ids": ["source-textbook"],
            },
            {
                "artifact_id": "artifact-worksheet",
                "module_id": "html-worksheet-generator",
                "audience": "student",
                "required": True,
                "path": "artifacts/03_worksheet.md",
                "task_ids": ["task-observe", "task-exit"],
                "source_ids": ["source-textbook"],
            },
        ],
        "criteria": [
            {
                "criterion_id": "criterion-evidence",
                "task_ids": ["task-observe", "task-exit"],
                "evidence_required": "관찰 근거와 설명",
                "feedback_use": "다음 수업의 재설명 자료",
            }
        ],
        "safety": {
            "pii_check": "passed",
            "ai_verification_required": False,
            "license_notice_required": False,
        },
    }


class ValidateManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        (self.base_dir / "artifacts").mkdir()
        (self.base_dir / "artifacts/01_board.md").write_text("교사용 판서안", encoding="utf-8")
        (self.base_dir / "artifacts/03_worksheet.md").write_text("학생 활동지", encoding="utf-8")
        (self.base_dir / "fixture-source.pdf").write_bytes(b"fixture")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_manifest_has_no_errors(self):
        self.assertEqual(validate_manifest(make_manifest(), self.base_dir), [])

    def test_orphan_task_and_inactive_module_are_rejected(self):
        manifest = make_manifest()
        manifest["tasks"].append(
            {
                "task_id": "task-orphan",
                "phase": "확장",
                "student_action": "추가 조사한다.",
                "evidence": "메모",
                "minutes": 0,
                "module_owners": ["pbl-lesson-designer"],
            }
        )
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("duration" in error for error in errors))
        self.assertTrue(any("not active" in error for error in errors))
        self.assertTrue(any("not referenced" in error for error in errors))

    def test_unverified_standard_requires_confirmation_marker(self):
        manifest = make_manifest()
        manifest["standard"] = {
            "code": "[9과03-01]",
            "text": "생태계 구성 요소의 상호작용을 설명한다.",
            "status": "pending",
            "source": "",
        }
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("confirmation" in error for error in errors))

    def test_student_artifact_and_source_license_gates_are_enforced(self):
        manifest = make_manifest()
        manifest["artifacts"][1]["path"] = "artifacts/student_with_pii.md"
        (self.base_dir / "artifacts/student_with_pii.md").write_text(
            "교사 메모 학생 연락처 test@example.com", encoding="utf-8"
        )
        manifest["sources"][0]["copyright_status"] = "attribution_required"
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("teacher-only" in error for error in errors))
        self.assertTrue(any("PII" in error for error in errors))
        self.assertTrue(any("attribution" in error for error in errors))

    def test_learner_profile_and_subject_pedagogy_contract_are_required(self):
        manifest = make_manifest()
        manifest.pop("learner_profile")
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("learner_profile" in error for error in errors))

        manifest = make_manifest()
        manifest["pedagogy_profile"]["subject"] = "수학"
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("pedagogy_profile.subject" in error for error in errors))

    def test_student_ability_labels_are_rejected(self):
        manifest = make_manifest()
        path = self.base_dir / "artifacts/03_worksheet.md"
        path.write_text("학생 활동지 보충반", encoding="utf-8")
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("ability label" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
