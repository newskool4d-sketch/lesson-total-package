"""Synthetic regressions for the six adversarial review findings."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_differentiation import validate_differentiation
from scripts.validate_package import validate_manifest
from scripts.validation_common import (
    MAX_FILE_BYTES, MAX_MANIFEST_CHARS, MAX_MANIFEST_NODES, contains_pii,
)
from tests.test_validate_differentiation import make_manifest as differentiation_manifest
from tests.test_validate_package import FIXTURES, copy_package_fixtures, make_manifest as package_manifest


ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = (
    ("package", package_manifest, validate_manifest, "validate_package.py"),
    ("differentiation", differentiation_manifest, validate_differentiation, "validate_differentiation.py"),
)


class SecurityRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / "package"
        self.base.mkdir()
        for _, factory, _, _ in VALIDATORS:
            for artifact in factory()["artifacts"]:
                path = self.base / artifact["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("학생 활동 자료", encoding="utf-8")
        copy_package_fixtures(self.base)

    def cli(self, manifest, script):
        path = self.base / "manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / script), str(path)],
            capture_output=True, encoding="utf-8", errors="replace", timeout=10,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, cwd=ROOT,
        )

    def test_manifest_pii_in_nested_keys_and_values_is_not_echoed(self):
        for name, factory, validate, script in VALIDATORS:
            for value in ("fixture@example.invalid", "000000-1000000", "010-0000-0000"):
                for payload in ({"nested": [value]}, {value: "synthetic"}):
                    with self.subTest(validator=name, payload=payload):
                        manifest = factory()
                        manifest["extra"] = payload
                        manifest["artifacts"][0]["artifact_id"] = value
                        manifest["artifacts"][0]["audience"] = "invalid"
                        self.assertEqual(validate(manifest), ["PII detected in manifest"])
                        result = self.cli(manifest, script)
                        self.assertEqual(result.returncode, 1)
                        self.assertNotIn(value, result.stdout + result.stderr)
                        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_resident_number_in_artifacts_is_rejected_by_both_validators(self):
        for name, factory, validate, _ in VALIDATORS:
            with self.subTest(validator=name):
                manifest = factory()
                (self.base / manifest["artifacts"][0]["path"]).write_text("000000-1000000", encoding="utf-8")
                self.assertTrue(any("PII" in error for error in validate(manifest, self.base)))

    def test_html_entities_attributes_and_inline_text_are_checked(self):
        contents = (
            "<p>fixture&#64;example.invalid</p>",
            "<p>fixture<span>@</span>example.invalid</p>",
            '<a href="mailto:fixture&#x40;example.invalid">연락</a>',
            '<img alt="fixture&#64;example.invalid">',
            "<p>010<span>-0000</span>-0000</p>",
            "<p>000000<b>-1000000</b></p>",
            "<p>fixture<script>const n = 1;</script>@example.invalid</p>",
        )
        for name, factory, validate, _ in VALIDATORS:
            for content in contents:
                with self.subTest(validator=name, content=content):
                    manifest = factory()
                    path = self.base / manifest["artifacts"][0]["path"]
                    path.write_text(content, encoding="utf-8")
                    self.assertTrue(any("PII" in error for error in validate(manifest, self.base)))

    def test_student_content_gates_check_decoded_inline_text(self):
        manifest = package_manifest()
        path = self.base / manifest["artifacts"][1]["path"]
        for content in ("<p>교<span>사</span> 메모</p>", "<p>&#44368;사용</p>"):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                self.assertTrue(any("teacher-only" in error for error in validate_manifest(manifest, self.base)))
        for name, factory, validate, _ in VALIDATORS:
            with self.subTest(validator=name):
                manifest = factory()
                artifact = next(item for item in manifest["artifacts"] if item["audience"] == "student")
                (self.base / artifact["path"]).write_text("<p>하위 <b>수준</b></p>", encoding="utf-8")
                self.assertTrue(any("ability label" in error for error in validate(manifest, self.base)))

    def test_implicit_head_end_does_not_hide_body_safety_checks(self):
        for name, factory, validate, _ in VALIDATORS:
            contents = [("fixture<span>@</span>example.invalid", "PII"),
                        ("하위 <b>수준</b>", "ability label")]
            if name == "package":
                contents.append(("교<span>사</span> 메모", "teacher-only"))
            for content, expected in contents:
                for body_tag in ("<body>", ""):
                    with self.subTest(validator=name, expected=expected, body_tag=body_tag):
                        manifest = factory()
                        artifact = next(item for item in manifest["artifacts"] if item["audience"] == "student")
                        (self.base / artifact["path"]).write_text(
                            f"<html><head><title>자료</title>{body_tag}<p>{content}</p></html>", encoding="utf-8")
                        self.assertTrue(any(expected in error for error in validate(manifest, self.base)))

    def test_path_forms_cannot_escape_package_root(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("외부 합성 자료", encoding="utf-8")
        paths = (str(outside), r"\outside.txt", r"C:outside.txt", r"D:outside.txt",
                 r"\\server\share\file.txt", r"\\?\C:\outside.txt", "../outside.txt", r"..\outside.txt")
        if os.name == "nt":
            paths += (str(outside)[2:],)
        for name, factory, validate, _ in VALIDATORS:
            for path in paths:
                with self.subTest(validator=name, path=path):
                    manifest = factory()
                    manifest["artifacts"][0]["path"] = path
                    self.assertTrue(any("escapes package root" in error for error in validate(manifest, self.base)))

    def test_link_to_external_directory_is_rejected(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "data.txt").write_text("외부 합성 자료", encoding="utf-8")
        link = self.base / "linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                self.skipTest("directory symlinks unavailable")
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
            if result.returncode:
                self.skipTest("symlinks and junctions unavailable")
        self.addCleanup(lambda: link.unlink() if link.is_symlink() else link.rmdir())
        for name, factory, validate, _ in VALIDATORS:
            with self.subTest(validator=name):
                manifest = factory()
                manifest["artifacts"][0]["path"] = "linked/data.txt"
                self.assertTrue(any("escapes package root" in error for error in validate(manifest, self.base)))

    def test_metadata_only_validation_does_not_read_artifacts(self):
        for name, factory, validate, _ in VALIDATORS:
            with self.subTest(validator=name):
                manifest = factory()
                manifest["artifacts"][0]["path"] = "missing/file.txt"
                self.assertEqual(validate(manifest), [])

    def test_invalid_enum_types_return_errors_in_api_and_cli(self):
        fields = (("output_mode",), ("standard", "status"), ("learner_profile", "mode"),
                  ("sources", 0, "verification_status"), ("sources", 0, "copyright_status"),
                  ("artifacts", 0, "audience"))
        for name, factory, validate, script in VALIDATORS:
            for field in (fields if name == "package" else (("standard", "status"),)):
                for bad_value in ([], {}, None):
                    with self.subTest(validator=name, field=field, value=bad_value):
                        manifest = factory()
                        target = manifest
                        for part in field[:-1]:
                            target = target[part]
                        target[field[-1]] = copy.deepcopy(bad_value)
                        self.assertTrue(validate(manifest, self.base))
                        result = self.cli(manifest, script)
                        self.assertEqual(result.returncode, 1)
                        self.assertIn("FAIL:", result.stdout)
                        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_required_modules_must_be_active_and_have_artifacts(self):
        for change in ("add-required", "remove-board", "inactive-required"):
            with self.subTest(change=change):
                manifest = package_manifest()
                if change == "add-required":
                    manifest["modules"].append({"module_id": "mindmap-html-generator", "active": True, "required": True})
                elif change == "remove-board":
                    manifest["artifacts"] = manifest["artifacts"][1:]
                else:
                    manifest["modules"][2]["required"] = True
                self.assertTrue(any("required module" in error for error in validate_manifest(manifest, self.base)))

    def test_optional_module_without_artifacts_remains_valid(self):
        manifest = package_manifest()
        manifest["modules"].append({"module_id": "mindmap-html-generator", "active": True, "required": False})
        self.assertEqual(validate_manifest(manifest, self.base), [])

    def test_required_module_flag_must_be_boolean(self):
        for value in ("true", 1, [], {}):
            with self.subTest(value=value):
                manifest = package_manifest()
                manifest["modules"][0]["required"] = value
                self.assertIn("module.required must be boolean", validate_manifest(manifest, self.base))

    def test_long_email_near_misses_finish_within_bounded_time(self):
        for suffix in ("", "@incomplete"):
            with self.subTest(suffix=suffix):
                result = subprocess.run(
                    [sys.executable, "-B", "-c", "from scripts.validate_package import _contains_pii; "
                     f"assert not _contains_pii('a.' * 100_000 + {suffix!r})"],
                    cwd=ROOT, capture_output=True, timeout=3,
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

    def test_email_variants_and_late_email_are_detected(self):
        for text in (".fixture@example.invalid", "+fixture@example.invalid.",
                     "fixture+demo@sub.example.invalid", "한글_예시@example.invalid",
                     "fixture@1.2.3", "a." * 100_000 + " fixture@example.invalid"):
            with self.subTest(text=text[:60]):
                self.assertTrue(contains_pii(text))

    def test_encoded_manifest_pii_is_rejected_without_echo(self):
        for name, factory, validate, _ in VALIDATORS:
            for value in ("fixture&#64;example.invalid", "fixture<b>@</b>example.invalid"):
                with self.subTest(validator=name, value=value):
                    manifest = factory()
                    manifest["extra"] = {value: "synthetic"}
                    self.assertEqual(validate(manifest), ["PII detected in manifest"])

    def test_cdn_exception_is_shared_and_limited_to_exact_version(self):
        urls = ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/icons.css",
                "https://cdn.jsdelivr.net/npm/@scope/package@1.2.3/style.css")
        for name, factory, validate, _ in VALIDATORS:
            for url in urls:
                with self.subTest(validator=name, url=url):
                    manifest = factory()
                    path = self.base / manifest["artifacts"][0]["path"]
                    manifest["extra"] = url
                    relative = manifest["artifacts"][0]["path"]
                    body = (FIXTURES / relative).read_text(encoding="utf-8") if name == "package" else ""
                    path.write_text(body + f'\n<link href="{url}">', encoding="utf-8")
                    self.assertEqual(validate(manifest, self.base), [])
                    for tail in ("?contact=fixture@example.invalid", "/fixture@example.invalid"):
                        path.write_text(f'<link href="{url}{tail}">', encoding="utf-8")
                        self.assertTrue(any("PII" in error for error in validate(manifest, self.base)))

    def test_separate_html_blocks_and_attributes_do_not_create_pii(self):
        contents = (
            "<p>fixture</p><p>@example.invalid</p>",
            '<span data-first="fixture" data-second="@example.invalid">자료</span>',
            "<div>010</div><div>0000</div><div>0000</div>",
            "<p>학생 <b>활동</b> 자료 &amp; 관찰 기록</p>",
            "<html><head><title>fixture</title><body><p>@example.invalid</p></body></html>",
        )
        for name, factory, validate, _ in VALIDATORS:
            for content in contents:
                with self.subTest(validator=name, content=content):
                    manifest = factory()
                    relative = manifest["artifacts"][0]["path"]
                    body = (FIXTURES / relative).read_text(encoding="utf-8") if name == "package" else ""
                    (self.base / relative).write_text(body + "\n" + content, encoding="utf-8")
                    self.assertEqual(validate(manifest, self.base), [])

    def test_manifest_limits_fail_explicitly_instead_of_skipping_checks(self):
        deep = "safe"
        for _ in range(80):
            deep = [deep]
        for name, factory, validate, _ in VALIDATORS:
            for extra in ("x" * (MAX_MANIFEST_CHARS + 1), [""] * MAX_MANIFEST_NODES, deep):
                with self.subTest(validator=name, kind=type(extra).__name__):
                    manifest = factory()
                    manifest["extra"] = extra
                    errors = validate(manifest)
                    self.assertEqual(len(errors), 1)
                    self.assertIn("limit", errors[0])

    def test_artifact_size_and_utf8_errors_fail_in_api_and_cli(self):
        for name, factory, validate, script in VALIDATORS:
            for data, expected in ((b"x" * (MAX_FILE_BYTES + 1), "size limit"), (b"\xff", "UTF-8")):
                with self.subTest(validator=name, expected=expected):
                    manifest = factory()
                    (self.base / manifest["artifacts"][0]["path"]).write_bytes(data)
                    self.assertTrue(any(expected in error for error in validate(manifest, self.base)))
                    result = self.cli(manifest, script)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(expected, result.stdout)
                    self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_manifest_file_size_and_encoding_errors_have_clean_cli_failure(self):
        path = self.base / "oversized.json"
        for data in (b"x" * (MAX_FILE_BYTES + 1), b"\xff", b"[" * 2000 + b"]" * 2000):
            path.write_bytes(data)
            for name, _, _, script in VALIDATORS:
                with self.subTest(validator=name, size=len(data)):
                    result = subprocess.run(
                        [sys.executable, "-B", str(ROOT / "scripts" / script), str(path)],
                        capture_output=True, timeout=10, cwd=ROOT,
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(b"FAIL:", result.stdout)
                    self.assertNotIn(b"Traceback", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
