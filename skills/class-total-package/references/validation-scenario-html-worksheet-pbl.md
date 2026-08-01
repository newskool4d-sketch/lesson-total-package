# Validation Scenario: HTML Worksheet With PBL

Use this note as a smoke-test example for `class-total-package`.

## Scenario

- school level: middle or high school
- subject: social studies, science, or integrated inquiry
- requested modules: `html-worksheet-generator` + `pbl-lesson-designer`
- output mode: `패키지형`
- source: textbook PDF, lesson PDF, or captured source material is provided
- emphasis: source-grounded exploration, PBL phase alignment, AI and source verification

## Why package mode is correct

- the worksheet supplies common source evidence for the PBL inquiry
- the PBL flow uses the worksheet activities as exploration and evidence-gathering steps
- direct-skill routing would risk separating source reading from the project artifact

## Expected module choice

- required:
  - `html-worksheet-generator`
  - `pbl-lesson-designer`
- optional:
  - `board-writing-generator`
  - `mindmap-html-generator`
  - `inquiry-report-assessment`

## Expected template or reference choice

- from `html-worksheet-generator`
  - `pdf-textbook-html-worksheet.md`
- from `pbl-lesson-designer`
  - `pbl-template-pack.md`
  - `source-validation-guide.md`
  - `ai-verification-log.md`

## Expected shared anchors

- shared driving question
- source-based inquiry question
- source evidence students must extract
- final project artifact
- AI verification and source-checking expectation

## Expected minimum output set

1. package overview
2. PBL overview
3. phase plan
4. source-grounded HTML worksheet plan or generated worksheet contract
5. source evidence activity
6. AI and source verification log
7. teacher connection memo

## Pass condition

- only HTML worksheet and PBL modules are required
- no inquiry-report assessment or rubric is generated unless explicitly requested
- worksheet sections support the PBL exploration sequence
- PDF facts, visuals, tables, maps, or diagrams are used only when visible in the source
- PBL outputs include AI verification and source-checking expectations
- worksheet expectations include print controls and basic file/path validation when an HTML file is generated
- final project artifact grows from the source evidence gathered in the worksheet
