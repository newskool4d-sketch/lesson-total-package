import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_differentiation import validate_differentiation
from scripts.validate_package import validate_manifest
from scripts.validation_common import audience_content_errors, safety_views


class AudiencePolicyTests(unittest.TestCase):
    def test_teacher_sections_in_student_and_shared_material(self):
        headings = (
            "교사용 판서안",
            "## 교사 관찰 메모",
            "## 학생 관찰 기록",
            "# 정답",
            "<h2>정답·해설</h2>",
            "**모범 답안**: 두 조건의 차이를 비교했다.",
        )
        for heading in headings:
            for audience in ("student", "shared"):
                with self.subTest(heading=heading, audience=audience):
                    problems = audience_content_errors(audience, safety_views(heading), "notes.md")
                    self.assertEqual(problems, [f"teacher-only content in {audience} artifact notes.md"])

    def test_student_observation_and_answer_prompts_are_allowed(self):
        content = ("## 나의 관찰 기록\n관찰 기록표에 모종의 변화를 적으세요.\n"
                   "정답을 정한 이유를 설명하세요.\n정답: ____\n예시 답안을 비교해 보세요.")
        for audience in ("student", "shared"):
            self.assertEqual(audience_content_errors(audience, safety_views(content), "activity.md"), [])

    def test_teacher_and_student_uses_of_labels(self):
        views = safety_views("<h2>교사용 판서안</h2><p>보충반</p>")
        self.assertEqual(audience_content_errors("teacher", views, "plan.html"), [])
        for audience in ("student", "shared"):
            self.assertIn(f"student ability label in {audience} artifact plan.html",
                          audience_content_errors(audience, views, "plan.html"))

    def test_both_validators_reject_teacher_section_in_student_and_shared_files(self):
        fixtures = Path(__file__).resolve().parents[1] / "evals" / "fixtures"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            shutil.copytree(fixtures, root)
            cases = (("package-manifest.valid.json", validate_manifest),
                     ("differentiation.valid.json", validate_differentiation))
            for name, validate in cases:
                manifest = json.loads((root / name).read_text(encoding="utf-8"))
                student_file = next(a for a in manifest["artifacts"] if a["audience"] == "student")
                path = root / student_file["path"]
                content = path.read_text(encoding="utf-8")
                if path.suffix == ".html":
                    edited = content.replace("</body>", "<h2>교사 관찰 메모</h2></body>")
                    self.assertNotEqual(edited, content)
                else:
                    edited = content + "\n## 교사 관찰 메모\n"
                path.write_text(edited, encoding="utf-8")
                for audience in ("student", "shared"):
                    with self.subTest(manifest=name, audience=audience):
                        student_file["audience"] = audience
                        problems = validate(manifest, root)
                        self.assertIn(f"teacher-only content in {audience} artifact {student_file['path']}", problems)


if __name__ == "__main__":
    unittest.main()
