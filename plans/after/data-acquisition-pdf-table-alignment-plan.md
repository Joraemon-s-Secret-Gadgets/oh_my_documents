# 데이터 취득 PDF 표 정렬/폭 조정 계획

## Summary

- 대상은 PDF 전용 산출물 3종으로 제한한다.
  - `pdf/data_collect_plan.tex` / `.pdf`
  - `pdf/korea_data_acquisition_plan.tex` / `.pdf`
  - `pdf/japan_data_acquisition_plan.tex` / `.pdf`
- Markdown, HTML, `index.html`, 생성 스크립트는 수정하지 않는다.
- TeX의 `longtable` 컬럼 정의만 직접 조정하고 PDF를 재빌드한다.

## Key Changes

- 세 PDF TeX의 모든 표를 확인해 숫자, 버전, 날짜, 상태 코드, 순서처럼 짧고 정렬 기준이 명확한 컬럼을 가운데 정렬로 바꾼다.
- 해당 컬럼은 `m{...}` 폭을 좁히고, 줄어든 폭은 같은 표의 설명/기준/처리 내용/변경 내용 같은 긴 텍스트 컬럼에 배분한다.
- 긴 본문 컬럼은 왼쪽 정렬을 유지한다.
- 표 안의 의미 있는 문장, 값, 항목명은 변경하지 않는다.

## Implementation Details

- 선택된 컬럼은 `>{\RaggedRight\arraybackslash}`를 `>{\centering\arraybackslash}`로 변경한다.
- 폭 조정 기준:
  - 상태 코드: 약 `0.080`-`0.115\linewidth`
  - 순서: 약 `0.070`-`0.090\linewidth`
  - 버전: 약 `0.085`-`0.125\linewidth`
  - 날짜: 약 `0.120`-`0.135\linewidth`
  - 작성자/국가/구분/대상 등 짧은 라벨 컬럼: 내용 길이에 따라 `0.090`-`0.160\linewidth`
- 각 표의 전체 폭은 기존 합계와 거의 동일하게 유지한다.
- 향후 Markdown에서 PDF를 재생성하면 이번 TeX 직접 수정이 덮어써질 수 있다는 전제를 기록한다.

## Test Plan

- `xelatex`로 세 TeX 파일을 각각 2회 빌드해 PDF를 갱신한다.
- LaTeX 로그에서 다음 문제가 없는지 확인한다.
  - `Overfull \hbox`
  - `Missing character`
  - `! LaTeX Error`
- `git diff`로 변경 범위가 `pdf/*.tex`, `pdf/*.pdf`에만 한정되는지 확인한다.
- TeX diff에서 표 컬럼 폭/정렬 외 문서 본문 변경이 없는지 확인한다.
- 필요 시 `pdftotext -layout`으로 숫자/버전/상태 코드 컬럼이 가운데 정렬되어 보이는지 샘플 확인한다.

## Assumptions

- 이번 요청의 "표 전부"는 사용자가 선택한 데이터 취득 PDF 3종 안의 표 전체로 해석한다.
- 숫자/버전 컬럼 중심 정렬이 우선이며, 긴 설명성 컬럼은 가독성을 위해 왼쪽 정렬을 유지한다.
- 기존에 dirty 상태인 `docs/`, `pages/`, `index.html` 변경은 이번 작업 범위 밖으로 둔다.
