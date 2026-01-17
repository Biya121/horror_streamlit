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
# Enhanced CSS (Fixed UI & Sticky Menu)
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
}

/* 1. Black Box & Gap Removal */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}
[data-testid="stVerticalBlock"] > div {
    gap: 0rem !important;  /* 이미지와 텍스트 사이의 검은 공백 제거 */
}
.stImage {
    margin-bottom: -10px !important; /* 이미지 하단 여백 강제 조정 */
}

/* Base App Style */
.stApp {
    background-color: var(--bg-dark);
    background-image: radial-gradient(circle at 50% -20%, #2a2518 0%, #070708 80%);
    color: var(--text-main);
}

/* Sticky Navigation Logic */
[data-testid="stSidebar"] {
    display: none; /* 기본 사이드바 숨김 */
}

/* 3. Scroll-Follow Navigation (Sticky) */
.sticky-nav {
    position: -webkit-sticky;
    position: sticky;
    top: 2rem;
    z-index: 100;
}

/* Header & Typography */
h1, h2, h3, .bigtitle {
    font-family: 'Cinzel', serif !important;
    color: var(--gold-bright) !important;
    text-shadow: 0 0 15px rgba(199, 170, 92, 0.4);
}

/* BG3 Obsidian Panel */
.bg3-panel {
    background: var(--panel-dark);
    border: 1px solid var(--gold-darker);
    border-top: 2px solid var(--gold-primary);
    padding: 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8);
    margin-bottom: 2rem;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(180deg, #2a2518 0%, #000000 100%) !important;
    color: var(--gold-bright) !important;
    border: 1px solid var(--gold-primary) !important;
    font-family: 'Cinzel', serif !important;
    letter-spacing: 1px;
    padding: 0.6rem !important;
    margin-bottom: 5px;
}
div.stButton > button:hover {
    background: var(--gold-primary) !important;
    color: black !important;
}

/* Gallery Grid */
.gallery-img {
    border: 1px solid var(--gold-darker);
    transition: transform 0.3s ease;
}
.gallery-img:hover {
    border: 1px solid var(--gold-bright);
    transform: scale(1.02);
}

.gold-hr {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 1.5rem 0;
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
# Data Structure
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
    img_url: str = ""
    is_gallery: bool = False
    gallery_images: list = None

CATEGORIES = [
    Category(
        "Most Importantly",
        "커뮤니티에서 화제가 된 특이하고 재미있는 기록들입니다.",
        [
            StatItem("Cheese Wheel", "1.9 million", "190만 명의 모험가가 치즈 바퀴로 변신했습니다."),
            StatItem("Friendly Dinosaurs", "3.5 million", "350만 명이 친절한 공룡들을 만났습니다."),
            StatItem("Freed Us", "2 million", "지능 포식자 '우리(Us)'를 해방해 준 기록입니다."),
            StatItem("Spared Alfira", "377,000+", "다크 어지의 숙명을 거스르고 알피라를 살려냈습니다.")
        ],
        "https://pbs.twimg.com/media/GUYneuVXkAAhKSS?format=jpg&name=medium"
    ),
    Category(
        "Honour Mode",
        "치명적인 난이도와 단 하나의 세이브 파일. 영광스러운 정복자들의 수치입니다.",
        [
            StatItem("Conquered", "141,660", "황금 주사위를 쟁취하며 명예를 증명했습니다."),
            StatItem("Level 1 Only", "4,647", "레벨 1로 명예를 클리어한 기적의 기록입니다."),
            StatItem("Defeats", "1,223,305", "실패로 끝난 명예 모드 도전 횟수입니다."),
            StatItem("Honourable Choice", "76%", "실패 후 76%는 명예롭게 세이브를 지웠습니다.")
        ],
        "https://pbs.twimg.com/media/GUYn_GlXkAA-rs6?format=jpg&name=medium"
    ),
    Category(
        "Gallery: Realms of BG3",
        "포가튼 렐름의 아름다운 풍경과 순간들을 감상하십시오.",
        [], # 갤러리는 통계 아이템이 필요 없음
        "https://giffiles.alphacoders.com/219/219996.gif",
        is_gallery=True,
        gallery_images=[
            "https://pbs.twimg.com/media/GUYoM75WsAAFgNc?format=jpg&name=medium",
            "https://pbs.twimg.com/media/GUYoazpXQAAS2QF?format=jpg&name=medium",
            "https://pbs.twimg.com/media/GUYoj1AXkAAitOX?format=jpg&name=medium",
            "https://pbs.twimg.com/media/GxhDmNaXcAADB9_?format=jpg&name=medium"
        ]
    ),
    Category(
        "Origin & Avatars",
        "누가 이 거대한 서사의 중심에 섰을까요?",
        [
            StatItem("Custom Avatar", "93%+", "대부분의 모험가는 자신만의 영웅을 창조했습니다."),
            StatItem("Astarion", "1.21 M", "오리진 캐릭터 중 가장 많은 선택을 받았습니다."),
            StatItem("Gale", "1.20 M", "마법사 게일이 근소한 차이로 뒤를 잇습니다."),
            StatItem("Shadowheart", "0.86 M", "섀도하트가 오리진 선택지 중 3위를 차지했습니다.")
        ],
        "https://pbs.twimg.com/media/GUYoM75WsAAFgNc?format=jpg&name=medium"
    ),
    Category(
        "Romance & Intimacy",
        "캠프에서의 사랑은 전투만큼이나 치열했습니다.",
        [
            StatItem("Companion Kisses", "75M+", "동료들과 나눈 입맞춤 횟수입니다."),
            StatItem("Kiss Leader", "Shadowheart", "2,700만 번의 키스로 섀도하트가 1위를 기록했습니다."),
            StatItem("The Emperor", "1.1 million", "110만 명의 모험가가 마인드 플레이어와 사랑을 나누었습니다."),
            StatItem("Halsin Split", "70% / 30%", "할신과의 관계 중 30%는 곰의 형상이었습니다.")
        ],
        "https://pbs.twimg.com/media/GUYoazpXQAAS2QF?format=jpg&name=medium"
    ),
    Category(
        "Pets & Epilogues",
        "동물 친구들과의 교감, 그리고 그 후의 이야기입니다.",
        [
            StatItem("Scratch", "120 million", "스크래치는 세상에서 가장 많이 사랑받은 강아지입니다."),
            StatItem("Owlbear Cub", "41 million", "아울베어 새끼 역시 수천만 번의 손길을 받았습니다."),
            StatItem("Halsin Hug", "1.1 million", "에필로그에서 110만 명이 할신을 안아주었습니다."),
            StatItem("Petted Tara", "54,000", "게일의 친구 타라를 쓰다듬은 기록입니다.")
        ],
        "https://pbs.twimg.com/media/GUYoj1AXkAAitOX?format=jpg&name=medium"
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
# Renderers
# ----------------------------

if st.session_state.page == "Home":
    st.image("https://giffiles.alphacoders.com/219/219996.gif", use_container_width=True)
    st.markdown('<div class="bigtitle" style="font-size: 5rem; text-align:center; margin-top: -80px;">ARCHIVE OF FATE</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-family:Cinzel; letter-spacing:5px;">A Repository of Every Decision, Every Roll, Every Death.</p>', unsafe_allow_html=True)
    st.markdown('<div class="gold-hr"></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="bg3-panel">', unsafe_allow_html=True)
        st.write("포가튼 렐름에서 당신이 내린 모든 결정은 이곳에 기록되어 있습니다. 모험가들이 남긴 거대한 흔적을 확인하십시오.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("보관소 입장 (Enter Archive)", use_container_width=True):
            go("Browse")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Browse":
    st.markdown('<div style="padding: 1.5rem 0 0 0;"><h2 style="text-align: left; font-size: 2.5rem;">The Archive</h2></div>', unsafe_allow_html=True)
    
    col_nav, col_main = st.columns([0.8, 2.2], gap="large")
    
    # 3. Sticky Navigation Menu
    with col_nav:
        st.markdown('<div class="sticky-nav">', unsafe_allow_html=True)
        st.markdown('<div class="bg3-panel" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<p style="color: var(--gold-primary); font-family: Cinzel; font-weight: bold;">Navigation</p>', unsafe_allow_html=True)
        for cat in CATEGORIES:
            if st.button(cat.title_en, use_container_width=True):
                st.session_state.selected_cat = cat.title_en
        st.markdown('<div class="gold-hr" style="margin: 1rem 0;"></div>', unsafe_allow_html=True)
        if st.button("← Main Menu", use_container_width=True):
            go("Home")
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col_main:
        current_cat = next(c for c in CATEGORIES if c.title_en == st.session_state.selected_cat)
        
        # Category Banner
        if current_cat.img_url:
            st.image(current_cat.img_url, use_container_width=True)
        
        st.markdown(f'<div class="bg3-panel">', unsafe_allow_html=True)
        st.markdown(f'<h1 style="text-align: left; font-size: 3rem; margin-bottom: 0;">{current_cat.title_en}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: var(--text-muted); font-style: italic;">{current_cat.description_ko}</p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-hr"></div>', unsafe_allow_html=True)
        
        # 2. Gallery Logic
        if current_cat.is_gallery and current_cat.gallery_images:
            # 갤러리 그리드 (2열 구성)
            g_cols = st.columns(2)
            for idx, g_img in enumerate(current_cat.gallery_images):
                with g_cols[idx % 2]:
                    st.image(g_img, use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            # Statistics Logic
            for i in range(0, len(current_cat.items), 2):
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    item = current_cat.items[i]
                    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                    st.metric(label=item.headline, value=item.value)
                    st.write(item.detail_ko)
                    st.markdown('</div>', unsafe_allow_html=True)
                if i + 1 < len(current_cat.items):
                    with m_col2:
                        item = current_cat.items[i+1]
                        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                        st.metric(label=item.headline, value=item.value)
                        st.write(item.detail_ko)
                        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
