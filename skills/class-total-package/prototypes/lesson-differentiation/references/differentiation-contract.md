# Differentiation Contract (Prototype)

차별화는 서로 다른 수업을 세 개 만드는 것이 아니라 같은 목표와 맥락에 접근 경로를 다르게 제공하는 것이다.

## Required manifest

- `shared_context`, `shared_objective`, `standard`
- `core_task_ids[]`
- `tiers[]`: `support`, `core`, `extension` 정확히 3개
- `grouping.basis`, `grouping.revisable: true`
- 학생용 `artifacts[]`
- `safety.pii_check: passed`, `safety.no_ability_labels: true`

## Tier rules

| Tier | Required behavior |
|---|---|
| `support` | 모든 핵심 과제, 구체적 접근 지원, `scaffold_fade: true` |
| `core` | 모든 핵심 과제, 최소 공통 지원, `scaffold_fade: true` |
| `extension` | 모든 핵심 과제, 전이·근거 확장 과제, `scaffold_fade: true` |

세 tier의 `task_ids`는 `core_task_ids`를 모두 포함해야 한다. 맥락·목표·성취기준을 tier별로 바꾸지 않는다.

## Artifact rules

- `support`, `core`, `extension` 각각에 `audience: student`인 산출물이 최소 1개 있어야 한다. `teacher`·`shared` 산출물은 이를 대신하지 않는다.
- 모든 산출물의 `tier_id`는 위 세 문자열 중 하나이며, `task_ids`는 비어 있지 않은 문자열로 이루어진 목록이어야 한다.
- 산출물의 과제 ID는 해당 tier의 `task_ids` 또는 `extension_task_ids`에 선언되어 있어야 한다. 다른 tier에만 선언된 과제는 참조할 수 없다.
- 각 tier의 학생 산출물 전체가 `core_task_ids`와 해당 tier의 `extension_task_ids`를 모두 포함해야 한다. 과제는 여러 학생 산출물에 나눠 담을 수 있으며, 교사·공유 산출물의 과제는 이 충족 여부에 포함하지 않는다.
- 매니페스트 중첩 키·값과 모든 산출물에서 이메일·전화번호·주민등록번호 형태를 검사한다. `safety.pii_check: passed` 선언만으로 검사를 대체하지 않는다. 개인정보 오류에 원문 값을 출력하지 않는다.
- 개인정보·HTML 해석·경로 경계·입력 한도는 [패키지 공통 안전 규칙](../../../references/package-manifest-contract.md#source-and-safety-rules)을 따른다. 학생용·공용 자료 모두 교사용 메모·정답 해설과 수준 낙인 표현을 검사하며 엔티티와 인라인 태그가 해석된 텍스트도 확인한다.

## Admission gates

- 정식 직접 스킬이 독립 경로에 존재한다.
- 학생·교사 대상이 분리된다.
- 수준 낙인 표현과 개인정보가 없다.
- 지원 소거와 유연한 집단 재편성 근거가 있다.
- 단독 routing smoke test와 fixture validator가 통과한다.
- 템플릿팩과 실제 출력 예시가 있다.
