import json
import time
from dataclasses import dataclass, asdict
import streamlit as st

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="BG3 — Tome of Statistics",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Theme / CSS (BG3 Style: Obsidian & Gold)
# ----------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Nanum+Myeongjo:wght@400;700&display=swap');

:root {
    --bg-dark: #0a0a0c;
    --panel-dark: #121214;
    --gold-primary: #c7aa5c;
    --gold-bright: #e7d6a2;
    --gold-darker: #8a733e;
    --text-main: #f2efe6;
    --text-muted: #a8a08d;
    --accent-red: #8b0000;
}

/* Background & Body */
.stApp {
    background-color: var(--bg-dark);
    background-image: 
        radial-gradient(circle at 20% 20%, rgba(199, 170, 92, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(139, 0, 0, 0.03) 0%, transparent 40%);
    color: var(--text-main);
}

/* Typography */
h1, h2, h3, .bigtitle {
    font-family: 'Cinzel', serif !important;
    color: var(--gold-bright) !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    font-weight: 700 !important;
}

p, span, label, .stMarkdown {
    font-family: 'Nanum Myeongjo', serif !important;
}

/* Panel Design */
.bg3-panel {
    background: var(--panel-dark);
    border: 1px solid var(--gold-darker);
    border-radius: 4px; /* Medieval style usually has sharper corners */
    padding: 2rem;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 10px 30px rgba(0,0,0,0.5);
    margin-bottom: 20px;
}

/* Gold Divider */
.gold-hr {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 1.5rem 0;
}

/* Custom Metric Style */
[data-testid="stMetricValue"] {
    font-family: 'Cinzel', serif !important;
    color: var(--gold-bright) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-weight: bold;
    letter-spacing: 1px;
}

/* 버튼 스타일 - 흰색 방지 및 황금색 테두리 */
div.stButton > button {
    background-color: rgba(199, 170, 92, 0.1) !important;
    color: var(--gold-bright) !important;
    border: 1px solid var(--gold-primary) !important;
    border-radius: 2px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s ease !important;
    width: 100%;
}

div.stButton > button:hover {
    background-color: var(--gold-primary) !important;
    color: var(--bg-dark) !important;
    box-shadow: 0 0 15px var(--gold-primary);
}

/* Selectbox/Input styling */
.stSelectbox div[data-baseweb="select"] {
    background-color: #1a1a1d !important;
    border: 1px solid var(--gold-darker) !important;
}

/* Expander Style */
.streamlit-expanderHeader {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid var(--gold-darker) !important;
    color: var(--gold-bright) !important;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------
# Data Logic
# ----------------------------
@dataclass
class StatItem:
    headline: str
    value: str
    detail_ko: str
    notes: str = ""

@dataclass
class Category:
    title_en: str
    description_ko: str
    items: list

# Data Injection (Fixed common spacing/char errors)
CATEGORIES = [
    Category(
        title_en="Honour Mode",
        description_ko="치명적인 난이도, 단 하나의 세이브. 명예 모드의 기록입니다.",
        items=[
            StatItem("Conquered Honour Mode", "141,660", "141,660명의 모험가가 명예 모드를 정복했습니다."),
            StatItem("Defeats (Total)", "1,223,305", "1,223,305개의 여정이 중간에 종결되었습니다."),
            StatItem("Level 1 Legend", "4,647", "4,647명은 레벨 1로만 명예 모드를 클리어했습니다."),
            StatItem("Honourably Deleted", "76%", "실패자의 76%는 미련 없이 세이브 파일을 삭제했습니다."),
        ],
    ),
    Category(
        title_en="Romance & Bonds",
        description_ko="캠프에서 피어난 연정의 통계입니다.",
        items=[
            StatItem("Total Kisses", "75M+", "동료들과의 입맞춤이 7,500만 번을 넘었습니다."),
            StatItem("Shadowheart", "27M", "로맨스 1위는 섀도하트가 차지했습니다."),
            StatItem("The Emperor", "1.1M", "110만 명의 플레이어가 황제와 깊은 관계를 맺었습니다."),
            StatItem("Bear Form", "30%", "할신과의 관계 중 30%는 곰 형태에서 이루어졌습니다."),
        ],
    ),
    Category(
        title_en="The Furry Friends",
        description_ko="모험 중 만난 가장 충성스러운 동료들의 기록입니다.",
        items=[
            StatItem("Scratch", "120M Pets", "스크래치는 1억 2천만 번 넘게 쓰다듬어졌습니다."),
            StatItem("Owlbear Cub", "41M Pets", "아울베어 새끼도 4,100만 번의 사랑을 받았습니다."),
            StatItem("His Majesty", "141,660", "14만 명이 감히 폐하를 쓰다듬으려 시도했습니다."),
        ],
    )
]

# ----------------------------
# Navigation Logic
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

def go(page_name: str):
    st.session_state.page = page_name

# ----------------------------
# Page Renderers
# ----------------------------
def render_header():
    st.markdown('<div style="text-align: center; margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown('<div class="bigtitle" style="font-size: 4rem;">BALDUR\'S GATE III</div>', unsafe_allow_html=True)
    st.markdown('<div style="letter-spacing: 5px; color: var(--gold-primary); font-family: Cinzel;">THE GREAT ARCHIVE</div>', unsafe_allow_html=True)
    st.markdown('<div class="gold-hr"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def page_home():
    render_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="bg3-panel">', unsafe_allow_html=True)
        st.write("주사위는 던져졌습니다. 라리안 스튜디오에서 제공한 공식 데이터를 기반으로 기록된 모험가들의 흔적을 탐색하십시오.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("기록 보관소 입장 (Browse Stats)"):
            go("Browse")
        if st.button("데이터 추출 (Export Data)"):
            go("Export")
        st.markdown('</div>', unsafe_allow_html=True)

def page_browse():
    render_header()
    
    col_nav, col_content = st.columns([1, 3])
    
    with col_nav:
        st.markdown("### Categories")
        for cat in CATEGORIES:
            if st.button(cat.title_en):
                st.session_state.selected_cat = cat.title_en
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Main Menu"):
            go("Home")

    with col_content:
        selected_name = st.session_state.get("selected_cat", CATEGORIES[0].title_en)
        cat = next(c for c in CATEGORIES if c.title_en == selected_name)
        
        st.markdown(f'<div class="bg3-panel">', unsafe_allow_html=True)
        st.markdown(f"<h2>{cat.title_en}</h2>", unsafe_allow_html=True)
        st.write(cat.description_ko)
        st.markdown('<div class="gold-hr"></div>', unsafe_allow_html=True)
        
        # Metrics display
        m_cols = st.columns(len(cat.items))
        for i, item in enumerate(cat.items):
            with m_cols[i % len(m_cols)]:
                st.metric(label=item.headline, value=item.value)
                st.caption(item.detail_ko)
        st.markdown('</div>', unsafe_allow_html=True)

def page_export():
    render_header()
    st.markdown('<div class="bg3-panel">', unsafe_allow_html=True)
    st.markdown("### Scroll of Data")
    st.write("아카이브의 모든 데이터를 JSON 형태로 두루마리에 복사합니다.")
    
    full_data = [asdict(c) for c in CATEGORIES]
    st.code(json.dumps(full_data, indent=4, ensure_ascii=False), language="json")
    
    if st.button("← Return"):
        go("Home")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Router
# ----------------------------
if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Browse":
    page_browse()
elif st.session_state.page == "Export":
    page_export()
