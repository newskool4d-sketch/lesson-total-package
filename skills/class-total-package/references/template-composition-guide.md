# Template Composition Guide

Use this reference when `class-total-package` needs to assemble outputs from linked skill template packs.

## Core principle

Do not start from a blank page when a linked module already has a strong reusable template.
Do not invoke template composition at all when the request is clearly single-module and should be routed to a direct skill.

## Linked template packs

### PBL

From `pbl-lesson-designer`:

- `pbl-template-pack.md`

Recommended outputs:

- PBL 수업 개요
- 단계별 수업 흐름
- 팀 역할표
- 탐구 기록지
- AI 사용 및 검증 기록표
- 중간 점검표

### Inquiry-report assessment

From `inquiry-report-assessment`:

- `inquiry-report-template-pack.md`
- `inquiry-report-template-pack-middle.md`
- `inquiry-report-template-pack-high.md`
- `inquiry-report-template-pack-social.md`

Recommended outputs:

- 학생 과제 안내문
- 수행평가 기준표
- 개인/모둠 반영 방식
- AI 사용 및 검증 기록표
- 교사용 피드백 양식
- 기록용 메모

## Selection rules

- school level first
- subject next
- module purpose after that
- confirm that this is actually a multi-module package before composing

### School level rule

- `중학교`, `중등 공통`, `기초형` -> middle template
- `고등학교`, `심화`, `논리형`, `분석형` -> high template

### Subject rule

- `사회`, `역사`, `지리`, `정치`, `경제`, `윤리`, `국제` -> social studies template

## Composition rule

When several modules are selected:

- unify the objective
- unify the key question
- unify the final artifact
- unify the evaluation point wording

Then assemble the minimum useful output set.

If only one module is selected:

- do not wrap it in package framing by default
- prefer the direct module output shape
- use package composition only if the user explicitly asked for package framing

## Minimum useful output sets

- `PBL only`
  - overview
  - phase plan
  - inquiry record
- `Assessment only`
  - task sheet
  - rubric
  - feedback form
- `PBL + Assessment`
  - overview
  - phase plan
  - task sheet
  - rubric
  - AI log if needed
  - teacher memo
