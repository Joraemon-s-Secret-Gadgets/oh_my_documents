# 슬라이드 5 — 시스템 흐름

> 원본 위치: `../01_midterm_presentation.md`
> 상태: Slide Content
> 역할: 사용자 흐름이 아니라 책임 경계를 보여주는 시스템 개요

## 화면 문구

**책임 경계로 나눕니다**

| 계층 | 역할 |
| --- | --- |
| Client Web | 입력, 지도, 결과 표시 |
| Backend API / SAM | 인증, 검증, 추천 실행 |
| Agent Runtime | 검색, 검증, 일정 생성 |
| Retrieval & Data | 근거 후보, 정규 상세, 캐시 |
| External APIs | 지도, 날씨, 딥링크 |

## 발표자 노트

- Client, Backend, Agent, Data, External API의 책임을 분리한다.
- 세부 Agent 동작은 뒤 장에서 확대한다.

## 제작 체크

- [ ] 유저 흐름처럼 보이지 않게 계층명과 책임만 남긴다.
