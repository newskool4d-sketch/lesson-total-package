# Lesson Total Package

> 필요한 모듈만 골라 쓰는 한국어 수업 설계 패키지 플러그인 for Codex

---

## 개요

`lesson-total-package`는 판서, 마인드맵, PBL, 탐구 보고서 수행평가를 하나의 번들로 묶은 Codex 플러그인입니다.

모든 모듈은 기본적으로 **선택 사항**입니다. 필요한 모듈만 골라 쓸 수 있으며, 전체를 한꺼번에 출력하도록 강제하지 않습니다.

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
git clone https://github.com/newskool4d-sketch/lesson-total-package

# Codex에서 플러그인 경로 등록 후 사용
```

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
