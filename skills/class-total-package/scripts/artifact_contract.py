"""Validate actual lesson outputs against the shared anchor and worksheet contract."""

from __future__ import annotations

import importlib.util
from html.parser import HTMLParser
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote

if __package__:
    from .check_module_dependencies import WORKSHEET_VALIDATOR, default_skill_roots, find_module
else:
    from check_module_dependencies import WORKSHEET_VALIDATOR, default_skill_roots, find_module


ANCHOR_TITLE = "> **[수업 패키지 앵커]**"
FIELDS = (
    ("수업 주제", "topic"), ("학교급·학년군", "grade_band"), ("교과·단원", "subject"),
    ("성취기준", "standard"), ("수업 목표", "objective"), ("핵심 질문", "essential_question"),
    ("핵심 개념", "key_concepts"), ("학생 활동 동사", "student_actions"),
    ("최종 결과물", "final_artifact"), ("평가 포인트", "evaluation_points"),
)
HTML_SUFFIXES = {".html", ".htm"}
WORKSHEET_MODULE = "html-worksheet-generator"


def _markdown_block(text: str) -> tuple[str, ...]:
    lines = text.lstrip("\ufeff\r\n").splitlines()
    if not lines or lines[0] != ANCHOR_TITLE:
        return ()
    length = 1 + len(FIELDS)
    block = tuple(lines[:length])
    if len(block) != length or any(
        not line.startswith(f"> - {label}: ") for line, (label, _) in zip(block[1:], FIELDS)
    ):
        return ()
    return block


