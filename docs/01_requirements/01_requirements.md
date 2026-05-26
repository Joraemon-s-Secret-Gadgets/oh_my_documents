```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>로브 (Lovv) — 요구사항 정의서 v1.1</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+KR:wght@600;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../assets/css/requirements.css" />
  </head>
  <body>
    <div class="layout">
      <!-- ═══ SIDEBAR ═══ -->
      <aside>
        <div class="aside-brand">
          <div class="aside-logo">🗺 로브</div>
          <div class="aside-ver">Requirements Spec · v1.1</div>
          <div class="aside-status">
            <div class="status-dot"></div>
            <span>기획 단계</span>
          </div>
        </div>
        <nav class="toc">
          <div class="toc-section">
            <a class="toc-link active" href="#cover">표지 / 문서 정보</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">1. 문서 개요</div>
            <a class="toc-link" href="#s1-1">1.1 목적</a>
            <a class="toc-link" href="#s1-2">1.2 범위</a>
            <a class="toc-link" href="#s1-3">1.3 용어 정의</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">2. 서비스 개요</div>
            <a class="toc-link" href="#s2-1">2.1 서비스 소개</a>
            <a class="toc-link" href="#s2-2">2.2 핵심 가치 제안</a>
            <a class="toc-link" href="#s2-3">2.3 타겟 사용자</a>
            <a class="toc-link" href="#s2-4">2.4 서비스 흐름</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">3. 기능 요구사항</div>
            <a class="toc-link" href="#s3-1">3.1 공통 사용자 인터페이스</a>
            <a class="toc-link" href="#s3-2">3.2 추천·탐색 기능</a>
            <a class="toc-link" href="#s3-3">3.3 지도·위치·경로 기능</a>
            <a class="toc-link" href="#s3-4">3.4 RAG·챗봇·에이전트</a>
            <a class="toc-link" href="#s3-5">3.5 외부 데이터/API 연동</a>
            <a class="toc-link" href="#s3-6">3.6 서비스별 세부 기능</a>
            <a class="toc-link" href="#s3-7">3.7 운영·관리·검증 기능</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">4. API 연동 요구사항</div>
            <a class="toc-link" href="#s4-1">4.1 Google Maps</a>
            <a class="toc-link" href="#s4-2">4.2 Kakao Maps</a>
            <a class="toc-link" href="#s4-3">4.3 Yahoo Japan</a>
            <a class="toc-link" href="#s4-4">4.4 WeatherAPI</a>
            <a class="toc-link" href="#s4-5">4.5 연동 현황 요약</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">5. 비기능 요구사항</div>
            <a class="toc-link" href="#s5-1">5.1 성능</a>
            <a class="toc-link" href="#s5-2">5.2 보안</a>
            <a class="toc-link" href="#s5-3">5.3 호환성</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">6. 데이터 요구사항</div>
            <a class="toc-link" href="#s6-1">6.1 필요 데이터 항목</a>
            <a class="toc-link" href="#s6-2">6.2 데이터 품질 기준</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">7. 제약사항 및 가정</div>
            <a class="toc-link" href="#s7-1">7.1 기술적 제약</a>
            <a class="toc-link" href="#s7-2">7.2 가정사항</a>
          </div>
          <div class="toc-section">
            <a class="toc-section-hd toc-section-link" href="#s8">8. 변경 이력</a>
          </div>
        </nav>
        <div class="aside-footer">
          <button class="print-btn" onclick="window.print()">
            🖨 인쇄 / PDF 저장
          </button>
          CONFIDENTIAL<br />외부 공유 금지
        </div>
      </aside>

      <!-- ═══ MAIN ═══ -->
      <main>
        <!-- COVER -->
        <div class="doc-cover" id="cover">
          <div class="cover-label">Requirements Specification Document</div>
          <div class="cover-title">로브 (Lovv)</div>
          <div class="cover-subtitle">
            Local(소도시) + Vibe(분위기·감성), 또는 Voyage(항해·여행)를 뜻한다.
            일반적인 Love와 달리 알파벳 v를 겹쳐 써서 트렌디한 스타트업이나
            테크 서비스 같은 힙한 인상을 준다.
          </div>
          <div class="cover-meta">
            <div class="meta-item">
              <div class="meta-key">문서 버전</div>
              <div class="meta-val">v1.1 — 기획 개정</div>
            </div>
            <div class="meta-item">
              <div class="meta-key">작성일</div>
              <div class="meta-val" id="todayDate"></div>
            </div>
            <div class="meta-item">
              <div class="meta-key">문서 상태</div>
              <div class="meta-val green">기획 단계 (Planning)</div>
            </div>
            <div class="meta-item">
              <div class="meta-key">적용 범위</div>
              <div class="meta-val">로브 서비스 전체</div>
            </div>
          </div>
        </div>



        <!-- ═══ 1. 문서 개요 ═══ -->
        <div class="doc-section" id="s1">
          <div class="section-num">Section 01</div>
          <h1 class="s-h1">1. 문서 개요</h1>

          <h2 class="s-h2" id="s1-1">1.1 목적</h2>
          <p class="doc-p">
            본 문서는 로브(Lovv) 서비스의 아이디어 기획 단계에서
            제품의 핵심 기능, API 연동 요구사항, 비기능 요구사항을 정의한다.
            개발 착수 전 이해관계자 간 요구사항에 대한 공통 이해를 확보하는 것을
            목적으로 한다.
          </p>

          <h2 class="s-h2" id="s1-2">1.2 범위</h2>
          <p class="doc-p">본 문서는 다음 범위를 포함한다.</p>
          <ul class="bullet-list">
            <li>
              대화형 챗봇 인터페이스 및 6개 테마 기반 소도시 여정 추천 엔진
            </li>
            <li>
              국내 소도시 (강원·전남·경남 등) 및 일본 소도시 (호쿠리쿠·기후·산인
              등) 추천 — 나라별 독립 트랙
            </li>
            <li>
              여행 시기(달/계절) 입력에 따른 계절 적합 소도시 및 축제·행사 연동
            </li>
            <li>
              RAG(검색증강) 기반 grounding 및 멀티스텝 에이전트 추천 파이프라인
            </li>
            <li>
              Google Maps Platform, Kakao Maps, Yahoo Japan, WeatherAPI 연동
            </li>
            <li>지도 표시, 장소 상세 정보, 날씨 정보, 외부 링크 제공 기능</li>
          </ul>

          <h2 class="s-h2" id="s1-3">1.3 용어 정의</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">용어</th>
                <th>정의</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell">오버투어리즘</td>
                <td>
                  특정 여행지에 관광객이 과도하게 집중되어 현지 생활환경·자연이
                  훼손되는 현상
                </td>
              </tr>
              <tr>
                <td class="key-cell">소도시</td>
                <td>
                  관광객 집중도가 낮고 로컬 경험이 풍부한 지방 도시 및 읍·면
                  단위 지역
                </td>
              </tr>
              <tr>
                <td class="key-cell">테마</td>
                <td>
                  소도시를 묶는 6개 분류 축 — 온천·휴양 / 바다·해안 / 역사·전통
                  / 미식·노포 / 자연·트레킹 / 예술·감성
                </td>
              </tr>
              <tr>
                <td class="key-cell">여정 (Route)</td>
                <td>
                  하나의 테마로 묶인 2~4개 소도시와 방문 순서로 구성된 추천 결과
                  단위
                </td>
              </tr>
              <tr>
                <td class="key-cell">계절 적합도</td>
                <td>
                  각 소도시가 봄·여름·가을·겨울 각 시기에 얼마나 적합한지
                  나타내는 점수
                </td>
              </tr>
              <tr>
                <td class="key-cell">RAG</td>
                <td>
                  검색증강생성 — LLM이 답변 시 소도시 관련 지식 데이터를 검색해
                  근거로 활용, 환각을 방지하는 기법
                </td>
              </tr>
              <tr>
                <td class="key-cell">멀티스텝 에이전트</td>
                <td>
                  추천을 단일 호출이 아닌 "분류 → 검색 → 군집 → 여정 구성"
                  단계로 나눠 처리하는 LLM 파이프라인
                </td>
              </tr>
              <tr>
                <td class="key-cell">추천 엔진</td>
                <td>
                  사용자의 취향·시기·혼잡도·이동 편의를 입력받아 테마 여정을
                  제안하는 RAG·에이전트 기반 시스템
                </td>
              </tr>
              <tr>
                <td class="key-cell">드로어 (Drawer)</td>
                <td>하단에서 슬라이드업되는 상세 정보 패널 UI 컴포넌트</td>
              </tr>
              <tr>
                <td class="key-cell">API 딥링크</td>
                <td>
                  API 직접 호출 없이 외부 플랫폼(Kakao, Yahoo)의
                  검색·지도 페이지로 연결하는 URL
                </td>
              </tr>
              <tr>
                <td class="key-cell">CORS 제약</td>
                <td>
                  브라우저 보안 정책(Same-Origin Policy)으로 인해 외부 API를
                  클라이언트에서 직접 호출할 수 없는 제약
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 2. 서비스 개요 ═══ -->
        <div class="doc-section" id="s2">
          <div class="section-num">Section 02</div>
          <h1 class="s-h1">2. 서비스 개요</h1>

          <h2 class="s-h2" id="s2-1">2.1 서비스 소개</h2>
          <p class="doc-p">
            로브(Lovv)는 오버투어리즘 회피를 목적으로 국내 및 일본의 비주류
            소도시를 6개 테마 여정으로 추천하는 대화형 챗봇 서비스다. 사용자가
            자연어로 취향과 여행 시기를 입력하면, 멀티스텝 에이전트가 취향을
            테마로 해석하고 RAG로 검색한 소도시 데이터에 근거하여 적합한 소도시
            2~4곳을 하나의 여정으로 묶어 추천 이유와 함께 제공한다. 한국은 한국
            소도시만, 일본은 일본 소도시만 추천하는 나라별 독립 트랙으로
            운영된다.
          </p>
          <p class="doc-p">
            서비스명 로브(Lovv)는 Local(소도시)과 Vibe(분위기·감성), 또는
            Voyage(항해·여행)의 의미를 결합한 이름이다. 일반적인 Love와 달리
            알파벳 v를 겹쳐 사용해 감성적인 여행 서비스이면서도 트렌디한
            스타트업·테크 서비스의 인상을 전달한다.
          </p>
          <p class="doc-p">
            추천 시 여행 시기(달/계절)에 빛나는 소도시와 그 시기 열리는
            축제·행사를 함께 묶어 제공하며, 각 결과에는 Google Maps, Kakao Maps, Yahoo Japan, WeatherAPI의 4개 플랫폼 API가 역할 분담하여 지도·장소
            상세·날씨·링크 정보를 보완 제공한다.
          </p>

          <h2 class="s-h2" id="s2-2">2.2 핵심 가치 제안</h2>
          <table class="val-tbl">
            <thead>
              <tr>
                <th style="width:28%">가치 항목</th>
                <th>설명</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="val-key">테마 여정 추천</td>
                <td>
                  단일 도시가 아닌 6개 테마로 묶은 2~4곳 소도시 여정을 설계해
                  제공
                </td>
              </tr>
              <tr>
                <td class="val-key">계절·축제 연동</td>
                <td>
                  여행 시기에 빛나는 소도시와 그 시기 축제·행사를 함께 추천
                  (시간축 확장)
                </td>
              </tr>
              <tr>
                <td class="val-key">혼잡 회피형 추천</td>
                <td>단순 인기순이 아닌 혼잡도 낮은 대체 여행지를 우선 추천</td>
              </tr>
              <tr>
                <td class="val-key">RAG 기반 정확성</td>
                <td>
                  직접 구축한 소도시 데이터를 검색·근거로 활용해 환각 없는 사실
                  기반 추천
                </td>
              </tr>
              <tr>
                <td class="val-key">멀티스텝 에이전트</td>
                <td>
                  분류→검색→군집→여정 구성을 단계별로 추론하여 추천 품질 확보
                </td>
              </tr>
              <tr>
                <td class="val-key">국내·일본 통합</td>
                <td>
                  한국 소도시와 일본 소도시를 단일 서비스에서 나라별 트랙으로
                  탐색
                </td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s2-3">2.3 타겟 사용자</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">구분</th>
                <th>설명</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell">주 타겟</td>
                <td>
                  국내외 여행을 즐기지만 혼잡한 인기 여행지를 피하고 싶은
                  20~40대 성인
                </td>
              </tr>
              <tr>
                <td class="key-cell">부 타겟</td>
                <td>
                  일본 여행 경험이 있어 도쿄·오사카 외 소도시를 탐색하는 여행자
                </td>
              </tr>
              <tr>
                <td class="key-cell">공통 특성</td>
                <td>
                  자연어 대화에 익숙하고, 스마트폰 중심의 여행 정보 탐색 습관
                  보유
                </td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s2-4">2.4 서비스 흐름 요약</h2>
          <table class="flow-tbl">
            <thead>
              <tr>
                <th style="width:52px">단계</th>
                <th style="width:28%">입력</th>
                <th>처리 / 출력</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="flow-num">1</td>
                <td class="flow-in">취향·시기 입력</td>
                <td>
                  챗봇이 나라·취향·여행 시기(달/계절)·이동수단·혼잡 회피
                  선호도를 파악
                </td>
              </tr>
              <tr>
                <td class="flow-num">2</td>
                <td class="flow-in">테마 분류</td>
                <td>에이전트가 사용자 발화를 6개 테마 중 적합한 것으로 해석</td>
              </tr>
              <tr>
                <td class="flow-num">3</td>
                <td class="flow-in">RAG 검색·군집</td>
                <td>
                  테마+계절 적합도 데이터를 기준으로 소도시를 검색해 2~4곳 선별
                </td>
              </tr>
              <tr>
                <td class="flow-num">4</td>
                <td class="flow-in">여정 구성</td>
                <td>
                  방문 순서를 제안하고 그 시기 축제·행사를 결합해 여정 카드로
                  표시
                </td>
              </tr>
              <tr>
                <td class="flow-num">5</td>
                <td class="flow-in">상세 정보 조회</td>
                <td>드로어 패널에서 지도·장소 정보·날씨·외부 링크 확인</td>
              </tr>
              <tr>
                <td class="flow-num">6</td>
                <td class="flow-in">외부 연동</td>
                <td>Kakao / Yahoo Japan 딥링크로 추가 정보 확인</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 3. 기능 요구사항 ═══ -->
        <div class="doc-section" id="s3">
          <div class="section-num">Section 03</div>
          <h1 class="s-h1">3. 기능 요구사항</h1>
          <p class="doc-p">
            본 섹션은 로브 서비스가 제공해야 하는 사용자 기능과 시스템 동작을 정의한다. 각 요구사항은 개발, 설계, 테스트에서 공통 기준으로 사용할 수 있도록 식별자, 적용 영역, 요구사항 내용, 비고로 구분한다.
          </p>
          <p class="doc-p">
            기능 요구사항 표에서는 우선순위 컬럼을 제외한다. 실제 개발 우선순위는 별도 백로그에서 P1~P5 구간으로 산정한다.
          </p>

          <h2 class="s-h2" id="s3-1">3.1 공통 사용자 인터페이스</h2>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-COM-001</td>
                <td>공통 UI</td>
                <td>사용자는 자연어, 조건 입력, 선택형 칩 또는 필터를 통해 여행 조건을 입력할 수 있어야 한다.</td>
                <td>기존 FR-001, F2 통합</td>
              </tr>
              <tr>
                <td class="req-id">FR-COM-002</td>
                <td>공통 UI</td>
                <td>추천 결과는 카드, 표, 지도, 상세 패널 등 사용자가 비교 가능한 형태로 표시되어야 한다.</td>
                <td>결과 비교 가능성</td>
              </tr>
              <tr>
                <td class="req-id">FR-COM-003</td>
                <td>공통 UI</td>
                <td>서비스는 모바일과 데스크톱에서 핵심 탐색, 추천, 상세 확인 기능을 사용할 수 있는 반응형 화면을 제공해야 한다.</td>
                <td>접근성/호환성 연계</td>
              </tr>
              <tr>
                <td class="req-id">FR-COM-004</td>
                <td>다국어/국가 선택</td>
                <td>국가 또는 언어가 서비스 흐름에 영향을 주는 경우 사용자는 대상 국가와 표시 언어를 선택할 수 있어야 한다.</td>
                <td>한국/일본 확장 기준</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-2">3.2 추천·탐색 기능</h2>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-REC-001</td>
                <td>테마 추천</td>
                <td>시스템은 사용자 입력을 테마, 계절, 동행자, 지역, 혼잡 회피 선호 등 추천 조건으로 분류해야 한다.</td>
                <td>기존 테마 분류 통합</td>
              </tr>
              <tr>
                <td class="req-id">FR-REC-002</td>
                <td>대체 추천</td>
                <td>시스템은 혼잡도가 높거나 조건에 맞지 않는 대상 대신 대체 관광지, 축제, 방문 시간 또는 경로를 추천해야 한다.</td>
                <td>분산 추천 핵심</td>
              </tr>
              <tr>
                <td class="req-id">FR-REC-003</td>
                <td>추천 결과 구성</td>
                <td>추천 결과에는 추천 대상, 추천 이유, 주요 태그, 예상 이동 또는 방문 맥락, 후속 행동 링크가 포함되어야 한다.</td>
                <td>결과 설명 가능성</td>
              </tr>
              <tr>
                <td class="req-id">FR-REC-004</td>
                <td>개인화</td>
                <td>시스템은 사용자 취향, 이동 조건, 일정, 예산, 동행자 조건을 반영해 추천 결과를 개인화해야 한다.</td>
                <td>서비스별 세부 조건 적용</td>
              </tr>
              <tr>
                <td class="req-id">FR-REC-005</td>
                <td>저장/비교</td>
                <td>사용자는 추천 관광지, 코스, 축제 또는 경로 후보를 저장하거나 비교할 수 있어야 한다.</td>
                <td>일정 후보 관리</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-3">3.3 지도·위치·경로 기능</h2>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-MAP-001</td>
                <td>지도 표시</td>
                <td>추천 결과와 혼잡도 또는 목적지 위치는 지도 기반으로 표시되어야 한다.</td>
                <td>기존 지도 연동 통합</td>
              </tr>
              <tr>
                <td class="req-id">FR-MAP-002</td>
                <td>지도 플랫폼</td>
                <td>국내 목적지는 Google Maps와 Kakao Maps 링크 또는 탭을 제공하고, 일본 목적지는 Google Maps 및 일본 현지 플랫폼 링크를 제공해야 한다.</td>
                <td>국가별 플랫폼 분기</td>
              </tr>
              <tr>
                <td class="req-id">FR-MAP-003</td>
                <td>경로/패스</td>
                <td>철도 기반 서비스는 출발지, 도착지, 패스권, 예상 비용을 비교해 최적 경로 또는 패스를 추천해야 한다.</td>
                <td>RailRoute 전용</td>
              </tr>
              <tr>
                <td class="req-id">FR-MAP-004</td>
                <td>상세 패널</td>
                <td>목적지 또는 추천 카드 선택 시 위치, 날씨, 주변 명소, 외부 링크를 확인할 수 있는 상세 패널을 제공해야 한다.</td>
                <td>드로어/상세 카드</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-4">3.4 RAG·챗봇·에이전트 기능</h2>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-RAG-001</td>
                <td>RAG 검색</td>
                <td>서비스는 실제 수집 데이터 또는 벡터화된 지식베이스를 근거로 추천과 답변을 생성해야 한다.</td>
                <td>환각 방지</td>
              </tr>
              <tr>
                <td class="req-id">FR-RAG-002</td>
                <td>멀티스텝 에이전트</td>
                <td>추천 파이프라인은 조건 분류, 데이터 검색, 후보 선별, 결과 구성, 검증 단계를 순차적으로 처리해야 한다.</td>
                <td>다단계 처리</td>
              </tr>
              <tr>
                <td class="req-id">FR-RAG-003</td>
                <td>대화형 Q&amp;A</td>
                <td>추천 이후 사용자는 추가 질문을 할 수 있고, 시스템은 메타데이터와 추천 근거를 바탕으로 후속 답변을 제공해야 한다.</td>
                <td>후속 질의응답</td>
              </tr>
              <tr>
                <td class="req-id">FR-RAG-004</td>
                <td>폴백/검증</td>
                <td>각 에이전트 단계가 실패하거나 데이터 근거가 부족한 경우 재시도, 폴백 응답, 안내 메시지를 제공해야 한다.</td>
                <td>안정성</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-5">3.5 외부 데이터/API 연동</h2>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-API-001</td>
                <td>공공/관광 데이터</td>
                <td>서비스는 관광지, 축제, 교통, 날씨, 혼잡도 등 외부 데이터 소스를 연동하거나 수집할 수 있어야 한다.</td>
                <td>데이터 기반 서비스 공통</td>
              </tr>
              <tr>
                <td class="req-id">FR-API-002</td>
                <td>지도/날씨 API</td>
                <td>지도, 장소 상세, 날씨 정보는 외부 API 키 또는 공개 API 상태에 따라 연동되고, 미설정 시 안내 UI를 제공해야 한다.</td>
                <td>API 키 설정 포함</td>
              </tr>
              <tr>
                <td class="req-id">FR-API-003</td>
                <td>데이터 최신성</td>
                <td>축제, 혼잡도, 촬영지, 상품 정보처럼 변경 가능성이 높은 데이터는 갱신 주기와 최신성 상태를 관리해야 한다.</td>
                <td>품질 기준</td>
              </tr>
              <tr>
                <td class="req-id">FR-API-004</td>
                <td>외부 링크</td>
                <td>추천 대상에는 지도, 블로그, 예약, 현지 플랫폼 등 사용자가 후속 행동을 할 수 있는 외부 링크를 제공해야 한다.</td>
                <td>예약/탐색 연결</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-6">3.6 서비스별 세부 기능</h2>
          <section class="detail-docs service-requirements">
            <h3>서비스별 세부 기능 범위</h3>
            <p>
              로브의 서비스별 세부 기능 요구사항은 아래 영역을 기준으로 정의한다. 각 영역은 사용자에게 제공되는 기능, 시스템 처리, 데이터 활용, 검증 기준을 기능 요구사항 표에서 추적할 수 있어야 한다.
            </p>
            <ul class="detail-doc-list">
              <li>
                <strong>오버투어리즘 대응 여행 추천 서비스</strong>
                <span>혼잡도 분산과 지역 관광 균형을 위한 추천 기능</span>
              </li>
              <li>
                <strong>한일 축제 여행 챗봇</strong>
                <span>한국과 일본 축제 정보를 활용한 대화형 추천 기능</span>
              </li>
              <li>
                <strong>RailRoute-RAG</strong>
                <span>철도 여행 경로 추천과 RAG 기반 응답 기능</span>
              </li>
              <li>
                <strong>StarryNight-RAG</strong>
                <span>아스트로 투어리즘 후보 추천과 관측 조건 분석 기능</span>
              </li>
              <li>
                <strong>K-drama 촬영지 데이터 파이프라인</strong>
                <span>촬영지 데이터 수집, 정제, 검증, 탐색 기능</span>
              </li>
            </ul>
          </section>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-OTR-001</td>
                <td>오버투어리즘</td>
                <td>시스템은 관광지별 혼잡도를 조회하고 혼잡도가 높은 지역의 대체 관광지와 대체 방문 시간대를 추천해야 한다.</td>
                <td>FR-01~FR-05 통합</td>
              </tr>
              <tr>
                <td class="req-id">FR-OTR-002</td>
                <td>오버투어리즘</td>
                <td>운영자는 지역별 혼잡도, 추천 분산 결과, 데이터 수집 상태를 모니터링할 수 있어야 한다.</td>
                <td>관리자 요구사항</td>
              </tr>
              <tr>
                <td class="req-id">FR-FES-001</td>
                <td>한일 축제</td>
                <td>사용자는 국가, 언어, 날짜, 지역, 테마, 동행자 조건을 입력해 한국 또는 일본 축제를 추천받을 수 있어야 한다.</td>
                <td>F1~F3 통합</td>
              </tr>
              <tr>
                <td class="req-id">FR-FES-002</td>
                <td>한일 축제</td>
                <td>축제 추천 결과에는 축제명, 기간, 지역, 추천 이유, 주변 관광 자원, 후속 질의응답 진입점을 포함해야 한다.</td>
                <td>F4~F6 통합</td>
              </tr>
              <tr>
                <td class="req-id">FR-RAIL-001</td>
                <td>RailRoute-RAG</td>
                <td>시스템은 철도망, 교통 패스, 소도시 관광 상품을 결합해 이동 가능한 소도시 여정을 추천해야 한다.</td>
                <td>철도 기반 추천</td>
              </tr>
              <tr>
                <td class="req-id">FR-RAIL-002</td>
                <td>RailRoute-RAG</td>
                <td>시스템은 패스권 구매비, 절약 금액, 추천 경로, 연결 상품을 비교해 사용자가 비용 효율을 판단할 수 있게 해야 한다.</td>
                <td>패스 절약 계산기</td>
              </tr>
              <tr>
                <td class="req-id">FR-ASTRO-001</td>
                <td>StarryNight-RAG</td>
                <td>시스템은 관측지, 날씨, 달 위상, 빛공해, 장비 또는 프로그램 정보를 바탕으로 아스트로 투어리즘 후보를 추천해야 한다.</td>
                <td>천문 관광 추천</td>
              </tr>
              <tr>
                <td class="req-id">FR-ASTRO-002</td>
                <td>StarryNight-RAG</td>
                <td>사용자는 관측회, 장비 대여, 숙박 또는 프로그램 예약으로 이어지는 후속 링크를 확인할 수 있어야 한다.</td>
                <td>예약 연계</td>
              </tr>
              <tr>
                <td class="req-id">FR-KDRAMA-001</td>
                <td>K-drama 파이프라인</td>
                <td>시스템은 K-drama 촬영지 데이터를 수집, 정제, 검증하고 장소별 메타데이터를 구조화해야 한다.</td>
                <td>데이터 파이프라인</td>
              </tr>
              <tr>
                <td class="req-id">FR-KDRAMA-002</td>
                <td>K-drama 파이프라인</td>
                <td>촬영지 결과는 작품명, 위치, 검증 상태, 신뢰도, 태그, 참조 링크와 함께 탐색 가능해야 한다.</td>
                <td>검색/검증 화면</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-7">3.7 운영·관리·검증 기능</h2>
          <table class="req-tbl feature-req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>서비스/영역</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-OPS-001</td>
                <td>관리자</td>
                <td>운영자는 추천 정책, 노출 기준, 공지사항, 데이터 갱신 상태를 관리할 수 있어야 한다.</td>
                <td>운영 관리</td>
              </tr>
              <tr>
                <td class="req-id">FR-OPS-002</td>
                <td>검증</td>
                <td>추천 또는 데이터 파이프라인 결과에는 출처, 검증 상태, 실패 여부 또는 신뢰도 정보를 표시해야 한다.</td>
                <td>추적성/신뢰도</td>
              </tr>
              <tr>
                <td class="req-id">FR-OPS-003</td>
                <td>확장성</td>
                <td>서비스는 신규 지역, 축제, 관광 상품, 촬영지, 데이터 소스를 추가할 수 있는 구조를 가져야 한다.</td>
                <td>데이터 확장</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 4. API 연동 요구사항 ═══ -->
        <div class="doc-section" id="s4">
          <div class="section-num">Section 04</div>
          <h1 class="s-h1">4. API 연동 요구사항</h1>
          <p class="doc-p">
            각 플랫폼 API는 역할을 분담하여 정보를 보완 제공한다. 클라이언트 측
            직접 호출이 불가한 REST API는 딥링크로 대체하며, 향후 백엔드
            프록시를 통해 연동한다.
          </p>

          <div class="api-grid">
            <div class="api-card">
              <div class="api-card-hd">
                <div class="api-card-ico api-ic-g">🌐</div>
                <div>
                  <div class="api-card-name">Google Maps Platform</div>
                  <div class="api-card-role">
                    장소 상세 · 사진 · 주변 명소 (전 지역)
                  </div>
                </div>
              </div>
              <div class="api-card-body">
                <p>
                  <strong>역할:</strong> 플랫폼 공통 지도 + Places API로 실시간
                  장소 정보
                </p>
                <p>
                  <strong>상태:</strong>
                  <span class="sbadge sb-ok">✓ 클라이언트 직접 연동</span>
                </p>
              </div>
            </div>
            <div class="api-card">
              <div class="api-card-hd">
                <div class="api-card-ico api-ic-k">🟡</div>
                <div>
                  <div class="api-card-name">Kakao Maps</div>
                  <div class="api-card-role">
                    카카오 지도 · 주변 맛집·숙박 (국내 전용)
                  </div>
                </div>
              </div>
              <div class="api-card-body">
                <p>
                  <strong>역할:</strong> 카카오 지도 SDK + Local REST API (맛집
                  검색)
                </p>
                <p>
                  <strong>상태:</strong>
                  <span class="sbadge sb-part">△ SDK + REST Key 선택</span>
                </p>
              </div>
            </div>
            <div class="api-card">
              <div class="api-card-hd">
                <div class="api-card-ico api-ic-y">🔴</div>
                <div>
                  <div class="api-card-name">Yahoo Japan</div>
                  <div class="api-card-role">
                    일본 여행 · 숙박 · 맛집 (일본 전용)
                  </div>
                </div>
              </div>
              <div class="api-card-body">
                <p>
                  <strong>역할:</strong> Yahoo Travel · じゃらん · 食べログ
                  딥링크
                </p>
                <p>
                  <strong>상태:</strong>
                  <span class="sbadge sb-link">딥링크 / REST 백엔드 예정</span>
                </p>
              </div>
            </div>
            <div class="api-card">
              <div class="api-card-hd">
                <div class="api-card-ico api-ic-w">☀</div>
                <div>
                  <div class="api-card-name">WeatherAPI</div>
                  <div class="api-card-role">
                    실시간 날씨 (전 지역 · API Key 필요)
                  </div>
                </div>
              </div>
              <div class="api-card-body">
                <p>
                  <strong>역할:</strong> 기온, 날씨 상태, 풍속, 습도 자동 제공
                </p>
                <p>
                  <strong>상태:</strong>
                  <span class="sbadge sb-part">△ API Key 설정 필요</span>
                </p>
              </div>
            </div>
          </div>

          <h2 class="s-h2" id="s4-1">4.1 Google Maps Platform</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">항목</th>
                <th>내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell">역할</td>
                <td>
                  장소 상세 정보, 지도 표시, 주변 명소 검색 (전 지역 공통)
                </td>
              </tr>
              <tr>
                <td class="key-cell">사용 API</td>
                <td>
                  Maps JavaScript API, Places API — Text Search / Find Place /
                  Get Details / Nearby Search
                </td>
              </tr>
              <tr>
                <td class="key-cell">연동 방식</td>
                <td>JavaScript SDK — 클라이언트 직접 호출 가능</td>
              </tr>
              <tr>
                <td class="key-cell">필수 키</td>
                <td>
                  Google Cloud API Key (Maps JS API + Places API 활성화 필요)
                </td>
              </tr>
              <tr>
                <td class="key-cell">제공 데이터</td>
                <td>
                  평점, 리뷰 수, 사진(최대 4장), 운영시간, 현재 영업 여부, 공식
                  사이트, 주변 명소(반경 3km)
                </td>
              </tr>
              <tr>
                <td class="key-cell">적용 국가</td>
                <td>국내 소도시 + 일본 소도시 (공통 적용)</td>
              </tr>
              <tr>
                <td class="key-cell">CORS 제약</td>
                <td>없음 — SDK 방식으로 브라우저에서 직접 사용 가능</td>
              </tr>
            </tbody>
          </table>


          <h2 class="s-h2" id="s4-2">4.2 Kakao Maps</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">항목</th>
                <th>내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell amber-key">역할</td>
                <td>국내 소도시 카카오 지도 표시, 주변 맛집·카페·숙박 검색</td>
              </tr>
              <tr>
                <td class="key-cell amber-key">사용 API</td>
                <td>
                  Kakao Maps JavaScript SDK (지도), Kakao Local REST API (주변
                  검색)
                </td>
              </tr>
              <tr>
                <td class="key-cell amber-key">연동 방식</td>
                <td>
                  JavaScript SDK (지도): 클라이언트 직접 / Local REST: REST Key
                  필요
                </td>
              </tr>
              <tr>
                <td class="key-cell amber-key">필수 키</td>
                <td>
                  Kakao JavaScript App Key (지도 필수), Kakao REST API Key (로컬
                  검색, 선택)
                </td>
              </tr>
              <tr>
                <td class="key-cell amber-key">제공 데이터</td>
                <td>카카오 지도, 주변 맛집/카페/숙박 검색 결과, 장소 URL</td>
              </tr>
              <tr>
                <td class="key-cell amber-key">적용 국가</td>
                <td>국내 소도시 전용</td>
              </tr>
              <tr>
                <td class="key-cell amber-key">CORS 제약</td>
                <td>
                  Maps SDK: 없음 / Local REST: 등록 도메인 한정 (로컬 파일 환경
                  제약) → 오류 시 딥링크 대체
                </td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s4-3">4.3 Yahoo Japan</h2>
          <div class="warn-box">
            <strong>⚠ Yahoo Japan Maps JS SDK 지원 중단:</strong> Yahoo Japan
            Maps JavaScript SDK(Yjans)가 서비스 종료되어 일본 소도시 지도는
            Google Maps API로 대체 제공한다. Yahoo Japan REST API는 CORS
            제한으로 클라이언트 직접 호출이 불가하며, 딥링크 방식으로 제공한다.
          </div>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">항목</th>
                <th>내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell red-key">역할</td>
                <td>일본 소도시 여행 정보, 숙박·음식점 플랫폼 딥링크 제공</td>
              </tr>
              <tr>
                <td class="key-cell red-key">사용 API</td>
                <td>
                  Yahoo Japan Local Search REST API (향후),
                  じゃらん/食べログ/楽天トラベル 딥링크 (현재)
                </td>
              </tr>
              <tr>
                <td class="key-cell red-key">연동 방식</td>
                <td>
                  현재: 딥링크 URL 제공 / 향후: 백엔드 프록시를 통한 REST API
                  연동
                </td>
              </tr>
              <tr>
                <td class="key-cell red-key">필수 키</td>
                <td>
                  Yahoo Japan App ID (향후 적용 예정, 현재 입력 항목만 준비)
                </td>
              </tr>
              <tr>
                <td class="key-cell red-key">제공 데이터</td>
                <td>
                  Yahoo Japan Maps 링크, Yahoo Travel 링크, じゃらん, 食べログ,
                  楽天トラベル 링크
                </td>
              </tr>
              <tr>
                <td class="key-cell red-key">적용 국가</td>
                <td>일본 소도시 전용</td>
              </tr>
              <tr>
                <td class="key-cell red-key">지도 대체</td>
                <td>
                  Yahoo Japan Maps JS SDK 지원 중단 → Google Maps 대체 제공
                </td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s4-4">4.4 WeatherAPI (날씨)</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">항목</th>
                <th>내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell blue-key">역할</td>
                <td>전 목적지 실시간 날씨 정보 제공 (API Key 필요)</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">사용 API</td>
                <td>WeatherAPI Current Weather API 및 Forecast API</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">연동 방식</td>
                <td>REST API — API Key 기반 호출, 운영 환경에서는 백엔드 프록시 권장</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">필수 키</td>
                <td>WeatherAPI API Key</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">제공 데이터</td>
                <td>현재 기온(℃), 날씨 상태, 풍속(km/h), 습도(%), 강수 확률, 예보 데이터</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">적용 국가</td>
                <td>국내 + 일본 소도시 공통 적용</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">제약사항</td>
                <td>요금제, 호출량 제한, API Key 노출 방지 정책 확인 필요</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s4-5">4.5 API 연동 현황 요약</h2>
          <table class="cmp-tbl">
            <thead>
              <tr>
                <th>플랫폼</th>
                <th>역할 특화</th>
                <th>지도 SDK</th>
                <th>REST API</th>
                <th>현재 상태</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Google Maps</strong></td>
                <td>장소 상세·사진·주변 명소</td>
                <td><span class="sym-ok">✓</span> 지원</td>
                <td><span class="sym-ok">✓</span> 지원</td>
                <td>클라이언트 직접 연동</td>
              </tr>
              <tr>
                <td><strong>Kakao Maps</strong></td>
                <td>맛집·카페·숙박 검색</td>
                <td><span class="sym-ok">✓</span> 지원</td>
                <td><span class="sym-pt">△</span> 조건부</td>
                <td>SDK + REST Key 선택</td>
              </tr>
              <tr>
                <td><strong>Yahoo Japan</strong></td>
                <td>일본 여행·숙박·맛집</td>
                <td><span class="sym-no">✗</span> SDK 중단</td>
                <td><span class="sym-no">✗</span> CORS</td>
                <td>딥링크 제공</td>
              </tr>
              <tr>
                <td><strong>WeatherAPI</strong></td>
                <td>실시간 날씨·예보</td>
                <td>—</td>
                <td><span class="sym-pt">△</span> Key 필요</td>
                <td>API Key 설정 필요</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 5. 비기능 요구사항 ═══ -->
        <div class="doc-section" id="s5">
          <div class="section-num">Section 05</div>
          <h1 class="s-h1">5. 비기능 요구사항</h1>
          <h2 class="s-h2" id="s5-1">5.1 성능</h2>
          <table class="req-tbl nfr-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">NFR-001</td>
                <td>챗봇 응답은 사용자 입력 후 1.5초 이내에 시작되어야 한다</td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-001B</td>
                <td>
                  멀티스텝 에이전트 전체 처리(분류→검색→여정 구성)는 8초 이내를
                  목표로 한다
                </td>
                <td class="req-note">단계별 병렬화 고려</td>
              </tr>
              <tr>
                <td class="req-id">NFR-001C</td>
                <td>RAG 벡터 검색은 1초 이내에 결과를 반환해야 한다</td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-002</td>
                <td>
                  지도 초기 렌더링은 SDK 로드 완료 후 2초 이내에 완료되어야 한다
                </td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-003</td>
                <td>
                  Google Places API 호출은 결과 수신까지 3초 이내를 목표로 한다
                </td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-004</td>
                <td>날씨 API(WeatherAPI) 응답은 2초 이내를 목표로 한다</td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-005</td>
                <td>
                  API 타임아웃 시 오류 메시지를 표시하고 기본 정보로 폴백한다
                </td>
                <td class="req-note">폴백 UI 필수</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s5-2">5.2 보안</h2>
          <table class="req-tbl nfr-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">NFR-010</td>
                <td>
                  API 키는 클라이언트 로컬 스토리지에 저장하며 외부 서버로
                  전송하지 않는다
                </td>
                <td class="req-note">데모 환경 기준</td>
              </tr>
              <tr>
                <td class="req-id">NFR-011</td>
                <td>
                  서비스 배포 시 API 키는 환경 변수 또는 서버 사이드에서
                  관리한다
                </td>
                <td class="req-note">배포 환경 적용</td>
              </tr>
              <tr>
                <td class="req-id">NFR-012</td>
                <td>
                  Google API 키에 HTTP Referer 제한을 설정하여 무단 사용을
                  방지한다
                </td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-013</td>
                <td>
                  사용자 대화 내용은 로컬에서만 처리하며 별도 서버에 저장하지
                  않는다
                </td>
                <td class="req-note">—</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s5-3">5.3 호환성 및 접근성</h2>
          <table class="req-tbl nfr-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">NFR-020</td>
                <td>Chrome, Safari, Edge 최신 버전에서 정상 동작해야 한다</td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-021</td>
                <td>모바일(iOS/Android) 브라우저에서 사용 가능해야 한다</td>
                <td class="req-note">반응형 레이아웃</td>
              </tr>
              <tr>
                <td class="req-id">NFR-022</td>
                <td>
                  화면 너비 375px 이상에서 주요 기능이 모두 사용 가능해야 한다
                </td>
                <td class="req-note">iPhone SE 기준</td>
              </tr>
              <tr>
                <td class="req-id">NFR-023</td>
                <td>다크 모드를 지원해야 한다</td>
                <td class="req-note">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 6. 데이터 요구사항 ═══ -->
        <div class="doc-section" id="s6">
          <div class="section-num">Section 06</div>
          <h1 class="s-h1">6. 데이터 요구사항</h1>

          <h2 class="s-h2" id="s6-1">6.1 필요 데이터 항목</h2>
          <p class="doc-p">
            본 절은 저장 구조 설계가 아니라, 로브 서비스가 추천·설명·검증을 수행하기 위해 확보해야 하는 데이터의 종류를 정의한다.
          </p>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:24%">데이터 구분</th>
                <th>필요 내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell">목적지 기본 정보</td>
                <td>소도시명, 국가, 지역, 대표 설명, 주요 이미지, 위치 좌표, 접근 방법</td>
              </tr>
              <tr>
                <td class="key-cell">테마 분류 정보</td>
                <td>온천·휴양, 바다·해안, 역사·전통, 미식·노포, 자연·트레킹, 예술·감성 등 6개 테마와 관련 태그</td>
              </tr>
              <tr>
                <td class="key-cell">계절·시기 정보</td>
                <td>월별 또는 계절별 추천 적합도, 방문하기 좋은 시기, 비추천 시기와 그 사유</td>
              </tr>
              <tr>
                <td class="key-cell">축제·행사 정보</td>
                <td>행사명, 개최 지역, 개최 시기, 간단 설명, 공식 또는 참고 링크</td>
              </tr>
              <tr>
                <td class="key-cell">혼잡도·대체지 정보</td>
                <td>혼잡 가능성이 높은 관광지, 대체 방문지, 대체 시간대, 분산 추천 사유</td>
              </tr>
              <tr>
                <td class="key-cell">지도·장소 정보</td>
                <td>Google Maps, Kakao Maps, Yahoo Japan 등 외부 플랫폼에서 확인 가능한 지도, 장소 상세, 후속 탐색 링크</td>
              </tr>
              <tr>
                <td class="key-cell">날씨·환경 정보</td>
                <td>WeatherAPI 기반 현재 날씨, 예보, 기온, 강수 확률, 풍속 등 여행 판단에 필요한 정보</td>
              </tr>
              <tr>
                <td class="key-cell">추천 근거 정보</td>
                <td>추천 이유, 사용자 조건과의 매칭 근거, 참고 출처, 검증 상태, 신뢰도 표시 정보</td>
              </tr>
              <tr>
                <td class="key-cell">외부 행동 링크</td>
                <td>지도 열기, 공식 관광 정보, 예약, 교통, 숙박, 맛집, 현지 플랫폼으로 이어지는 링크</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s6-2">6.2 데이터 품질 기준</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:24%">품질 기준</th>
                <th>요구사항</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell">지역 커버리지</td>
                <td>국내와 일본 소도시를 모두 포함하되, 국가별 추천 흐름은 독립적으로 운영할 수 있어야 한다.</td>
              </tr>
              <tr>
                <td class="key-cell">테마 커버리지</td>
                <td>각 테마별로 추천 후보를 구성할 수 있을 만큼 충분한 목적지와 설명 데이터를 확보해야 한다.</td>
              </tr>
              <tr>
                <td class="key-cell">최신성</td>
                <td>축제, 영업 정보, 날씨, 혼잡도처럼 변동성이 높은 데이터는 갱신 시점 또는 유효 기간을 함께 관리해야 한다.</td>
              </tr>
              <tr>
                <td class="key-cell">출처 추적성</td>
                <td>추천 결과에 사용된 주요 데이터는 사용자가 신뢰할 수 있도록 출처 또는 확인 가능한 링크를 제공해야 한다.</td>
              </tr>
              <tr>
                <td class="key-cell">설명 가능성</td>
                <td>추천 결과는 단순 목록이 아니라 사용자 조건과 어떤 데이터가 매칭되었는지 설명할 수 있어야 한다.</td>
              </tr>
              <tr>
                <td class="key-cell">결측 대응</td>
                <td>필수 데이터가 부족한 목적지는 추천에서 제외하거나, 부족한 정보와 대체 안내를 명확히 표시해야 한다.</td>
              </tr>
              <tr>
                <td class="key-cell">국가별 분리</td>
                <td>한국 여행 요청에는 한국 소도시 데이터만, 일본 여행 요청에는 일본 소도시 데이터만 사용해야 한다.</td>
              </tr>
            </tbody>
          </table>
          <div class="note-box">
            <strong>정의 범위:</strong> 본 문서는 어떤 데이터가 필요한지를 정의한다. 테이블 구조, 컬렉션 구조, 인덱스, 저장소 선택 등 저장 구조 설계는 별도 설계 문서에서 다룬다.
          </div>
        </div>

        <!-- ═══ 7. 제약사항 및 가정 ═══ -->
        <div class="doc-section" id="s7">
          <div class="section-num">Section 07</div>
          <h1 class="s-h1">7. 제약사항 및 가정</h1>

          <h2 class="s-h2" id="s7-1">7.1 기술적 제약사항</h2>
          <div class="warn-box">
            <strong>Yahoo Japan Maps SDK 지원 중단:</strong> Yahoo Japan Maps
            JavaScript SDK(Yjans)가 지원 중단되어 일본 소도시 지도는 Google Maps
            API로 대체 제공한다.
          </div>
          <div class="warn-box">
            <strong>Yahoo Japan REST API CORS:</strong> Local Search 등 REST
            API는 CORS 제한이 있다. 향후 백엔드 프록시 서버를 통해 연동한다. App
            ID는 향후 사용을 위해 입력 항목만 준비한다.
          </div>
          <div class="warn-box">
            <strong>Kakao REST API 도메인 제약:</strong> 로컬 파일
            환경(<code>file://</code>)에서는 CORS 정책으로 Kakao Local REST API
            호출이 제한될 수 있다. 등록된 도메인 환경에서 정상 동작한다.
          </div>
          <div class="warn-box">
            <strong>Google Places API 과금:</strong> Places API는 무료 한도 초과
            시 과금이 발생한다. 서비스 규모에 따른 비용 산정이 필요하다.
          </div>

          <h2 class="s-h2" id="s7-2">7.2 가정사항</h2>
          <ul class="bullet-list">
            <li>
              서비스 초기에는 단일 HTML 파일 기반 데모로 운영하며, API 키는
              사용자가 직접 입력한다.
            </li>
            <li>
              초기 데이터는 정적 파일 또는 외부 API 기반으로 관리하며, 저장 구조는
              별도 데이터 설계 단계에서 결정한다.
            </li>
            <li>
              추천 엔진은 RAG(검색증강) + 멀티스텝 에이전트 구조로 구현하며, LLM
              API를 활용한다.
            </li>
            <li>
              자체 모델 학습(sLLM)은 본 범위에서 제외하며, 기성 LLM API + RAG +
              에이전트 설계로 품질을 확보한다.
            </li>
            <li>
              축제·계절 정보는 월·계절 단위로만 관리하여 연도별 갱신 부담과 환각
              위험을 최소화한다.
            </li>
            <li>
              이동 동선은 방문 순서 제안 수준으로 한정하며, 실시간 교통·항공편
              최적화는 제외한다.
            </li>
            <li>
              WeatherAPI는 API Key 기반으로 사용하며 상업적 서비스 전환 시
              요금제, 호출량 제한, 키 보안 정책을 재확인한다.
            </li>
          </ul>
        </div>

        <!-- ═══ 8. 변경 이력 ═══ -->
        <div class="doc-section" id="s8">
          <div class="section-num">Section 08</div>
          <h1 class="s-h1">8. 변경 이력</h1>
          <table class="log-tbl">
            <thead>
              <tr>
                <th style="width:70px">버전</th>
                <th style="width:130px">날짜</th>
                <th style="width:160px">작성자</th>
                <th>변경 내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>v1.0</td>
                <td id="logDate"></td>
                <td>로브 기획팀</td>
                <td>
                  최초 작성 — 기능 요구사항, API 연동 명세, 비기능 요구사항 초안
                </td>
              </tr>
              <tr>
                <td>v1.1</td>
                <td id="logDate2"></td>
                <td>로브 기획팀</td>
                <td>
                  6개 테마 여정 추천 도입, 계절·축제 연동 추가, RAG·멀티스텝
                  에이전트 기반으로 추천 엔진 정의 (규칙기반→RAG 전환), 소도시
                  필요 데이터 항목에 테마·계절·축제·추천 근거 정보 추가
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>

    <script src="../assets/js/requirements.js" defer></script>
  </body>
</html>
```




