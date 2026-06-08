# 데이터 취득 PDF 표 단독 값 글자 크기 보정 계획

## Summary

- 대상은 데이터 취득 PDF 3종의 TeX/PDF 산출물로 제한한다.
  - `pdf/data_collect_plan.tex` / `.pdf`
  - `pdf/korea_data_acquisition_plan.tex` / `.pdf`
  - `pdf/japan_data_acquisition_plan.tex` / `.pdf`
- 표 안에서 단독으로 들어간 값이 주변 표 본문보다 작게 보이는 경우만 보정한다.
- Markdown, HTML, `index.html`, 생성 스크립트는 수정하지 않는다.

## Key Changes

- 표 셀 안의 단독 파일 경로에서 `\mbox{\footnotesize ...}` 축소 래퍼를 제거하고 일반 `\texttt{...}` 크기로 맞춘다.
- 표 셀 안의 단독 엔티티명/출처명에서 `{\scriptsize ...}` 래퍼를 제거한다.
- 변경 이력 표의 날짜 값에서 `{\footnotesize ...}` 래퍼를 제거해 버전/작성자와 같은 크기로 맞춘다.
- 표 캡션, 페이지 헤더, 전체 `small`/`footnotesize` 표 환경은 유지한다.

## Test Plan

- 세 TeX 파일을 각각 `xelatex`로 2회 빌드해 PDF를 갱신한다.
- 로그에서 `Overfull \hbox`, `Missing character`, `! LaTeX Error`를 확인한다.
- TeX diff가 글자 크기 래퍼 제거 중심인지 확인한다.
- `docs/`, `pages/`, `index.html`은 이번 작업에서 수정하지 않는다.
