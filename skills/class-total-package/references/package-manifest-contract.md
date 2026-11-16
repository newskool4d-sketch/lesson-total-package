# Package Manifest Contract

`package-manifest.json`은 두 개 이상의 모듈을 연결할 때 사용하는 내부 정본이다. 각 모듈의 native 출력 형식은 유지하며, 패키지 레이어는 선택·공통 내용·근거·검증 관계만 관리한다.

## 목적

- 공통 앵커를 한 번만 정의한다.
- 과제·자료·평가·산출물 사이의 연결을 안정적인 ID로 표현한다.
- 선택하지 않은 모듈의 과확장을 막는다.
- 수정 후 모든 관련 산출물을 재검증한다.
- 학생 개인정보와 확인되지 않은 교육과정 정보를 차단한다.

## Top-level schema

| Field | Required | Rule |
|---|---:|---|
| `schema_version` | O | 현재 `1.0` |
| `package_id` | O | 패키지 인스턴스의 유일 ID |
| `output_mode` | O | `간단형`·`수업형`·`패키지형` 중 하나 |
| `context` | O | 주제·교과·학교급·학년군·수업 시간 |
| `standard` | O | 코드·문장·상태·출처 |
| `anchor` | O | 모듈에 공통 삽입할 수업 앵커 |
| `learner_profile` | O | 비식별 지원·UDL·유연한 집단 규칙 |
| `pedagogy_profile` | O | 교과 비협상 원리와 선택 검증 |
| `modules` | O | 활성·비활성 모듈과 required 여부 |
| `tasks` | O | 학생 과제와 단계·시간·근거 |
| `sources` | O | 자료 위치·확인 상태·저작권 상태 |
| `artifacts` | O | 모듈 산출물·대상·경로·참조 ID |
| `criteria` | O | 평가 포인트와 근거 과제 |
| `safety` | O | 개인정보·AI·라이선스 게이트 |

## Anchor

`anchor`는 기존 [package-anchor-contract.md](package-anchor-contract.md)의 표시 형식과 같은 내용을 갖는다.

필수 필드:

- `topic`
- `grade_band`
- `subject`
- `objective`
- `essential_question`
- `key_concepts[]`
- `student_actions[]`
- `final_artifact`
- `evaluation_points[]`

성취기준은 `standard`에서 참조한다. 코드가 확정되지 않으면 `status: "pending"`, `confirmation_required: true`, 코드 또는 문장에 `확인 필요`를 남긴다.

## Relationship rules

- 모든 ID는 배열 안에서 유일해야 한다.
- 모든 `task_id`는 하나 이상의 `artifact.task_ids`에서 참조되어야 한다.
- `artifact.module_id`는 활성 모듈이어야 한다.
- `module.required`를 지정할 때는 boolean 값이어야 한다. `required: true`인 모듈은 활성 상태이며 해당 `module_id`를 가진 산출물이 최소 1개 있어야 한다. 선택 모듈(`required: false` 또는 생략)에는 이 의무를 적용하지 않는다.
- `task.module_owners`에는 비활성 모듈을 넣지 않는다.
- `artifact.source_ids`와 `criterion.task_ids`는 실제 ID만 참조한다.
- `module_owners`, `task_ids`, `source_ids`를 기재할 때는 비어 있지 않은 문자열을 원소로 하는 배열로 기록한다.
- 모든 과제 시간의 합은 `context.duration_minutes`와 같아야 한다.
- 경로는 패키지 루트 상대 경로이며 절대 경로, Windows 드라이브·루트 지정 경로, `..`를 허용하지 않는다. 심볼릭 링크·junction을 해석한 실제 대상도 루트 안에 있어야 한다.

## Source and safety rules

`standard.status`와 `source.verification_status`는 다음 중 하나다.

- `verified`: 출처와 문장이 확인됨
- `user-provided`: 사용자가 제공한 자료를 기준으로 함
- `pending`: 확인 전 상태. 확정형 문장으로 출력하지 않음

`copyright_status`는 `cleared`, `attribution_required`, `unknown` 중 하나다. `unknown`은 통과시키지 않으며, `attribution_required`에는 `attribution`을 기록한다.

학생 산출물에는 교사용 메모·학생 관찰 기록·정답 및 해설을 넣지 않는다. 이메일·전화번호·주민등록번호 형태의 값은 fixture와 산출물에 넣지 않는다.

검증기는 매니페스트 문자열과 로컬 산출물 본문에서 이메일·전화번호·주민등록번호 형태를 확인한다. 이름, 학번, 상세 진단 등 형태로 판별하기 어려운 정보는 작성·검토 단계에서 제거한다.

두 검증기는 같은 안전 검사를 사용한다. 매니페스트의 중첩 키·값을 먼저 검사하며 개인정보가 발견되면 해당 값을 오류 메시지에 출력하지 않는다. HTML은 원문, 엔티티를 해석한 값, 인라인 태그 사이의 연결된 텍스트, 속성값을 검사한다. 학생용 금지 표현에도 같은 텍스트 해석을 적용한다. jsDelivr npm의 고정 버전 구간만 이메일 검사에서 제외하며 URL의 나머지 부분은 검사한다. CSS·JavaScript 실행 후 생성되는 내용은 이 정적 검사의 범위 밖이다.

JSON·산출물 파일은 각각 최대 8 MiB이며, 메모리에서 받은 매니페스트는 문자열 합계 8,388,608자·키와 값을 포함한 100,000개 노드·깊이 64까지 검사한다. 한도를 넘으면 명시적 검증 오류를 반환하며 생략해서 통과시키지 않는다. `base_dir=None`인 Python API는 매니페스트만 검사하며 파일 존재·내용·경로 해석 검사는 수행하지 않는다.

## Learner variability and subject pedagogy

`learner_profile`은 [learner-variability-rules.md](learner-variability-rules.md)의 필수 필드와 비낙인·인지 요구 보존·지원 소거 규칙을 따른다. `pedagogy_profile.subject`는 `context.subject`와 같아야 하며, 교과별 비협상 원리와 이번 산출물에서 확인할 증거를 각각 하나 이상 가진다. 세부 생성 규칙은 직접 모듈의 정본을 우선한다.

## Korean secondary curriculum adapter

한국 중등 학습 그래프 MCP를 사용한 경우에만 다음 선택 필드를 추가한다.

- `curriculum_adapter`
- `taxonomy_version`
- `standard_key`
- `topic_ids[]`
- `prerequisite_edges[]`
- `transition_ids[]`
- `course_pathway_status`
- `data_release`

선수관계·중→고 전이·과목관계는 추천 구조로 기록한다. 의무 이수 순서나 학생 진단 결과로 표현하지 않는다. MCP가 없거나 범위 밖이면 `curriculum_adapter: "none"`과 `standard.status: "pending"`을 사용한다.

## Validation command

```powershell
py scripts/validate_package.py evals/fixtures/package-manifest.valid.json
```

정상 fixture는 종료 코드 0과 `PASS`를 반환해야 한다. 오류 fixture는 종료 코드 1과 구체적인 실패 항목을 반환해야 한다.
