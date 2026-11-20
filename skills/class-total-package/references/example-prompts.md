# Example Prompts

Use these as representative invocation patterns for `class-total-package`.

## Basic package selection

- 수업 토탈 패키지에서 모든 스킬은 선택사항으로 두고, 이번에는 판서와 PBL만 묶어 줘.
- 수업 패키지로 사회과 수업을 구성해 줘. 판서와 마인드맵만 있으면 돼.
- 모듈을 정하지 않았어. 중학교 과학 개념을 한눈에 볼 수 있는 수업 패키지를 만들어 줘. → 판서와 마인드맵을 선정하고 그 이유를 설명한다.
- 중학생용 수업 패키지로 PBL과 수행평가를 같이 묶어 줘.

## Direct-skill handoff examples

These should not trigger `class-total-package` as the first choice:

- PBL만 설계해 줘.
- 판서안만 만들어 줘.
- HTML 마인드맵만 만들어 줘.
- 탐구 보고서 수행평가만 짜 줘.
- 고등학생용 탐구 보고서 수행평가만 필요해. 과제지와 기준표를 패키지로 줘. → `inquiry-report-assessment`에서 두 파일을 함께 만든다.

## Subject-specific package requests

- 사회과 탐구 수업 패키지로 PBL과 탐구 보고서 수행평가를 함께 설계해 줘.
- 국어 수업에서 고전 읽기 판서와 PBL을 연결해 줘.
- 수학 프로젝트 수업용으로 PBL 흐름과 HTML 학습지를 만들어 줘.
- 과학 수업용으로 실험 설계형 PBL과 평가 기준을 같이 짜 줘.

## Template-first requests

- 템플릿 기준으로만 구성해 줘. 자유 형식은 최소화해 줘.
- 수행평가는 사회과 변형 템플릿으로, PBL은 기본 템플릿으로 묶어 줘.
- 고등 심화형 수행평가 템플릿을 기준으로 PBL 패키지를 연결해 줘.
- 중등 공통형 탐구 보고서 수행평가와 PBL 수업을 간단형으로 묶어 줘.

## Full package requests

- 판서, 마인드맵, HTML 학습지, PBL, 수행평가를 모두 연결한 사회과 공개수업 패키지를 만들어 줘.
- 단원 수업용 전체 패키지를 짜 줘. 수업 흐름과 평가까지 한 번에 보고 싶어.
- 교사용 메모까지 포함한 패키지형으로 만들어 줘.

## AI and verification focused requests

- AI 사용과 정보 검증이 드러나는 PBL+수행평가 패키지로 설계해 줘.
- 학생들이 AI를 쓰더라도 검증 기록까지 포함하게 만들어 줘.
- 탐색, 토론, 글쓰기, AI 검증이 모두 보이도록 패키지를 짜 줘.

## Output-shaping requests

- 결과는 간단형으로 줘.
- 수업형으로 줘. 교사용 흐름 메모도 넣어 줘.
- 패키지형으로 줘. 학생 과제 안내문과 루브릭까지 포함해 줘.
- 판서와 HTML 학습지의 구성안만 줘. → `deliverable_stage: design`으로 검증한다.
- 판서와 인쇄할 HTML 학습지를 만들어 줘. → `deliverable_stage: generated`로 작성하고 HTML 파일에 학습지 전용 검사를 실행한다.
