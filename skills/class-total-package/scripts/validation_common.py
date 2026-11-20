"""Shared, bounded safety checks for both manifest validators (stdlib only)."""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path, PureWindowsPath
from typing import Any, Iterator


MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_MANIFEST_CHARS = 8 * 1024 * 1024
MAX_MANIFEST_NODES = 100_000
MAX_MANIFEST_DEPTH = 64

TEACHER_MARKERS = re.compile(r"교사용|교사[ \t]*(?:전용|메모|관찰[ \t]*(?:기록|메모))")
# Match answer-key/observation section labels; ordinary prompts such as
# "정답을 쓰세요" and a student's own observation log are valid activities.
TEACHER_SECTION = re.compile(
    r"(?:^|[\n\x00])[ \t#>*\[\-]*"
    r"(?:정답(?:[ \t]*(?:및|[·ㆍ/])[ \t]*해설|[ \t]+해설)?|해설|(?:모범|예시)[ \t]*답안"
    r"|학생[ \t]*관찰[ \t]*(?:기록|메모))"
    r"[ \t*\]]*(?=[\r\n\x00]|$|[:：][ \t]*[^\s_\x00])"
)
ABILITY_LABELS = re.compile(r"하위 수준|낮은 수준|보충반|기초반|상위 수준|심화반|Below|Above|Group A|Group C")

# Each run is consumed once. Adjacent runs around an @ are inspected at most
# twice, avoiding a new unbounded email search at every word boundary.
EMAIL_PART = re.compile(r"[\w.+-]+")
WORD = re.compile(r"\w")
PII_PATTERNS = (
    re.compile(r"(?<!\d)(?:01[016789]|02|0[3-9]\d)[-\s.]?\d{3,4}[-\s.]?\d{4}(?!\d)"),
    re.compile(r"(?<!\d)\d{6}[-\s.]?[1-4]\d{6}(?!\d)"),
)
JSDELIVR_NPM_VERSION = re.compile(
    r"\bhttps://cdn\.jsdelivr\.net/npm/(?:@[a-z0-9._-]+/)?"
    r"(?P<package_version>[a-z0-9._-]+@[0-9]+\.[0-9]+\.[0-9]+)(?=/)",
    re.IGNORECASE,
)


class ValidationInputError(ValueError):
    """Input cannot be safely or completely checked; never treat it as PASS."""


def _email_spans(text: str) -> Iterator[tuple[int, int]]:
    previous = None
    for part in EMAIL_PART.finditer(text):
        if previous is not None and previous.end() + 1 == part.start() and text[previous.end()] == "@":
            local_start = WORD.search(text, previous.start(), previous.end())
            plus = text.find("+", part.start(), part.end())
            domain_end = plus if plus != -1 else part.end()
            dot = text.find(".", part.start(), domain_end)
            if local_start is not None and dot > part.start():
                # The old email rule ends at a word boundary, excluding trailing
                # punctuation. The first domain label may contain words/hyphens.
                end = domain_end
                while end > dot + 1 and not (text[end - 1].isalnum() or text[end - 1] == "_"):
                    end -= 1
                if end > dot + 1:
                    yield local_start.start(), end
        previous = part


def _text_contains_pii(text: str) -> bool:
    version_spans = {match.span("package_version") for match in JSDELIVR_NPM_VERSION.finditer(text)}
    if any(span not in version_spans for span in _email_spans(text)):
        return True
    return any(pattern.search(text) for pattern in PII_PATTERNS)


class _HTMLSafetyText(HTMLParser):
    # Separate block text and attribute values without creating a phone number
    # from unrelated fields. Inline tags intentionally do not insert separators.
    BLOCKS = frozenset((
        "address", "article", "aside", "blockquote", "body", "br", "dd", "div", "dl", "dt",
        "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4",
        "h5", "h6", "head", "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section",
        "table", "tbody", "td", "th", "thead", "title", "tr", "ul",
    ))
    # </head> (and <body>) may be omitted in HTML. Never require an explicit
    # head end tag to resume inspection of the document's visible body.
    HIDDEN = frozenset(("script", "style", "template"))

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.attributes: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        self.attributes.extend(value for _, value in attrs if value is not None)
        if tag in self.HIDDEN:
            self.hidden_depth += 1
        if not self.hidden_depth and tag in self.BLOCKS:
            self.text.append("\0")

    def handle_endtag(self, tag):
        if tag in self.HIDDEN and self.hidden_depth:
            self.hidden_depth -= 1
        if not self.hidden_depth and tag in self.BLOCKS:
            self.text.append("\0")

    def handle_data(self, data):
        if not self.hidden_depth:
            self.text.append(data)


