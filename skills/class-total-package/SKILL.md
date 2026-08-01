---
name: class-total-package
description: Assemble Korean lesson packages by routing to board-writing, mind map, worksheet, PBL, or assessment modules as needed.
metadata:
  short-description: 선택형 수업 모듈 패키지를 연결 설계하는 번들 스킬
---

# Class Total Package

## Safety And Preflight

- Do not expose student personal data or private school records in lesson packages.
- Verify source files, curriculum scope, grade level, and output destination before creating bundled artifacts.
- If connector or sandbox writes fail, provide local Markdown/HTML fallback output and report the blocked path.

Use this skill to orchestrate a lesson package from multiple teaching modules.

This is a bundle and routing skill, not the default for single outputs.

- Use it when two or more lesson modules need to be linked.
- Do not swallow single-module requests that have a clearer direct skill.
- If the user only wants PBL, 판서, 마인드맵, HTML 학습지, or 수행평가 alone, prefer the direct module skill.

Read these bundled files only when needed:

- For package selection and linking logic, use [references/package-rules.md](references/package-rules.md)
- For the shared anchor block contract, use [references/package-anchor-contract.md](references/package-anchor-contract.md)
- For package-level IDs, source status, safety gates, and cross-artifact validation, use [references/package-manifest-contract.md](references/package-manifest-contract.md)
- For template-first composition rules, use [references/template-composition-guide.md](references/template-composition-guide.md)
- For representative invocation examples, use [references/example-prompts.md](references/example-prompts.md)
- For smoke-test validation scenarios, use [references/validation-scenarios.md](references/validation-scenarios.md)
- For routing regression checks after skill changes, use [references/routing-smoke-test.md](references/routing-smoke-test.md)
- For the shared P/R/O/M/S quality criteria and fixture runner, use `evals/rubrics/shared.csv` and `scripts/run_contract_tests.py`
- For learner variability, subject pedagogy, and audience density rules, use [references/learner-variability-rules.md](references/learner-variability-rules.md), [references/subject-pedagogy-routing.md](references/subject-pedagogy-routing.md), and [references/audience-and-density-rules.md](references/audience-and-density-rules.md)

## Core rule

- Do not assume every module must be used.
- Let the user's request determine which modules are required now.
- If the user does not specify modules, infer a sensible minimal set and state the assumption.
- Keep single-module requests out of this bundle unless the user explicitly asks for a package structure.

## Current module set

- `board-writing-generator` (optional)
- `mindmap-html-generator` (optional)
- `html-worksheet-generator` (optional)
- `pbl-lesson-designer` (optional)
- `inquiry-report-assessment` (optional)

## Selection and template rules

- Treat every module as optional by default.
- Activate only the modules the user explicitly requests or clearly approves.
- Present non-selected modules only as optional suggestions.
- Prefer linked module template packs when they fit the request.
- For detailed selection, handoff, and AI-literacy rules, read [references/package-rules.md](references/package-rules.md).
- For linked template pack rules, read [references/template-composition-guide.md](references/template-composition-guide.md).

## Module invocation rules

Use the module names explicitly in planning and execution.

- If the user asks for `판서`, invoke the logic of `board-writing-generator`
- If the user asks for `마인드맵`, invoke the logic of `mindmap-html-generator`
- If the user asks for `HTML 학습지`, `PDF 교과서 학습지`, or print-ready worksheet output, invoke the logic of `html-worksheet-generator`
- If the user asks for `PBL`, invoke the logic of `pbl-lesson-designer`
- If the user asks for `수행평가`, `탐구 보고서`, or `평가 기준`, invoke the logic of `inquiry-report-assessment`

If the user asks for a package without naming modules, infer the minimal useful module set from [references/package-rules.md](references/package-rules.md).

## Package logic

Treat the package as a selectable set of lesson components, not a fixed production line.

Typical selectable outputs include lesson overview, board-writing plan, concept map, PDF-grounded HTML worksheet, PBL flow, inquiry-report assessment, teacher notes, and template-based worksheets.

## Required package workflow

1. Identify the lesson topic, subject, learner level, and time scope.
2. Identify which modules are explicitly requested.
3. Infer optional modules that materially improve the lesson flow.
4. Separate `required modules` from `optional modules`.
5. When two or more modules are selected, fix the shared anchor block first using [references/package-anchor-contract.md](references/package-anchor-contract.md), show it to the user, then insert the identical block at the top of every module output.
6. For package-mode work, create or update the internal package manifest before generating module artifacts; run `scripts/validate_package.py` when a manifest and local artifact paths are available.
7. Produce only the required outputs unless the user asks for more.
8. Keep terminology, inquiry question, and activity sequence consistent across all selected modules.
9. In the response, label which output came from which module when multiple modules are combined.
10. Prefer template-based outputs when the selected modules already provide reusable packs.
11. Keep all non-selected modules inactive.

## PBL and assessment core requirements

When selected modules include PBL or inquiry-report assessment, apply the AI-literacy and evidence-checking rules in [references/package-rules.md](references/package-rules.md).

## Output storage

When the package produces multiple files, save them under one folder:

- folder: `수업패키지_{주제}(YYYY-MM-DD)/`
- file prefixes by module: `00_패키지개요` `01_판서` `02_마인드맵` `03_학습지` `04_PBL` `05_수행평가` `06_교사메모`
- confirm the destination root (Vault vs local) with the user before writing when not specified

## Output modes

- `간단형`: selected core modules only
- `수업형`: selected modules plus teacher notes and flow
- `패키지형`: selected modules plus linked assessment and artifact plan

Default to `수업형` when unspecified.

## Response structure

When producing a full package, prefer this order:

1. `패키지 개요`
2. `선택 모듈`
   Show `required` and `optional` separately when both exist.
3. `공통 수업 흐름`
4. `모듈별 결과물`
5. `교사용 연결 메모`

If only one or two modules are selected, do not force the full structure.

## Output composition examples

For composition examples and validation scenarios, read `references/example-prompts.md`, `references/template-composition-guide.md`, and `references/validation-scenarios.md` as needed.

## Quality checklist

Before finishing, confirm all of the following:

- the package uses only the modules that are needed
- optional modules are clearly separated from required modules
- the anchor block is character-identical at the top of every module output, and includes 성취기준 (code or `확인 필요`)
- PBL and assessment outputs include discussion, writing, exploration, AI verification, and source checking
- terminology is consistent across selected outputs
- the assessment matches the lesson activity rather than sitting separately
- template packs are used when they fit the request
- HTML worksheets, when selected, remain source-grounded and pass basic file/path validation
- package-mode manifests pass the package-level ID, timing, source, privacy, and audience gates when the validator is available
- the shared P/R/O/M/S rubric contains 24 unique criteria and its fixture suite passes before release
- learner profiles are non-identifying, preserve cognitive demand, and include a regrouping rule
- subject pedagogy profiles match the requested subject and include at least one non-negotiable principle
