"""Resolve a lesson request and check its selected, separately installed skills."""

import argparse
import os
from pathlib import Path


WORKSHEET_VALIDATOR = "scripts/verify_html_worksheet.py"
MODULE_REQUIREMENTS = {
    "board-writing-generator": ("references/board-modes.md",),
    "mindmap-html-generator": ("scripts/build_mindmap.py",),
    "html-worksheet-generator": ("templates/worksheet_base.html", WORKSHEET_VALIDATOR),
    "pbl-lesson-designer": ("references/pbl-template-pack.md",),
    "inquiry-report-assessment": ("references/inquiry-report-template-pack.md",),
}


def default_skill_roots() -> list[Path]:
    """Use the package's sibling skills, then the user's configured skills."""
    codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    return list(dict.fromkeys((
        Path(__file__).resolve().parents[2], codex_home / "skills", Path.home() / ".agents" / "skills"
    )))


def find_module(module_id: str, roots: list[Path]) -> Path | None:
    """Return the first installation with its entry point and required assets."""
    requirements = ("SKILL.md", *MODULE_REQUIREMENTS[module_id])
    for root in roots:
        candidate = root / module_id
        if all((candidate / path).is_file() for path in requirements):
            return candidate
    return None


def select_modules(named: list[str], *, infer: bool = False, full: bool = False) -> tuple[str, ...]:
    selected = tuple(dict.fromkeys(named))
    if full:
        if selected:
            raise ValueError("Use --full-package alone or name the exact modules for a narrower request.")
        return tuple(MODULE_REQUIREMENTS)
    if infer:
        if not 2 <= len(selected) < len(MODULE_REQUIREMENTS):
            raise ValueError("Infer the smallest useful combination; use --full-package for an explicit full package.")
    elif not selected:
        raise ValueError("Name the requested modules, use --infer, or use --full-package.")
    for module_id in selected:
        if module_id not in MODULE_REQUIREMENTS:
            raise ValueError(f"Unknown lesson module: {module_id}")
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="*", help="requested or inferred module IDs")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--infer", action="store_true", help="the user requested a package without naming modules")
    selection.add_argument("--full-package", action="store_true", help="the user explicitly requested all five modules")
    parser.add_argument("--skills-root", type=Path, action="append", help="search only these trusted parent directories")
    args = parser.parse_args(argv)
    try:
        modules = select_modules(args.modules, infer=args.infer, full=args.full_package)
    except ValueError as exc:
        parser.error(str(exc))

    roots = args.skills_root or default_skill_roots()
    print("route:", "direct" if len(modules) == 1 else "package")
    missing = False
    for module_id in modules:
        folder = find_module(module_id, roots)
        if folder:
            print(f"READY {module_id}: {folder}")
        else:
            missing = True
            required = ", ".join(("SKILL.md", *MODULE_REQUIREMENTS[module_id]))
            print(f"MISSING {module_id}: install the complete skill ({required}) "
                  "or pass --skills-root for its registered location.")
    return int(missing)


if __name__ == "__main__":
    raise SystemExit(main())
