# Validation Scenario: Full Public Lesson Package

Use this note as a smoke-test example for `class-total-package`.

## Scenario

- school level: middle or high school
- subject: social studies
- requested modules: all five modules
- output mode: `패키지형`
- emphasis: public lesson readiness, coherence across outputs, teacher usability

## Why package mode is correct

- all five modules are explicitly requested
- the user wants one connected public-lesson artifact, not separate single outputs
- direct-skill routing would fragment the shared objective, terminology, and teacher memo

## Expected module choice

- required:
  - `board-writing-generator`
  - `mindmap-html-generator`
  - `html-worksheet-generator`
  - `pbl-lesson-designer`
  - `inquiry-report-assessment`
- optional:
  - none

## Expected template choice

- from `html-worksheet-generator`
  - `pdf-textbook-html-worksheet.md`
- from `pbl-lesson-designer`
  - `pbl-template-pack.md`
- from `inquiry-report-assessment`
  - choose one of:
    - `inquiry-report-template-pack-middle.md`
    - `inquiry-report-template-pack-high.md`
    - `inquiry-report-template-pack-social.md`

## Expected shared anchors

- one common objective
- one common key question
- one consistent final artifact
- source-grounded student activity sequence
- evaluation points aligned with lesson activity

## Expected minimum output set

1. package overview
2. selected modules summary
3. common lesson flow
4. board-writing plan
5. mind map structure
6. PDF-grounded HTML worksheet plan or generated worksheet contract
7. PBL overview and phase plan
8. inquiry-report task sheet and rubric
9. AI verification record
10. teacher connection memo

## Pass condition

- all five outputs read as one package, not five isolated documents
- selected assessment template matches school level and subject
- HTML worksheet expectations include source grounding, print controls, and basic file/path validation
- board, mind map, HTML worksheet, PBL, and assessment share the same terminology
- teacher memo explicitly explains how outputs connect in class
- this scenario is not downgraded into separate direct-skill outputs
