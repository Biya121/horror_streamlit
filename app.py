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
# Enhanced CSS (Obsidian & Antique Gold)
# ----------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Nanum+Myeongjo:wght@400;700&display=swap');

:root {
    --bg-dark: #070708;
    --panel-dark: rgba(18, 18, 20, 0.95);
    --gold-primary: #c7aa5c;
    --gold-bright: #e7d6a2;
    --gold-darker: #5e4d26;
    --text-main: #f2efe6;
    --text-muted: #a8a08d;
    --accent-red: #8b0000;
}

/* Base App Style */
.stApp {
    background-color: var(--bg-dark);
    background-image: radial-gradient(circle at 50% -20%, #2a2518 0%, #070708 80%);
    color: var(--text-main);
}

/* Header & Typography */
h1, h2, h3, .bigtitle {
    font-family: 'Cinzel', serif !important;
    color: var(--gold-bright) !important;
    text-shadow: 0 0 15px rgba(199, 170, 92, 0.4);
    text-align: center;
}

/* BG3 Obsidian Panel */
.bg3-panel {
    background: var(--panel-dark);
    border: 1px solid var(--gold-darker);
    border-top: 2px solid var(--gold-primary);
    border-radius: 2px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8);
    margin-bottom: 2rem;
    position: relative;
}

