# Validation Scenario: Full Public Lesson Package

Use this note as a smoke-test example for `class-total-package`.

## Scenario

- school level: middle or high school
- subject: social studies
- requested modules: all four modules
- output mode: `패키지형`
- emphasis: public lesson readiness, coherence across outputs, teacher usability

## Expected module choice

- required:
  - `board-writing-generator`
  - `mindmap-html-generator`
  - `pbl-lesson-designer`
  - `inquiry-report-assessment`
- optional:
  - none

## Expected template choice

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
- evaluation points aligned with lesson activity

## Expected minimum output set

1. package overview
2. selected modules summary
3. common lesson flow
4. board-writing plan
5. mind map structure or HTML plan
6. PBL overview and phase plan
7. inquiry-report task sheet and rubric
8. AI verification record
9. teacher connection memo

## Pass condition

- all four outputs read as one package, not four isolated documents
- selected assessment template matches school level and subject
- board, mind map, PBL, and assessment share the same terminology
- teacher memo explicitly explains how outputs connect in class
