```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>로컬루트 — 요구사항 정의서 v1.1</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+KR:wght@600;700&display=swap"
      rel="stylesheet"
    />
    <style>
      /* ── TOKENS ── */
      :root {
        --brand-green: #1B3B32;
        --brand-green-900: #10251F;
        --brand-green-800: #173329;
        --brand-green-100: #E6EEE9;
        --brand-gold: #D4AF37;
        --brand-gold-700: #A9821E;
        --brand-gold-100: #F6EBC4;
        --navy: #1B3B32;
        --navy2: #10251F;
        --navy-lt: #E6EEE9;
        --navy-xlt: #F7F3EA;
        --green: #1B3B32;
        --green-lt: #E6EEE9;
        --terra: #A9821E;
        --terra-lt: #F6EBC4;
        --ink: #111827;
        --ink2: #374151;
        --ink3: #6b7280;
        --ink4: #9ca3af;
        --rule: #e5e7eb;
        --paper: #fafafa;
        --white: #ffffff;
        --p0-bg: #fef2f2;
        --p0-txt: #991b1b;
        --p0-bdr: #fecaca;
        --p1-bg: #fffbeb;
        --p1-txt: #92400e;
        --p1-bdr: #fde68a;
        --p2-bg: #f0fdf4;
        --p2-txt: #166534;
        --p2-bdr: #bbf7d0;
        --sidebar-w: 240px;
        --doc-max: 900px;
      }

      /* ── RESET ── */
      *,
      *::before,
      *::after {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }
      html {
        font-size: 15px;
        scroll-behavior: smooth;
      }
      body {
        font-family: "IBM Plex Sans KR", sans-serif;
        background: var(--paper);
        color: var(--ink);
        line-height: 1.7;
      }
      a {
        color: var(--navy);
        text-decoration: none;
      }
      ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
      }
      ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
      }

      /* ── LAYOUT ── */
      .layout {
        display: flex;
        min-height: 100vh;
      }

      /* ── SIDEBAR ── */
      aside {
        width: var(--sidebar-w);
        flex-shrink: 0;
        background: var(--navy2);
        position: sticky;
        top: 0;
        height: 100vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
      }
      .aside-brand {
        padding: 22px 20px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }
      .aside-logo {
        font-family: "Noto Serif KR", serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 3px;
      }
      .aside-ver {
        font-size: 0.65rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.45);
      }
      .aside-status {
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 5px;
      }
      .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #4ade80;
      }
      .aside-status span {
        font-size: 0.67rem;
        color: rgba(255, 255, 255, 0.5);
      }
      nav.toc {
        padding: 14px 0;
        flex: 1;
      }
      .toc-section {
        margin-bottom: 2px;
      }
      .toc-section-hd {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 6px 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.35);
        cursor: pointer;
        transition: all 0.2s;
      }
      .toc-section-hd:hover {
        color: rgba(255, 255, 255, 0.6);
      }
      .toc-link {
        display: block;
        padding: 5px 20px 5px 30px;
        font-size: 0.74rem;
        color: rgba(255, 255, 255, 0.55);
        transition: all 0.18s;
        border-left: 2px solid transparent;
      }
      .toc-link:hover {
        color: #fff;
        background: rgba(255, 255, 255, 0.05);
      }
      .toc-link.active {
        color: #fff;
        border-left-color: #D4AF37;
        background: rgba(212, 175, 55, 0.14);
      }
      .aside-footer {
        padding: 16px 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.64rem;
        color: rgba(255, 255, 255, 0.3);
        line-height: 1.6;
      }
      .print-btn {
        width: 100%;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 7px;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.72rem;
        cursor: pointer;
        font-family: "IBM Plex Sans KR", sans-serif;
        transition: all 0.2s;
        margin-bottom: 10px;
      }
      .print-btn:hover {
        background: rgba(255, 255, 255, 0.14);
        color: #fff;
      }

      /* ── MAIN DOCUMENT ── */
      main {
        flex: 1;
        padding: 0 48px 80px;
        max-width: calc(var(--doc-max) + 96px);
        min-width: 0;
      }

      /* ── DOCUMENT COVER ── */
      .doc-cover {
        padding: 56px 0 44px;
        border-bottom: 2px solid var(--navy);
        margin-bottom: 44px;
      }
      .cover-label {
        font-size: 0.67rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--navy);
        margin-bottom: 10px;
      }
      .cover-title {
        font-family: "Noto Serif KR", serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1.2;
        margin-bottom: 6px;
      }
      .cover-subtitle {
        font-size: 1rem;
        color: var(--ink3);
        margin-bottom: 32px;
        font-style: italic;
      }
      .cover-meta {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 0;
        border: 1px solid var(--rule);
        border-radius: 8px;
        overflow: hidden;
      }
      .meta-item {
        padding: 11px 16px;
        border-right: 1px solid var(--rule);
      }
      .meta-item:last-child {
        border-right: none;
      }
      .meta-item:nth-child(n + 3) {
        border-top: 1px solid var(--rule);
      }
      .meta-key {
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--ink4);
        margin-bottom: 3px;
      }
      .meta-val {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--ink);
      }
      .meta-val.green {
        color: var(--green);
      }
      .detail-docs {
        margin: 0 0 44px;
        padding: 24px;
        border: 1px solid var(--rule);
        border-left: 4px solid var(--green);
        border-radius: 8px;
        background: var(--white);
      }
      .detail-docs h2 {
        margin: 0 0 8px;
        color: var(--navy);
        font-family: "Noto Serif KR", serif;
        font-size: 1.2rem;
      }
      .detail-docs p {
        margin: 0 0 18px;
        color: var(--ink3);
        font-size: 0.9rem;
      }
      .detail-doc-list {
        display: grid;
        gap: 10px;
        margin: 0;
        padding: 0;
        list-style: none;
      }
      .detail-doc-list a {
        display: block;
        padding: 13px 15px;
        border: 1px solid var(--rule);
        border-radius: 8px;
        color: var(--ink);
        text-decoration: none;
        background: var(--navy-xlt);
      }
      .detail-doc-list a:hover {
        border-color: var(--green);
        background: var(--green-lt);
      }
      .detail-doc-list strong {
        display: block;
        color: var(--navy);
        font-size: 0.92rem;
      }
      .detail-doc-list span {
        display: block;
        margin-top: 3px;
        color: var(--ink3);
        font-size: 0.8rem;
      }

      /* ── SECTION ── */
      .doc-section {
        margin-bottom: 52px;
        scroll-margin-top: 28px;
      }
      .section-num {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--navy);
        margin-bottom: 5px;
      }
      h1.s-h1 {
        font-family: "Noto Serif KR", serif;
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--navy);
        padding-bottom: 10px;
        border-bottom: 2px solid var(--navy);
        margin-bottom: 24px;
      }
      h2.s-h2 {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--ink);
        margin: 28px 0 12px;
        padding-left: 10px;
        border-left: 3px solid var(--navy);
      }
      h3.s-h3 {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--green);
        margin: 20px 0 10px;
      }
      p.doc-p {
        font-size: 0.86rem;
        color: var(--ink2);
        line-height: 1.85;
        margin-bottom: 10px;
      }
      .bullet-list {
        display: flex;
        flex-direction: column;
        gap: 5px;
        margin: 10px 0 14px;
        padding-left: 16px;
      }
      .bullet-list li {
        font-size: 0.84rem;
        color: var(--ink2);
        line-height: 1.7;
        list-style: none;
        display: flex;
        gap: 8px;
      }
      .bullet-list li::before {
        content: "—";
        color: var(--ink4);
        flex-shrink: 0;
      }

      /* ── SIMPLE 2-COL TABLE ── */
      .info-tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        margin: 12px 0 20px;
      }
      .info-tbl th {
        background: var(--navy);
        color: #fff;
        padding: 9px 14px;
        font-weight: 600;
        font-size: 0.78rem;
        text-align: left;
      }
      .info-tbl td {
        padding: 9px 14px;
        border-bottom: 1px solid var(--rule);
        vertical-align: top;
        line-height: 1.65;
      }
      .info-tbl tr:last-child td {
        border-bottom: none;
      }
      .info-tbl tr:nth-child(even) td {
        background: var(--navy-xlt);
      }
      .info-tbl .key-cell {
        background: var(--navy-lt);
        font-weight: 600;
        color: var(--navy);
        white-space: nowrap;
        width: 22%;
      }
      .info-tbl .key-cell.green-key {
        background: var(--green-lt);
        color: var(--green);
      }
      .info-tbl .key-cell.amber-key {
        background: #fdf3eb;
        color: var(--terra);
      }
      .info-tbl .key-cell.red-key {
        background: #fef2f2;
        color: #991b1b;
      }
      .info-tbl .key-cell.blue-key {
        background: #eff6ff;
        color: #1d4ed8;
      }
      .info-tbl code {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.76rem;
        background: var(--paper);
        padding: 1px 5px;
        border-radius: 3px;
        border: 1px solid var(--rule);
      }

      /* ── REQUIREMENTS TABLE ── */
      .req-tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.81rem;
        margin: 10px 0 22px;
      }
      .req-tbl thead th {
        background: var(--navy);
        color: #fff;
        padding: 9px 12px;
        font-weight: 600;
        font-size: 0.75rem;
        text-align: left;
        position: sticky;
        top: 0;
      }
      .req-tbl thead th:first-child {
        width: 100px;
      }
      .req-tbl thead th:nth-child(3) {
        width: 88px;
        text-align: center;
      }
      .req-tbl thead th:last-child {
        width: 150px;
      }
      .req-tbl tbody td {
        padding: 9px 12px;
        border-bottom: 1px solid var(--rule);
        vertical-align: top;
        line-height: 1.65;
      }
      .req-tbl tbody tr:nth-child(even) td {
        background: var(--navy-xlt);
      }
      .req-tbl tbody tr:hover td {
        background: #eef4ff;
      }
      .req-id {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.74rem;
        font-weight: 500;
        color: var(--navy);
        white-space: nowrap;
      }
      .req-note {
        font-size: 0.74rem;
        color: var(--ink4);
      }

      /* ── PRIORITY BADGES ── */
      .pri {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 20px;
        letter-spacing: 0.05em;
        white-space: nowrap;
      }
      .pri.p0 {
        background: var(--p0-bg);
        color: var(--p0-txt);
        border: 1px solid var(--p0-bdr);
      }
      .pri.p1 {
        background: var(--p1-bg);
        color: var(--p1-txt);
        border: 1px solid var(--p1-bdr);
      }
      .pri.p2 {
        background: var(--p2-bg);
        color: var(--p2-txt);
        border: 1px solid var(--p2-bdr);
      }

      /* ── STATUS BADGES ── */
      .sbadge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 9px;
        border-radius: 12px;
      }
      .sb-ok {
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
      }
      .sb-part {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
      }
      .sb-no {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
      }
      .sb-link {
        background: #fdf3eb;
        color: var(--terra);
        border: 1px solid #fed7aa;
      }
      .sb-auto {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
      }

      /* ── API SUMMARY GRID ── */
      .api-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 14px;
        margin: 14px 0 24px;
      }
      .api-card {
        border: 1px solid var(--rule);
        border-radius: 10px;
        overflow: hidden;
      }
      .api-card-hd {
        padding: 11px 14px;
        display: flex;
        align-items: center;
        gap: 9px;
      }
      .api-card-ico {
        width: 32px;
        height: 32px;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
      }
      .api-ic-g {
        background: #eff6ff;
      }
      .api-ic-n {
        background: #f0fdf4;
      }
      .api-ic-k {
        background: #fffbeb;
      }
      .api-ic-y {
        background: #fef2f2;
      }
      .api-ic-w {
        background: #eff6ff;
      }
      .api-card-name {
        font-size: 0.85rem;
        font-weight: 700;
      }
      .api-card-role {
        font-size: 0.71rem;
        color: var(--ink4);
      }
      .api-card-body {
        padding: 10px 14px;
        border-top: 1px solid var(--rule);
        background: var(--navy-xlt);
      }
      .api-card-body p {
        font-size: 0.75rem;
        color: var(--ink3);
        line-height: 1.65;
        margin-bottom: 4px;
      }
      .api-card-body p:last-child {
        margin-bottom: 0;
      }
      .api-card-body strong {
        color: var(--ink);
      }

      /* ── COMPARISON TABLE ── */
      .cmp-tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        margin: 12px 0 20px;
      }
      .cmp-tbl th {
        background: var(--navy);
        color: #fff;
        padding: 9px 12px;
        font-weight: 600;
        font-size: 0.76rem;
      }
      .cmp-tbl td {
        padding: 9px 12px;
        border-bottom: 1px solid var(--rule);
        vertical-align: middle;
      }
      .cmp-tbl tr:nth-child(even) td {
        background: var(--navy-xlt);
      }
      .cmp-tbl tr:hover td {
        background: #eef4ff;
      }
      .sym-ok {
        color: #16a34a;
        font-weight: 700;
      }
      .sym-no {
        color: #dc2626;
        font-weight: 700;
      }
      .sym-pt {
        color: #d97706;
        font-weight: 700;
      }

      /* ── VALUE TABLE ── */
      .val-tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.81rem;
        margin: 12px 0 18px;
      }
      .val-tbl th {
        background: var(--green);
        color: #fff;
        padding: 9px 14px;
        font-weight: 600;
        font-size: 0.76rem;
        text-align: left;
      }
      .val-tbl td {
        padding: 9px 14px;
        border-bottom: 1px solid var(--rule);
        line-height: 1.65;
      }
      .val-tbl tr:last-child td {
        border-bottom: none;
      }
      .val-tbl tr:nth-child(even) td {
        background: var(--green-lt);
      }
      .val-key {
        font-weight: 700;
        color: var(--green);
      }

      /* ── PRIORITY LEGEND ── */
      .pri-legend {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        padding: 10px 14px;
        background: var(--navy-xlt);
        border-radius: 7px;
        margin-bottom: 16px;
        font-size: 0.75rem;
        color: var(--ink3);
      }
      .pri-legend span:first-child {
        font-weight: 600;
        color: var(--ink);
        margin-right: 4px;
      }

      /* ── FLOW TABLE ── */
      .flow-tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        margin: 10px 0 18px;
      }
      .flow-tbl th {
        background: var(--navy);
        color: #fff;
        padding: 9px 13px;
        font-weight: 600;
        font-size: 0.76rem;
      }
      .flow-tbl td {
        padding: 9px 13px;
        border-bottom: 1px solid var(--rule);
        line-height: 1.65;
        vertical-align: top;
      }
      .flow-tbl tr:nth-child(even) td {
        background: var(--navy-xlt);
      }
      .flow-num {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--navy);
        text-align: center;
      }
      .flow-in {
        background: var(--navy-lt);
        color: var(--navy);
        font-size: 0.78rem;
      }

      /* ── CONSTRAINT / NOTE BOX ── */
      .note-box {
        background: var(--navy-lt);
        border-left: 3px solid var(--navy);
        border-radius: 0 7px 7px 0;
        padding: 12px 16px;
        margin: 12px 0 16px;
        font-size: 0.82rem;
        color: var(--ink2);
        line-height: 1.75;
      }
      .warn-box {
        background: var(--terra-lt);
        border-left: 3px solid var(--terra);
        border-radius: 0 7px 7px 0;
        padding: 12px 16px;
        margin: 12px 0 16px;
        font-size: 0.82rem;
        color: var(--ink2);
        line-height: 1.75;
      }
      .note-box strong,
      .warn-box strong {
        font-weight: 700;
        color: var(--navy);
      }
      .warn-box strong {
        color: var(--terra);
      }

      /* ── CHANGE LOG TABLE ── */
      .log-tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        margin: 12px 0;
      }
      .log-tbl th {
        background: var(--navy);
        color: #fff;
        padding: 9px 14px;
        font-weight: 600;
        font-size: 0.76rem;
      }
      .log-tbl td {
        padding: 10px 14px;
        border-bottom: 1px solid var(--rule);
      }

      /* ── RESPONSIVE ── */
      @media (max-width: 840px) {
        aside {
          display: none;
        }
        main {
          padding: 20px 16px 60px;
        }
        .cover-title {
          font-size: 1.7rem;
        }
      }

      /* ── PRINT ── */
      @media print {
        aside {
          display: none;
        }
        main {
          padding: 0;
        }
        body {
          background: #fff;
        }
        .doc-cover {
          padding: 24px 0 20px;
        }
        .doc-section {
          break-inside: avoid;
        }
        .req-tbl thead th {
          background: #1B3B32 !important;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }
      }
    </style>
  </head>
  <body>
    <div class="layout">
      <!-- ═══ SIDEBAR ═══ -->
      <aside>
        <div class="aside-brand">
          <div class="aside-logo">🗺 로컬루트</div>
          <div class="aside-ver">Requirements Spec · v1.1</div>
          <div class="aside-status">
            <div class="status-dot"></div>
            <span>기획 단계</span>
          </div>
        </div>
        <nav class="toc">
          <div class="toc-section">
            <a class="toc-link active" href="#cover">표지 / 문서 정보</a>
            <a class="toc-link" href="#detail-requirements">세부 기능 요구사항</a>
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
            <a class="toc-link" href="#s3-1">3.1 챗봇 인터페이스</a>
            <a class="toc-link" href="#s3-2">3.2 추천 엔진 (테마)</a>
            <a class="toc-link" href="#s3-3">3.3 계절·축제 연동</a>
            <a class="toc-link" href="#s3-3b">3.4 RAG·에이전트</a>
            <a class="toc-link" href="#s3-3c">3.5 지도 연동</a>
            <a class="toc-link" href="#s3-4">3.6 장소 상세 정보</a>
            <a class="toc-link" href="#s3-5">3.7 외부 링크</a>
            <a class="toc-link" href="#s3-6">3.8 API 키 설정</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">4. API 연동 요구사항</div>
            <a class="toc-link" href="#s4-1">4.1 Google Maps</a>
            <a class="toc-link" href="#s4-2">4.2 Naver Maps</a>
            <a class="toc-link" href="#s4-3">4.3 Kakao Maps</a>
            <a class="toc-link" href="#s4-4">4.4 Yahoo Japan</a>
            <a class="toc-link" href="#s4-5">4.5 Open-Meteo</a>
            <a class="toc-link" href="#s4-6">4.6 연동 현황 요약</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">5. 비기능 요구사항</div>
            <a class="toc-link" href="#s5-1">5.1 성능</a>
            <a class="toc-link" href="#s5-2">5.2 보안</a>
            <a class="toc-link" href="#s5-3">5.3 호환성</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">6. 데이터 요구사항</div>
            <a class="toc-link" href="#s6-1">6.1 소도시 DB 구조</a>
            <a class="toc-link" href="#s6-2">6.2 DB 규모 목표</a>
          </div>
          <div class="toc-section">
            <div class="toc-section-hd">7. 제약사항 및 가정</div>
            <a class="toc-link" href="#s7-1">7.1 기술적 제약</a>
            <a class="toc-link" href="#s7-2">7.2 가정사항</a>
          </div>
          <div class="toc-section">
            <a class="toc-link" href="#s8">8. 변경 이력</a>
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
          <div class="cover-title">로컬루트 (Local Route)</div>
          <div class="cover-subtitle">
            오버투어리즘 회피형 국내·일본 소도시 테마 여정 추천 챗봇 — RAG ×
            멀티스텝 에이전트 기반
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
              <div class="meta-val">로컬루트 서비스 전체</div>
            </div>
          </div>
        </div>

        <section class="detail-docs" id="detail-requirements">
          <h2>세부 기능 요구사항</h2>
          <p>
            아래 문서는 모두 본 요구사항 정의서에 속한 세부 기능 요구사항이다.
            각 항목은 별도 HTML로 생성하지만, 정보 구조상 <code>01_requirements.html</code>의 하위 문서로 관리한다.
          </p>
          <ul class="detail-doc-list">
            <li>
              <a href="./02_overturizim.html">
                <strong>02. 오버투어리즘 대응 여행 추천 서비스</strong>
                <span>혼잡도 분산과 지역 관광 균형을 위한 기능 요구사항</span>
              </a>
            </li>
            <li>
              <a href="./03_korea_japan.html">
                <strong>03. 한일 축제 여행 챗봇</strong>
                <span>한국과 일본 축제 정보를 활용한 챗봇 기능 요구사항</span>
              </a>
            </li>
            <li>
              <a href="./04_trip_train.html">
                <strong>04. RailRoute-RAG</strong>
                <span>철도 여행 경로 추천과 RAG 응답 기능 요구사항</span>
              </a>
            </li>
            <li>
              <a href="./05_astro_rag_proposal.html">
                <strong>05. StarryNight-RAG</strong>
                <span>아스트로 투어리즘 플랫폼 기능 요구사항</span>
              </a>
            </li>
            <li>
              <a href="./06_kdrama-pipeline.html">
                <strong>06. K-drama 촬영지 데이터 파이프라인</strong>
                <span>촬영지 데이터 수집, 정제, 제공 파이프라인 요구사항</span>
              </a>
            </li>
          </ul>
        </section>

        <!-- ═══ 1. 문서 개요 ═══ -->
        <div class="doc-section" id="s1">
          <div class="section-num">Section 01</div>
          <h1 class="s-h1">1. 문서 개요</h1>

          <h2 class="s-h2" id="s1-1">1.1 목적</h2>
          <p class="doc-p">
            본 문서는 로컬루트(Local Route) 서비스의 아이디어 기획 단계에서
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
              Google Maps Platform, Naver Maps, Kakao Maps, Yahoo Japan,
              Open-Meteo API 연동
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
                  검색증강생성 — LLM이 답변 시 소도시 데이터(벡터DB)를 검색해
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
                  API 직접 호출 없이 외부 플랫폼(Naver, Kakao, Yahoo)의
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
            로컬루트는 오버투어리즘 회피를 목적으로 국내 및 일본의 비주류
            소도시를 6개 테마 여정으로 추천하는 대화형 챗봇 서비스다. 사용자가
            자연어로 취향과 여행 시기를 입력하면, 멀티스텝 에이전트가 취향을
            테마로 해석하고 RAG로 검색한 소도시 데이터에 근거하여 적합한 소도시
            2~4곳을 하나의 여정으로 묶어 추천 이유와 함께 제공한다. 한국은 한국
            소도시만, 일본은 일본 소도시만 추천하는 나라별 독립 트랙으로
            운영된다.
          </p>
          <p class="doc-p">
            추천 시 여행 시기(달/계절)에 빛나는 소도시와 그 시기 열리는
            축제·행사를 함께 묶어 제공하며, 각 결과에는 Google Maps, Naver Maps,
            Kakao Maps, Yahoo Japan의 4개 플랫폼 API가 역할 분담하여 지도·장소
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
                  벡터DB에서 테마+계절 적합도로 소도시를 검색해 2~4곳 선별
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
                <td>Naver / Kakao / Yahoo Japan 딥링크로 추가 정보 확인</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 3. 기능 요구사항 ═══ -->
        <div class="doc-section" id="s3">
          <div class="section-num">Section 03</div>
          <h1 class="s-h1">3. 기능 요구사항</h1>
          <div class="pri-legend">
            <span>우선순위</span>
            <span class="pri p0">P0 필수</span>
            <span class="pri p1">P1 권장</span>
            <span class="pri p2">P2 선택</span>
          </div>

          <h2 class="s-h2" id="s3-1">3.1 챗봇 인터페이스</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-001</td>
                <td>사용자가 자연어로 여행 조건을 자유롭게 입력할 수 있다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-002</td>
                <td>
                  챗봇은 출발지, 예산, 이동수단, 여행 스타일, 혼잡 회피 선호도를
                  대화로 수집한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-003</td>
                <td>빠른 입력을 위한 칩(Chip) 형태의 추천 질문을 제공한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-004</td>
                <td>
                  Google Places API 연동 시 장소 검색 기반 응답을 제공한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">API 키 필요</td>
              </tr>
              <tr>
                <td class="req-id">FR-005</td>
                <td>챗봇은 모바일 및 데스크톱 화면 모두에서 사용 가능하다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">반응형</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-2">3.2 추천 엔진 (테마 여정)</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-010</td>
                <td>
                  사용자 발화를 6개 테마(온천·바다·역사·미식·자연·예술) 중 하나
                  이상으로 분류한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">에이전트 1단계</td>
              </tr>
              <tr>
                <td class="req-id">FR-011</td>
                <td>
                  분류된 테마와 계절 적합도를 기준으로 소도시 후보를 선별한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">RAG 검색</td>
              </tr>
              <tr>
                <td class="req-id">FR-012</td>
                <td>
                  추천 결과는 하나의 테마로 묶인 2~4곳 소도시 여정을 추천 이유와
                  함께 제공한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">여정 단위</td>
              </tr>
              <tr>
                <td class="req-id">FR-013</td>
                <td>
                  여정 내 소도시의 방문 순서를 제안한다 (이동 동선은 순서 제안
                  수준)
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">동선 가볍게</td>
              </tr>
              <tr>
                <td class="req-id">FR-014</td>
                <td>혼잡도 낮은 소도시를 우선순위로 추천한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">핵심 가치</td>
              </tr>
              <tr>
                <td class="req-id">FR-015</td>
                <td>
                  국내(한국) 소도시와 일본 소도시를 나라별 독립 트랙으로 분리
                  추천한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">두 나라 미혼합</td>
              </tr>
              <tr>
                <td class="req-id">FR-016</td>
                <td>
                  국내 소도시 DB는 강원·충청·전남·경남 등 50개 이상을 포함한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">초기 DB 기준</td>
              </tr>
              <tr>
                <td class="req-id">FR-017</td>
                <td>
                  일본 소도시 DB는 호쿠리쿠·기후·산인 등 40개 이상을 포함한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">초기 DB 기준</td>
              </tr>
              <tr>
                <td class="req-id">FR-018</td>
                <td>
                  추천 여정 카드에 테마·이동 순서·예상 소요시간·태그를 표시한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-3">3.3 계절 · 축제 연동</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-020</td>
                <td>사용자가 여행 시기(달 또는 계절)를 입력할 수 있다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-021</td>
                <td>
                  각 소도시의 계절 적합도 점수(봄·여름·가을·겨울)를 추천에
                  반영한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">계절 매칭</td>
              </tr>
              <tr>
                <td class="req-id">FR-022</td>
                <td>
                  입력 시기에 해당 소도시에서 열리는 축제·행사를 함께 표시한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">시간축 확장</td>
              </tr>
              <tr>
                <td class="req-id">FR-023</td>
                <td>
                  축제·행사 정보는 월·계절 단위로만 관리한다 (정확한 연도별 날짜
                  미관리)
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">갱신 부담·환각 방지</td>
              </tr>
              <tr>
                <td class="req-id">FR-024</td>
                <td>
                  "가을에 좋은 자연 소도시"처럼 테마와 시기를 결합한 추천을
                  지원한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">복합 조건</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-3b">3.4 RAG · 멀티스텝 에이전트</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-027</td>
                <td>
                  소도시 데이터를 벡터DB에 임베딩하여 RAG 검색이 가능하도록 한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">grounding 기반</td>
              </tr>
              <tr>
                <td class="req-id">FR-028</td>
                <td>
                  추천 생성 시 검색된 실제 데이터를 근거로 사용하여 환각을
                  방지한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">핵심 차별점</td>
              </tr>
              <tr>
                <td class="req-id">FR-029</td>
                <td>
                  추천 파이프라인을 분류→검색→군집→여정 구성의 다단계로 처리한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">멀티스텝</td>
              </tr>
              <tr>
                <td class="req-id">FR-02A</td>
                <td>
                  각 단계의 출력을 검증하고, 실패 시 재시도 또는 폴백 처리한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">안정성</td>
              </tr>
              <tr>
                <td class="req-id">FR-02B</td>
                <td>
                  한·일이 동일한 파이프라인을 공유하며 벡터DB 데이터만 교체해
                  동작한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">재사용성</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-3c">3.5 지도 연동</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-020</td>
                <td>목적지 카드 클릭 시 하단 드로어(Drawer) 패널이 열린다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-021</td>
                <td>드로어의 지도 탭에서 목적지 위치를 지도로 표시한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-022</td>
                <td>
                  국내 목적지는 Google Maps / Naver Maps / Kakao Maps 탭을
                  제공한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">3개 탭</td>
              </tr>
              <tr>
                <td class="req-id">FR-023</td>
                <td>일본 목적지는 Google Maps 탭을 제공한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">Yahoo JS SDK 지원 중단</td>
              </tr>
              <tr>
                <td class="req-id">FR-024</td>
                <td>지도에 목적지 위치 마커와 이름 레이블을 표시한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-025</td>
                <td>
                  API 키 미설정 시 "API 설정 안내" 메시지와 설정 버튼을 표시한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">폴백 UI</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-4">3.6 장소 상세 정보</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-030</td>
                <td>Google Places API로 목적지의 평점, 리뷰 수를 표시한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">Google API 키 필요</td>
              </tr>
              <tr>
                <td class="req-id">FR-031</td>
                <td>Google Places API로 목적지 사진을 최대 4장 표시한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">Google API 키 필요</td>
              </tr>
              <tr>
                <td class="req-id">FR-032</td>
                <td>Google Places API로 운영시간(요일별)을 표시한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">Google API 키 필요</td>
              </tr>
              <tr>
                <td class="req-id">FR-033</td>
                <td>Google Places API로 현재 영업 중 여부를 표시한다</td>
                <td><span class="pri p2">P2</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-034</td>
                <td>
                  Google Places API로 주변 명소(관광지) 최대 4곳을 표시한다
                </td>
                <td><span class="pri p2">P2</span></td>
                <td class="req-note">반경 3km</td>
              </tr>
              <tr>
                <td class="req-id">FR-035</td>
                <td>Open-Meteo API로 목적지 현재 날씨를 자동 표시한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">API 키 불필요</td>
              </tr>
              <tr>
                <td class="req-id">FR-036</td>
                <td>날씨 정보에 아이콘, 기온, 풍속, 습도를 포함한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">WMO 코드 기반</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-5">3.7 외부 링크 및 플랫폼 연동</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-040</td>
                <td>
                  국내 목적지에 네이버 지도, 네이버 블로그 검색 딥링크를
                  제공한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-041</td>
                <td>국내 목적지에 카카오맵 딥링크를 제공한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-042</td>
                <td>
                  국내 목적지에 Kakao Local API로 주변 맛집·카페·숙박을 검색한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">REST Key 필요</td>
              </tr>
              <tr>
                <td class="req-id">FR-043</td>
                <td>
                  일본 목적지에 Yahoo Japan Maps, Yahoo Travel 딥링크를 제공한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-044</td>
                <td>
                  일본 목적지에 じゃらん, 食べログ, 楽天トラベル 딥링크를
                  제공한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-045</td>
                <td>드로어의 링크 탭에서 플랫폼별 연동 현황을 요약 표시한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s3-6">3.8 API 키 설정</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">FR-050</td>
                <td>
                  사용자가 UI에서 4개 플랫폼 API 키를 직접 입력·저장할 수 있다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">FR-051</td>
                <td>API 키는 브라우저 로컬 스토리지에 저장된다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">데모 환경 기준</td>
              </tr>
              <tr>
                <td class="req-id">FR-052</td>
                <td>내비게이션에 각 API 연결 상태를 색상 도트로 표시한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">G/N/K/Y/W</td>
              </tr>
              <tr>
                <td class="req-id">FR-053</td>
                <td>키 저장 후 SDK를 동적으로 로드하고 상태를 업데이트한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
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
                <div class="api-card-ico api-ic-n">🟢</div>
                <div>
                  <div class="api-card-name">Naver Maps (NCP)</div>
                  <div class="api-card-role">
                    한국 로컬 지도 · 블로그 리뷰 (국내 전용)
                  </div>
                </div>
              </div>
              <div class="api-card-body">
                <p>
                  <strong>역할:</strong> 한국어 지도 SDK + 블로그 검색 딥링크
                </p>
                <p>
                  <strong>상태:</strong>
                  <span class="sbadge sb-part">△ SDK 직접 / REST 딥링크</span>
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
                  <div class="api-card-name">Open-Meteo</div>
                  <div class="api-card-role">
                    실시간 날씨 (전 지역 · 키 불필요)
                  </div>
                </div>
              </div>
              <div class="api-card-body">
                <p>
                  <strong>역할:</strong> 기온, 날씨 상태, 풍속, 습도 자동 제공
                </p>
                <p>
                  <strong>상태:</strong>
                  <span class="sbadge sb-auto">✓ 항상 활성 (키 불필요)</span>
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

          <h2 class="s-h2" id="s4-2">4.2 Naver Maps (NCP)</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:22%">항목</th>
                <th>내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell green-key">역할</td>
                <td>
                  국내 소도시 한국어 지도 표시, 네이버 블로그 리뷰 딥링크 제공
                </td>
              </tr>
              <tr>
                <td class="key-cell green-key">사용 API</td>
                <td>
                  Naver Maps JavaScript SDK (지도 표시), Naver Local Search API
                  (향후)
                </td>
              </tr>
              <tr>
                <td class="key-cell green-key">연동 방식</td>
                <td>
                  JavaScript SDK — 클라이언트 직접 호출 / REST API는 백엔드
                  프록시 필요
                </td>
              </tr>
              <tr>
                <td class="key-cell green-key">필수 키</td>
                <td>Naver Cloud Platform NCP Client ID</td>
              </tr>
              <tr>
                <td class="key-cell green-key">제공 데이터</td>
                <td>한국어 지도, 커스텀 마커, 네이버 블로그 검색 딥링크</td>
              </tr>
              <tr>
                <td class="key-cell green-key">적용 국가</td>
                <td>국내 소도시 전용</td>
              </tr>
              <tr>
                <td class="key-cell green-key">CORS 제약</td>
                <td>
                  Maps SDK: 없음 / Local Search REST API: CORS 제한 → 딥링크
                  대체 제공
                </td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s4-3">4.3 Kakao Maps</h2>
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

          <h2 class="s-h2" id="s4-4">4.4 Yahoo Japan</h2>
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

          <h2 class="s-h2" id="s4-5">4.5 Open-Meteo (날씨)</h2>
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
                <td>전 목적지 실시간 날씨 정보 자동 제공 (API 키 불필요)</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">사용 API</td>
                <td>Open-Meteo Forecast API v1 (WMO 날씨 코드 기반)</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">연동 방식</td>
                <td>REST API — CORS 지원, 클라이언트 직접 호출 가능</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">필수 키</td>
                <td><strong>불필요</strong> (무료 오픈 API)</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">제공 데이터</td>
                <td>현재 기온(℃), 날씨 상태(WMO 코드), 풍속(km/h), 습도(%)</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">적용 국가</td>
                <td>국내 + 일본 소도시 공통 적용</td>
              </tr>
              <tr>
                <td class="key-cell blue-key">제약사항</td>
                <td>상업적 사용 시 Open-Meteo API 이용 정책 재확인 필요</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s4-6">4.6 API 연동 현황 요약</h2>
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
                <td><strong>Naver Maps</strong></td>
                <td>한국 로컬·블로그 리뷰</td>
                <td><span class="sym-ok">✓</span> 지원</td>
                <td><span class="sym-no">✗</span> CORS</td>
                <td>지도 SDK / REST 딥링크</td>
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
                <td><strong>Open-Meteo</strong></td>
                <td>실시간 날씨 (키 불필요)</td>
                <td>—</td>
                <td><span class="sym-ok">✓</span> CORS 지원</td>
                <td>항상 활성</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 5. 비기능 요구사항 ═══ -->
        <div class="doc-section" id="s5">
          <div class="section-num">Section 05</div>
          <h1 class="s-h1">5. 비기능 요구사항</h1>
          <div class="pri-legend">
            <span>우선순위</span><span class="pri p0">P0 필수</span
            ><span class="pri p1">P1 권장</span
            ><span class="pri p2">P2 선택</span>
          </div>

          <h2 class="s-h2" id="s5-1">5.1 성능</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">NFR-001</td>
                <td>챗봇 응답은 사용자 입력 후 1.5초 이내에 시작되어야 한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-001B</td>
                <td>
                  멀티스텝 에이전트 전체 처리(분류→검색→여정 구성)는 8초 이내를
                  목표로 한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">단계별 병렬화 고려</td>
              </tr>
              <tr>
                <td class="req-id">NFR-001C</td>
                <td>RAG 벡터 검색은 1초 이내에 결과를 반환해야 한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-002</td>
                <td>
                  지도 초기 렌더링은 SDK 로드 완료 후 2초 이내에 완료되어야 한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-003</td>
                <td>
                  Google Places API 호출은 결과 수신까지 3초 이내를 목표로 한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-004</td>
                <td>날씨 API(Open-Meteo) 응답은 2초 이내를 목표로 한다</td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-005</td>
                <td>
                  API 타임아웃 시 오류 메시지를 표시하고 기본 정보로 폴백한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">폴백 UI 필수</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s5-2">5.2 보안</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
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
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">데모 환경 기준</td>
              </tr>
              <tr>
                <td class="req-id">NFR-011</td>
                <td>
                  서비스 배포 시 API 키는 환경 변수 또는 서버 사이드에서
                  관리한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">배포 환경 적용</td>
              </tr>
              <tr>
                <td class="req-id">NFR-012</td>
                <td>
                  Google API 키에 HTTP Referer 제한을 설정하여 무단 사용을
                  방지한다
                </td>
                <td><span class="pri p1">P1</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-013</td>
                <td>
                  사용자 대화 내용은 로컬에서만 처리하며 별도 서버에 저장하지
                  않는다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s5-3">5.3 호환성 및 접근성</h2>
          <table class="req-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>요구사항 내용</th>
                <th>우선순위</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="req-id">NFR-020</td>
                <td>Chrome, Safari, Edge 최신 버전에서 정상 동작해야 한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">—</td>
              </tr>
              <tr>
                <td class="req-id">NFR-021</td>
                <td>모바일(iOS/Android) 브라우저에서 사용 가능해야 한다</td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">반응형 레이아웃</td>
              </tr>
              <tr>
                <td class="req-id">NFR-022</td>
                <td>
                  화면 너비 375px 이상에서 주요 기능이 모두 사용 가능해야 한다
                </td>
                <td><span class="pri p0">P0</span></td>
                <td class="req-note">iPhone SE 기준</td>
              </tr>
              <tr>
                <td class="req-id">NFR-023</td>
                <td>다크 모드를 지원해야 한다</td>
                <td><span class="pri p2">P2</span></td>
                <td class="req-note">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ═══ 6. 데이터 요구사항 ═══ -->
        <div class="doc-section" id="s6">
          <div class="section-num">Section 06</div>
          <h1 class="s-h1">6. 데이터 요구사항</h1>

          <h2 class="s-h2" id="s6-1">6.1 소도시 DB 구조</h2>
          <p class="doc-p">각 목적지는 다음 데이터 항목을 포함해야 한다.</p>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:20%">필드</th>
                <th style="width:18%">타입</th>
                <th>설명</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell"><code>id</code></td>
                <td>String</td>
                <td>고유 식별자 (영문 소문자, 예: <code>yeongwol</code>)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>nameKo</code></td>
                <td>String</td>
                <td>한국어 목적지명 (예: 강원 영월)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>nameJa</code></td>
                <td>String (선택)</td>
                <td>일본어 목적지명 (일본 소도시 한정)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>region</code></td>
                <td>String</td>
                <td>행정 구역명 (예: 강원도, 石川県)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>type</code></td>
                <td>Enum</td>
                <td>
                  국가 구분 — <code>KR</code> (국내) / <code>JP</code> (일본)
                </td>
              </tr>
              <tr>
                <td class="key-cell"><code>coords</code></td>
                <td>Object</td>
                <td>
                  위도(<code>lat</code>), 경도(<code>lng</code>) 좌표 (WGS84)
                </td>
              </tr>
              <tr>
                <td class="key-cell"><code>desc</code></td>
                <td>String</td>
                <td>30자 이내 핵심 설명문</td>
              </tr>
              <tr>
                <td class="key-cell"><code>reasons</code></td>
                <td>String[]</td>
                <td>추천 이유 3가지 (각 40자 이내)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>themes</code></td>
                <td>Object</td>
                <td>
                  6개 테마별 가중치 점수 (온천·바다·역사·미식·자연·예술, 0~100)
                </td>
              </tr>
              <tr>
                <td class="key-cell"><code>seasonScore</code></td>
                <td>Object</td>
                <td>
                  계절 적합도 —
                  <code>spring</code
                  >/<code>summer</code>/<code>autumn</code>/<code>winter</code>
                  (각 0~100)
                </td>
              </tr>
              <tr>
                <td class="key-cell"><code>festivals</code></td>
                <td>Object[]</td>
                <td>축제·행사 목록 — 명칭, 시기(월·계절 단위), 간단 설명</td>
              </tr>
              <tr>
                <td class="key-cell"><code>embedding</code></td>
                <td>Float[]</td>
                <td>RAG 검색용 벡터 임베딩 (desc·reasons·themes 기반)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>tags</code></td>
                <td>Object[]</td>
                <td>태그 레이블 및 스타일 타입 목록</td>
              </tr>
              <tr>
                <td class="key-cell"><code>travel</code></td>
                <td>String</td>
                <td>주요 출발지 기준 이동 방법 및 소요 시간</td>
              </tr>
              <tr>
                <td class="key-cell"><code>tip</code></td>
                <td>String</td>
                <td>시즌·코스 등 여행 팁 (100자 이내)</td>
              </tr>
              <tr>
                <td class="key-cell"><code>googleQuery</code></td>
                <td>String</td>
                <td>Google Places 검색 쿼리 문자열</td>
              </tr>
              <tr>
                <td class="key-cell"><code>links</code></td>
                <td>Object</td>
                <td>플랫폼별 외부 링크 URL 맵</td>
              </tr>
              <tr>
                <td class="key-cell"><code>naverBlogs</code></td>
                <td>Object[] (KR)</td>
                <td>네이버 블로그 추천 검색 키워드 목록</td>
              </tr>
              <tr>
                <td class="key-cell"><code>yahooLinks</code></td>
                <td>Object[] (JP)</td>
                <td>Yahoo Japan 계열 딥링크 목록</td>
              </tr>
            </tbody>
          </table>

          <h2 class="s-h2" id="s6-2">6.2 DB 규모 목표</h2>
          <table class="info-tbl">
            <thead>
              <tr>
                <th style="width:25%">구분</th>
                <th style="width:22%">목표 수량</th>
                <th>포함 지역 / 기준</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="key-cell">국내 소도시</td>
                <td>50개 이상</td>
                <td>강원·충청·전북·전남·경남·경북·제주 포함</td>
              </tr>
              <tr>
                <td class="key-cell">일본 소도시</td>
                <td>40개 이상</td>
                <td>호쿠리쿠·긴키·주부·주고쿠·시코쿠·규슈 포함</td>
              </tr>
              <tr>
                <td class="key-cell">테마 커버리지</td>
                <td>테마당 5곳 이상</td>
                <td>
                  6개 테마 각각 최소 5개 소도시 보유 (여정 구성 가능 수량)
                </td>
              </tr>
              <tr>
                <td class="key-cell">축제·행사</td>
                <td>도시당 1개 이상</td>
                <td>월·계절 단위 표기 (대표 축제 우선 수집)</td>
              </tr>
            </tbody>
          </table>
          <div class="note-box">
            <strong>핵심 트릭:</strong> 한·일이 동일한 6개 테마 체계와
            RAG·에이전트 파이프라인을 공유하므로, 한국 트랙을 먼저 완성·검증한
            뒤 일본은 <strong>벡터DB 데이터만 교체</strong>하여 적용한다. 개발
            효율을 높이고 리스크를 분산한다.
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
            <strong>Naver Local Search REST API CORS:</strong> 브라우저에서 직접
            호출 시 CORS 오류가 발생한다. 현재 블로그 검색은 딥링크로 대체하며,
            향후 백엔드 프록시를 통해 실시간 데이터를 제공한다.
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
              소도시 DB는 정적 JSON + 벡터 임베딩 형태로 관리하며, 향후 동적
              DB로 전환한다.
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
              Open-Meteo API는 무료 플랜을 사용하며 상업적 서비스 전환 시
              라이선스를 재확인한다.
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
                <td>로컬루트 기획팀</td>
                <td>
                  최초 작성 — 기능 요구사항, API 연동 명세, 비기능 요구사항 초안
                </td>
              </tr>
              <tr>
                <td>v1.1</td>
                <td id="logDate2"></td>
                <td>로컬루트 기획팀</td>
                <td>
                  6개 테마 여정 추천 도입, 계절·축제 연동 추가, RAG·멀티스텝
                  에이전트 기반으로 추천 엔진 정의 (규칙기반→RAG 전환), 소도시
                  DB에 테마·계절·축제·임베딩 필드 추가
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>

    <script>
      // Date
      const d = new Date();
      const ds = `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
      document.getElementById("todayDate").textContent = ds;
      document.getElementById("logDate").textContent = ds;
      const logDate2 = document.getElementById("logDate2");
      if (logDate2) logDate2.textContent = ds;

      // Active TOC
      const links = document.querySelectorAll(".toc-link");
      const sections = [...document.querySelectorAll("[id]")].filter(
        (el) => el.id !== "cover",
      );

      function updateTOC() {
        const scrollY = window.scrollY + 80;
        let current = "cover";
        sections.forEach((s) => {
          if (s.offsetTop <= scrollY) current = s.id;
        });
        links.forEach((l) => {
          const href = l.getAttribute("href").slice(1);
          l.classList.toggle("active", href === current);
        });
      }
      window.addEventListener("scroll", updateTOC, { passive: true });
      updateTOC();
    </script>
  </body>
</html>
```


