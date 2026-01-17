# app.py
import streamlit as st

st.set_page_config(
    page_title="Baldur's Gate 3 — In Numbers",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- THEME (premium dark + bronze) ----------
CSS = """
<style>
:root{
  --bg: #0b0d10;
  --panel: rgba(255,255,255,0.04);
  --panel2: rgba(255,255,255,0.06);
  --line: rgba(233, 197, 121, 0.25);
  --gold: #E9C579;
  --muted: rgba(255,255,255,0.70);
  --text: rgba(255,255,255,0.92);
}

html, body, [class*="css"]  { background: var(--bg) !important; }
.block-container { padding-top: 2.0rem; padding-bottom: 3.0rem; max-width: 1200px; }

h1, h2, h3, h4 { color: var(--text) !important; letter-spacing: 0.2px; }
p, li, span, div { color: var(--muted); }

.hr-gold { height:1px; background: var(--line); border:0; margin: 18px 0 20px 0; }

.badge {
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  border: 1px solid var(--line); color: var(--gold); background: rgba(233,197,121,0.08);
  font-size: 12px; letter-spacing: 0.3px; margin-right: 8px;
}

.panel {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, var(--panel), rgba(255,255,255,0.02));
  border-radius: 18px;
  padding: 18px 18px 16px 18px;
}

.panel-title { font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 1.2px; }
.panel-big { font-size: 44px; color: var(--text); font-weight: 750; margin-top: 6px; line-height: 1.0; }
.panel-sub { font-size: 13px; color: var(--muted); margin-top: 10px; }

.small-note { font-size: 12px; color: rgba(255,255,255,0.55); }

div[data-testid="stMetric"]{
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px 16px;
  background: var(--panel);
}
div[data-testid="stMetricLabel"] p { color: rgba(255,255,255,0.70) !important; }
div[data-testid="stMetricValue"] { color: rgba(255,255,255,0.92) !important; }
div[data-testid="stMetricDelta"] { color: var(--gold) !important; }

.stButton>button{
  border-radius: 999px; border: 1px solid var(--line);
  background: rgba(233,197,121,0.10);
  color: var(--text);
  padding: 10px 16px;
}
.stButton>button:hover{
  background: rgba(233,197,121,0.18);
  border-color: rgba(233,197,121,0.55);
}

section[data-testid="stSidebar"] { background: rgba(255,255,255,0.02); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- HEADER / HERO ----------
st.markdown(
    """
<div class="panel">
  <div class="panel-title">Baldur's Gate 3</div>
  <div class="panel-big">IN NUMBERS</div>
  <div class="panel-sub">
    숫자로 들여다보는 페이룬의 혼돈. <span class="badge">CHOICE</span><span class="badge">CHAOS</span><span class="badge">CONSEQUENCE</span>
    <br/>*이미지는 최소, 분위기는 최대. (그리고 가끔은 개발자도 당황합니다)
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<hr class="hr-gold"/>', unsafe_allow_html=True)

# ---------- QUICK STATS (placeholders) ----------
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("모드 다운로드", "265M", "커뮤니티의 집단지성(?)")
with c2:
    st.metric("업로드된 모드", "8.5K", "장인정신이 폭주함")
with c3:
    st.metric("명예 모드 클리어", "141,660", "고통을 사랑한 자들")
with c4:
    st.metric("전설급 선택률", "93%+", "커스텀 캐릭터가 대세")

st.markdown('<hr class="hr-gold"/>', unsafe_allow_html=True)

# ---------- MAIN CONTENT TABS ----------
tabs = st.tabs(["OVERVIEW", "HONOUR", "ROMANCE", "ODD STATS", "INTERACTIVE"])

with tabs[0]:
    left, right = st.columns([1.2, 0.8])
    with left:
        st.subheader("한 번에 이해하는 BG3")
        st.write(
            "발더스 게이트 3는 **선택이 결과를 만들고**, 그 결과가 다시 당신의 선택을 비틀어버리는 게임이야. "
            "우리는 그 과정을 ‘데이터’로 보면 더 웃기고(가끔은 무섭고), 더 사랑스러워진다는 걸 증명하려고 해."
        )
        with st.expander("이 페이지의 톤(중요)"):
            st.write(
                "- 진지한 듯하지만 한 줄은 꼭 웃기게\n"
                "- 스포일러는 가능하면 숨기기\n"
                "- 숫자는 크게, 설명은 짧게\n"
                "- 이미지가 없으면 ‘여백’이 디자인이다"
            )
    with right:
        st.markdown(
            """
<div class="panel">
  <div class="panel-title">Editor’s Note</div>
  <div class="panel-sub">
    이 페이지는 ‘공식 인포그래픽 감성’을 참고해,
    Streamlit 기능을 <b>티 안 나게</b> 섞는 것이 목표야.
    <br/><br/>
    다음 단계에서: 차트, 필터, 데이터테이블, 다운로드까지 얹을 수 있어.
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

with tabs[1]:
    st.subheader("HONOUR MODE — 존엄한 삭제의 미학")
    a, b, c = st.columns([1, 1, 1])
    with a:
        st.markdown(
            """
<div class="panel">
  <div class="panel-title">클리어한 사람</div>
  <div class="panel-big">141,660</div>
  <div class="panel-sub">“난 여기서 멈추지 않아.”라고 말하고 진짜로 멈추지 않은 분들.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            """
<div class="panel">
  <div class="panel-title">패배한 플레이</div>
  <div class="panel-big">1,223,305</div>
  <div class="panel-sub">죽음은 한 번. 리셋은… 글쎄요.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            """
<div class="panel">
  <div class="panel-title">선택의 분기</div>
  <div class="panel-big">76% / 24%</div>
  <div class="panel-sub">“명예롭게 삭제” vs “커스텀 모드로 계속” — 인간은 다들 이유가 있다.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.caption("※ 지금은 레이아웃 테스트용 더미 숫자/문구야. 나중에 실제 수치/출처 넣자.")

with tabs[2]:
    st.subheader("ROMANCE — 페이룬의 연애는 통계가 된다")
    st.write("여긴 특히 **스포일러**가 될 수 있으니, 기본은 접어두는 구조가 좋아.")
    with st.expander("로맨스 통계(눌러서 보기)"):
        r1, r2 = st.columns([1, 1])
        with r1:
            st.markdown(
                """
<div class="panel">
  <div class="panel-title">동료 키스</div>
  <div class="panel-big">75M+</div>
  <div class="panel-sub">‘전투’보다 ‘눈빛’이 더 치명적일 때가 있다.</div>
</div>
""",
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown(
                """
<div class="panel">
  <div class="panel-title">가장 인기</div>
  <div class="panel-big">Shadowheart</div>
  <div class="panel-sub">이유요? 다들 마음속에 어두운 성당 하나쯤은…</div>
</div>
""",
                unsafe_allow_html=True,
            )

with tabs[3]:
    st.subheader("ODD STATS — 개발자도 ‘이게 왜 이렇게 많지?’ 하는 구간")
    grid1, grid2 = st.columns([1, 1])
    with grid1:
        st.markdown(
            """
<div class="panel">
  <div class="panel-title">치즈 휠이 된 플레이어</div>
  <div class="panel-big">1.9M</div>
  <div class="panel-sub">페이룬에서 치즈는 식품이 아니라 ‘상태 이상’일 수 있다.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with grid2:
        st.markdown(
            """
<div class="panel">
  <div class="panel-title">“이건… 괜찮은가?”</div>
  <div class="panel-big">Are you OK?</div>
  <div class="panel-sub">숫자가 커질수록 개발자의 멘트가 솔직해진다.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        """
<div class="panel">
  <div class="panel-title">미니 테이블 (나중에 데이터프레임으로 교체)</div>
  <div class="panel-sub">여기엔 ‘기묘한 업적’, ‘이상한 선택’, ‘누구나 한 번쯤 해본 실수’ 같은 항목을 넣으면 예뻐져.</div>
</div>
""",
        unsafe_allow_html=True,
    )

with tabs[4]:
    st.subheader("INTERACTIVE — 당신의 첫 런은 어떤 맛?")
    st.write("Streamlit의 입력 위젯을 ‘게임 메뉴’처럼 보이게 쓰는 구간. (난잡하게 말고, 우아하게.)")

    colA, colB = st.columns([1, 1])
    with colA:
        narrative = st.slider("서사 vs 전투", 0, 100, 65, help="0이면 전투 몰빵, 100이면 대사·선택 몰빵")
        chaos = st.slider("질서 vs 혼돈", 0, 100, 58, help="0이면 깔끔한 진행, 100이면 “일단 해보자”")
        party = st.radio("플레이 스타일", ["파티 중심", "솔로 도전(무모)"], index=0, horizontal=True)

    def recommend(narrative, chaos, party):
        # 더미 로직(레이아웃 테스트용). 나중에 룰/텍스트를 디테일하게 만들면 됨.
        if narrative >= 60 and chaos >= 60:
            vibe = "이야기와 사고(사건)의 향연"
            rec = "바드/워락/소서러 계열 + 즉흥 선택을 사랑하는 조합"
        elif narrative >= 60:
            vibe = "대사 한 줄에 심장이 흔들리는 타입"
            rec = "팔라딘/클레릭/바드 — ‘선택’에 무게를 두는 조합"
        elif chaos >= 60:
            vibe = "오늘도 계획은 없다. 대신 결과는 있다."
            rec = "바바리안/몬크/로그 — 몸으로 말하는 조합"
        else:
            vibe = "깔끔하게, 그러나 단단하게"
            rec = "파이터/레인저/클레릭 — 안정적인 조합"
        if party.startswith("솔로"):
            rec += " (단, 솔로면 자존심 대신 물약을 챙기자)"
        return vibe, rec

    vibe, rec = recommend(narrative, chaos, party)

    with colB:
        st.markdown(
            f"""
<div class="panel">
  <div class="panel-title">당신의 런 요약</div>
  <div class="panel-big">{vibe}</div>
  <div class="panel-sub"><b>추천:</b> {rec}</div>
  <div class="panel-sub small-note">※ 지금은 ‘레이아웃용’ 결과 문구야. 다음 단계에서 BG3스러운 위트로 더 맛있게 다듬자.</div>
</div>
""",
            unsafe_allow_html=True,
        )

    btn1, btn2 = st.columns([1, 1])
    with btn1:
        if st.button("이 설정 저장(세션)"):
            st.session_state["build"] = {"narrative": narrative, "chaos": chaos, "party": party}
            st.toast("저장 완료. 이제 당신의 선택은… 되돌릴 수 없습니다. (농담)", icon="🎲")
    with btn2:
        if st.button("초기화"):
            for k in ["build"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.toast("초기화 완료. 새 인생… 아니 새 캐릭터로 가자.", icon="✨")

    if "build" in st.session_state:
        st.caption(f"현재 저장됨: {st.session_state['build']}")

# ---------- FOOTER ----------
st.markdown('<hr class="hr-gold"/>', unsafe_allow_html=True)
st.markdown(
    """
<div class="panel">
  <div class="panel-title">Next</div>
  <div class="panel-sub">
    다음 단계에서는 아래 중 원하는 것부터 붙이면 돼:
    <br/>• 공식 인포그래픽 느낌의 ‘패널 카드’ 추가
    <br/>• 데이터/차트(Plotly) + 필터(시즌/패치/테마)
    <br/>• 스포일러 토글, 다운로드(PDF/텍스트), 출처 표기
  </div>
</div>
""",
    unsafe_allow_html=True,
)

