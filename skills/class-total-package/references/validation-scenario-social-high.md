# Validation Scenario: High School Social Studies

Use this note as a smoke-test example for `class-total-package`.

## Scenario

- school level: high school
- subject: social studies
- requested modules: `pbl-lesson-designer` + `inquiry-report-assessment`
- output mode: `패키지형`
- emphasis: discussion, writing, exploration, AI verification

## Expected module choice

- required:
  - `pbl-lesson-designer`
  - `inquiry-report-assessment`
- optional:
  - `board-writing-generator`
  - `mindmap-html-generator`

## Expected template choice

- from `pbl-lesson-designer`
  - `pbl-template-pack.md`
- from `inquiry-report-assessment`
  - `inquiry-report-template-pack-social.md`
  - `feedback-sentence-frames.md`
  - `record-observation-examples.md`

## Expected shared anchors

- shared objective
- shared driving question
- shared final artifact
- shared evaluation points

## Expected minimum output set

1. PBL overview
2. phase plan
3. social studies inquiry-report task sheet
4. social studies rubric
5. AI verification log
6. teacher feedback form
7. record memo

## Pass condition

- package selects only needed modules
- social studies variant is chosen over the general assessment template
- high-school level wording is maintained
- discussion, evidence comparison, and AI verification are visible
- PBL flow and assessment task read as one connected lesson
