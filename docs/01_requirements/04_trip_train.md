```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RailRoute-RAG - 서비스 기획서 및 제안서</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <!-- Glow Background elements -->
    <div class="ambient-glow-1"></div>
    <div class="ambient-glow-2"></div>

    <div class="app-container">
      <!-- Sidebar Navigation -->
      <aside class="sidebar">
        <div>
          <div class="brand">
            <div class="brand-icon">
              <svg viewBox="0 0 24 24">
                <path
                  d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"
                />
              </svg>
            </div>
            <div class="brand-text">
              <h1>RailRoute-RAG</h1>
              <span>Planning Proposal</span>
            </div>
          </div>

          <nav class="nav-menu">
            <a href="#overview" class="active">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
              1. 기획 배경 및 목적
            </a>
            <a href="#personas">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              2. 타겟 페르소나
            </a>
            <a href="#key-features">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
              </svg>
              3. 서비스 핵심 기능
            </a>
            <a href="#user-journey">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              4. 사용자 여정 (저니맵)
            </a>
            <a href="#pass-optimizer">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
              </svg>
              5. 패스 절약 계산기
            </a>
            <a href="#biz-synergy">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
              6. 비즈니스 모델 & 비전
            </a>
          </nav>
        </div>

        <div class="sidebar-footer">
          <p>RailRoute-RAG v1.2</p>
          <p>© 2026 RailRoute-RAG Lab.</p>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="content-area">
        <!-- Document Header -->
        <header class="doc-header" id="doc-top">
          <div class="meta-tag">
            <div class="pulse-dot"></div>
            소도시 상생 및 철도 여행 플랫폼 기획안
          </div>
          <h2 class="doc-title">
            RailRoute-RAG<br />철도망 기반 소도시 추천 서비스 기획서
          </h2>
          <p class="doc-subtitle">
            본 기획안은 수도권/대도시 집중으로 인한 지방 소도시 소멸 위기를
            해결하고, 철도 패스 및 관광 열차 인프라를 활용하여
            인바운드/아웃바운드 관광객을 숨겨진 소도시로 분산 정밀 매칭하는
            차세대 여행 에이전트 서비스 기획서입니다.
          </p>

          <!-- Dynamic Statistics Board -->
          <div class="dashboard-grid">
            <div class="dash-card">
              <div class="dash-card-icon">
                <svg
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div class="dash-card-value">89%</div>
              <div class="dash-card-label">
                한일 주요 대도시(서울/도쿄) 관광객 집중도 해소 필요
              </div>
            </div>
            <div class="dash-card">
              <div class="dash-card-icon">
                <svg
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div class="dash-card-value">약 35%</div>
              <div class="dash-card-label">
                패스 최적화 엔진 활용 시 개별 승차권 대비 교통비 평균 절감율
              </div>
            </div>
            <div class="dash-card">
              <div class="dash-card-icon">
                <svg
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div class="dash-card-value">O(1) Direct Map</div>
              <div class="dash-card-label">
                사용자 맞춤 의도 분석 기반 초정밀 로컬 패키지 매칭 속도
              </div>
            </div>
          </div>
        </header>

        <!-- Section 1: Background & Objectives -->
        <section class="doc-section" id="overview">
          <div class="section-header">
            <div class="section-num">01</div>
            <h3 class="section-title">서비스 기획 배경 및 목적</h3>
          </div>

          <p class="intro-text">
            현재 관광 산업은 유명 대도시 중심의 '오버투어리즘'과 인구 급감에
            처한 '지방 소도시의 관광 소멸'이라는 양극화 문제에 직면해 있습니다.
            본 서비스는 철도 네트워크라는 훌륭한 물리적 연계망을 통해 대도시
            관광객을 매력적인 로컬 소도시로 흘려보내는 선순환적 관광 상생
            생태계를 지향합니다.
          </p>

          <div class="problem-solution-grid">
            <!-- Problem Card -->
            <div class="ps-card problem">
              <span class="ps-tag">Problem (기존 시장의 한계)</span>
              <h4 class="ps-title">대도시 밀집 현상과 복잡한 대중교통 장벽</h4>
              <p class="ps-desc">
                한국의 수도권 및 일본의 도쿄/교토 중심 여행 편중이 심화되고
                있습니다. 여행자가 소도시로 떠나고 싶어도, 복잡한 철도 노선도와
                상이한 교통 패스 조합(JR패스, 지역 패스, 내일로), 그리고
                한정적인 관광열차 예약 정보 때문에 동선 설계 단계에서 포기하게
                됩니다.
              </p>
            </div>

            <!-- Solution Card -->
            <div class="ps-card solution">
              <span class="ps-tag">Solution (우리의 비전)</span>
              <h4 class="ps-title">AI 철도 매핑 기반 소도시 추천 에이전트</h4>
              <p class="ps-desc">
                철도 물리적 토폴로지망과 테마 상품 지식을 결합하여, 사용자가
                일상적인 자연어로 원하는 감성을 입력하면 목적지에 인접한 거점역
                경로와 가장 효율적인 '패스권 조합', 그리고 연계된 로컬 관광
                패키지를 최적 정렬하여 즉시 예약 가능한 UI로 제공합니다.
              </p>
            </div>
          </div>
        </section>

        <!-- Section 2: Target Personas -->
        <section class="doc-section" id="personas">
          <div class="section-header">
            <div class="section-num">02</div>
            <h3 class="section-title">핵심 타겟 페르소나 및 시나리오</h3>
          </div>

          <p class="intro-text">
            다양한 라이프스타일을 대변하는 세 가지 핵심 페르소나를 도출하고,
            이들이 철도 여행에서 겪는 페인 포인트와 엔진을 통한 해결 시나리오를
            구성했습니다.
          </p>

          <!-- Interactive Persona Tab Widget -->
          <div class="persona-container">
            <div class="persona-tabs">
              <button
                class="persona-tab-btn active"
                onclick="switchPersona(event, 'persona-silver')"
              >
                👵 실버/가족 웰니스 여행
              </button>
              <button
                class="persona-tab-btn"
                onclick="switchPersona(event, 'persona-backpack')"
              >
                🎒 2030 갓성비 배낭여행
              </button>
              <button
                class="persona-tab-btn"
                onclick="switchPersona(event, 'persona-mania')"
              >
                👑 럭셔리 철도 크루즈
              </button>
            </div>

            <!-- Persona 1 Content -->
            <div
              id="persona-silver"
              class="persona-content-wrapper active"
              style="--avatar-gradient-start: #fbc2eb; --avatar-gradient-end: #a6c1ee; --avatar-shadow: rgba(166, 193, 238, 0.4);"
            >
              <div class="persona-profile-card">
                <div class="persona-avatar">👵</div>
                <h4 class="persona-name">김정숙 씨 (62세)</h4>
                <span class="persona-tagline"
                  >"부모님/가족 동반 편안한 온천 힐링"</span
                >
                <p class="persona-bio">
                  부모님을 모시고 번잡한 도쿄 시내가 아닌 고즈넉한 온천마을로
                  여행을 가고 싶어 합니다. 렌터카 운전은 부담스럽고, 환승 횟수가
                  적고 안락한 전용 열차가 포함된 패키지를 선호합니다.
                </p>
              </div>

              <div class="persona-details-grid">
                <div class="detail-group">
                  <div class="detail-group-title">
                    <svg
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                    Pain Point (불편 사항)
                  </div>
                  <div class="detail-items-list">
                    <div class="detail-bullet-item">
                      소도시 료칸으로 가는 신칸센 및 로컬 열차 환승 연결편
                      설계가 너무 어려움
                    </div>
                    <div class="detail-bullet-item">
                      부모님이 오래 걸으실 수 없어 도보 이동 거리가 적은 연계
                      교통편 필수
                    </div>
                  </div>
                </div>

                <div class="detail-group">
                  <div class="detail-group-title">
                    <svg
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    RailRoute 매칭 시나리오
                  </div>
                  <div class="detail-items-list">
                    <div class="detail-bullet-item">
                      <strong>추천 노선</strong>: 하카타역 출도착 → 특급
                      유후인의 모리(관광열차) → 유후인 소도시 연결
                    </div>
                    <div class="detail-bullet-item">
                      <strong>제공 솔루션</strong>: 환승 0회 직통 편수 우선 배치
                      + 온천 료칸 픽업 차량이 결합된 기성 로컬 투어 패키지 링크
                      다이렉트 추천
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Persona 2 Content -->
            <div
              id="persona-backpack"
              class="persona-content-wrapper"
              style="--avatar-gradient-start: #84fab0; --avatar-gradient-end: #8fd3f4; --avatar-shadow: rgba(143, 211, 244, 0.4);"
            >
              <div class="persona-profile-card">
                <div class="persona-avatar">🎒</div>
                <h4 class="persona-name">이민우 군 (24세)</h4>
                <span class="persona-tagline"
                  >"가성비와 인스타 감성을 갖춘 전국 철도 일주"</span
                >
                <p class="persona-bio">
                  방학 기간 내일로 패스나 지역 할인 레일패스를 활용하여 사람이
                  적고 이색적인 소도시를 탐방해 SNS에 업로드하고 싶어 하는
                  대학생 배낭여행족입니다.
                </p>
              </div>

              <div class="persona-details-grid">
                <div class="detail-group">
                  <div class="detail-group-title">
                    <svg
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                    Pain Point (불편 사항)
                  </div>
                  <div class="detail-items-list">
                    <div class="detail-bullet-item">
                      구간별 개별 승차권 구매 시 전체 교통비 예산 초과
                    </div>
                    <div class="detail-bullet-item">
                      알려진 관광 대도시 외에 트렌디하면서도 가성비 좋은 시골
                      소도시 정보 부족
                    </div>
                  </div>
                </div>

                <div class="detail-group">
                  <div class="detail-group-title">
                    <svg
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    RailRoute 매칭 시나리오
                  </div>
                  <div class="detail-items-list">
                    <div class="detail-bullet-item">
                      <strong>추천 노선</strong>: JR 호쿠리쿠 패스 활용 →
                      가나자와 → 도야마 → 후쿠이 소도시 순회 루트
                    </div>
                    <div class="detail-bullet-item">
                      <strong>제공 솔루션</strong>: 블로그 감성 텍스트 매칭을
                      통한 SNS 핫플레이스(감성 카페, 바다 전망 기차역) 연계
                      소도시 및 '가장 저렴한 패스권 최적 조합' 계산 제시
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Persona 3 Content -->
            <div
              id="persona-mania"
              class="persona-content-wrapper"
              style="--avatar-gradient-start: #a18cd1; --avatar-gradient-end: #fbc2eb; --avatar-shadow: rgba(161, 140, 209, 0.4);"
            >
              <div class="persona-profile-card">
                <div class="persona-avatar">👑</div>
                <h4 class="persona-name">박영호 부부 (55세)</h4>
                <span class="persona-tagline"
                  >"특별한 고부가 가치 레일 크루즈 체험"</span
                >
                <p class="persona-bio">
                  결혼 30주년을 기념하여 고가의 레일크루즈 해랑 혹은 일본의
                  프리미엄 테마 열차 투어를 경험해 보고자 하는 럭셔리 지향
                  여유층 고객입니다.
                </p>
              </div>

              <div class="persona-details-grid">
                <div class="detail-group">
                  <div class="detail-group-title">
                    <svg
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                    Pain Point (불편 사항)
                  </div>
                  <div class="detail-items-list">
                    <div class="detail-bullet-item">
                      인터넷상의 단편적인 정보로는 최고급 열차 상품의 일정표
                      구성 및 실제 예약 링크 매칭이 번거로움
                    </div>
                    <div class="detail-bullet-item">
                      공급량이 적은 럭셔리 상품 특성상 실시간 예약 가능 잔여
                      좌석 여부를 확인하기 어려움
                    </div>
                  </div>
                </div>

                <div class="detail-group">
                  <div class="detail-group-title">
                    <svg
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    RailRoute 매칭 시나리오
                  </div>
                  <div class="detail-items-list">
                    <div class="detail-bullet-item">
                      <strong>추천 노선</strong>: 서해금빛열차 온돌마루실 패키지
                      또는 JR 동일본 Shiki-Shima 럭셔리 투어
                    </div>
                    <div class="detail-bullet-item">
                      <strong>제공 솔루션</strong>: 실시간 예약 잔여 정보 크로스
                      매칭 에이전트 검증 후 즉시 결제 가능한 고부가 VIP 투어
                      상품 큐레이션 노출
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section 3: Key Features -->
        <section class="doc-section" id="key-features">
          <div class="section-header">
            <div class="section-num">03</div>
            <h3 class="section-title">서비스 핵심 기능 기획</h3>
          </div>

          <p class="intro-text">
            철도 데이터를 매개로 한 맞춤 추천을 실현하기 위한 핵심 서비스 기능
            4가지를 소개합니다.
          </p>

          <div class="features-tabs-layout">
            <!-- Features List Menu -->
            <div class="features-list-menu">
              <div
                class="feature-menu-item active"
                onclick="switchFeatureShowcase(0)"
              >
                <div class="feature-icon-badge">🛤️</div>
                <div>
                  <div class="feature-menu-title">AI 맞춤 기차 노선 빌더</div>
                  <div class="feature-menu-desc">
                    지리 정보와 기차역 최단 환승 결합
                  </div>
                </div>
              </div>

              <div class="feature-menu-item" onclick="switchFeatureShowcase(1)">
                <div class="feature-icon-badge">🎟️</div>
                <div>
                  <div class="feature-menu-title">로컬 테마 패키지 매칭</div>
                  <div class="feature-menu-desc">
                    정형 노선과 비정형 관광 상품의 결합
                  </div>
                </div>
              </div>

              <div class="feature-menu-item" onclick="switchFeatureShowcase(2)">
                <div class="feature-icon-badge">⚖️</div>
                <div>
                  <div class="feature-menu-title">패스 조합 최적화 엔진</div>
                  <div class="feature-menu-desc">
                    이동 구간 기준 가장 저렴한 패스 판별
                  </div>
                </div>
              </div>

              <div class="feature-menu-item" onclick="switchFeatureShowcase(3)">
                <div class="feature-icon-badge">📉</div>
                <div>
                  <div class="feature-menu-title">소도시 혼잡도 피드백</div>
                  <div class="feature-menu-desc">
                    실시간 인구 데이터를 통한 분산 유도
                  </div>
                </div>
              </div>
            </div>

            <!-- Feature Detail Showcase -->
            <div class="feature-detail-showcase">
              <!-- Showcase Item 1 -->
              <div class="feature-showcase-content active" id="f-showcase-0">
                <h4 class="showcase-title">AI 맞춤형 철도 노선 자동 빌더</h4>
                <span class="showcase-badge">Core Engine</span>
                <p class="showcase-desc">
                  단순히 역 간의 거리를 보여주는 것을 넘어 사용자가 지정한 숙소,
                  관광지 목록을 기차역 노선 네트워크에 실시간으로 매핑합니다.
                  도보 및 현지 시내버스 연계까지 고려하여, 환승 스트레스를
                  최소화하는 개인 맞춤형 타임라인 동선을 구성해 줍니다.
                </p>
                <div class="showcase-bullets">
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>출발-도착 지능형 보정</strong>:
                      고속열차(신칸센/KTX)와 로컬 지선 열차의 환승 소요 시간
                      최적화 계산
                    </div>
                  </div>
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>사용자 이동 속도 설정</strong>: 보행
                      속도(실버/어린이 동반 등)에 맞춘 갈아타기 유휴 시간 조절
                      기능
                    </div>
                  </div>
                </div>
              </div>

              <!-- Showcase Item 2 -->
              <div class="feature-showcase-content" id="f-showcase-1">
                <h4 class="showcase-title">
                  관광열차 연계 로컬 여행 패키지 매칭
                </h4>
                <span class="showcase-badge">Commerce Sync</span>
                <p class="showcase-desc">
                  서해금빛열차, 남도해양열차, 일본의 다채로운 디자인/테마
                  열차(D&S Train)처럼 좌석 확보가 매우 어려운 특수 관광열차
                  정보를 여행 패키지 상품과 직결합니다. 단순한 이동 수단 예약이
                  아니라 기차 안에서의 체험 프로그램과 연계 숙박까지 묶어 원클릭
                  결제로 안내합니다.
                </p>
                <div class="showcase-bullets">
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>기성 패키지 매핑</strong>: 코레일관광개발 및 현지
                      에이전시 상품 데이터 베이스의 유기적인 연동
                    </div>
                  </div>
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>테마 태깅</strong>: 맛집 기차여행, 전통 가옥 료칸
                      기차여행 등 감성적 카테고리 태깅 검색 지원
                    </div>
                  </div>
                </div>
              </div>

              <!-- Showcase Item 3 -->
              <div class="feature-showcase-content" id="f-showcase-2">
                <h4 class="showcase-title">
                  초정밀 교통 패스 가격 비교 및 추천
                </h4>
                <span class="showcase-badge">Cost Saving</span>
                <p class="showcase-desc">
                  한일 양국에는 수십 종류의 외국인 전용 혹은 기간 한정 철도
                  자유이용 패스가 존재합니다. 서비스 엔진이 여행자의 최종 기획
                  동선 전체를 역산하여, 개별 티켓을 사는 가격과 패스(JR 전국
                  패스, 규슈 패스, 돗토리 마쓰에 패스 등)를 사용할 때의 예상
                  경비를 1초 만에 비교해 가장 합리적인 옵션을 도출합니다.
                </p>
                <div class="showcase-bullets">
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>최적 조합 시뮬레이션</strong>: 여러 지역 패스(예:
                      JR 간사이 패스 + JR 히로시마 패스)의 병합 구매 메리트 검증
                    </div>
                  </div>
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>실시간 렌더링</strong>: 패스 사용 시 누적되는
                      세이빙 비용을 시각적 그래프로 표출
                    </div>
                  </div>
                </div>
              </div>

              <!-- Showcase Item 4 -->
              <div class="feature-showcase-content" id="f-showcase-3">
                <h4 class="showcase-title">
                  소도시 혼잡도 모니터링 및 분산 추천
                </h4>
                <span class="showcase-badge">B2G & Sustainability</span>
                <p class="showcase-desc">
                  유명 대도시에 몰려있는 관광객을 분산하기 위해 소도시들의
                  실시간 혼잡도를 분석하고 피드백을 제공합니다. 혼잡도가 낮고
                  한적한 매력의 2선, 3선 소도시를 우선 노출하도록 리랭킹
                  스코어를 가중 보정하여, 여행자에게는 한적한 여유를, 소도시
                  지역 상권에는 새로운 경제 활력을 선사합니다.
                </p>
                <div class="showcase-bullets">
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>인구 혼잡도 가치 보정</strong>: 공공 유동 인구
                      통계 API를 활용한 소도시별 혼잡 등급 산출
                    </div>
                  </div>
                  <div class="showcase-bullet">
                    <div class="showcase-bullet-indicator"></div>
                    <div class="showcase-bullet-text">
                      <strong>상생 리워드 연계</strong>: 에이전트가 추천한
                      저혼잡 소도시를 방문 및 결제 시 현지 철도역 모바일 특산품
                      쿠폰 발행 연계
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section 4: User Journey Map -->
        <section class="doc-section" id="user-journey">
          <div class="section-header">
            <div class="section-num">04</div>
            <h3 class="section-title">사용자 여정 및 서비스 흐름</h3>
          </div>

          <p class="intro-text">
            여행 계획 수립부터 패스 비교, 최종 소도시 패키지 결제 단계까지
            자연스러운 대화형 인터페이스를 따르는 유저 저니(User Journey)
            경로입니다.
          </p>

          <!-- Storyboard Timeline Nodes -->
          <div class="journey-timeline-wrapper">
            <div class="journey-nodes-row">
              <div
                class="journey-step-node active"
                onclick="setChatScenario(0)"
              >
                <div class="journey-step-dot">💬</div>
                <div class="journey-step-title">1. 자연어 질문</div>
                <div class="journey-step-desc">
                  여행자의 구체적인 감성, 목적 정보 발화
                </div>
              </div>

              <div class="journey-step-node" onclick="setChatScenario(1)">
                <div class="journey-step-dot">📊</div>
                <div class="journey-step-title">2. 의도 & 비용 분석</div>
                <div class="journey-step-desc">
                  최적 소도시 선별 및 패스 할인 비교 분석
                </div>
              </div>

              <div class="journey-step-node" onclick="setChatScenario(2)">
                <div class="journey-step-dot">🚞</div>
                <div class="journey-step-title">3. 테마 매칭 및 검증</div>
                <div class="journey-step-desc">
                  관광 열차 운행 및 실제 좌석 잔여 확인
                </div>
              </div>

              <div class="journey-step-node" onclick="setChatScenario(3)">
                <div class="journey-step-dot">💳</div>
                <div class="journey-step-title">4. 예약/원클릭 안내</div>
                <div class="journey-step-desc">
                  여행 제안 수용 및 에이전시 링크 결제
                </div>
              </div>
            </div>

            <!-- Chat window mockup simulating conversation -->
            <div class="chat-simulator-card">
              <div class="chat-header">
                <span class="chat-badge"
                  ><span
                    class="pulse-dot"
                    style="width:6px; height:6px; background-color:var(--accent-blue);"
                  ></span
                  >RailRoute-RAG AI Agent</span
                >
                <div style="font-size:0.75rem; color:var(--text-muted);">
                  Interactive Live Mockup
                </div>
              </div>

              <div class="chat-body" id="chat-scroller">
                <!-- Dynamically populated messages based on journey steps -->
              </div>
            </div>
          </div>
        </section>

        <!-- Section 5: Pass Optimizer Calculator -->
        <section class="doc-section" id="pass-optimizer">
          <div class="section-header">
            <div class="section-num">05</div>
            <h3 class="section-title">인터랙티브 패스 절약 계산기 기획 검증</h3>
          </div>

          <p class="intro-text">
            본 플랫폼 기획의 핵심 셀링 포인트인 **교통비 패스 최적화 효과**를
            시각적으로 보여주는 데모 시뮬레이터입니다. 사용자가 다중 소도시 이동
            경로를 정하면 철도 연동 엔진이 최적의 레일 패스를 선정하여 절감액을
            실시간으로 추정해 줍니다.
          </p>

          <!-- Interactive Calculator Widget -->
          <div class="calculator-card">
            <div class="calc-controls">
              <h3>📍 가상의 여행 경로 선택</h3>
              <p
                style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:1rem;"
              >
                원하시는 경로 모델을 클릭해보세요.
              </p>

              <div class="calc-routes-list">
                <div
                  class="calc-route-item selected"
                  onclick="selectCalcRoute(0)"
                >
                  <div>
                    <div class="calc-route-name">규슈 명품 온천 투어</div>
                    <div class="calc-route-details">
                      하카타 → 유후인 → 구마모토 → 아소
                    </div>
                  </div>
                  <div style="font-weight:bold; color:var(--accent-blue);">
                    KRW 38만~
                  </div>
                </div>

                <div class="calc-route-item" onclick="selectCalcRoute(1)">
                  <div>
                    <div class="calc-route-name">
                      일본 호쿠리쿠 미술·미식 여행
                    </div>
                    <div class="calc-route-details">
                      도야마 → 가나자와 → 후쿠이 → 기노사키
                    </div>
                  </div>
                  <div style="font-weight:bold; color:var(--accent-blue);">
                    KRW 42만~
                  </div>
                </div>

                <div class="calc-route-item" onclick="selectCalcRoute(2)">
                  <div>
                    <div class="calc-route-name">
                      동해&남해 명품 철도 교차 크루즈
                    </div>
                    <div class="calc-route-details">
                      서울 → 삼척(동해산타) → 강릉 → 부산 → 남해
                    </div>
                  </div>
                  <div style="font-weight:bold; color:var(--accent-blue);">
                    KRW 28만~
                  </div>
                </div>
              </div>

              <button class="calc-action-btn" onclick="runCalculation()">
                최적 패스 혜택 분석하기
              </button>
            </div>

            <div class="calc-results">
              <div>
                <div class="calc-result-header">
                  📊 최적 패스 매칭 시뮬레이션 결과
                </div>

                <div class="calc-metric-row">
                  <span class="calc-metric-label"
                    >개별 구간 열차 예매 시 총합</span
                  >
                  <span class="calc-metric-val" id="lbl-raw-cost"
                    >KRW 384,000</span
                  >
                </div>

                <div class="calc-metric-row">
                  <span class="calc-metric-label">추천 최적 레일패스 명칭</span>
                  <span
                    class="calc-metric-val"
                    id="lbl-pass-name"
                    style="color:var(--accent-purple);"
                    >JR 규슈 레일패스 (5일권)</span
                  >
                </div>

                <div class="calc-metric-row">
                  <span class="calc-metric-label">추천 패스권 구매비</span>
                  <span class="calc-metric-val" id="lbl-pass-cost"
                    >KRW 240,000</span
                  >
                </div>
              </div>

              <div class="calc-saving-total">
                <span class="calc-saving-lbl">최종 절감 비용 예상</span>
                <span class="calc-saving-val" id="lbl-saving-val"
                  >KRW 144,000</span
                >
              </div>
            </div>
          </div>
        </section>

        <!-- Section 6: Business Model & Vision -->
        <section class="doc-section" id="business-model">
          <div class="section-header">
            <div class="section-num">06</div>
            <h3 class="section-title">비즈니스 모델 및 로컬 상생 시너지</h3>
          </div>

          <p class="intro-text">
            단순 정보 제공 앱을 넘어 철도 회사, 지자체, 여행 상품 유통 대행사를
            잇는 통합 비즈니스 허브로 성장하기 위한 수익 모델 기획안입니다.
          </p>

          <div class="biz-value-grid">
            <div class="biz-card">
              <div class="biz-icon">
                <svg
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <div class="biz-title">에이전시 중개 수수료</div>
              <div class="biz-desc">
                KORAIL 관광상품, JR 규슈 공식 여행 예약 에이전시와의 API 연결을
                통해 최종 예약 및 결제가 발생하면 5~8%의 판매 제휴 중개
                수수료(Affiliate Fee)를 수취합니다.
              </div>
            </div>

            <div class="biz-card">
              <div class="biz-icon">
                <svg
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L16 4m0 13V4m0 0L9 7"
                  />
                </svg>
              </div>
              <div class="biz-title">B2G 지자체 협업 수익</div>
              <div class="biz-desc">
                소멸 위기 지방자치단체와 협력하여 특정 로컬 소도시 관광객 집중
                유치 캠페인을 대행하고, 지자체 보조금 및 홍보 펀딩 수익을
                정산받습니다.
              </div>
            </div>

            <div class="biz-card">
              <div class="biz-icon">
                <svg
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
                  />
                </svg>
              </div>
              <div class="biz-title">로컬 바우처 연계 패키징</div>
              <div class="biz-desc">
                소도시 지역의 맛집, 온천, 문화 체험 공방과 제휴하여,
                패밀리/청년층 타겟의 특별 로컬 상품을 독점 개발해 유통
                마진(Mark-up)을 창출합니다.
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- JavaScript Interaction Logic -->
  </body>
</html>
```


