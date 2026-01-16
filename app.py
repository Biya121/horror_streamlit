import streamlit as st
import time
import random
from pathlib import Path

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="🕯️ 금지된 방",
    page_icon="🕯️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ASSETS = Path(__file__).parent / "assets"
JUMPSCARE_IMG = ASSETS / "jumpscare.png"
WHISPER_AUDIO = ASSETS / "whisper.mp3"


def typewriter(text: str, speed: float = 0.04):
    """타이핑 효과 (텍스트 깨짐 없음)"""
    box = st.empty()
    out = ""
    for ch in text:
        out += ch
        box.markdown(f"<div class='typing'>{out}</div>", unsafe_allow_html=True)
        time.sleep(speed)


# =========================
# 스타일(CSS)
# =========================
st.markdown(
    """
<style>
/* 전체 배경 */
.stApp {
  background: radial-gradient(circle at 20% 20%, #141414 0%, #060606 55%, #000 100%);
  color: #e6e6e6;
}

/* 제목 */
h1, h2, h3 {
  letter-spacing: 0.5px;
}

/* 카드 */
.block {
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  padding: 18px 18px;
  border-radius: 14px;
  box-shadow: 0 10px 35px rgba(0,0,0,0.35);
}

/* 경고 텍스트 */
.warn {
  color: #ff6b6b;
  font-weight: 700;
}

/* 타이핑 텍스트 */
.typing {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 1.05rem;
  line-height: 1.55;
  white-space: pre-wrap;
}

/* 버튼 스타일 */
.stButton>button {
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: #f1f1f1;
}
.stButton>button:hover {
  border: 1px solid rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.10);
}

/* GAME OVER 전체 화면 느낌 */
.gameover-wrap {
  padding: 22px;
  border-radius: 16px;
  border: 1px solid rgba(255, 70, 70, 0.35);
  background: rgba(20, 0, 0, 0.50);
  box-shadow: 0 14px 50px rgba(0,0,0,0.55);
  text-align: center;
}

.gameover-title {
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: 2px;
  margin-bottom: 10px;
  color: #ff4d4d;
  text-transform: uppercase;
}

.gameover-sub {
  font-size: 1.15rem;
  font-weight: 800;
  margin-top: 14px;
  margin-bottom: 6px;
}

.gameover-msg {
  font-size: 1.05rem;
  opacity: 0.92;
  line-height: 1.6;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# 세션 상태
# =========================
if "stage" not in st.session_state:
    st.session_state.stage = "intro"
if "room" not in st.session_state:
    st.session_state.room = None
if "screamed" not in st.session_state:
    st.session_state.screamed = False

# =========================
# 사이드바(옵션)
# =========================
with st.sidebar:
    st.markdown("### 설정")
    sound_on = st.toggle("🔊 사운드 켜기", value=True)
    fast_mode = st.toggle("⚡ 빠른 연출", value=False)
    typing_speed = 0.01 if fast_mode else 0.04

# =========================
# 타이틀
# =========================
st.title("🕯️ 금지된 방")

# =========================
# 단계별 렌더링
# =========================
if st.session_state.stage == "intro":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("**이 페이지는 단순한 연출(공포 스토리)입니다.**")
    st.markdown("불편하면 언제든지 **탈출** 버튼을 누르세요.")
    st.markdown("<span class='warn'>※ 점프스케어(깜짝 이미지)가 있습니다.</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("들어간다"):
            st.session_state.stage = "warning"
            st.rerun()
    with col2:
        if st.button("나간다(안전)"):
            st.stop()

elif st.session_state.stage == "warning":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    typewriter("문이... 잠겼다.\n\n뒤에서 누가 숨 쉬는 소리가 난다.\n\n'...누구야?'", speed=typing_speed)
    st.markdown("</div>", unsafe_allow_html=True)

    if sound_on and WHISPER_AUDIO.exists():
        st.audio(str(WHISPER_AUDIO), autoplay=True)

    st.write("")
    if st.button("주위를 둘러본다"):
        st.session_state.stage = "choose_room"
        st.rerun()

elif st.session_state.stage == "choose_room":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("세 개의 문이 보인다. 문 손잡이는 모두… **차갑다.**")
    st.markdown("</div>", unsafe_allow_html=True)

    rooms = {
        "1번 문 — 거울의 방": [
            "거울 속의 너는… 0.5초 늦게 따라 한다.",
            "분명히 웃지 않았는데, 거울 속 네가 먼저 웃는다.",
            "거울에 손을 대자, 손바닥이 안쪽에서 잡아당긴다.",
        ],
        "2번 문 — 타자기의 방": [
            "낡은 타자기가 혼자 움직인다.",
            "종이에 찍힌 글자: '뒤를 봐'.",
            "너는 절대 뒤를 보면 안 된다… 그런데…",
        ],
        "3번 문 — 전화기의 방": [
            "전화기가 울린다. 오래된 벨소리.",
            "수화기를 들자, 너의 목소리가 들린다.",
            "'지금 당장… 문을 잠가.'",
        ],
    }

    choice = st.radio("어느 문을 열래?", list(rooms.keys()), index=0)
    st.write("")
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("**문 너머에서 들리는 소리**")
    st.write("• " + "\n• ".join(rooms[choice]))
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("문을 연다"):
            st.session_state.room = choice
            st.session_state.stage = "story"
            st.rerun()
    with col2:
        if st.button("탈출"):
            st.session_state.stage = "escape"
            st.rerun()

elif st.session_state.stage == "story":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown(f"**선택한 문:** {st.session_state.room}")
    st.markdown("</div>", unsafe_allow_html=True)

    story_map = {
        "1번 문 — 거울의 방": "거울은 네가 보는 순간, 너를 '기억'한다.\n그리고… 기억은 보통, 다시 찾아온다.",
        "2번 문 — 타자기의 방": "타자기엔 리본이 없다.\n그런데도 글자가 찍힌다.\n\n누가 치고 있는 걸까?",
        "3번 문 — 전화기의 방": "통화기록엔 네 번호가 없다.\n그런데도… 네 이름으로 저장돼 있다.",
    }

    st.markdown("<div class='block'>", unsafe_allow_html=True)
    typewriter(story_map.get(st.session_state.room, "문이 열렸다."), speed=typing_speed)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("더 깊이 들어간다"):
        st.session_state.stage = "event"
        st.rerun()

elif st.session_state.stage == "event":
    events = [
        "바닥이 삐걱인다. 네 발소리가… 두 개다.",
        "벽지가 들썩인다. 안쪽에서 뭔가 기어 다닌다.",
        "불이 깜빡인다. 잠깐 꺼졌던 사이… 방 구조가 바뀌었다.",
        "손목에 차가운 손가락이 스친다. 그런데 네 주변엔 아무도 없다.",
    ]

    st.markdown("<div class='block'>", unsafe_allow_html=True)
    typewriter(random.choice(events), speed=typing_speed)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("문 손잡이를 돌린다"):
            st.session_state.stage = "jumpscare"
            st.rerun()
    with col2:
        if st.button("숨을 죽인다"):
            st.session_state.stage = "jumpscare"
            st.rerun()
    with col3:
        if st.button("탈출"):
            st.session_state.stage = "escape"
            st.rerun()

elif st.session_state.stage == "jumpscare":
    # ✅ 글리치 없음 / 점프스케어 후 GAME OVER로 이동
    st.markdown("<div class='block'>", unsafe_allow_html=True)

    if not st.session_state.screamed:
        time.sleep(0.25)  # 짧은 정적
        if JUMPSCARE_IMG.exists():
            st.image(str(JUMPSCARE_IMG), use_container_width=True)
        else:
            st.markdown("### 👁️")
            st.markdown("*(assets/jumpscare.png 가 없어 대체 연출 중)*")

        st.session_state.screamed = True

    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

    # 점프스케어 직후 문구 + 전용 화면으로
    st.markdown(
        """
        <div style="
            margin-top: 10px;
            padding: 16px;
            border-radius: 12px;
            background: rgba(120, 0, 0, 0.22);
            border: 1px solid rgba(255, 80, 80, 0.50);
            text-align: center;
            font-size: 1.15rem;
            font-weight: 800;
        ">
        당신은 죽었습니다.<br>안타깝네요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("GAME OVER 화면으로"):
        st.session_state.stage = "game_over"
        st.rerun()

elif st.session_state.stage == "game_over":
    # ✅ 전용 GAME OVER 화면
    st.markdown(
        """
        <div class="gameover-wrap">
          <div class="gameover-title">GAME OVER</div>
          <div class="gameover-sub">당신은 죽었습니다.</div>
          <div class="gameover-msg">안타깝네요.</div>
          <div style="height:14px;"></div>
          <div class="gameover-msg" style="opacity:0.75;">
            (심장이 두근거리면 잠깐 쉬어도 좋아요.)
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 다시 시작"):
            st.session_state.stage = "intro"
            st.session_state.room = None
            st.session_state.screamed = False
            st.rerun()
    with col2:
        if st.button("🚪 종료(탈출)"):
            st.session_state.stage = "escape"
            st.rerun()

elif st.session_state.stage == "ending":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    typewriter("문이 다시 열린다.\n밖이다.\n\n…정말 밖일까?", speed=typing_speed)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 들어간다(2회차)"):
            st.session_state.stage = "choose_room"
            st.rerun()
    with col2:
        if st.button("완전 탈출"):
            st.session_state.stage = "escape"
            st.rerun()

elif st.session_state.stage == "escape":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("### ✅ 탈출 성공")
    st.markdown("심장이 뛰면 물 한 잔 마시고, 창문을 열어 환기하자.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("처음으로"):
        st.session_state.stage = "intro"
        st.session_state.room = None
        st.session_state.screamed = False
        st.rerun()
