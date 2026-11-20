# Validation Scenario: HTML Worksheet With Board Writing

Use this note as a smoke-test example for `class-total-package`.

## Scenario

- school level: middle school
- subject: science or social studies
- requested modules: `board-writing-generator` + `html-worksheet-generator`
- output mode: `수업형`
- source: textbook PDF, lesson PDF, or captured source material is provided
- emphasis: source-grounded student worksheet and classroom board flow alignment

## Why package mode is correct

- two lesson outputs must stay aligned as one classroom sequence
- the board-writing plan introduces the same concepts the worksheet asks students to use
- direct-skill routing would weaken the shared goal, concept wording, and final check alignment

## Expected module choice

- required:
  - `board-writing-generator`
  - `html-worksheet-generator`
- optional:
  - `mindmap-html-generator`
  - `pbl-lesson-designer`
  - `inquiry-report-assessment`

## Expected template or reference choice

- from `board-writing-generator`
  - `board-modes.md`
  - `subject-patterns.md`
- from `html-worksheet-generator`
  - `pdf-textbook-html-worksheet.md`

## Expected shared anchors

- textbook learning goal
- shared lesson objective
- shared key concept labels
- board-writing sequence matched to worksheet sections
- worksheet final check matched to board summary

## Expected minimum output set

1. lesson overview
2. source material handling note
3. board-writing plan
4. final board snapshot or board sequence
5. a generated student worksheet (`.html`) based on the source, with its final check activity
6. basic HTML worksheet validation checklist
7. teacher flow memo

## Pass condition

- only board-writing and HTML worksheet modules are required
- no mind map, PBL, or assessment output is generated unless explicitly requested
- worksheet content is grounded in the provided PDF or source material
- source PDF is preserved and source visuals are not invented
- the HTML file opens, passes the worksheet skill's `scripts/verify_html_worksheet.py`, and prints with its goal and final activity visible
- check the referenced local image files when source visuals are used
- board summary and worksheet final check use the same key concept wording

For an explicit outline-only request, set `deliverable_stage: design` and report the outline as design work. The generation scenario above requires the classroom file.
