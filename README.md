# Lesson Total Package

> 필요한 모듈만 골라 쓰는 한국어 수업 설계 패키지 플러그인 for Codex

---

## 개요

`lesson-total-package`는 판서, 마인드맵, PBL, 탐구 보고서 수행평가를 하나의 번들로 묶은 Codex 플러그인입니다.

모든 모듈은 기본적으로 **선택 사항**입니다. 필요한 모듈만 골라 쓸 수 있으며, 전체를 한꺼번에 출력하도록 강제하지 않습니다.

현재 플러그인 버전은 `0.1.0`입니다.

---

## 포함 모듈

| 모듈 | 역할 |
|------|------|
| `board-writing-generator` | 교실 수업용 판서 구조·보드 흐름 설계 |
| `mindmap-html-generator` | 데스크톱 우선 시각형 HTML 마인드맵 생성 |
| `pbl-lesson-designer` | 토론·탐색·글쓰기 기반 PBL 수업 설계 |
| `inquiry-report-assessment` | 탐구 보고서형 수행평가 설계 |

---

## 사용 예시

```
판서와 마인드맵만 묶어서 중학교 과학 수업 설계해줘.
```

```
고등학교 사회과 PBL 수업과 탐구 보고서 수행평가를 함께 설계해줘.
```

```
판서, 마인드맵, PBL, 수행평가를 모두 연결한 공개수업 패키지를 패키지형으로 만들어줘.
```

---

## 출력 모드

| 모드 | 내용 |
|------|------|
| `간단형` | 선택한 핵심 모듈만 출력 |
| `수업형` | 선택 모듈 + 교사용 흐름 메모 (기본값) |
| `패키지형` | 선택 모듈 + 평가·산출물 계획까지 포함 |

---

## 모듈 선택 가이드

| 목적 | 권장 모듈 |
|------|-----------|
| 개념 정리 중심 수업 | `board-writing-generator` 또는 `mindmap-html-generator` |
| 수업 시각화까지 필요 | `board-writing-generator` + `mindmap-html-generator` |
| 프로젝트형 문제 해결 | `pbl-lesson-designer` |
| 보고서형 결과물 평가 | `inquiry-report-assessment` |
| 수업과 평가를 함께 설계 | `pbl-lesson-designer` + `inquiry-report-assessment` |
| 전체 수업 패키지 | 4개 모듈 전체 |

---

## 설치

Codex CLI에서 로컬 플러그인으로 설치합니다.

```bash
# 저장소 클론
git clone https://github.com/newskool4d-sketch/lesson-total-package.git
cd lesson-total-package

# Codex 플러그인 디렉터리로 복사 또는 연결
# plugin.json 이 있는 루트 디렉터리를 등록 대상으로 사용
```

플러그인 메타데이터는 `.codex-plugin/plugin.json`에 있고, 실제 스킬 본문은 `skills/class-total-package/` 아래에 있습니다.

---

## 저장소 구조

| 경로 | 내용 |
|------|------|
| `.codex-plugin/plugin.json` | 플러그인 메타데이터와 인터페이스 정의 |
| `skills/class-total-package/SKILL.md` | 핵심 스킬 설명과 실행 규칙 |
| `skills/class-total-package/agents/openai.yaml` | 에이전트 설정 |
| `skills/class-total-package/references/` | 예시 프롬프트, 조합 규칙, 검증 시나리오 |

---

## 개발 및 배포

```bash
# 변경 확인
git status

# 버전 태그 확인
git tag
```

첫 공개 버전 태그는 `v0.1.0`을 기준으로 관리합니다.

---

## 참고한 스킬 및 레퍼런스

이 저장소의 개선·검증·학습지 산출물은 아래 자료를 참고했습니다. 외부 자료의 원문이나 사용자 보유 교과서 PDF는 저장소에 복제하지 않았습니다.

### 구현에 사용한 Codex 스킬

| 스킬 | 적용 범위 | 위치 또는 링크 |
|------|------|------|
| `class-total-package` | 모듈 선택, 공통 앵커, 패키지 manifest, 학습자·교과·대상 계약 | [`skills/class-total-package/SKILL.md`](./skills/class-total-package/SKILL.md) |
| `html-worksheet-generator` | PDF 근거 학습지, A4 인쇄 CSS, 교사용·학생용 분리, HTML 검증 | Codex 로컬 런타임 스킬 |
| `education-file-intake` | 교과서 PDF 페이지 범위 확인과 후속 학습지 라우팅 | Codex 로컬 런타임 스킬 |
| `mcp-health` | MCP 등록·활성화 상태 진단 절차 | Codex 로컬 런타임 스킬 |
| `github:yeet` | 변경 범위 확인, 작업 브랜치, 커밋·푸시 절차 | Codex GitHub 배포 스킬 |

### 외부 레퍼런스

| 레퍼런스 | 참고 내용 |
|------|------|
| [`anthropics/k12-teacher-skills`](https://github.com/anthropics/k12-teacher-skills) | 교사 업무 스킬 구조, 안전·검증·교사용 산출물 설계의 벤치마크 |
| [`raphysicst-create/korean-secondary-learning-map-mcp`](https://github.com/raphysicst-create/korean-secondary-learning-map-mcp) | 중등 성취기준·주제·선수학습 관계 MCP의 연결 대상 |
| [`newskool4d-sketch/lesson-total-package`](https://github.com/newskool4d-sketch/lesson-total-package) | 본 구현의 저장소·플러그인 구조·배포 기준 |

### MCP 조회 근거

`korean-secondary-learning-map` MCP에서 다음 2022 개정 중학교 사회 성취기준을 조회하여 국제 사회 학습지에 반영했습니다.

- `[9사(일사)11-01]` 국제 사회를 구성하는 여러 행위 주체의 활동을 조사하고, 이를 토대로 국제 사회의 특징을 도출한다.
- `[9사(일사)11-02]` 국제 사회의 다양한 분쟁에 대해 조사하고, 지역·국가·세계의 시민으로서 우리의 역할에 대해 토의한다.
- 원자료 식별자: `kr-nec-2024-3-annex7`, 교육과정: `kr-2022-middle-사회`, 원문 PDF 71쪽

교사용 교과서 PDF는 사용자가 제공한 로컬 원본을 근거로 109~110쪽만 읽었으며, 저작권 보호를 위해 저장소에는 포함하지 않았습니다.

---

## 라이선스

[MIT](./LICENSE)

---

## 개인정보처리방침 및 이용약관

- [개인정보처리방침](./PRIVACY.md)
- [이용약관](./TERMS.md)

---

## 제작자

Hong Ju-hyung · [github.com/newskool4d-sketch](https://github.com/newskool4d-sketch) · newskool4d@gmail.com