/* Custom Button (BG3 Gold Style) */
div.stButton > button {
    background: linear-gradient(180deg, #2a2518 0%, #000000 100%) !important;
    color: var(--gold-bright) !important;
    border: 1px solid var(--gold-primary) !important;
    border-radius: 0px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    letter-spacing: 2px;
    padding: 0.8rem !important;
    transition: all 0.3s ease !important;
}

div.stButton > button:hover {
    background: var(--gold-primary) !important;
    color: black !important;
    box-shadow: 0 0 20px var(--gold-primary);
}

/* Metric & Details */
[data-testid="stMetricValue"] { font-family: 'Cinzel' !important; color: var(--gold-bright) !important; font-size: 2.8rem !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; letter-spacing: 1px; }

.gold-hr {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 2rem 0;
}

.stat-card {
    border-left: 2px solid var(--gold-darker);
    padding-left: 15px;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------
# Data Structure & Full Content
# ----------------------------
@dataclass
class StatItem:
    headline: str
    value: str
    detail_ko: str

@dataclass
class Category:
    title_en: str
    description_ko: str
    items: list
    img_url: str = "" # 카테고리별 사진

CATEGORIES = [
    Category(
        "Most Importantly",
        "커뮤니티에서 가장 화제가 된 특이하고 재미있는 기록들입니다.",
        [
            StatItem("Cheese Wheel", "1.9 million", "190만 명의 모험가가 치즈 바퀴로 변신하는 굴욕(혹은 행운)을 겪었습니다."),
            StatItem("Friendly Dinosaurs", "3.5 million", "350만 명이 쥬라기 시대를 방불케 하는 친절한 공룡들을 만났습니다."),
            StatItem("Freed Us", "2 million", "200만 명의 플레이어가 지능 포식자 '우리(Us)'를 해방해 주었습니다."),
            StatItem("Spared Alfira", "377,000+", "다크 어지의 숙명을 거스르고 알피라를 살려낸 의지의 기록입니다.")
        ],
        "https://pbs.twimg.com/media/GUYneuVXkAAhKSS?format=jpg&name=medium" # 이미지 주소 교체 가능
    ),
    Category(
        "Honour Mode",
        "치명적인 난이도와 단 하나의 세이브 파일. 영광스러운 정복자들의 수치입니다.",
        [
            StatItem("Conquered", "141,660", "황금 주사위를 쟁취하며 명예를 증명한 수입니다."),
            StatItem("Level 1 Only", "4,647", "레벨 1로 명예를 클리어한 믿기 힘든 기록입니다."),
            StatItem("Defeats", "1,223,305", "실패로 끝난 명예 모드 횟수입니다."),
            StatItem("Honourable Choice", "76%", "실패 후 76%는 명예롭게 세이브를 지웠고, 24%는 모험을 이어갔습니다.")
        ],
        "https://pbs.twimg.com/media/GUYn_GlXkAA-rs6?format=jpg&name=medium"
    ),
    Category(
        "Origin & Avatars",
        "누가 이 거대한 서사의 중심에 섰을까요?",
        [
            StatItem("Custom Avatar", "93%+", "대부분의 모험가는 자신만의 영웅을 직접 빚어냈습니다."),
            StatItem("Astarion", "1.21 M", "오리진 캐릭터 중 가장 많은 선택을 받은 주인공입니다."),
            StatItem("Gale", "1.20 M", "마법사 게일이 아주 근소한 차이로 뒤를 잇습니다."),
            StatItem("Shadowheart", "0.86 M", "섀도하트가 오리진 선택지 중 3위를 차지했습니다.")
        ],
        "https://pbs.twimg.com/media/GUYoM75WsAAFgNc?format=jpg&name=medium"
    ),
    Category(
        "Romance & Intimacy",
        "캠프에서의 사랑은 전투만큼이나 치열했습니다.",
        [
            StatItem("Companion Kisses", "75M+", "동료들과 나눈 입맞춤은 이미 7,500만 번을 돌파했습니다."),
            StatItem("Kiss Leader", "Shadowheart", "2,700만 번의 키스로 섀도하트가 독보적 1위를 기록했습니다."),
            StatItem("The Emperor", "1.1 million", "110만 명의 모험가가 마인드 플레이어와 사랑을 나누었습니다."),
            StatItem("Halsin Split", "70% / 30%", "할신과의 관계 중 30%는 곰의 형상으로 이루어졌습니다.")
        ],
        "https://pbs.twimg.com/media/GUYoazpXQAAS2QF?format=jpg&name=medium"
    ),
    Category(
        "Pets & Epilogues",
        "동물 친구들과의 교감, 그리고 그 후의 이야기입니다.",
        [
            StatItem("Scratch", "120 million", "스크래치는 세상에서 가장 많이 사랑받은 강아지입니다."),
            StatItem("Owlbear Cub", "41 million", "아울베어 새끼 역시 수천만 번의 손길을 받았습니다."),
            StatItem("Halsin Hug", "1.1 million", "에필로그에서 110만 명의 플레이어가 할신을 안아주었습니다."),
            StatItem("Petted Tara", "54,000", "게일의 친구 타라를 쓰다듬은 정성 어린 기록입니다.")
        ],
        "https://pbs.twimg.com/media/GUYoj1AXkAAitOX?format=jpg&name=medium"
    ),
    Category(
        "Class Respec Stats",
        "운명을 바꾼 모험가들. 리스펙(Respec)의 모든 것입니다.",
        [
            StatItem("Shadowheart", "4.89M times", "가장 많이 직업이 바뀐 동료 1위입니다."),
            StatItem("Wyll", "1.41M times", "윌은 주로 헥스블레이드로 새로운 길을 찾았습니다."),
            StatItem("Minsc", "350 people", "민스크를 '죽음 권역' 클레릭으로 바꾼 독특한 취향의 모험가들입니다."),
            StatItem("Multiclass", "2.30%", "단 한 번의 플레이로 모든 클래스를 경험한 달인들입니다.")
        ],
        "https://pbs.twimg.com/media/GxhDmNaXcAADB9_?format=jpg&name=medium"
    )
]

# ----------------------------
# Session State
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = CATEGORIES[0].title_en

def go(page_name):
    st.session_state.page = page_name

# ----------------------------
# Page Renderers
# ----------------------------

# --- HOME PAGE ---
if st.session_state.page == "Home":
    # 1. 대표 배너 사진 (URL 입력 가능)
    st.image("https://giffiles.alphacoders.com/219/219996.gif", use_container_width=True)
    
    st.markdown('<div class="bigtitle" style="font-size: 5rem; margin-top: -80px;">ARCHIVE OF FATE</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-family:Cinzel; letter-spacing:5px;">A Repository of Every Decision, Every Roll, Every Death.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="gold-hr"></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="bg3-panel">', unsafe_allow_html=True)
        st.write("발더스 게이트 3의 세계에서 플레이어들이 남긴 방대한 발자취를 공식 통계로 정리했습니다. 당신의 모험은 이 숫자들 중 어디에 속해 있습니까?")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("기록 보관소 입장 (Browse Stats)", use_container_width=True):
            go("Browse")
        st.markdown('</div>', unsafe_allow_html=True)

# --- BROWSE PAGE ---
elif st.session_state.page == "Browse":
    st.markdown('<div style="padding: 1rem 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: left; font-size: 2.5rem;">The Archive</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col_nav, col_main = st.columns([0.8, 2.2], gap="large")
    
    with col_nav:
        st.markdown('<div class="bg3-panel" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<p style="color: var(--gold-primary); font-family: Cinzel; font-weight: bold;">Navigation</p>', unsafe_allow_html=True)
        for cat in CATEGORIES:
            if st.button(cat.title_en, use_container_width=True):
                st.session_state.selected_cat = cat.title_en
        
        st.markdown('<div class="gold-hr" style="margin: 1rem 0;"></div>', unsafe_allow_html=True)
        if st.button("← Main Menu", use_container_width=True):
            go("Home")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        # 선택된 카테고리 데이터 찾기
        current_cat = next(c for c in CATEGORIES if c.title_en == st.session_state.selected_cat)
        
        # 2. 카테고리별 사진 (설정된 경우에만 표시)
        if current_cat.img_url:
            st.image(current_cat.img_url, use_container_width=True)
        
        st.markdown(f'<div class="bg3-panel">', unsafe_allow_html=True)
        st.markdown(f'<h1 style="text-align: left; font-size: 3rem; margin-bottom: 0;">{current_cat.title_en}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: var(--text-muted); font-style: italic;">{current_cat.description_ko}</p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-hr"></div>', unsafe_allow_html=True)
        
        # 통계 아이템 렌더링 (2개씩 정렬)
        for i in range(0, len(current_cat.items), 2):
            m_col1, m_col2 = st.columns(2)
            
            # 첫 번째 아이템
            with m_col1:
                item = current_cat.items[i]
                st.markdown(f'<div class="stat-card">', unsafe_allow_html=True)
                st.metric(label=item.headline, value=item.value)
                st.write(item.detail_ko)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 두 번째 아이템 (존재하는 경우)
            if i + 1 < len(current_cat.items):
                with m_col2:
                    item = current_cat.items[i+1]
                    st.markdown(f'<div class="stat-card">', unsafe_allow_html=True)
                    st.metric(label=item.headline, value=item.value)
                    st.write(item.detail_ko)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
