# Package Rules

## Selection-first rule

수업 패키지는 모든 결과물을 한꺼번에 출력하는 번들이 아니다.

- 모든 모듈은 기본적으로 선택 사항이다.
- 필요한 모듈만 사용한다.
- 선택하지 않은 모듈은 제안만 하고 강제로 생성하지 않는다.
- 사용자가 `전체 패키지`를 명시할 때만 전체 연동형 결과를 만든다.
- 단일 모듈 요청이면 패키지 스킬로 흡수하지 말고 직접 모듈 스킬로 보낸다.

## Direct-skill handoff rule

다음 경우에는 `class-total-package`가 아니라 직접 스킬을 우선한다.

- `판서만` 필요 -> `board-writing-generator`
- `마인드맵만` 필요 -> `mindmap-html-generator`
- `HTML 학습지만`, `PDF 교과서 학습지만` 필요 -> `html-worksheet-generator`
- `PBL만` 필요 -> `pbl-lesson-designer`
- `수행평가만` 필요 -> `inquiry-report-assessment`

패키지 스킬은 두 개 이상 모듈이 실제로 연결될 때만 우선한다.

## Recommended module combinations

- 개념 정리 중심 수업
  - `board-writing-generator` 또는 `mindmap-html-generator`
- 수업 시각화까지 필요
  - `board-writing-generator` + `mindmap-html-generator`
- PDF 교과서 기반 학생 학습지 필요
  - `html-worksheet-generator`
- 판서 또는 마인드맵과 학생용 학습지를 함께 준비
  - `board-writing-generator` 또는 `mindmap-html-generator` + `html-worksheet-generator`
- 프로젝트형 문제 해결
  - `pbl-lesson-designer`
- 보고서형 결과물 평가
  - `inquiry-report-assessment`
- 수업과 평가를 함께 설계
  - `pbl-lesson-designer` + `inquiry-report-assessment`
- `판서 + PBL`
  - 수업 흐름과 프로젝트 흐름을 함께 설계
- `판서 + 마인드맵`
  - 개념 이해 중심 수업
- `PBL + 수행평가`
  - 탐구, 협업, 결과물 중심 수업
- `판서 + PBL + 수행평가`
  - 수업 흐름과 평가 연계를 함께 설계
- `전체`
  - 단원 수업 패키지 또는 공개수업 준비

## Selectable outputs

- lesson overview
- board-writing plan
- concept or mind map
- PDF-grounded HTML worksheet
- PBL lesson flow
- inquiry report performance assessment
- teacher facilitation notes
- template-based worksheets or forms

## Cross-module anchors

모듈을 연결할 때는 [package-anchor-contract.md](package-anchor-contract.md)의 앵커 블록을 먼저 확정하고 모든 산출물 상단에 동일하게 삽입한다. 통일 항목:

- 수업 목표
- 핵심 질문
- 핵심 개념
- 학생 활동 동사
- 최종 결과물
- 평가 포인트
- 성취기준 (2022 개정 교육과정 코드, 불확실하면 `확인 필요` 표기)

## Mode x module output matrix

과확장 방지 기준. 각 모드에서 **선택된 모듈에 한해** 아래 범위만 산출한다.

| 산출물 | 간단형 | 수업형 (기본) | 패키지형 |
|---|---|---|---|
| 앵커 블록 | O | O | O |
| 모듈 본체 (판서안·마인드맵·학습지·PBL 흐름·평가기준) | O | O | O |
| 공통 수업 흐름 | - | O | O |
| 교사용 연결 메모 | - | O | O |
| 학생 과제 안내문 | - | - | O |
| 루브릭·피드백 양식 | - | - | O |
| AI 사용·검증 기록표 | PBL/평가 포함 시 | PBL/평가 포함 시 | O |

- 간단형에서 수업 흐름·교사 메모를 만들지 않는다.
- 수업형에서 과제 안내문·루브릭을 만들지 않는다 (수행평가 모듈이 명시 선택된 경우 제외).

## Module admission criteria

신규 모듈을 이 패키지에 편입하려면 세 조건을 모두 충족해야 한다.

1. 직접 스킬이 `~/.codex/skills/`에 독립 존재한다.
2. 재사용 가능한 템플릿팩(또는 동급의 산출 규격 문서)을 보유한다.
3. 편입과 동시에 [routing-smoke-test.md](routing-smoke-test.md)에 must-trigger / must-not-trigger 케이스를 추가한다.

편입 후보 검토 중: `google-form-builder` (수행평가 온라인 배포 연계).

## AI literacy anchor

PBL 또는 수행평가가 포함되면 다음을 기본 원칙으로 둔다.

- AI는 초안, 관점 확장, 비교 재료로 사용한다.
- AI 결과는 검증 대상이다.
- 학생은 출처와 검증 흔적을 남긴다.
- 교사는 정답 생성보다 판단 과정과 근거 확인을 본다.

## Current active selection example

If the current request is `판서 + PBL`, then:

- active modules:
  - `board-writing-generator`
  - `pbl-lesson-designer`
- inactive modules:
  - `mindmap-html-generator`
  - `html-worksheet-generator`
  - `inquiry-report-assessment`

Do not generate outputs from inactive modules.

`lesson-differentiation`은 현재 `prototypes/` 아래의 비활성 후보이다. 기존 수업의 동일 목표·맥락을 유지한 차별화 요청에만 입편 계약을 적용하며, 실제 형제 스킬로 승격하기 전에는 직접 라우팅하지 않는다.
