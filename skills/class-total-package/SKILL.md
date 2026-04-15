---
name: class-total-package
description: Use when the user wants a Korean lesson package that selectively combines existing teaching skills such as board-writing, mind map, PBL lesson design, and inquiry-report assessment rather than forcing a fixed bundle. Trigger for requests like 수업 토탈 패키지, 수업팩, 수업 번들, 판서+마인드맵+PBL 묶기, 수행평가까지 포함한 수업 설계, or 선택형 수업 모듈 구성.
metadata:
  short-description: 선택형 수업 모듈 패키지를 연결 설계하는 번들 스킬
---

# Class Total Package

Use this skill to orchestrate a lesson package from multiple teaching modules.

Read these bundled files only when needed:

- For package selection and linking logic, use [references/package-rules.md](references/package-rules.md)
- For template-first composition rules, use [references/template-composition-guide.md](references/template-composition-guide.md)
- For representative invocation examples, use [references/example-prompts.md](references/example-prompts.md)
- For smoke-test validation scenarios, use [references/validation-scenarios.md](references/validation-scenarios.md)

## Core rule

- Do not assume every module must be used.
- Let the user's request determine which modules are required now.
- If the user does not specify modules, infer a sensible minimal set and state the assumption.

## Current module set

- `board-writing-generator` (optional)
- `mindmap-html-generator` (optional)
- `pbl-lesson-designer` (optional)
- `inquiry-report-assessment` (optional)

## All-modules-optional rule

Treat every module in this package as optional by default.

- Never assume any module is mandatory.
- Activate only the modules the user explicitly requests or clearly approves.
- When the user asks for one or two modules only, do not add the others unless the user asks for suggestions.
- Present non-selected modules only as optional suggestions.

## Template-first rule

When a selected module already has a reusable template pack, prefer composing from that pack instead of inventing the structure from scratch.

- For `pbl-lesson-designer`, prefer `references/pbl-template-pack.md`
- For `inquiry-report-assessment`, prefer:
  - `references/inquiry-report-template-pack.md`
  - `references/inquiry-report-template-pack-middle.md`
  - `references/inquiry-report-template-pack-high.md`
  - `references/inquiry-report-template-pack-social.md`

Use freeform generation only when:

- the user asks for a novel format
- the template does not fit the lesson type
- the template needs substantial adaptation

## Module invocation rules

Use the module names explicitly in planning and execution.

- If the user asks for `판서`, invoke the logic of `board-writing-generator`
- If the user asks for `마인드맵`, invoke the logic of `mindmap-html-generator`
- If the user asks for `PBL`, invoke the logic of `pbl-lesson-designer`
- If the user asks for `수행평가`, `탐구 보고서`, or `평가 기준`, invoke the logic of `inquiry-report-assessment`

If the user asks for a package without naming modules, choose from this matrix:

- 개념 정리 중심 수업 -> `board-writing-generator` or `mindmap-html-generator`
- 수업 시각화까지 필요 -> `board-writing-generator` + `mindmap-html-generator`
- 프로젝트형 문제 해결 -> `pbl-lesson-designer`
- 보고서형 결과물 평가 -> `inquiry-report-assessment`
- 수업과 평가를 함께 설계 -> `pbl-lesson-designer` + `inquiry-report-assessment`
- 전체 수업 패키지 -> all four modules when useful

## Package logic

Treat the package as a selectable set of lesson components, not a fixed production line.

Typical selectable outputs:

- lesson overview
- board-writing plan
- concept or mind map
- PBL lesson flow
- inquiry report performance assessment
- teacher facilitation notes
- template-based worksheets or forms

## Default module selection logic

- concept-heavy lesson -> prefer `board-writing-generator` + `mindmap-html-generator`
- project or problem solving lesson -> prefer `pbl-lesson-designer`
- inquiry evidence or writing outcome needed -> prefer `inquiry-report-assessment`
- if the user asks for a full package -> combine all relevant modules

## Template selection logic

If the package includes `inquiry-report-assessment`, choose the template pack like this:

- middle school or simpler classroom use -> middle template
- high school or more analytical work -> high template
- social studies inquiry -> social studies template
- unspecified general case -> basic template

If the package includes `pbl-lesson-designer`, use the PBL template pack as the default scaffold for:

- PBL overview
- phase plan
- team role sheet
- inquiry record
- AI verification log
- mid-project checkpoint

## Required package workflow

1. Identify the lesson topic, subject, learner level, and time scope.
2. Identify which modules are explicitly requested.
3. Infer optional modules that materially improve the lesson flow.
4. Separate `required modules` from `optional modules`.
5. Produce only the required outputs unless the user asks for more.
6. Keep terminology, inquiry question, and activity sequence consistent across all selected modules.
7. In the response, label which output came from which module when multiple modules are combined.
8. Prefer template-based outputs when the selected modules already provide reusable packs.
9. Keep all non-selected modules inactive.

## PBL and assessment core requirements

When the selected modules include `pbl-lesson-designer` or `inquiry-report-assessment`, always build around these learning actions:

- discussion
- writing
- exploration or research
- appropriate and critical AI use
- information verification

Never present AI use as simple answer generation.

Always require students to:

- distinguish claim from evidence
- compare AI output with source-based information
- record how AI was used
- verify important facts through credible materials
- reflect on bias, omission, or hallucination risk

## Output modes

Choose the output breadth based on the request:

- `간단형`: only the selected core modules
- `수업형`: selected modules plus teacher notes and flow
- `패키지형`: selected modules plus linked assessment and artifact plan

If the user does not specify a mode, default to `수업형`.

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

- `판서 + 마인드맵`
  - board layout
  - concept map structure
- `PBL`
  - PBL overview
  - phase plan
  - team role sheet
  - inquiry record
- `수행평가`
  - student task sheet
  - rubric
  - AI verification log if needed
  - teacher feedback form
- `PBL + 수행평가`
  - PBL overview
  - phase plan
  - inquiry report task sheet
  - rubric
  - mid-project checkpoint
  - teacher feedback and record memo

## Quality checklist

Before finishing, confirm all of the following:

- the package uses only the modules that are needed
- optional modules are clearly separated from required modules
- PBL and assessment outputs include discussion, writing, exploration, AI verification, and source checking
- terminology is consistent across selected outputs
- the assessment matches the lesson activity rather than sitting separately
- template packs are used when they fit the request
