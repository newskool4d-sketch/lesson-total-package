import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import check_module_dependencies as dependencies


BOARD = "board-writing-generator"
MINDMAP = "mindmap-html-generator"
WORKSHEET = "html-worksheet-generator"
ASSESSMENT = "inquiry-report-assessment"


class RoutingDependencyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.skill_root = Path(temporary.name)

    def install(self, module, root=None):
        folder = (root or self.skill_root) / module
        for relative in ("SKILL.md", *dependencies.MODULE_REQUIREMENTS[module]):
            path = folder / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return folder

    def check(self, *args):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            status = dependencies.main(["--skills-root", str(self.skill_root), *args])
        return status, stdout.getvalue()

    def test_clean_plugin_reports_only_requested_missing_dependencies(self):
        (self.skill_root / "class-total-package").mkdir()
        status, output = self.check(BOARD, WORKSHEET)
        self.assertEqual(status, 1)
        self.assertIn("route: package", output)
        self.assertIn(f"MISSING {BOARD}", output)
        self.assertIn(f"MISSING {WORKSHEET}", output)
        self.assertIn("verify_html_worksheet.py", output)
        self.assertIn("--skills-root", output)
        self.assertNotIn(ASSESSMENT, output)

    def test_single_assessment_with_multiple_handouts_routes_directly(self):
        self.install(ASSESSMENT)
        status, output = self.check(ASSESSMENT)
        self.assertEqual(status, 0)
        self.assertIn("route: direct", output)
        self.assertIn(f"READY {ASSESSMENT}", output)
        self.assertNotIn("MISSING", output)

    def test_unnamed_concept_package_checks_only_inferred_pair(self):
        self.install(BOARD)
        self.install(MINDMAP)
        status, output = self.check("--infer", BOARD, MINDMAP)
        self.assertEqual(status, 0)
        self.assertIn("route: package", output)
        self.assertEqual(output.count("READY "), 2)
        with self.assertRaises(ValueError):
            dependencies.select_modules([BOARD, BOARD], infer=True)
        self.assertEqual(dependencies.select_modules([BOARD, MINDMAP, ASSESSMENT], infer=True),
                         (BOARD, MINDMAP, ASSESSMENT))

    def test_assessment_only_prompt_belongs_to_direct_examples(self):
        path = Path(__file__).resolve().parents[1] / "references" / "example-prompts.md"
        examples = path.read_text(encoding="utf-8")
        basic, other = examples.split("## Direct-skill handoff examples", 1)
        direct = other.split("## ", 1)[0]
        self.assertNotIn("수행평가만", basic)
        self.assertIn("수행평가만", direct)

    def test_requested_subset_preserves_modules_and_full_checks_all_five(self):
        all_modules = (BOARD, MINDMAP, WORKSHEET, "pbl-lesson-designer", ASSESSMENT)
        for module in all_modules:
            self.install(module)
        status, output = self.check("--full-package")
        self.assertEqual(status, 0)
        self.assertEqual(output.count("READY "), 5)
        for module in all_modules:
            self.assertIn(f"READY {module}", output)
        self.assertEqual(dependencies.select_modules([WORKSHEET, BOARD]), (WORKSHEET, BOARD))
        with self.assertRaises(ValueError):
            dependencies.select_modules(["unknown-generator"])

    def test_partial_module_fails_but_another_complete_installation_works(self):
        partial = self.install(WORKSHEET)
        (partial / dependencies.WORKSHEET_VALIDATOR).unlink()
        status, output = self.check(WORKSHEET)
        self.assertEqual(status, 1)
        self.assertIn(f"MISSING {WORKSHEET}", output)
        another_root = self.skill_root / "other-skills"
        complete = self.install(WORKSHEET, another_root)
        self.assertEqual(dependencies.find_module(WORKSHEET, [self.skill_root, another_root]), complete)

    def test_default_roots_include_configured_codex_home(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.skill_root)}):
            self.assertIn(self.skill_root / "skills", dependencies.default_skill_roots())


if __name__ == "__main__":
    unittest.main()
