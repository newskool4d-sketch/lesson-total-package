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

## Admission gates

- 정식 직접 스킬이 독립 경로에 존재한다.
- 학생·교사 대상이 분리된다.
- 수준 낙인 표현과 개인정보가 없다.
- 지원 소거와 유연한 집단 재편성 근거가 있다.
- 단독 routing smoke test와 fixture validator가 통과한다.
- 템플릿팩과 실제 출력 예시가 있다.
