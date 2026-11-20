import json
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.validate_package import main, validate_manifest


FIXTURES = Path(__file__).resolve().parents[1] / "evals" / "fixtures"


def example():
    return json.loads((FIXTURES / "package-manifest.valid.json").read_text(encoding="utf-8"))


class DeliveryAndEvidenceTests(unittest.TestCase):
    def test_exit_task_must_reach_students_through_its_owner(self):
        course = example()
        board, worksheet = course["artifacts"]
        worksheet["task_ids"].remove("task-exit")
        board["task_ids"].append("task-exit")
        errors = validate_manifest(course)
        self.assertTrue(any("does not own task task-exit" in e for e in errors), errors)
        self.assertTrue(any("task-exit requires a student/shared" in e for e in errors), errors)
        course["tasks"][1]["module_owners"].append(board["module_id"])
        self.assertTrue(any("task-exit requires a student/shared" in e for e in validate_manifest(course)))
        board["audience"] = "shared"
        self.assertEqual(validate_manifest(course), [])

    def test_oral_delivery_has_a_teacher_prompt_and_teacher_material(self):
        course = example()
        exit_task = course["tasks"][1]
        board, sheet = course["artifacts"]
        exit_task.update(delivery="teacher-oral", module_owners=[board["module_id"]])
        sheet["task_ids"].remove("task-exit")
        board["task_ids"].append("task-exit")
        self.assertTrue(any("requires oral_prompt" in e for e in validate_manifest(course)))
        exit_task["oral_prompt"] = "두 관찰 중 어느 쪽이 설명을 지지하나요?"
        self.assertEqual(validate_manifest(course), [])
        board["audience"] = "student"
        self.assertTrue(any("task-exit requires a teacher/shared" in e for e in validate_manifest(course)))

    def test_pending_status_requires_both_a_display_marker_and_a_boolean(self):
        course = example()
        for fields in ({"confirmation_required": True}, {"text": "확인 필요"},
                       {"code": "확인 필요", "confirmation_required": "true"}):
            with self.subTest(fields=fields):
                course["standard"] = {"status": "pending", **fields}
                self.assertTrue(any("pending standard" in e for e in validate_manifest(course)))
        course["standard"] = {"status": "pending", "code": "확인 필요", "confirmation_required": True}
        self.assertEqual(validate_manifest(course), [])

    def test_non_mcp_evidence_supports_both_confirmed_states(self):
        for status in ("verified", "user-provided"):
            with self.subTest(status=status):
                course = example()
                course["curriculum_adapter"] = "none"
                standard = course["standard"]
                standard["status"] = status
                self.assertEqual(validate_manifest(course), [])
                for field in ("code", "text", "source"):
                    with self.subTest(field=field):
                        saved = standard.pop(field)
                        self.assertIn(f"{status} standard requires {field}", validate_manifest(course))
                        standard[field] = saved

    def test_source_location_kinds_and_legacy_binary_file(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            course = example()
            # The design stage lets this test isolate source validation.
            course["deliverable_stage"] = "design"
            for index, artifact in enumerate(course["artifacts"]):
                artifact["path"] = f"plan-{index}.md"
                (base / artifact["path"]).write_text("수업 구성안", encoding="utf-8")
            source = course["sources"][0]
            def check():
                return validate_manifest(course, base, expected_stage="design")
            source.pop("location_kind", None)
            source["location"] = "원자료.pdf"
            self.assertTrue(any("source file not found" in e for e in check()))
            (base / source["location"]).touch()
            self.assertTrue(any("empty packaged file" in e for e in check()))
            (base / source["location"]).write_bytes(b"%PDF-1.7\n%\xff")
            self.assertEqual(check(), [])
            source.update(location_kind="packaged", location="누락.pdf")
            self.assertTrue(any("source file not found" in e for e in check()))
            source.update(location_kind="teacher-held", location="지도서 10~12쪽")
            self.assertEqual(check(), [])
            source.update(location_kind="external", location="누락.pdf")
            self.assertTrue(any("HTTP(S)" in e for e in check()))
            source["location"] = "https://example.org/curriculum"
            self.assertEqual(check(), [])
            source.pop("location_kind")
            self.assertEqual(check(), [])

    def test_stage_matches_request_and_supplement_cannot_replace_primary(self):
        course = example()
        course["deliverable_stage"] = "design"
        self.assertTrue(any("requested stage" in e for e in validate_manifest(course)))
        self.assertEqual(validate_manifest(course, expected_stage="design"), [])
        course["artifacts"][1]["artifact_role"] = "supplement"
        self.assertTrue(any("required module html-worksheet-generator" in e
                            for e in validate_manifest(course, expected_stage="design")))

    def test_two_required_modules_cannot_claim_the_same_file(self):
        course = example()
        course["artifacts"][0]["path"] = course["artifacts"][1]["path"]
        errors = validate_manifest(course, FIXTURES)
        self.assertTrue(any("duplicate primary artifact file" in e for e in errors), errors)

    def test_anchor_identity_agrees_with_lesson_context(self):
        for field in ("topic", "subject", "grade_band"):
            with self.subTest(field=field):
                course = example()
                course["anchor"][field] = "다른 수업"
                self.assertIn(f"anchor.{field} must match context.{field}", validate_manifest(course))

    def test_actual_files_must_agree_on_legacy_unit(self):
        course = example()
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            for artifact in course["artifacts"]:
                relative = artifact["path"]
                text = (FIXTURES / relative).read_text(encoding="utf-8")
                if artifact["audience"] == "teacher":
                    text = text.replace("교과·단원: 과학", "교과·단원: 과학 / 다른 단원")
                target = base / relative
                target.parent.mkdir(exist_ok=True)
                target.write_text(text, encoding="utf-8")
            (base / "fixture-source.txt").write_bytes(b"observations")
            errors = validate_manifest(course, base)
            self.assertTrue(any("03_worksheet.html" in e and "anchor" in e for e in errors), errors)

    def test_cli_design_cannot_be_presented_as_generated(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            course = example()
            course["deliverable_stage"] = "design"
            for index, artifact in enumerate(course["artifacts"]):
                artifact["path"] = f"part-{index}.md"
                (base / artifact["path"]).write_text("수업 구성안", encoding="utf-8")
            (base / "fixture-source.txt").write_bytes(b"observations")
            manifest_path = base / "package-manifest.json"
            manifest_path.write_text(json.dumps(course), encoding="utf-8")
            with redirect_stdout(out := io.StringIO()):
                self.assertEqual(main([str(manifest_path)]), 1)
            self.assertIn("requested stage", out.getvalue())
            with redirect_stdout(out := io.StringIO()):
                self.assertEqual(main([str(manifest_path), "--stage", "design"]), 0)
            self.assertIn("PASS: design", out.getvalue())

    def test_cli_uses_same_trusted_skill_roots_as_preflight(self):
        with TemporaryDirectory() as empty_install:
            with redirect_stdout(out := io.StringIO()):
                code = main([str(FIXTURES / "package-manifest.valid.json"),
                             "--skills-root", empty_install])
            self.assertEqual(code, 1)
            self.assertIn("html-worksheet-generator", out.getvalue())
