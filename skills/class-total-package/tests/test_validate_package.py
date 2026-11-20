import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_package import validate_manifest


VERSIONED_ICON_CSS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"


FIXTURES = Path(__file__).resolve().parents[1] / "evals" / "fixtures"


def make_manifest():
    return json.loads((FIXTURES / "package-manifest.valid.json").read_text(encoding="utf-8"))


def copy_package_fixtures(base):
    manifest = make_manifest()
    for relative in [a["path"] for a in manifest["artifacts"]] + ["fixture-source.txt"]:
        path = base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((FIXTURES / relative).read_bytes())


class ValidateManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        copy_package_fixtures(self.base_dir)

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

    def test_manifest_pii_is_rejected_without_echoing_the_value(self):
        manifest = make_manifest()
        manifest["learner_profile"]["supports"].append("fixture@example.test")
        self.assertEqual(validate_manifest(manifest), ["PII detected in manifest"])

    def test_versioned_cdn_stylesheet_is_not_treated_as_email(self):
        manifest = make_manifest()
        manifest["artifacts"][1]["path"] = "artifacts/student.html"
        worksheet = (FIXTURES / "artifacts/03_worksheet.html").read_text(encoding="utf-8")
        (self.base_dir / "artifacts/student.html").write_text(
            worksheet.replace("</head>", f'<link rel="stylesheet" href="{VERSIONED_ICON_CSS}"></head>'),
            encoding="utf-8",
        )
        self.assertEqual(validate_manifest(manifest, self.base_dir), [])

    def test_versioned_cdn_stylesheet_does_not_hide_emails(self):
        manifest = make_manifest()
        manifest["artifacts"][1]["path"] = "artifacts/student.html"
        stylesheet = f'<link rel="stylesheet" href="{VERSIONED_ICON_CSS}">'
        address = "student.fixture+demo@example.test"
        cases = {
            "visible text": f"{stylesheet}<p>{address}</p>",
            "mailto": f'{stylesheet}<a href="mailto:{address}">연락처</a>',
            "same URL query": f'<link rel="stylesheet" href="{VERSIONED_ICON_CSS}?contact={address}">',
            "same URL path": f'<link rel="stylesheet" href="{VERSIONED_ICON_CSS}/{address}">',
            "in place of version": f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/{address}/style.css">',
            "version-like email in text": f"{stylesheet}<p>fixture@1.2.3</p>",
        }
        for context, content in cases.items():
            with self.subTest(context=context):
                (self.base_dir / "artifacts/student.html").write_text(content, encoding="utf-8")
                self.assertEqual(
                    validate_manifest(manifest, self.base_dir),
                    ["PII detected in artifact artifacts/student.html"],
                )

    def test_reference_fields_reject_wrong_shapes(self):
        cases = (
            ("tasks", "module_owners", "pbl-lesson-designer"),
            ("artifacts", "source_ids", "missing-source"),
            ("artifacts", "task_ids", [["task-observe"]]),
            ("criteria", "task_ids", None),
        )
        for section, field, value in cases:
            with self.subTest(section=section, field=field):
                manifest = make_manifest()
                manifest[section][0][field] = value
                errors = validate_manifest(manifest, self.base_dir)
                self.assertTrue(
                    any(f"{field} must be a list of non-empty strings" in error for error in errors),
                    errors,
                )

    def test_top_level_array_rejects_wrong_shape(self):
        manifest = make_manifest()
        manifest["criteria"] = {}
        self.assertIn("criteria must be a list", validate_manifest(manifest, self.base_dir))

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
        path = self.base_dir / manifest["artifacts"][1]["path"]
        path.write_text("학생 활동지 보충반", encoding="utf-8")
        errors = validate_manifest(manifest, self.base_dir)
        self.assertTrue(any("ability label" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
