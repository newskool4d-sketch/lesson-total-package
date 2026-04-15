# Validation Scenarios

Use these notes as smoke-test cases for `class-total-package`.

## Included scenarios

- [validation-scenario-social-high.md](validation-scenario-social-high.md)
  - high school social studies
  - `PBL + inquiry-report-assessment`
  - package mode
- [validation-scenario-middle-concept.md](validation-scenario-middle-concept.md)
  - middle school concept lesson
  - `board-writing-generator + mindmap-html-generator`
  - lesson mode
- [validation-scenario-full-package.md](validation-scenario-full-package.md)
  - integrated public lesson package
  - all four modules
  - package mode

## Validation coverage map

- module selection logic
- optional vs required separation
- template-first behavior
- shared anchor consistency
- AI verification visibility
- output breadth control by mode

## Quick check rule

When validating the package, prefer checking:

1. whether only the needed modules are activated
2. whether the chosen templates match school level and subject
3. whether shared objective, key question, artifact, and evaluation wording stay aligned
4. whether the output breadth matches `간단형`, `수업형`, or `패키지형`
