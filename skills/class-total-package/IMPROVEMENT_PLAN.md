# class-total-package 분석 및 고도화 계획안

> 작성일: 2026-07-06 · 대상: `~/.codex/skills/class-total-package` (SKILL.md + references 10종 + agents/openai.yaml, 총 12파일 약 660줄 전수 검토)
> 상태: **실행 완료 (2026-07-06)** — Phase 1~3 반영. 잔여: full-package 시나리오 실전 1회 검증(다음 실제 패키지 요청 시)

## 1. 스킬 개요

| 항목 | 내용 |
|---|---|
| 성격 | 순수 프롬프트 기반 **번들·라우팅 스킬** (스크립트·자동화 없음) |
| 역할 | 판서·마인드맵·HTML학습지·PBL·수행평가 5개 모듈 스킬을 2개 이상 연결할 때만 패키지로 조립 |
| 연결 모듈 | `board-writing-generator` / `mindmap-html-generator` / `html-worksheet-generator` / `pbl-lesson-designer` / `inquiry-report-assessment` |
| 산출 모드 | 간단형 / 수업형(기본) / 패키지형 |

## 2. 현황 진단

### 2.1 강점 (유지할 것)

- **선택형 설계 원칙이 일관됨**: 모든 모듈 옵셔널, 단일 모듈 요청은 직접 스킬로 handoff, inactive 모듈 출력 금지 — SKILL.md·package-rules·smoke-test 3중으로 명문화
- **참조 무결성 정상**: 링크된 모듈 스킬 5종, 템플릿팩 5종(`pbl-template-pack.md`, `inquiry-report-template-pack{,-middle,-high,-social}.md`) 전부 실존 확인
- **검증 문서 체계**: 라우팅 스모크 테스트(must/must-not/boundary/failure signals) + 검증 시나리오 5종 — 스킬치고 드물게 충실
- **AI 리터러시 앵커**: PBL·수행평가 포함 시 AI 검증 기록 요구 — 교육 맥락 정합
- progressive disclosure 준수 (SKILL.md는 얇고 세부는 references로)

### 2.2 문제점·개선 여지

| # | 항목 | 내용 |
|---|---|---|
| G1 | **앵커 handoff 계약 부재** | "목표·핵심질문·핵심개념·활동동사·결과물·평가포인트를 통일하라"는 원칙만 있고, 모듈 간 전달 **형식**(공통 앵커 블록 포맷)이 없음 → 5모듈 패키지에서 일관성이 전적으로 모델 재량. 가장 큰 품질 리스크 |
| G2 | **성취기준 연계 부재** | 앵커에 2022 개정 교육과정 성취기준·학년군 필드가 없음 — 사용자 환경의 프로그램기획 스킬은 성취기준 연계를 상시 요구하는 것과 불일치 |
| G3 | **산출물 저장 규약 부재** | 패키지형이면 파일 다수 생성인데 저장 경로·폴더 구조·파일명 규칙이 없음 (환경 표준: `폴더명(YYYY-MM-DD)`, Vault 경로) |
| G4 | **모드×모듈 산출 매트릭스 부재** | 간단형/수업형/패키지형이 각 모듈에서 무엇을 내는지 한 줄 정의뿐 — 과확장(smoke-test의 failure signal)을 막을 구체 기준 약함 |
| G5 | **routing-smoke-test.md가 SKILL.md에서 미링크** | validation-scenarios만 링크됨 — 라우팅 변경 시 스모크 테스트 존재를 놓치기 쉬움 |
| G6 | **모듈 확장 절차 없음** | `google-form-builder`(수행평가 배포), `lecture-outline-writer` 등 연계 가능 스킬이 이미 존재하나 신규 모듈 편입 기준·절차 미정의 |
| G7 | **검증 시나리오가 기대치 문서에 그침** | 실행 절차(언제·어떻게 돌리고 결과를 어디에 기록하는지) 없음 — 회귀 확인 불가 |
| G8 | Claude Code 쪽 대응 미정 | 5개 모듈 중 Claude 세션에는 `mindmap-html-generator`만 스킬로 존재. Claude에서 패키지 요청 시 이 codex 정본을 Read하여 수행하는지 여부가 CLAUDE.md·스킬 어디에도 없음 (daily-news-picker·education-office-document-templates는 명시돼 있음) |

