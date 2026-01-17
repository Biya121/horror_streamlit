# app.py
import json
import time
from dataclasses import dataclass, asdict
import streamlit as st

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Baldur's Gate 3 — In Numbers",
    page_icon="🜂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Theme / CSS (Gold + Black, minimal but premium)
# ----------------------------
CSS = """
<style>
:root{
  --bg: #070708;
  --panel: rgba(17, 17, 18, 0.72);
  --panel2: rgba(17, 17, 18, 0.55);
  --border: rgba(199, 170, 92, 0.35);
  --border2: rgba(199, 170, 92, 0.22);
  --gold: #C7AA5C;
  --gold2: #E7D6A2;
  --text: rgba(245, 245, 245, 0.92);
  --muted: rgba(245, 245, 245, 0.65);
  --shadow: rgba(0,0,0,0.6);
}

html, body, [class*="css"] { background: var(--bg) !important; }
.block-container { padding-top: 2.2rem; padding-bottom: 2.2rem; max-width: 1200px; }

h1, h2, h3, h4 { letter-spacing: 0.4px; }
h1 { color: var(--gold2); }
h2, h3 { color: var(--gold2); }
p, li, div { color: var(--text); }

a { color: var(--gold2) !important; }

hr{
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 1.2rem 0;
}

/* Hide Streamlit default menu/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Premium panel */
.panel{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 18px 14px 18px;
  box-shadow: 0 14px 40px var(--shadow);
  backdrop-filter: blur(8px);
}
.panel.soft{
  background: var(--panel2);
  border: 1px solid var(--border2);
}
.kicker{
  text-transform: uppercase;
  font-size: 0.82rem;
  letter-spacing: 0.18em;
  color: var(--muted);
  margin-bottom: 0.2rem;
}
.bigtitle{
  font-size: 3.1rem;
  line-height: 1.0;
  font-weight: 750;
  margin: 0.1rem 0 0.6rem 0;
  color: var(--gold2);
}
.subtitle{
  font-size: 1.05rem;
  color: var(--muted);
  margin-top: 0.2rem;
}
.badge{
  display:inline-block;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.18rem 0.7rem;
  font-size: 0.86rem;
  color: var(--gold2);
  background: rgba(199, 170, 92, 0.08);
  margin-right: 0.45rem;
  margin-bottom: 0.45rem;
}
.goldline{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(199,170,92,0.65), transparent);
  margin: 0.85rem 0 0.95rem 0;
}

/* Metric tweaks */
[data-testid="stMetricValue"]{
  color: var(--gold2) !important;
  font-weight: 800 !important;
}
[data-testid="stMetricLabel"]{
  color: var(--muted) !important;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* Buttons */
.stButton button{
  border-radius: 999px !important;
  border: 1px solid rgba(199,170,92,0.55) !important;
  background: rgba(199,170,92,0.10) !important;
  color: var(--gold2) !important;
  padding: 0.55rem 1.05rem !important;
  transition: all 160ms ease !important;
}
.stButton button:hover{
  transform: translateY(-1px);
  border: 1px solid rgba(231,214,162,0.75) !important;
  background: rgba(199,170,92,0.16) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"]{
  color: var(--muted) !important;
  border-radius: 999px !important;
  border: 1px solid rgba(199,170,92,0.18) !important;
  background: rgba(255,255,255,0.03) !important;
  margin-right: 6px !important;
}
.stTabs [aria-selected="true"]{
  color: var(--gold2) !important;
  border: 1px solid rgba(199,170,92,0.60) !important;
  background: rgba(199,170,92,0.10) !important;
}

/* Expander */
details{
  border-radius: 14px !important;
  border: 1px solid rgba(199,170,92,0.22) !important;
  background: rgba(255,255,255,0.03) !important;
}
details summary{
  padding: 0.35rem 0.55rem !important;
}

/* Fade transition container */
.fade-in{
  animation: fadeIn 240ms ease-out;
}
@keyframes fadeIn{
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0px); }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------
# Data structures
# ----------------------------
@dataclass
class StatItem:
    headline: str         # short title
    value: str            # number or percentage
    detail_ko: str        # Korean translation of the original sentence (neutral)
    notes: str = ""       # optional small note

@dataclass
class Category:
    title_en: str
    description_ko: str
    items: list

# ----------------------------
# Curated data (from the 15 reference images you sent)
# Category titles: English original tone
# Content: Natural Korean translation, no extra opinions
# ----------------------------
CATEGORIES = [
    Category(
        title_en="Most Importantly",
        description_ko="커뮤니티에서 특히 많이 공유된 ‘특이/재미’ 통계입니다.",
        items=[
            StatItem("Cheese Wheel", "1.9 million",
                     "1,900,000명의 플레이어가 치즈 바퀴로 변했습니다."),
            StatItem("Friendly Dinosaurs", "3.5 million",
                     "3,500,000명의 플레이어가 ‘친절한 공룡들’을 찾아갔습니다."),
            StatItem("Freed Us", "2 million",
                     "2,000,000명의 플레이어가 ‘Us’를 콜로니로부터 해방했습니다."),
            StatItem("Spared Alfira (Dark Urge)", "at least 377,000",
                     "최소 377,000명의 다크 어지 플레이어가 알피라를 살리는 방법을 찾아냈습니다."),
        ],
    ),
    Category(
        title_en="Honour Mode",
        description_ko="명예 모드(단 한 번의 실수도 치명적인 모드) 관련 통계입니다.",
        items=[
            StatItem("Conquered Honour Mode", "141,660",
                     "141,660명의 플레이어가 명예 모드를 정복했습니다."),
            StatItem("Level 1 Only", "4,647",
                     "4,647명의 플레이어가 레벨 1 캐릭터만으로 명예 모드를 클리어했습니다."),
            StatItem("Jack of All Trades", "31,180",
                     "31,180명의 플레이어가 ‘잭 오브 올 트레이즈’로 명예 모드를 클리어했습니다."),
            StatItem("Defeats (Playthroughs Ended)", "1,223,305",
                     "1,223,305번의 플레이가 패배로 끝났습니다."),
            StatItem("Honourably Deleted Save", "76%",
                     "그중 76%는 저장 파일을 ‘명예롭게’ 삭제했습니다."),
            StatItem("Continued in Custom Mode", "24%",
                     "그중 24%는 커스텀 모드에서 모험을 이어갔습니다."),
        ],
    ),
    Category(
        title_en="Top 3 Origin Characters As Avatars",
        description_ko="오리진 캐릭터를 아바타로 만든 상위 3명입니다.",
        items=[
            StatItem("Astarion", "1.21 M", "아스타리온을 아바타로 만든 플레이어는 121만 명입니다."),
            StatItem("Gale", "1.20 M", "게일을 아바타로 만든 플레이어는 120만 명입니다."),
            StatItem("Shadowheart", "0.86 M", "섀도하트를 아바타로 만든 플레이어는 86만 명입니다."),
            StatItem("Custom Avatar", "over 93%",
                     "하지만 93% 이상의 플레이어가 커스텀 아바타로 플레이했습니다."),
            StatItem("Dark Urge (within Custom)", "15%",
                     "그 커스텀 아바타 플레이어 중 15%가 다크 어지를 선택했습니다."),
        ],
    ),
    Category(
        title_en="Top Class Picks",
        description_ko="클래스 선택 경향(상위권)입니다.",
        items=[
            StatItem("Note", "—",
                     "이미지에는 ‘상위 클래스 분포’가 막대 그래프로 제시되어 있습니다. (앱에서는 동일 구조로 데이터프레임/차트로 재현 가능)"),
        ],
    ),
    Category(
        title_en="Top Race Picks",
        description_ko="종족 선택 경향(상위권)입니다.",
        items=[
            StatItem("Note", "—",
                     "이미지에는 ‘상위 종족 분포’가 막대 그래프로 제시되어 있습니다. (앱에서는 동일 구조로 데이터프레임/차트로 재현 가능)"),
        ],
    ),
    Category(
        title_en="Top 3 Character Classes Per Race",
        description_ko="각 종족별로 많이 선택된 상위 3개 클래스 구성표입니다.",
        items=[
            StatItem("Note", "—",
                     "이미지에는 종족별 상위 3개 클래스를 가로 막대(비율 축 포함)로 정리한 표가 제시되어 있습니다."),
        ],
    ),
    Category(
        title_en="Romance",
        description_ko="로맨스/관계 관련 통계입니다.",
        items=[
            StatItem("Companion Kisses", "over 75 million",
                     "동료에게 한 키스는 총 7,500만 번 이상입니다."),
            StatItem("Kiss Leader", "Shadowheart — 27 million",
                     "섀도하트가 2,700만 번으로 1위입니다."),
            StatItem("Next", "Astarion — 15 million",
                     "아스타리온이 1,500만 번으로 그다음입니다."),
            StatItem("Last", "Minthara — 169,937",
                     "민타라는 169,937번으로 가장 적었습니다."),
            StatItem("Act 1 Celebration Night", "32.5%",
                     "Act 1 축하의 밤에 32.5%의 플레이어가 섀도하트와 밤을 보냈습니다."),
            StatItem("Act 1 Celebration Night", "13.5%",
                     "같은 밤에 13.5%의 플레이어가 칼라크와 가까워졌습니다."),
            StatItem("Act 1 Celebration Night", "15.6%",
                     "같은 밤에 15.6%의 플레이어는 혼자 잠들었습니다."),
            StatItem("Act 3", "48.8%",
                     "Act 3에서 48.8%의 플레이어가 섀도하트의 최종 로맨스 장면을 경험했습니다."),
            StatItem("Act 3", "17.6%",
                     "Act 3에서 17.6%의 플레이어가 칼라크와 로맨틱한 식사를 했습니다."),
            StatItem("Act 3", "12.9%",
                     "Act 3에서 12.9%의 플레이어가 레이젤과 손을 잡았습니다."),
            StatItem("Halsin", "658,000",
                     "658,000명의 플레이어가 할신과 관계를 맺었습니다."),
            StatItem("Halsin Split", "70% / 30%",
                     "그중 70%는 인간 형태였고, 30%는 곰 형태를 선택했습니다."),
            StatItem("The Emperor", "1.1 million",
                     "1,100,000명의 플레이어가 황제(Emperor)와 관계를 맺었습니다."),
            StatItem("Dream Guardian Form", "63%",
                     "그중 63%는 드림 가디언 형태를 선택했습니다."),
            StatItem("Mind Flayer Tentacles", "37%",
                     "그중 37%는 마인드 플레이어의 형태(촉수)를 선택했습니다."),
        ],
    ),
    Category(
        title_en="Pets",
        description_ko="동물/펫 상호작용 관련 통계입니다.",
        items=[
            StatItem("Scratch", "120 million",
                     "스크래치는 1억 2천만 번 쓰다듬어졌습니다."),
            StatItem("Owlbear Cub", "41 million",
                     "아울베어 새끼는 4천1백만 번 쓰다듬어졌습니다."),
            StatItem("His Majesty", "141,660",
                     "141,660명의 플레이어가 ‘His Majesty’를 쓰다듬으려 시도했습니다."),
            StatItem("Lesson Learned", "—",
                     "결과 문구로 ‘교훈을 얻었다’는 뉘앙스가 함께 제시되어 있습니다."),
        ],
    ),
    Category(
        title_en="Epilogues",
        description_ko="에필로그/후일담 관련 통계입니다.",
        items=[
            StatItem("God Gale Goodbye Hug", "1,498",
                     "1,498명의 플레이어가 ‘신 게일’에게 작별 포옹을 했습니다."),
            StatItem("Halsin Hug", "1.1 million",
                     "110만 명의 플레이어가 할신에게 포옹을 했습니다."),
            StatItem("Tara Transformed (God Gale)", "2,185",
                     "2,185명의 ‘신 게일’이 타라를 털 없는 고양이로 변신시켰습니다."),
            StatItem("Petted Tara", "54,000",
                     "54,000명의 플레이어가 타라를 쓰다듬었습니다."),
        ],
    ),
    Category(
        title_en="Endings",
        description_ko="엔딩/주요 선택 결과 관련 통계입니다.",
        items=[
            StatItem("Betrayed the Emperor", "1.8 million",
                     "180만 명의 플레이어가 황제(Emperor)를 배신했습니다."),
            StatItem("Orpheus as Mind Flayer", "329,000",
                     "329,000명의 플레이어가 오르페우스를 마인드 플레이어로 살도록 설득했습니다."),
            StatItem("Killed the Netherbrain", "3.3 million",
                     "330만 명의 플레이어가 네더브레인을 처치했습니다."),
            StatItem("Gale Sacrifice (subset)", "200,000",
                     "그중 20만 명은 게일이 스스로를 희생하는 선택을 했습니다."),
            StatItem("Avatar Lae’zel (Vlaakith)", "34",
                     "아바타 레이젤로 플레이한 34명의 플레이어가, Vlaakith의 거절 이후 게임 끝에서 스스로를 죽이는 선택을 했습니다."),
        ],
    ),
    Category(
        title_en="Obscure Achievements",
        description_ko="희귀/특이 도전과제 및 행동 통계입니다.",
        items=[
            StatItem("100 Gold From Playing Music", "1.82%",
                     "전체 플레이어 중 1.82%가 연주로 100골드를 벌었습니다."),
            StatItem("PlayStation (same achievement)", "2.26%",
                     "플레이스테이션 플레이어 기준으로는 2.26%가 해당 업적을 달성했습니다."),
            StatItem("Defeated 20 Opponents While Drunk", "2.07%",
                     "2.07%의 플레이어가 술 취한 상태로 스무 명의 적을 쓰러뜨렸습니다."),
            StatItem("Multiclass Through Every Class", "2.30%",
                     "2.30%의 플레이어가 한 번의 플레이에서 모든 클래스를 멀티클래스로 거쳤습니다."),
            StatItem("Defeated Gortash Without Activating Traps", "3.87%",
                     "3.87%의 플레이어가 함정을 발동시키지 않고 고타쉬를 쓰러뜨렸습니다."),
            StatItem("Completed in Tactician Mode", "1.1 million",
                     "110만 명의 플레이어가 전술가(택티션) 난이도로 BG3를 완료했습니다."),
            StatItem("Knocked the Dragon Out of the Sky", "6.24%",
                     "6.24%의 플레이어가 비행 중인 드래곤을 하늘에서 떨어뜨리는 데 성공했습니다."),
            StatItem("Rescued Sazza Three Times", "2.65%",
                     "2.65%의 플레이어가 한 번의 플레이에서 사짜를 세 번 구해냈습니다."),
            StatItem("Avoided Tiefling Refugee Deaths", "just over 5%",
                     "5%가 조금 넘는 플레이어가 티플링 난민들에게 ‘불운한 죽음’이 닥치지 않도록 해냈습니다."),
            StatItem("Used an Enemy as an Improvised Weapon", "8.21%",
                     "8.21%의 플레이어가 적을 즉흥 무기처럼 사용했습니다."),
        ],
    ),
    Category(
        title_en="Baldur’s Gate 3 — In Numbers",
        description_ko="플랫폼/모드/기타 주요 수치입니다.",
        items=[
            StatItem("Mod Downloads", "265 million",
                     "모드 다운로드는 2억 6,500만 회입니다."),
            StatItem("Mods Uploaded", "8.5K",
                     "업로드된 모드는 8,500개입니다."),
            StatItem("Cross-Play", "446,718",
                     "446,718명의 플레이어가 크로스플레이로 서로 다른 플랫폼에서 함께 즐겼습니다."),
            StatItem("Respec: Minsc → Death Domain Cleric", "350",
                     "350명의 플레이어가 민스크를 ‘죽음 권역’ 클레릭으로 리스펙했습니다."),
            StatItem("Adopted a Child With Wyll", "598",
                     "598명의 플레이어가 와일과 함께 아이를 입양했습니다."),
        ],
    ),
    Category(
        title_en="Subclass Respec Stats",
        description_ko="자주 발생한 서브클래스/빌드 변경(리스펙) 통계입니다.",
        items=[
            StatItem("Karlach", "—",
                     "칼라크는 ‘복수의 맹세(Oath of Vengeance)’ 팔라딘으로 가장 많이 리스펙되었습니다."),
            StatItem("Shadowheart", "—",
                     "섀도하트는 ‘죽음 권역(Death)’ 또는 ‘생명 권역(Life)’ 클레릭으로 비슷한 빈도로 리스펙되었습니다."),
            StatItem("Lae’zel", "—",
                     "레이젤은 ‘왕관의 맹세(Oath of the Crown)’ 팔라딘으로 가장 많이 리스펙되었습니다."),
            StatItem("Gale", "—",
                     "게일은 ‘드라코닉 블러드라인’ 소서러로 가장 많이 리스펙되었습니다."),
            StatItem("Astarion", "27,682 campaigns",
                     "패치 8 이후, 아스타리온은 27,682번의 캠페인에서 ‘헥스블레이드’ 워락으로 가장 많이 리스펙되었습니다."),
            StatItem("Wyll", "333,403 campaigns",
                     "와일도 333,403번의 캠페인에서 ‘헥스블레이드’ 워락으로 리스펙되었습니다."),
        ],
    ),
    Category(
        title_en="Top 3 Most Respected Companions (By Number of Campaigns)",
        description_ko="캠페인 기준 ‘가장 많이 리스펙된 동료’(이미지에 제시된 상위권)입니다.",
        items=[
            StatItem("Wyll", "1,417,506", "와일: 1,417,506"),
            StatItem("Our Wizard (Gale)", "684,454", "우리의 마법사(게일): 684,454"),
            StatItem("Shart (Shadowheart)", "4,890,005", "섀도하트: 4,890,005"),
        ],
    ),
]

# ----------------------------
# Session state: page navigation + transition
# ----------------------------
PAGES = ["Home", "Browse", "Compare", "Export"]

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "fade_key" not in st.session_state:
    st.session_state.fade_key = 0

def go(page_name: str):
    st.session_state.page = page_name
    st.session_state.fade_key += 1
    st.toast(f"→ {page_name}", icon="🜂")

def hero():
    st.markdown('<div class="panel fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="kicker">BALDUR’S GATE 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="bigtitle">In Numbers</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">공식 인포그래픽 통계를 바탕으로, 카테고리별 데이터를 정리하고 Streamlit으로 재구성합니다.</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="goldline"></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([1,1,1,1])
    with c1:
        if st.button("Browse Stats", use_container_width=True):
            go("Browse")
    with c2:
        if st.button("Compare (Demo)", use_container_width=True):
            go("Compare")
    with c3:
        if st.button("Export Data", use_container_width=True):
            go("Export")
    with c4:
        st.markdown('<span class="badge">Gold + Black</span><span class="badge">Minimal UI</span><span class="badge">Session Nav</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def render_category(cat: Category):
    st.markdown('<div class="panel fade-in">', unsafe_allow_html=True)
    st.markdown(f"### {cat.title_en}")
    st.caption(cat.description_ko)
    st.markdown('<div class="goldline"></div>', unsafe_allow_html=True)

    # Show first 3 as metrics if they look numeric-ish; rest as expanders for minimalism
    metric_candidates = []
    rest = []
    for it in cat.items:
        if any(ch.isdigit() for ch in it.value) and len(metric_candidates) < 3 and it.value != "—":
            metric_candidates.append(it)
        else:
            rest.append(it)

    if metric_candidates:
        cols = st.columns(len(metric_candidates))
        for col, it in zip(cols, metric_candidates):
            with col:
                st.metric(label=it.headline, value=it.value)

    # Minimal list, expandable details
    for it in rest:
        with st.expander(f"{it.headline}  ·  {it.value}", expanded=False):
            st.write(it.detail_ko)
            if it.notes:
                st.caption(it.notes)

    st.markdown("</div>", unsafe_allow_html=True)

def browse():
    st.markdown(f'<div class="fade-in" key="fade-{st.session_state.fade_key}">', unsafe_allow_html=True)

    top = st.container()
    with top:
        st.markdown('<div class="panel soft">', unsafe_allow_html=True)
        st.markdown("#### Browse")
        st.write("카테고리 제목은 영문 원문을 유지하고, 내부 문장은 한국어로 자연스럽게 옮겼습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([0.9, 2.1], gap="large")

    with left:
        st.markdown('<div class="panel soft">', unsafe_allow_html=True)
        st.markdown("**Categories**")
        titles = [c.title_en for c in CATEGORIES]
        selected = st.radio(
            "Select",
            titles,
            label_visibility="collapsed",
            index=0,
        )
        st.markdown('<div class="goldline"></div>', unsafe_allow_html=True)
        if st.button("← Home", use_container_width=True):
            go("Home")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        cat = next(c for c in CATEGORIES if c.title_en == selected)
        render_category(cat)

    st.markdown("</div>", unsafe_allow_html=True)

def compare_demo():
    st.markdown(f'<div class="fade-in" key="fade-{st.session_state.fade_key}">', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Compare (Demo)")
    st.caption("Streamlit 기능을 ‘과시’하지 않고, 선택 → 결과 변화 흐름으로 보여주는 예시입니다.")

    # Two-select compare
    titles = [c.title_en for c in CATEGORIES]
    c1, c2 = st.columns(2)
    with c1:
        a = st.selectbox("Category A", titles, index=0)
    with c2:
        b = st.selectbox("Category B", titles, index=1 if len(titles) > 1 else 0)

    # Fake transition feel
    if st.button("Compare Now", use_container_width=True):
        with st.status("Comparing…", expanded=False):
            time.sleep(0.25)
            st.write("요약을 구성하는 중…")
            time.sleep(0.25)
            st.write("패널을 정리하는 중…")
            time.sleep(0.20)
        st.toast("Comparison ready", icon="✨")

    ca = next(c for c in CATEGORIES if c.title_en == a)
    cb = next(c for c in CATEGORIES if c.title_en == b)

    st.markdown('<div class="goldline"></div>', unsafe_allow_html=True)
    colA, colB = st.columns(2, gap="large")
    with colA:
        st.markdown("#### A")
        st.write(f"**{ca.title_en}**")
        st.caption(ca.description_ko)
        st.write(f"- 항목 수: {len(ca.items)}")
        # show a few lines
        for it in ca.items[:4]:
            st.write(f"• **{it.headline}** — {it.value}")
    with colB:
        st.markdown("#### B")
        st.write(f"**{cb.title_en}**")
        st.caption(cb.description_ko)
        st.write(f"- 항목 수: {len(cb.items)}")
        for it in cb.items[:4]:
            st.write(f"• **{it.headline}** — {it.value}")

    st.markdown('<div class="goldline"></div>', unsafe_allow_html=True)
    if st.button("← Home", use_container_width=True):
        go("Home")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def export_data():
    st.markdown(f'<div class="fade-in" key="fade-{st.session_state.fade_key}">', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Export")
    st.caption("이 앱에 들어있는 정리 데이터를 JSON으로 내보내는 예시입니다.")

    export_obj = {
        "theme": {"mood": "gold_black", "title": "Baldur’s Gate 3 — In Numbers"},
        "categories": [
            {
                "title_en": c.title_en,
                "description_ko": c.description_ko,
                "items": [asdict(i) for i in c.items],
            }
            for c in CATEGORIES
        ],
    }

    raw = json.dumps(export_obj, ensure_ascii=False, indent=2)
    st.code(raw[:3000] + ("\n… (truncated preview)" if len(raw) > 3000 else ""), language="json")

    st.download_button(
        "Download JSON",
        data=raw.encode("utf-8"),
        file_name="bg3_in_numbers_ko.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown('<div class="goldline"></div>', unsafe_allow_html=True)
    if st.button("← Home", use_container_width=True):
        go("Home")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Render
# ----------------------------
# Minimal top nav (buttons) with "page transition" vibe
nav = st.container()
with nav:
    cols = st.columns([1,1,1,1,2])
    with cols[0]:
        if st.button("Home", use_container_width=True):
            go("Home")
    with cols[1]:
        if st.button("Browse", use_container_width=True):
            go("Browse")
    with cols[2]:
        if st.button("Compare", use_container_width=True):
            go("Compare")
    with cols[3]:
        if st.button("Export", use_container_width=True):
            go("Export")
    with cols[4]:
        st.markdown('<div style="text-align:right; color: rgba(245,245,245,0.55); font-size: 0.92rem;">🜂 Minimal Streamlit — Gold/Black</div>', unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

if st.session_state.page == "Home":
    hero()

    # quick highlights (minimal, no clutter)
    st.markdown('<div class="panel soft fade-in">', unsafe_allow_html=True)
    st.markdown("#### Highlights")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Mod Downloads", "265 million")
    with c2:
        st.metric("Honour Mode Cleared", "141,660")
    with c3:
        st.metric("Companion Kisses", "75 million+")
    with c4:
        st.metric("Cross-Play", "446,718")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Browse":
    browse()
elif st.session_state.page == "Compare":
    compare_demo()
elif st.session_state.page == "Export":
    export_data()


