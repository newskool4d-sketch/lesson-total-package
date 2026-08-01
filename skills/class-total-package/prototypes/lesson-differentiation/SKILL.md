---
name: lesson-differentiation
description: Adapt an existing Korean secondary lesson into support, core, and extension profiles while preserving the same goal, context, and cognitive demand.
metadata:
  status: prototype-not-active
  short-description: 비식별 학습자 지원과 동일 목표를 보장하는 차별화 직접 스킬 초안
---

# Lesson Differentiation (Prototype)

이 프로토타입은 `class-total-package`에 아직 활성 모듈로 편입하지 않는다. 먼저 [references/differentiation-contract.md](references/differentiation-contract.md)와 `scripts/validate_differentiation.py`를 통과시킨 뒤 독립 스킬로 승격한다.

## Routing

- 기존 수업·수업 패키지를 수준별 지원으로 조정해 달라는 요청에만 사용한다.
- 새 수업을 처음 만드는 요청은 수업 설계 또는 선택된 직접 모듈로 보낸다.
- 평가·채점만 요청된 경우 수행평가 직접 스킬로 보낸다.
- 입력에 학생 이름·학번·상세 진단이 있으면 비식별 지원 정보로 바꾸거나 재공유를 요청한다.

## Required intake

확인할 항목은 기존 수업, 교과, 학년군, 성취기준 상태, 수업 시간, 학습자 지원 정보다. 정보가 없으면 UDL 기본값을 적용하되 교사에게 고지한다.

## Non-negotiables

1. 세 프로필은 같은 핵심 목표·맥락·성취기준을 유지한다.
2. 모든 프로필은 핵심 과제와 구조적 난도를 유지한다.
3. 지원 프로필은 초기 과제에 더 많은 지원을 두고 점차 줄인다.
4. 확장 프로필은 같은 맥락에서 전이·설명·근거 확장 과제를 추가한다.
5. 집단 편성 근거는 현재 수업의 증거이며 다음 형성평가로 재편할 수 있다.
6. 학생 자료에는 수준·능력군·교사용 평가 용어를 표시하지 않는다.

## Output contract

하나의 differentiation manifest에서 다음을 연결한다.

- 교사 계획: 공통 목표, 집단 편성 근거, 지원 차이, 형성평가, 다음 단계
- 지원 프로필 학생 자료: 핵심 과제 + 자연스러운 접근 지원
- 기본 프로필 학생 자료: 핵심 과제 + 최소 공통 지원
- 확장 프로필 학생 자료: 핵심 과제 + 전이·근거 확장

산출 전 `py scripts/validate_differentiation.py <manifest>`를 실행한다. 실패하면 문서를 제시하지 않고 원인을 수정한다.

## Prototype boundary

현재는 패키지의 선택 모듈 목록에 포함하지 않는다. 단독 smoke test, 템플릿팩, 직접 스킬 경로, 개인정보·저작권 검토를 완료한 뒤 Module admission criteria로 승격한다.
