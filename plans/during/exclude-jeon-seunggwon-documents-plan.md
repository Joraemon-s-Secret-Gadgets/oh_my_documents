---
작성자: llm팀
상태: 진행후
---

# 팀원 제외 문서 정리 계획

## 목적

현재 배포용 PDF 표지와 PDF 생성 명령에 남아 있는 제외 대상 팀원 표기를 제거하고, 이후 PDF 재생성 시 동일한 표기가 다시 들어가지 않도록 관련 생성 지침을 함께 정리한다.

## 대상 파일

- 전체 Markdown 문서: `*.md` 365개
- `pdf/*.tex`: 현재 배포용 PDF의 표지 팀원 목록
- `pdf/*.pdf`: TeX 재빌드 결과물
- `pdf/AGENT.md`: PDF 표지 규칙과 대표 생성 명령
- `plans/before/agent-spec-pdf-refresh-plan.md`: Agent 명세 PDF 생성 명령
- `plans/during/korea-acquisition-updated-pdf-plan.md`: 데이터 취득/전처리 PDF 생성 명령
- `plans/after/database-design-html-pdf-neptune-sync-plan.md`: DB 설계 PDF 생성 명령

## 유지할 항목

- 문서 제목, 서비스 라벨, 팀명, 멘토 표기
- 기존 `docs/` Markdown 원본과 `pages/` HTML 생성물
- 변경 이력에 기록된 실제 작성자명

## 변경할 항목

- 팀원 목록을 `이창우, 전종혁, 조동휘, 최수아`로 정리
- 위 팀원 목록을 포함한 PDF 생성 예시 명령

## Markdown 확인 결과

- 전체 Markdown 문서 365개를 대상으로 제외 대상 팀원명과 이전 5인 팀원 목록 패턴을 검색했다.
- `docs/` 원본 Markdown에는 수정 대상 표기가 없었다.
- 현재 4인 팀원 목록은 `pdf/AGENT.md`와 PDF 생성 계획 Markdown의 명령 예시에만 남아 있으며, 모두 최신 목록이다.

## 작업 체크리스트

- [x] 제외 대상 팀원 표기 포함 파일 전체 목록 확인
- [x] 전체 Markdown 문서에서 제외 대상 팀원 표기와 이전 팀원 목록 패턴 확인
- [x] 팀원 목록과 PDF 생성 명령에서 제외 대상 팀원 표기 제거
- [x] 변경된 TeX로 PDF 재빌드
- [x] `docs/`와 `pages/`가 변경되지 않았는지 확인
- [x] 잔여 참조와 PDF 텍스트 추출 결과 검증

## 검증 방법

- 제외 대상 팀원명 대상 `rg -n` 검색
- 전체 Markdown 대상 이전 팀원 목록 패턴 검색
- `pdftotext -layout` 기반 PDF 텍스트 추출 후 제외 대상 팀원명 검색
- `git diff --name-only -- docs pages`
- `git diff --check`
