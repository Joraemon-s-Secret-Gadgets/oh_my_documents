```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>K-drama 촬영지 데이터 파이프라인</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Noto+Serif+KR:wght@300;400;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
        --brand-green: #1B3B32;
        --brand-green-900: #10251F;
        --brand-green-800: #173329;
        --brand-green-100: #E6EEE9;
        --brand-gold: #D4AF37;
        --brand-gold-700: #A9821E;
        --brand-gold-100: #F6EBC4;
  --bg: #10251F;
  --bg2: #173329;
  --bg3: #1B3B32;
  --bg4: #244D41;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.12);
  --text: #e6e4de;
  --text2: #9a9895;
  --text3: #555350;
  --accent: #D4AF37;
  --accent2: #F6EBC4;
  --green: #E6EEE9;
  --blue: #D4AF37;
  --amber: #A9821E;
  --mono: 'DM Mono', monospace;
  --serif: 'Noto Serif KR', serif;
  --sans: 'Noto Sans KR', sans-serif;
}

html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text); font-family: var(--sans); font-size: 14px; line-height: 1.7; }

/* ── NAV ── */
nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(16,37,31,0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 32px; height: 52px;
}
.nav-logo {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 12px; color: var(--text2);
}
.nav-logo span { color: var(--accent); font-size: 16px; }
.nav-links { display: flex; gap: 28px; }
.nav-links a {
  font-size: 13px; color: var(--text2); text-decoration: none; letter-spacing: .02em;
  transition: color .2s;
}
.nav-links a:hover { color: var(--text); }

/* ── HERO ── */
.hero {
  min-height: 100vh; display: flex; flex-direction: column;
  justify-content: center; align-items: center;
  text-align: center; padding: 120px 32px 80px;
  position: relative; overflow: hidden;
}
.hero-bg-text {
  position: absolute; font-family: var(--serif); font-size: 220px; font-weight: 700;
  color: rgba(255,255,255,0.025); line-height: 1;
  user-select: none; pointer-events: none;
  right: -20px; top: 50%; transform: translateY(-50%);
  writing-mode: vertical-rl;
}
.hero-pill {
  display: inline-flex; align-items: center; gap: 8px;
  border: 1px solid var(--border2); border-radius: 20px;
  padding: 6px 16px; margin-bottom: 32px;
  font-family: var(--mono); font-size: 11px; letter-spacing: .1em;
  color: var(--text2);
}
.hero-pill span { color: var(--accent); }
.hero h1 {
  font-family: var(--serif); font-size: clamp(52px, 9vw, 96px);
  font-weight: 400; line-height: 1.15; color: var(--text);
  margin-bottom: 24px; letter-spacing: -.01em;
}
.hero h1 em { color: var(--accent); font-style: normal; }
.hero-sub { font-size: 14px; color: var(--text2); max-width: 480px; line-height: 1.9; margin-bottom: 56px; }
.hero-stats { display: flex; gap: 56px; justify-content: center; }
.stat-num { font-family: var(--serif); font-size: 40px; color: var(--accent); font-weight: 300; }
.stat-label { font-family: var(--mono); font-size: 10px; letter-spacing: .12em; color: var(--text3); text-transform: uppercase; margin-top: 2px; }

/* ── SECTIONS ── */
section { padding: 96px 32px; max-width: 1100px; margin: 0 auto; }
.section-eyebrow {
  font-family: var(--mono); font-size: 11px; color: var(--accent);
  letter-spacing: .1em; margin-bottom: 12px;
}
.section-eyebrow span { color: var(--text3); }
.section-title {
  font-family: var(--serif); font-size: clamp(36px, 5vw, 56px);
  font-weight: 400; line-height: 1.2; margin-bottom: 16px; letter-spacing: -.01em;
}
.section-desc { font-size: 14px; color: var(--text2); max-width: 560px; line-height: 1.9; margin-bottom: 48px; }

/* ── THEME CARDS ── */
.card-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
@media (max-width: 900px) { .card-grid { grid-template-columns: repeat(2,1fr); } }
.theme-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 24px 20px; cursor: pointer;
  transition: border-color .2s, background .2s;
}
.theme-card:hover { border-color: var(--border2); background: var(--bg3); }
.theme-card.active { border-color: var(--accent); background: var(--bg3); }
.card-icon { font-size: 28px; margin-bottom: 12px; }
.card-sub { font-family: var(--mono); font-size: 10px; color: var(--text3); letter-spacing: .06em; margin-bottom: 6px; }
.card-title { font-size: 16px; font-weight: 500; margin-bottom: 8px; }
.card-desc { font-size: 12px; color: var(--text2); line-height: 1.8; margin-bottom: 14px; }
.card-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  font-family: var(--mono); font-size: 10px; letter-spacing: .04em;
  border: 1px solid var(--border2); border-radius: 3px;
  padding: 2px 7px; color: var(--text2);
}
.tag.accent { border-color: rgba(212,175,55,.3); color: var(--accent); background: rgba(212,175,55,.07); }
.tag.green  { border-color: rgba(230,238,233,.3); color: var(--green); background: rgba(230,238,233,.07); }
.tag.blue   { border-color: rgba(212,175,55,.3); color: var(--blue); background: rgba(212,175,55,.07); }

/* ── SPOT CARDS ── */
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
.filter-btn {
  font-size: 13px; padding: 6px 16px; border-radius: 20px;
  border: 1px solid var(--border2); background: transparent;
  color: var(--text2); cursor: pointer; transition: all .15s;
  font-family: var(--sans);
}
.filter-btn:hover { border-color: var(--text2); color: var(--text); }
.filter-btn.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.spot-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }
@media (max-width: 800px) { .spot-grid { grid-template-columns: 1fr; } }
.spot-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 10px;
}
.spot-card-head { display: flex; align-items: center; justify-content: space-between; }
.drama-badge {
  font-family: var(--mono); font-size: 10px; letter-spacing: .04em;
  background: rgba(212,175,55,.12); border: 1px solid rgba(212,175,55,.25);
  color: var(--accent); border-radius: 3px; padding: 2px 8px;
}
.confidence {
  font-family: var(--mono); font-size: 10px; color: var(--green);
  display: flex; align-items: center; gap: 4px;
}
.confidence::before { content:''; width:6px; height:6px; border-radius:50%; background: var(--green); }
.spot-title { font-size: 16px; font-weight: 500; }
.spot-loc { font-size: 12px; color: var(--text2); display: flex; align-items: center; gap: 4px; }
.spot-desc { font-size: 12px; color: var(--text2); line-height: 1.8; }
.spot-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.spot-card-foot { display: flex; align-items: center; justify-content: space-between; padding-top: 8px; border-top: 1px solid var(--border); }
.spot-verify { font-size: 11px; color: var(--green); }
.spot-ref { font-family: var(--mono); font-size: 11px; color: var(--text3); cursor: pointer; }
.spot-ref:hover { color: var(--text2); }

/* ── SCHEMA ── */
.schema-wrap {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 16px; overflow: hidden;
}
.schema-head {
  display: flex; align-items: center; gap: 12px;
  padding: 20px 24px; border-bottom: 1px solid var(--border);
}
.schema-head-title { font-size: 16px; font-weight: 500; }
.schema-badge {
  font-family: var(--mono); font-size: 10px; letter-spacing: .06em;
  border: 1px solid var(--border2); border-radius: 3px;
  padding: 3px 8px; color: var(--text3);
}
.field-grid { display: grid; grid-template-columns: repeat(3,1fr); }
@media (max-width: 700px) { .field-grid { grid-template-columns: 1fr; } }
.field-cell {
  padding: 22px 24px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border);
}
.field-cell:nth-child(3n) { border-right: none; }
.field-num { font-family: var(--mono); font-size: 10px; color: var(--accent); letter-spacing: .08em; margin-bottom: 8px; }
.field-name { font-size: 16px; font-weight: 500; margin-bottom: 6px; }
.field-desc { font-size: 12px; color: var(--text2); line-height: 1.8; margin-bottom: 12px; }
.field-examples { display: flex; flex-wrap: wrap; gap: 5px; }
.field-ex {
  font-family: var(--mono); font-size: 10px;
  background: var(--bg3); border: 1px solid var(--border2);
  border-radius: 3px; padding: 2px 7px; color: var(--text2);
}
.field-ex.high { color: #50c8a0; border-color: rgba(230,238,233,.3); background: rgba(230,238,233,.07); }
.field-ex.mid  { color: #d8902a; border-color: rgba(169,130,30,.3); background: rgba(169,130,30,.07); }
.field-ex.low  { color: #e8607a; border-color: rgba(212,175,55,.3); background: rgba(212,175,55,.07); }

/* ── PIPELINE STEPS ── */
.pipeline-wrap { position: relative; padding-left: 60px; display: flex; flex-direction: column; gap: 0; }
.pipeline-line {
  position: absolute; left: 20px; top: 20px; bottom: 20px;
  width: 1px; background: linear-gradient(to bottom, var(--accent), transparent);
}
.pipeline-step { position: relative; padding: 0 0 48px 0; }
.pipeline-step:last-child { padding-bottom: 0; }
.step-circle {
  position: absolute; left: -48px; top: 0;
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(212,175,55,.12); border: 1px solid rgba(212,175,55,.3);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 12px; font-weight: 500; color: var(--accent);
}
.step-eyebrow { font-family: var(--mono); font-size: 10px; color: var(--text3); letter-spacing: .1em; text-transform: uppercase; margin-bottom: 6px; }
.step-title { font-size: 18px; font-weight: 500; margin-bottom: 8px; }
.step-desc { font-size: 13px; color: var(--text2); line-height: 1.9; margin-bottom: 14px; max-width: 600px; }
.code-block {
  background: var(--bg3); border: 1px solid var(--border2);
  border-radius: 8px; padding: 16px 18px;
  font-family: var(--mono); font-size: 12px; color: var(--text2); line-height: 1.9;
}
.code-block .k { color: var(--accent2); }
.code-block .v { color: var(--green); }
.code-block .c { color: var(--text3); }

/* ── NOTICE ── */
.notice {
  background: rgba(169,130,30,.07); border: 1px solid rgba(169,130,30,.2);
  border-left: 3px solid var(--amber); border-radius: 0 10px 10px 0;
  padding: 16px 20px; font-size: 13px; color: var(--text2); line-height: 1.9;
  margin-top: 16px;
}
.notice strong { color: var(--amber); font-weight: 500; }

/* ── SOURCE TABLE ── */
.source-table {
  width: 100%; border-collapse: collapse;
  background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
}
.source-table th {
  font-family: var(--mono); font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
  color: var(--text3); padding: 12px 18px; text-align: left;
  border-bottom: 1px solid var(--border2); font-weight: 400;
}
.source-table td { padding: 11px 18px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: middle; }
.source-table tr:last-child td { border-bottom: none; }
.source-table tr:hover td { background: rgba(255,255,255,.015); }
.source-table a { color: var(--blue); text-decoration: none; }
.source-table a:hover { text-decoration: underline; }
.priority { font-family: var(--mono); font-size: 10px; letter-spacing: .04em; padding: 3px 8px; border-radius: 3px; white-space: nowrap; }
.p-critical { background: rgba(212,175,55,.12); border: 1px solid rgba(212,175,55,.25); color: var(--accent); }
.p-high     { background: rgba(230,238,233,.1);  border: 1px solid rgba(230,238,233,.2);  color: var(--green); }
.p-mid      { background: rgba(212,175,55,.1);  border: 1px solid rgba(212,175,55,.2);  color: var(--blue); }
.p-ref      { background: rgba(169,130,30,.1);  border: 1px solid rgba(169,130,30,.2);  color: var(--amber); }

/* ── FOOTER ── */
footer {
  border-top: 1px solid var(--border); padding: 32px;
  text-align: center; font-family: var(--mono); font-size: 11px; color: var(--text3);
  letter-spacing: .05em;
}
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="nav-logo">
    <span>🌸</span> K-drama 촬영지 · DATA PIPELINE
  </div>
  <div class="nav-links">
    <a href="#sources">데이터 소스</a>
    <a href="#pipeline">파이프라인</a>
    <a href="#schema">데이터 모델</a>
    <a href="#spots">촬영지 스팟</a>
    <a href="#notice">주의사항</a>
  </div>
</nav>

<!-- HERO -->
<div class="hero" id="top">
  <div class="hero-bg-text">촬영지</div>
  <div class="hero-pill">
    <span>🌸</span> K-DRAMA · 촬영지 데이터 시스템
  </div>
  <h1>K-DRAMA<br><em>촬영지</em> 데이터<br>파이프라인</h1>
  <p class="hero-sub">
    공식 관광데이터 + 촬영지 큐레이션 + 자체 검증 조합의<br>
    현실적 데이터 파이프라인 설계 가이드
  </p>
  <div class="hero-stats">
    <div>
      <div class="stat-num">8+</div>
      <div class="stat-label">Data Sources</div>
    </div>
    <div>
      <div class="stat-num">26만</div>
      <div class="stat-label">Tour API 건수</div>
    </div>
    <div>
      <div class="stat-num">5</div>
      <div class="stat-label">Pipeline Steps</div>
    </div>
  </div>
</div>

<!-- 데이터 소스 -->
<section id="sources">
  <div class="section-eyebrow"><span>// 01</span> 데이터 소스</div>
  <h2 class="section-title">쓸만한 출처</h2>
  <p class="section-desc">
    K-drama 촬영지만 깔끔하게 API로 제공되는 단일 DB는 부족해서, 공식 관광 데이터 + 촬영지 큐레이션 데이터 + 자체 검증 조합이 현실적입니다.
  </p>
  <div style="overflow:hidden;border-radius:12px;">
  <table class="source-table">
    <thead>
      <tr>
        <th>용도</th>
        <th>데이터 소스</th>
        <th>우선순위</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>국내 관광지 기본 정보</td>
        <td><a href="https://www.data.go.kr/data/15101578/openapi.do" target="_blank">한국관광공사 TourAPI</a></td>
        <td><span class="priority p-critical">최우선</span></td>
      </tr>
      <tr>
        <td>공식 드라마 촬영지 콘텐츠</td>
        <td><a href="https://english.visitkorea.or.kr" target="_blank">VisitKorea Filming Locations</a></td>
        <td><span class="priority p-high">높음</span></td>
      </tr>
      <tr>
        <td>도시별 드라마 촬영지 코스</td>
        <td>VisitKorea K-drama course examples</td>
        <td><span class="priority p-high">높음</span></td>
      </tr>
      <tr>
        <td>서울권 촬영지</td>
        <td>Visit Seoul K-drama locations</td>
        <td><span class="priority p-mid">중간</span></td>
      </tr>
      <tr>
        <td>지역/지자체 촬영지</td>
        <td>각 시·도 관광공사, 시청/군청 관광 페이지</td>
        <td><span class="priority p-mid">중간</span></td>
      </tr>
      <tr>
        <td>영화/촬영지 데이터 참고</td>
        <td>한국영상자료원 촬영지 데이터</td>
        <td><span class="priority p-mid">중간</span></td>
      </tr>
      <tr>
        <td>좌표/지도 보강</td>
        <td>OpenStreetMap / Wikidata</td>
        <td><span class="priority p-mid">중간</span></td>
      </tr>
      <tr>
        <td>커뮤니티 보강</td>
        <td>K-drama Locations 팬 DB <span style="font-size:11px;color:var(--text3)">— 라이선스 확인 필요</span></td>
        <td><span class="priority p-ref">참고용</span></td>
      </tr>
    </tbody>
  </table>
  </div>
  <p style="font-size:12px;color:var(--text3);margin-top:12px;line-height:1.8;">
    가장 우선순위 높은 건 한국관광공사 TourAPI — 국내 관광정보 약 26만 건 제공. 지역기반 / 위치기반 / 키워드검색 / 공통정보 / 이미지정보 쿼리 지원.
  </p>
</section>

<!-- 파이프라인 -->
<section id="pipeline" style="background:var(--bg2);max-width:100%;padding:96px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 32px;">
  <div class="section-eyebrow"><span>// 02</span> 추천 데이터 파이프라인</div>
  <h2 class="section-title">사용자 쿼리 →<br>데이터 수집 파이프라인</h2>
  <p class="section-desc">VisitKorea seed 수집부터 신뢰도 등급 부여까지 5단계 플로우입니다.</p>

  <div class="pipeline-wrap">
    <div class="pipeline-line"></div>

    <div class="pipeline-step">
      <div class="step-circle">01</div>
      <div class="step-eyebrow">Seed Collection</div>
      <div class="step-title">드라마 촬영지 seed 수집</div>
      <p class="step-desc">VisitKorea / 지자체 페이지에서 드라마 촬영지 seed 수집. 수원 K-drama 코스, 제주 "King the Land" 촬영지 등 RAG 문서로 활용하기 좋은 콘텐츠.</p>
    </div>

    <div class="pipeline-step">
      <div class="step-circle">02</div>
      <div class="step-eyebrow">API Enrichment</div>
      <div class="step-title">TourAPI로 기본 정보 보강</div>
      <p class="step-desc">관광지 기본 정보, 주소, 이미지, 좌표. 드라마·촬영지·작품명 키워드로 검색해서 seed를 보강합니다.</p>
      <div class="code-block">
        <span class="c"># TourAPI 키워드 검색 예시</span><br>
        <span class="k">keyword</span>: <span class="v">"드라마 촬영지"</span> | <span class="v">"작품명"</span><br>
        <span class="k">contentTypeId</span>: <span class="v">12</span> <span class="c">(관광지)</span><br>
        <span class="k">areaCode</span>: <span class="v">지역코드</span> → 좌표·이미지 반환
      </div>
    </div>

    <div class="pipeline-step">
      <div class="step-circle">03</div>
      <div class="step-eyebrow">Geo Enrichment</div>
      <div class="step-title">OSM / Wikidata로 좌표·분류 보강</div>
      <p class="step-desc">좌표 누락 항목 보완. 행정구역·분류 태그 정규화. OpenStreetMap + Wikidata 조합으로 커버.</p>
    </div>

    <div class="pipeline-step">
      <div class="step-circle">04</div>
      <div class="step-eyebrow">Tagging</div>
      <div class="step-title">작품명·관계 타입 자체 태깅</div>
      <p class="step-desc">작품명, 장소명, 관계 타입을 자체 태깅. drama_id ↔ place_id 매핑 + relation_type 분류.</p>
      <div class="code-block">
        <span class="k">relation_type</span>:<br>
        &nbsp;&nbsp;<span class="v">official_filming_location</span> <span class="c">← 제작사 공식</span><br>
        &nbsp;&nbsp;<span class="v">tourism_board_recommended</span> <span class="c">← 관광공사</span><br>
        &nbsp;&nbsp;<span class="v">fan_pilgrimage</span>           <span class="c">← 팬 커뮤니티</span><br>
        &nbsp;&nbsp;<span class="v">atmosphere_match</span>         <span class="c">← 분위기 유사</span>
      </div>
    </div>

    <div class="pipeline-step">
      <div class="step-circle">05</div>
      <div class="step-eyebrow">Quality Scoring</div>
      <div class="step-title">신뢰도 등급 부여</div>
      <p class="step-desc">공식 관광공사 출처 → HIGH / 지자체 추천 → MID / 팬 커뮤니티 → LOW. confidence_level로 RAG 검색 시 필터링 활용.</p>
      <div class="code-block">
        <span class="k">confidence_level</span>:<br>
        &nbsp;&nbsp;<span class="v" style="color:#50c8a0">HIGH</span> — 공식 발표, 제작사 확인<br>
        &nbsp;&nbsp;<span class="v" style="color:#d8902a">MID</span> &nbsp;— 관광공사·지자체 추천<br>
        &nbsp;&nbsp;<span class="v" style="color:#e8607a">LOW</span> &nbsp;— 팬 커뮤니티, 블로그
      </div>
    </div>
  </div>
</div>
</section>

<!-- 데이터 모델 (Schema) -->
<section id="schema">
  <div class="section-eyebrow"><span>// 03</span> 데이터 모델</div>
  <h2 class="section-title">데이터 스키마</h2>
  <p class="section-desc">Drama · Place · DramaPlaceRelation 3개 엔티티로 구성. 관계 타입과 신뢰도 등급이 핵심 필드입니다.</p>

  <!-- Drama -->
  <div style="margin-bottom:12px;">
    <div class="schema-wrap">
      <div class="schema-head">
        <div class="schema-head-title">Drama</div>
        <div class="schema-badge">ENTITY</div>
      </div>
      <div class="field-grid">
        <div class="field-cell">
          <div class="field-num">FIELD_01</div>
          <div class="field-name">title</div>
          <div class="field-desc">작품 제목. 검색 및 매핑의 기준 키.</div>
          <div class="field-examples"><span class="field-ex">str</span></div>
        </div>
        <div class="field-cell">
          <div class="field-num">FIELD_02</div>
          <div class="field-name">original_title</div>
          <div class="field-desc">한국어 원제. 공식 표기 기준.</div>
          <div class="field-examples"><span class="field-ex">str</span></div>
        </div>
        <div class="field-cell">
          <div class="field-num">FIELD_03</div>
          <div class="field-name">year / genre</div>
          <div class="field-desc">방영 연도 및 장르 분류.</div>
          <div class="field-examples"><span class="field-ex">int</span><span class="field-ex">str</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Place -->
  <div style="margin-bottom:12px;">
    <div class="schema-wrap">
      <div class="schema-head">
        <div class="schema-head-title">Place</div>
        <div class="schema-badge">ENTITY</div>
      </div>
      <div class="field-grid">
        <div class="field-cell">
          <div class="field-num">FIELD_01</div>
          <div class="field-name">name</div>
          <div class="field-desc">실제 방문 가능한 구체적 장소명.</div>
          <div class="field-examples"><span class="field-ex">str</span></div>
        </div>
        <div class="field-cell">
          <div class="field-num">FIELD_02</div>
          <div class="field-name">country / region / city</div>
          <div class="field-desc">도도부현 + 시정촌 형태. 지역 여행 동선 구성에 필수.</div>
          <div class="field-examples"><span class="field-ex">서울</span><span class="field-ex">제주</span><span class="field-ex">부산</span></div>
        </div>
        <div class="field-cell">
          <div class="field-num">FIELD_03</div>
          <div class="field-name">lat / lng</div>
          <div class="field-desc">지도 표시 및 위치기반 검색 핵심 좌표.</div>
          <div class="field-examples"><span class="field-ex">float</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- DramaPlaceRelation -->
  <div class="schema-wrap">
    <div class="schema-head">
      <div class="schema-head-title">DramaPlaceRelation</div>
      <div class="schema-badge">RELATION</div>
    </div>
    <div class="field-grid">
      <div class="field-cell">
        <div class="field-num">FIELD_01</div>
        <div class="field-name">drama_id / place_id</div>
        <div class="field-desc">Drama ↔ Place 연결 FK.</div>
        <div class="field-examples"><span class="field-ex">fk</span></div>
      </div>
      <div class="field-cell">
        <div class="field-num">FIELD_02</div>
        <div class="field-name">relation_type</div>
        <div class="field-desc">스팟과 작품의 연결 근거. 신뢰도에 직결되는 핵심 필드.</div>
        <div class="field-examples">
          <span class="field-ex">공식 배경지</span>
          <span class="field-ex">팬 성지</span>
          <span class="field-ex">분위기 유사</span>
        </div>
      </div>
      <div class="field-cell">
        <div class="field-num">FIELD_03</div>
        <div class="field-name">confidence_level</div>
        <div class="field-desc">HIGH / MID / LOW 3단계. 공식 발표=HIGH, 팬 커뮤니티=LOW.</div>
        <div class="field-examples">
          <span class="field-ex high">HIGH</span>
          <span class="field-ex mid">MID</span>
          <span class="field-ex low">LOW</span>
        </div>
      </div>
      <div class="field-cell">
        <div class="field-num">FIELD_04</div>
        <div class="field-name">scene_description</div>
        <div class="field-desc">어느 장면에서 등장하는지 설명.</div>
        <div class="field-examples"><span class="field-ex">str</span></div>
      </div>
      <div class="field-cell">
        <div class="field-num">FIELD_05</div>
        <div class="field-name">evidence_url</div>
        <div class="field-desc">공식 관광청·제작사·지자체 등 1차 출처 URL.</div>
        <div class="field-examples"><span class="field-ex">url</span></div>
      </div>
      <div class="field-cell">
        <div class="field-num">FIELD_06</div>
        <div class="field-name">source_url</div>
        <div class="field-desc">팬사이트는 신뢰도 낮음 표기.</div>
        <div class="field-examples"><span class="field-ex">url</span></div>
      </div>
    </div>
  </div>
</section>

<!-- 촬영지 스팟 예시 -->
<section id="spots" style="background:var(--bg2);max-width:100%;padding:96px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 32px;">
  <div class="section-eyebrow"><span>// 04</span> 촬영지 스팟 예시</div>
  <h2 class="section-title">핵심 촬영지 스팟</h2>
  <p class="section-desc">작품별 대표 성지를 신뢰도와 관계 유형으로 구조화했습니다.</p>

  <div class="filter-row">
    <button class="filter-btn active">전체</button>
    <button class="filter-btn">🌸 킹더랜드</button>
    <button class="filter-btn">💙 이상한 변호사 우영우</button>
    <button class="filter-btn">🔥 오징어 게임</button>
    <button class="filter-btn">🌿 갯마을 차차차</button>
  </div>

  <div class="spot-grid">
    <div class="spot-card">
      <div class="spot-card-head">
        <span class="drama-badge">킹더랜드</span>
        <span class="confidence">HIGH</span>
      </div>
      <div class="spot-title">제주 성산일출봉 일대</div>
      <div class="spot-loc">📍 제주특별자치도 서귀포시</div>
      <p class="spot-desc">킹더랜드 주요 촬영지. 성산일출봉 주변 해안 산책로 및 카페 거리 다수 등장.</p>
      <div class="spot-tags">
        <span class="tag">자연경관</span>
        <span class="tag">해안</span>
        <span class="tag accent">공식 배경지</span>
      </div>
      <div class="spot-card-foot">
        <span class="spot-verify">✓ 연중 방문 가능</span>
        <span class="spot-ref">참고 →</span>
      </div>
    </div>
    <div class="spot-card">
      <div class="spot-card-head">
        <span class="drama-badge">이상한 변호사 우영우</span>
        <span class="confidence">HIGH</span>
      </div>
      <div class="spot-title">소덕동 팽나무 마을</div>
      <div class="spot-loc">📍 경상남도 창원시</div>
      <p class="spot-desc">드라마 핵심 배경. 실제 팽나무와 마을 전경이 그대로 보존되어 있어 성지 방문객 급증.</p>
      <div class="spot-tags">
        <span class="tag">마을</span>
        <span class="tag">자연</span>
        <span class="tag accent">공식 배경지</span>
      </div>
      <div class="spot-card-foot">
        <span class="spot-verify">✓ 연중 방문 가능</span>
        <span class="spot-ref">참고 →</span>
      </div>
    </div>
    <div class="spot-card">
      <div class="spot-card-head">
        <span class="drama-badge">오징어 게임</span>
        <span class="confidence" style="color:var(--amber)">MID</span>
      </div>
      <div class="spot-title">인천 을왕리 해수욕장</div>
      <div class="spot-loc">📍 인천광역시 중구</div>
      <p class="spot-desc">시즌 1 초반 배경 촬영지. 드라마 흥행 후 한국 관광명소로 부상. 방문객 안내 시설 운영 중.</p>
      <div class="spot-tags">
        <span class="tag">해변</span>
        <span class="tag blue">관광공사 추천</span>
      </div>
      <div class="spot-card-foot">
        <span class="spot-verify">✓ 연중 방문 가능</span>
        <span class="spot-ref">참고 →</span>
      </div>
    </div>
  </div>
</div>
</section>

<!-- 주의사항 -->
<section id="notice">
  <div class="section-eyebrow"><span>// 05</span> 라이선스 주의사항</div>
  <h2 class="section-title">MVP 전략 &<br>라이선스 가이드</h2>
  <div class="notice">
    <strong>⚠ 팬 사이트·블로그 데이터 직접 DB화 금지</strong><br>
    팬 사이트·블로그 데이터를 그대로 긁어와 DB화하면 라이선스 문제가 생길 수 있습니다.
    MVP는 <strong>공식 관광공사·지자체·공공데이터 중심</strong>으로 가고,
    팬 데이터는 <strong>링크·참고 수준</strong> 또는 <strong>직접 작성 요약</strong>으로 다루는 게 안전합니다.
  </div>
  <div style="margin-top:24px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
    <div style="background:var(--bg2);border:1px solid rgba(230,238,233,.2);border-radius:10px;padding:20px;">
      <div style="font-family:var(--mono);font-size:10px;color:var(--green);margin-bottom:8px;letter-spacing:.08em;">✓ 안전</div>
      <div style="font-size:14px;font-weight:500;margin-bottom:8px;">공공데이터 활용</div>
      <p style="font-size:12px;color:var(--text2);line-height:1.8;">한국관광공사 TourAPI, VisitKorea, 지자체 공식 관광 페이지. 공공누리 라이선스 확인 후 사용.</p>
    </div>
    <div style="background:var(--bg2);border:1px solid rgba(169,130,30,.2);border-radius:10px;padding:20px;">
      <div style="font-family:var(--mono);font-size:10px;color:var(--amber);margin-bottom:8px;letter-spacing:.08em;">△ 주의</div>
      <div style="font-size:14px;font-weight:500;margin-bottom:8px;">팬 데이터 참고</div>
      <p style="font-size:12px;color:var(--text2);line-height:1.8;">K-drama Locations 등 팬 DB는 링크·참고 수준으로만 활용. 직접 DB화 금지. 반드시 라이선스 확인.</p>
    </div>
    <div style="background:var(--bg2);border:1px solid rgba(212,175,55,.2);border-radius:10px;padding:20px;">
      <div style="font-family:var(--mono);font-size:10px;color:var(--accent);margin-bottom:8px;letter-spacing:.08em;">✗ 금지</div>
      <div style="font-size:14px;font-weight:500;margin-bottom:8px;">무단 스크래핑</div>
      <p style="font-size:12px;color:var(--text2);line-height:1.8;">블로그·SNS·팬사이트 콘텐츠 무단 수집 및 DB화. 저작권법 위반 가능. 요약 직접 작성으로 대체.</p>
    </div>
  </div>
</section>

<footer>
  K-drama 촬영지 데이터 파이프라인 · 공공데이터 기반 설계 가이드
</footer>

<script>
// filter buttons
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});
</script>
</body>
</html>
```

