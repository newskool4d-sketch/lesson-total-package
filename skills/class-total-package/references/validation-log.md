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