## 3. 고도화 과제

### Phase 1 — 품질 핵심: 앵커 계약 (중) ← G1·G2
1. `references/package-anchor-contract.md` 신설: 공통 앵커 블록 표준 포맷 정의
   - 필드: 수업주제 / 학교급·학년군 / 교과 / **성취기준 코드** / 수업목표 / 핵심질문 / 핵심개념(≤5) / 학생 활동 동사 / 최종 결과물 / 평가 포인트
   - 규칙: 패키지 착수 시 앵커 블록을 **먼저 확정·출력**하고, 모든 모듈 산출물 상단에 동일 블록 삽입 (모듈 간 복사 검증 가능)
2. SKILL.md workflow 1~2단계에 앵커 블록 확정 단계 삽입, Quality checklist에 "모든 산출물의 앵커 블록 동일" 항목 추가
- **검증**: full-package 시나리오 1회 실행 — 5개 산출물의 앵커 블록 diff 0

### Phase 2 — 운영 규약 (소) ← G3·G4·G5
1. 산출물 저장 규약 추가: `수업패키지_{주제}(YYYY-MM-DD)/` 폴더 + 모듈별 파일명 접두(`01_판서`, `02_마인드맵`…) — Vault/로컬 대상은 요청 시 확인
2. 모드×모듈 매트릭스 표를 package-rules.md에 추가 (간단형=앵커+선택 모듈 본체만 / 수업형=+교사 흐름 메모 / 패키지형=+과제안내·루브릭·AI기록)
3. SKILL.md에 routing-smoke-test.md 링크 추가 (한 줄)

### Phase 3 — 확장·검증 체계 (소~중) ← G6·G7·G8
1. 모듈 편입 기준 문서화: "직접 스킬 존재 + 템플릿팩 보유 + smoke-test에 must/must-not 추가" 3조건 — 1호 후보로 `google-form-builder`(수행평가 온라인 배포) 편입 검토
2. 검증 실행 절차 추가: 시나리오별 통과/실패 기록표(`references/validation-log.md`), 스킬 수정 시 최소 1개 시나리오 재실행 규칙
3. 크로스 하네스 규칙 1줄 명문화: Claude 세션에서 패키지 요청 시 이 폴더 정본(SKILL.md+references)을 Read하여 수행 — CLAUDE.md §5 기타 도구 표에 항목 추가 (사용자 승인 필요)

## 4. 우선순위·공수

| 순위 | 과제 | 공수 | 효과 |
|---|---|---|---|
| 1 | Phase 1 앵커 계약 (G1·G2) | 중 | 패키지 일관성 = 이 스킬의 존재 이유. 최대 품질 레버 |
| 2 | Phase 2 운영 규약 (G3·G4·G5) | 소 | 산출물 정리·과확장 방지, 즉시 체감 |
| 3 | Phase 3 확장·검증 (G6·G7·G8) | 소~중 | 지속 운영 기반. G8은 CLAUDE.md 수정이라 사용자 확인 후 |

## 5. 완료 기준

- [x] 앵커 계약 문서 신설 (`references/package-anchor-contract.md`) — full-package 실전 검증은 다음 패키지 요청 시
- [x] 앵커에 성취기준 코드 필드 포함
- [x] 저장 규약(SKILL.md Output storage)·모드×모듈 매트릭스(package-rules.md) 반영
- [x] SKILL.md에서 references 전 파일 도달 가능 (routing-smoke-test 링크 추가, validation-log는 validation-scenarios 경유)
- [x] 검증 로그 신설 (`references/validation-log.md`, 실행 규칙 포함)
- [x] G8: `~/.claude/CLAUDE.md` §5에 크로스 하네스 정본 규칙 1행 추가

## 6. 유의사항

- 이 스킬의 정체성은 **"선택형·비강제"** — 어떤 개선도 "모든 모듈 기본 활성화" 방향으로 흐르지 않게 유지 (smoke-test failure signals 기준 보존)
- 모듈 스킬 5종 본체는 이번 범위 밖 (패키지 스킬만 수정) — 앵커 계약은 모듈 스킬 수정 없이 패키지 레이어에서 삽입하는 방식으로 설계
- G8(CLAUDE.md 수정)은 기본 틀 변경이 아닌 §5 표에 1행 추가 수준이나, 사용자 확인 후 진행