class _LessonHTML(HTMLParser):
    """Read the visible leading anchor; a hidden template can only corroborate it."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.hidden_tags: list[str] = []
        self.before_anchor = False
        self.anchor_tags: list[str] = []
        self.anchor_count = 0
        self.item: list[str] | None = None
        self.summary: list[str] | None = None
        self.title = ""
        self.lines: list[str] = []
        self.source: list[str] | None = None
        self.source_blocks: list[str] = []
        self.images: list[str] = []
        self.has_body = False
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs["src"])
        if self.hidden_tags:
            if tag == self.hidden_tags[-1]:
                self.hidden_tags.append(tag)
            return
        if tag == "body":
            self.has_body = True
        if tag == "template" and attrs.get("id") == "package-anchor-source":
            self.source = []
        if tag in {"head", "script", "style", "template", "title"}:
            self.hidden_tags.append(tag)
            return
        if attrs.get("id") == "package-anchor" and tag in {"details", "section", "div"}:
            self.anchor_count += 1
            if "hidden" in attrs or attrs.get("aria-hidden") == "true":
                self.before_anchor = True
            self.anchor_tags.append(tag)
        elif self.anchor_tags:
            if tag == self.anchor_tags[-1]:
                self.anchor_tags.append(tag)
            if tag == "li":
                self.item = []
            elif tag in {"summary", "h1", "h2", "h3"}:
                self.summary = []
        elif not self.anchor_count and tag in {"img", "input", "textarea", "button", "canvas", "svg", "iframe"}:
            self.before_anchor = True

    def handle_endtag(self, tag):
        if self.hidden_tags:
            if tag == self.hidden_tags[-1]:
                self.hidden_tags.pop()
                if tag == "template" and self.source is not None and not self.hidden_tags:
                    self.source_blocks.append("".join(self.source))
                    self.source = None
            return
        if not self.anchor_tags:
            return
        if tag == "li" and self.item is not None:
            self.lines.append("> - " + "".join(self.item))
            self.item = None
        elif tag in {"summary", "h1", "h2", "h3"} and self.summary is not None:
            self.title = "".join(self.summary).strip()
            self.summary = None
        if tag == self.anchor_tags[-1]:
            self.anchor_tags.pop()

    def handle_data(self, data):
        if self.source is not None:
            self.source.append(data)
        if self.hidden_tags:
            return
        if self.item is not None:
            self.item.append(data)
        elif self.summary is not None:
            self.summary.append(data)
        elif not self.anchor_count and data.strip():
            self.before_anchor = True

    def anchor_block(self) -> tuple[str, ...]:
        if self.before_anchor or self.anchor_count != 1 or self.anchor_tags or self.title != "수업 패키지 앵커":
            return ()
        visible = _markdown_block("\n".join((ANCHOR_TITLE, *self.lines)))
        if len(self.lines) != len(FIELDS) or len(self.source_blocks) > 1:
            return ()
        if self.source_blocks and _markdown_block(self.source_blocks[0]) != visible:
            return ()
        return visible


def artifact_anchor_signature(path: Path, content: str) -> tuple[str, ...]:
    """Canonical display lines for equality comparison across selected outputs."""
    if path.suffix.lower() in HTML_SUFFIXES:
        return _LessonHTML(content).anchor_block()
    return _markdown_block(content)


def _anchor_errors(manifest: dict, block: tuple[str, ...]) -> list[str]:
    if not block:
        return ["missing or inconsistent leading package anchor"]
    anchor = manifest.get("anchor")
    context = manifest.get("context")
    standard = manifest.get("standard")
    if not all(isinstance(value, dict) for value in (anchor, context, standard)):
        return ["missing manifest fields for package anchor"]
    errors = []
    for line, (label, field) in zip(block[1:], FIELDS):
        actual = line.removeprefix(f"> - {label}: ")
        expected = anchor.get(field)
        if field == "subject":
            unit = context.get("unit")
            if unit:
                expected = f"{expected} / {unit}"
            elif isinstance(expected, str) and actual.startswith(expected + " / ") and actual.split(" / ", 1)[1].strip():
                # Older manifests keep the unit only in the shared display block.
                # Its complete value is still compared between all artifacts.
                continue
        elif field == "standard":
            if standard.get("status") == "pending":
                expected = "(성취기준 코드 확인 필요)"
            else:
                expected = " ".join(v.strip() for v in (standard.get("code"), standard.get("text"))
                                    if isinstance(v, str) and v.strip())
        elif isinstance(expected, list) and all(isinstance(value, str) for value in expected):
            expected = ", ".join(expected)
        if expected != actual:
            errors.append(f"package anchor differs from manifest: {field}")
    return errors


def _check_images(images: list[str], path: Path, package_root: Path) -> bool:
    """The native verifier opens local images. Bound these reads to the package."""
    root = package_root.resolve()
    for src in images:
        if src.startswith(("http://", "https://", "data:", "//")):
            continue
        local = unquote(src.split("?")[0].split("#")[0])
        if not local or PureWindowsPath(local).anchor or Path(local).anchor:
            return False
        try:
            resolved = (path.parent / local).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                return False
        except (OSError, ValueError, RuntimeError):
            return False
    return True


def _worksheet_errors(path: Path, package_root: Path, page: _LessonHTML,
                      audience: str, skills_roots: list[Path] | None) -> list[str]:
    if not _check_images(page.images, path, package_root):
        return ["worksheet contains a missing or invalid local image"]
    module = find_module(WORKSHEET_MODULE, default_skill_roots() if skills_roots is None else skills_roots)
    if module is None:
        return ["install html-worksheet-generator to run its native worksheet verifier"]
    verifier = module / WORKSHEET_VALIDATOR
    try:
        if not verifier.is_file() or not verifier.resolve().is_relative_to(module.resolve()):
            return ["native worksheet verifier is missing from html-worksheet-generator"]
        spec = importlib.util.spec_from_file_location("_lesson_native_worksheet", verifier)
        if spec is None or spec.loader is None:
            return ["cannot load the native worksheet verifier"]
        native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(native)
        rows = native.validate(path)
        # Answer keys are permitted in the teacher copy only.
        return [f"native worksheet check failed: {name}" for name, ok, _ in rows
                if not ok and not (audience == "teacher" and name == "teacher-only wording absent")]
    except (OSError, ImportError, ValueError, RuntimeError, AttributeError, SyntaxError):
        return ["native worksheet verifier could not validate the HTML and its assets"]


def artifact_contract_errors(manifest: dict, artifact: dict, path: Path, content: str,
                             package_root: Path, *, check_anchor=True, check_native=True,
                             expected_anchor: tuple[str, ...] | None = None,
                             skills_roots: list[Path] | None = None) -> list[str]:
    """Check an already resolved, safely read artifact; return input-neutral diagnostics."""
    is_html = path.suffix.lower() in HTML_SUFFIXES
    page = _LessonHTML(content) if is_html else None
    errors = []
    if check_anchor:
        block = page.anchor_block() if page else _markdown_block(content)
        errors.extend(_anchor_errors(manifest, block))
        if block and expected_anchor is not None and block != expected_anchor:
            errors.append("package anchor differs between module outputs")
    if check_native and artifact.get("module_id") in ("mindmap-html-generator", WORKSHEET_MODULE):
        if not is_html or not page.has_body:
            errors.append("generated HTML module requires an HTML document with a body")
        elif artifact["module_id"] == WORKSHEET_MODULE:
            errors.extend(_worksheet_errors(path, package_root, page, artifact.get("audience"), skills_roots))
    return errors