def safety_views(text: str) -> tuple[str, ...]:
    """Keep source checks and also inspect static decoded HTML text/attributes."""
    if len(text) > MAX_MANIFEST_CHARS:
        raise ValidationInputError("text exceeds validation size limit")
    views = [text]
    if "&" in text:
        views.append(unescape(text))
    if "<" in text:
        parser = _HTMLSafetyText()
        parser.feed(text)
        parser.close()
        views.extend(("".join(parser.text), "\0".join(parser.attributes)))
    return tuple(views)


def audience_content_errors(audience: object, views: tuple[str, ...], path_value: str) -> list[str]:
    """Apply the same content rules to every artifact distributed to students."""
    if audience not in ("student", "shared"):
        return []
    errors = []
    if any(TEACHER_MARKERS.search(view) or TEACHER_SECTION.search(view) for view in views):
        errors.append(f"teacher-only content in {audience} artifact {path_value}")
    if any(ABILITY_LABELS.search(view) for view in views):
        errors.append(f"student ability label in {audience} artifact {path_value}")
    return errors


def contains_pii(value: Any) -> bool:
    """Check JSON keys/values without recursion or echoing sensitive values."""
    pending = [(value, 0)]
    nodes = chars = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        if nodes > MAX_MANIFEST_NODES or depth > MAX_MANIFEST_DEPTH:
            raise ValidationInputError("manifest exceeds validation structure limit")
        if isinstance(item, str):
            chars += len(item)
            if chars > MAX_MANIFEST_CHARS:
                raise ValidationInputError("manifest exceeds validation size limit")
            if any(_text_contains_pii(view) for view in safety_views(item)):
                return True
        elif isinstance(item, (dict, list)):
            child_count = len(item) * (2 if isinstance(item, dict) else 1)
            if nodes + len(pending) + child_count > MAX_MANIFEST_NODES:
                raise ValidationInputError("manifest exceeds validation structure limit")
            if isinstance(item, dict):
                for key, child in item.items():
                    pending.extend(((key, depth + 1), (child, depth + 1)))
            else:
                pending.extend((child, depth + 1) for child in item)
    return False


def manifest_safety_errors(manifest: dict[str, Any]) -> list[str]:
    try:
        return ["PII detected in manifest"] if contains_pii(manifest) else []
    except ValidationInputError as exc:
        return [str(exc)]


def read_utf8_bounded(path: Path) -> str:
    with path.open("rb") as handle:
        data = handle.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValidationInputError("file exceeds validation size limit (8 MiB)")
    return data.decode("utf-8")


def resolve_package_file(path_value: str, base_dir: Path | str, *, label: str = "artifact") -> Path:
    """Return an existing package file after checking lexical and resolved paths."""
    path = Path(path_value)
    windows_path = PureWindowsPath(path_value)
    if path.anchor or windows_path.drive or windows_path.root or ".." in path.parts or ".." in windows_path.parts:
        raise ValidationInputError(f"{label} path escapes package root: {path_value}")
    try:
        root = Path(base_dir).resolve()
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root):
            raise ValidationInputError(f"{label} path escapes package root: {path_value}")
        if not resolved.is_file():
            raise ValidationInputError(f"{label} file not found: {path_value}")
        return resolved
    except ValidationInputError:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValidationInputError(f"{label} cannot be read: {path_value}") from exc


def read_artifact(path_value: str, base_dir: Path | str) -> str:
    resolved = resolve_package_file(path_value, base_dir)
    try:
        return read_utf8_bounded(resolved)
    except UnicodeDecodeError as exc:
        raise ValidationInputError(f"artifact is not UTF-8 text: {path_value}") from exc
    except ValidationInputError:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValidationInputError(f"artifact cannot be read: {path_value}") from exc
