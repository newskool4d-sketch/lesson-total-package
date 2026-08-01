# Routing Smoke Test for Class Total Package

Use this file to check whether `class-total-package` routes correctly as a bundle skill after description, package logic, or module-linking changes.

## Must trigger this skill

- 수업 패키지로 판서와 마인드맵을 같이 설계해 줘.
- 수업 패키지로 판서와 HTML 학습지를 같이 설계해 줘.
- 교과서 PDF 학습지와 PBL을 묶어서 수업 패키지로 만들어 줘.
- PBL과 수행평가를 묶어서 하나의 수업형 패키지로 만들어 줘.
- 전체 수업팩으로 판서, 마인드맵, HTML 학습지, PBL, 수행평가까지 연결해 줘.

## Must not trigger this skill

- 판서안만 만들어 줘.
- HTML 학습지만 만들어 줘.
- HTML 마인드맵만 만들어 줘.
- PBL 수업안만 설계해 줘.
- 탐구 보고서 수행평가만 만들어 줘.

## Adjacent skills

- `board-writing-generator`
- `mindmap-html-generator`
- `html-worksheet-generator`
- `pbl-lesson-designer`
- `inquiry-report-assessment`

## Boundary checks

- shortest valid bundle request: `판서랑 마인드맵 같이`
- ultra-short mixed-module request: `판서+마인드맵`
- ultra-short mixed-module request: `판서+HTML 학습지`
- ultra-short mixed-module request: `HTML 학습지+PBL`
- ultra-short mixed-module request: `PBL이랑 평가`
- deceptively similar non-bundle request: `PBL만 먼저 설계해 줘`
- deceptively similar non-bundle request: `HTML 학습지만 먼저 만들어 줘`
- archetype: `bundle and routing skill`

## Failure signals

- 단일 모듈 요청이 패키지 스킬로 먼저 잡힌다.
- 필요한 모듈이 둘뿐인데 네 모듈 전체 패키지로 과확장된다.
- 공통 목표나 핵심 질문 없이 결과물만 나열된다.
- HTML 학습지가 선택됐는데 source-grounded 검증 기준이 빠진다.
- inactive module output이 섞여 나온다.
