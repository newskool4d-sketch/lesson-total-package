import copy
import json
import tempfile
import unittest
from html import escape
from pathlib import Path
from unittest.mock import patch

from scripts.artifact_contract import artifact_anchor_signature, artifact_contract_errors


FIXTURES = Path(__file__).resolve().parents[1] / "evals" / "fixtures"
BOARD = FIXTURES / "artifacts/01_board.md"
WORKSHEET = FIXTURES / "artifacts/03_worksheet.html"


class ArtifactContractTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((FIXTURES / "package-manifest.valid.json").read_text(encoding="utf-8"))
        self.board = self.manifest["artifacts"][0]
        self.worksheet = self.manifest["artifacts"][1]
        self.md = BOARD.read_text(encoding="utf-8")
        self.html = WORKSHEET.read_text(encoding="utf-8")

    def test_printable_worksheet_passes_native_verifier(self):
        self.assertEqual(artifact_contract_errors(
            self.manifest, self.worksheet, WORKSHEET, self.html, FIXTURES), [])

    def test_worksheet_requires_actual_html_and_native_success(self):
        errors = artifact_contract_errors(self.manifest, self.worksheet, BOARD, self.md, FIXTURES)
        self.assertTrue(any("requires an HTML" in error for error in errors))
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "worksheet.html"
            content = self.html.replace("window.print()", "void(0)")
            file.write_text(content, encoding="utf-8")
            errors = artifact_contract_errors(self.manifest, self.worksheet, file, content, Path(tmp))
            self.assertIn("native worksheet check failed: window.print", errors)

    def test_missing_worksheet_dependency_fails_with_install_hint(self):
        with patch("scripts.artifact_contract.find_module", return_value=None):
            errors = artifact_contract_errors(self.manifest, self.worksheet, WORKSHEET, self.html, FIXTURES)
        self.assertTrue(any("install html-worksheet-generator" in error for error in errors))

    def test_design_plan_does_not_claim_native_validation(self):
        with patch("scripts.artifact_contract.find_module", side_effect=AssertionError):
            self.assertEqual(artifact_contract_errors(
                self.manifest, self.worksheet, BOARD, self.md, FIXTURES, check_native=False), [])

    def test_absent_or_displaced_anchor_fails_in_both_formats(self):
        cases = [(BOARD, "수업 자료"), (BOARD, "수업 자료\n" + self.md),
                 (WORKSHEET, self.html.replace('<details id="package-anchor">', '<section>소개</section><details id="package-anchor">')),
                 (WORKSHEET, self.html.replace('id="package-anchor"', 'id="different"'))]
        for path, content in cases:
            with self.subTest(path=path):
                errors = artifact_contract_errors(self.manifest, self.board, path, content, FIXTURES)
                self.assertTrue(any("leading package anchor" in error for error in errors))

    def test_manifest_mismatch_is_detected_in_both_formats(self):
        for path, content in ((BOARD, self.md), (WORKSHEET, self.html)):
            with self.subTest(path=path):
                errors = artifact_contract_errors(self.manifest, self.board, path,
                                                  content.replace("중학교 1-3학년군", "고등학교"), FIXTURES)
                self.assertIn("package anchor differs from manifest: grade_band", errors)

    def test_hidden_source_agrees_with_visible_html_and_markdown(self):
        canonical = artifact_anchor_signature(BOARD, self.md)
        template = '<template id="package-anchor-source">' + escape("\n".join(canonical)) + '</template>'
        with_template = self.html.replace("</details>", "</details>" + template)
        self.assertTrue(canonical)
        self.assertEqual(artifact_anchor_signature(WORKSHEET, with_template), canonical)
        self.assertEqual(artifact_anchor_signature(WORKSHEET, with_template.replace(
            "<li>수업 주제: 생태계의 상호작용</li>", "<li>수업 주제: 다른 주제</li>")), ())
        self.assertEqual(artifact_anchor_signature(WORKSHEET, "<body>" + template + "</body>"), ())

    def test_legacy_unit_is_retained_in_cross_artifact_signature(self):
        changed = self.md.replace("교과·단원: 과학", "교과·단원: 과학 / 생태")
        self.assertEqual(artifact_contract_errors(self.manifest, self.board, BOARD, changed, FIXTURES), [])
        self.assertNotEqual(artifact_anchor_signature(BOARD, changed), artifact_anchor_signature(BOARD, self.md))
        explicit_unit = copy.deepcopy(self.manifest)
        explicit_unit["context"]["unit"] = "생태"
        self.assertIn("package anchor differs from manifest: subject",
                      artifact_contract_errors(explicit_unit, self.board, BOARD, self.md, FIXTURES))
