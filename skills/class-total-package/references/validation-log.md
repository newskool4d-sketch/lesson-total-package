# Validation Log

스킬(SKILL.md·references) 수정 시 최소 1개 시나리오를 재실행하고 결과를 기록한다.
전체 시나리오 목록: [validation-scenarios.md](validation-scenarios.md)

## 실행 규칙

- 라우팅 관련 수정 → [routing-smoke-test.md](routing-smoke-test.md)의 must/must-not 케이스 우선
- 앵커·템플릿 관련 수정 → full-package 시나리오 우선 (앵커 블록 diff 0 확인)
- 실패 시: 원인 요약을 기록하고 수정 후 재실행 결과를 새 행으로 추가한다

## 기록

| 날짜 | 수정 내용 | 실행 시나리오 | 결과 | 비고 |
|---|---|---|---|---|
| 2026-07-06 | 앵커 계약 신설, 모드×모듈 매트릭스, 저장 규약, 편입 기준 추가 | (미실행) | 보류 | 다음 실제 패키지 요청 시 full-package 기준으로 확인 |
| 2026-07-30 | package manifest 계약·validator MVP·출처/개인정보/학생자료 게이트 추가 | `evals/fixtures/package-manifest.valid.json` + `package-manifest.invalid.json` + `py -m unittest tests.test_validate_package -v` | PASS | 정상 fixture 종료 코드 0, 오류 fixture 종료 코드 1, unittest 4건 통과. 기존 패키지 5종 시나리오는 별도 실행 필요 |
| 2026-07-30 | 한국형 P/R/O/M/S 24개 루브릭과 fixture 실행기 추가 | `py scripts/run_contract_tests.py` + `py -m unittest discover -s tests -v` | PASS | 루브릭 24개·fixture 2개·전체 unittest 6건 통과 |
| 2026-07-30 | 학습자 다양성·교과 원리·대상/밀도 계약과 validator 게이트 추가 | `py -m unittest discover -s tests -v` + `py scripts/run_contract_tests.py` | PASS | 비식별 프로필·인지 요구 보존·비낙인 학생자료·교과 일치 검사 통과 |
| 2026-07-30 | 차별화 수업 직접 스킬 프로토타입·support/core/extension 계약·학생자료 게이트 추가 | `py -m unittest discover -s tests -v` + `py scripts/run_contract_tests.py` + differentiation valid/invalid CLI fixture | PASS | 전체 unittest 13건, 패키지 rubric 24개·fixture 2개, 차별화 정상 0/오류 1 종료 코드 확인. 정식 형제 스킬 편입은 보류 |
| 2026-11-05 | 매니페스트 개인정보·참조 배열, 차별화 학생 자료·과제 검증 보강 | Windows Python 단위 테스트, 계약 실행기, 두 검증기 정상·오류 CLI fixture | PASS | 23건 통과, 루브릭 24개와 패키지 fixture 2개 통과. 각 CLI의 정상 0·오류 1 확인 |
| 2026-11-05 | 목표–증거 연결표, 형성평가 대응 카드, 피드백·재도전 칸 반영 | 중학교 과학 판서+마인드맵 수업형 시나리오를 가상 관찰 사례로 독립 수동 재실행 | PASS | 모듈 선택, 목표·증거·준거, 반응별 대응·재확인, 재도전, 간단형 경계, 학생·교사 분리 6항목 확인. 자동 스킬 호출·HTML 렌더링·교실 적용 미검증 |
| 2026-11-05 | jsDelivr npm 버전 토큰의 이메일 오탐 수정 | 원래 CDN 링크를 포함한 중학교 과학 마인드맵 패키지 CLI, 이메일 차단 회귀 테스트 | PASS | 같은 링크로 수정 전 종료 코드 1, 수정 후 0. HTML 본문·메일 링크·URL 경로와 쿼리 등 6개 입력 사례 차단. 전체 단위 테스트 25건, 루브릭 24개와 패키지 fixture 2개 통과 |
| 2026-11-16 | 적대적 리뷰 6건 수정: 공통 개인정보·HTML 해석·실경로 경계, enum 타입, 필수 모듈 산출물, 이메일 검사 성능 | 원본·배포 사본의 전체 unittest, 계약 실행기, 두 검증기 정상·오류 CLI, 기존 중학교 과학 패키지 | PASS | 각 사본 45개 테스트(20개 추가), 루브릭 24개·fixture 2개 통과. 외부 디렉터리 링크·Windows 경로 변형·민감값 오류 출력·입력 한도·생략된 head/body 태그 회귀 포함. 20만 자 이메일 유사 입력 약 0.01초, 합성 이메일 판정 3만 건 비교 일치. HTML/CSS/JavaScript 브라우저 실행은 검증 범위 밖 |
| 2026-11-20 | 리뷰 지적 8건 수정. 실물·설계 구분과 HTML 검사, 교사용 내용 분리, 공통 앵커, 학생 과제 전달, 성취기준 상태, 출처 파일, 모듈 설치 점검, 단일 요청 라우팅 | Windows Python 전체 단위 테스트 및 계약 검사, 기존 과학·국제사회 수업 자료 검증 | PASS | 설치본·배포본 각각 75/75 통과(기존 45개와 신규 30개). 루브릭 구조 24항목·패키지 fixture 2개 및 기존 중학교 과학 패키지 양쪽 통과. 오프라인 Chrome에서 과학 마인드맵 가지 5개 펼침·접힘 확인. 국제사회 HTML 3종은 양 사본 6개 모두 전용 검사 11/11, 각각 A4 2쪽 PDF 출력, 빈 페이지 0쪽. 경로 지정 단독 설치에서 선택 모듈 누락 감지, 현재 PC에서는 5개 모두 확인. Codex UI 자연어 자동 선택·온라인 아이콘·실물 프린터는 미검증. |
