# Validation Scenarios

Use these notes as smoke-test cases for `class-total-package`.

After any change to SKILL.md or references, rerun at least one scenario and record the result in [validation-log.md](validation-log.md).

## Included scenarios

- [validation-scenario-social-high.md](validation-scenario-social-high.md)
  - high school social studies
  - `PBL + inquiry-report-assessment`
  - package mode
- [validation-scenario-middle-concept.md](validation-scenario-middle-concept.md)
  - middle school concept lesson
  - `board-writing-generator + mindmap-html-generator`
  - lesson mode
- [validation-scenario-html-worksheet-board.md](validation-scenario-html-worksheet-board.md)
  - textbook PDF-based classroom lesson
  - `board-writing-generator + html-worksheet-generator`
  - lesson mode
- [validation-scenario-html-worksheet-pbl.md](validation-scenario-html-worksheet-pbl.md)
  - source-grounded inquiry lesson
  - `html-worksheet-generator + pbl-lesson-designer`
  - package mode
- [validation-scenario-full-package.md](validation-scenario-full-package.md)
  - integrated public lesson package
  - all five modules
  - package mode

## Validation coverage map

- module selection logic
- optional vs required separation
- single-module handoff correctness
- PDF-grounded HTML worksheet selection
- HTML worksheet file/path validation expectations
- template-first behavior
- shared anchor consistency
- AI verification visibility
- output breadth control by mode

## Quick check rule

When validating the package, prefer checking:

1. whether only the needed modules are activated
2. whether single-module requests were kept out of package mode unless explicitly bundled
3. whether the chosen templates match school level and subject
4. whether shared objective, key question, artifact, and evaluation wording stay aligned
5. whether the output breadth matches `간단형`, `수업형`, or `패키지형`
6. whether HTML worksheets, when selected, stay grounded in source material and include basic file/path validation expectations
