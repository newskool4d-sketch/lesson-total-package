# Validation Scenario: Middle School Concept Lesson

Use this note as a smoke-test example for `class-total-package`.

## Scenario

- school level: middle school
- subject: science
- requested modules: `board-writing-generator` + `mindmap-html-generator`
- output mode: `수업형`
- emphasis: concept clarity, visual structure, classroom readability

## Expected module choice

- required:
  - `board-writing-generator`
  - `mindmap-html-generator`
- optional:
  - `pbl-lesson-designer`
  - `inquiry-report-assessment`

## Expected template or reference choice

- from `board-writing-generator`
  - `board-modes.md`
  - `subject-patterns.md`
- from `mindmap-html-generator`
  - `output-modes.md`
  - `base-mindmap-template.html`

## Expected shared anchors

- shared lesson objective
- shared key concept labels
- shared summary wording

## Expected minimum output set

1. lesson overview
2. board-writing plan
3. final board snapshot
4. mind map branch structure
5. teacher flow memo

## Pass condition

- no PBL or assessment output is generated
- board and mind map use the same concept vocabulary
- output remains classroom-ready, not document-heavy
- visual mode stays within `수업형` breadth
