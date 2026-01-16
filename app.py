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


# =========================
# 유틸
# =========================
def reset_game():
    st.session_state.stage = "intro"
    st.session_state.room = None
    st.session_state.screamed = False
    # 텍스트 연출 재생 여부 플래그들 초기화
    st.session_state.played = {}


def ensure_state():
    if "stage" not in st.session_state:
        st.session_state.stage = "intro"
    if "room" not in st.session_state:
        st.session_state.room = None
    if "screamed" not in st.session_state:
        st.session_state.screamed = False
    if "played" not in st.session_state:
        st.session_state.played = {}


def play_once(key: str) -> bool:
    """해당 stage에서 텍스트 시퀀스를 한 번만 재생하기 위한 플래그"""
    if st.session_state.played.get(key, False):
        return False
    st.session_state.played[key] = True
    return True


def fade_sequence(lines, hold=1.7, fade=1.4, gap=0.25):
    """
    lines: 출력할 문자열 리스트
    각 줄이 나타났다 -> 서서히 사라짐 -> 완전히 사라진 뒤 다음 줄 표시
    """
    box = st.empty()
    total = hold + fade

    for line in lines:
        # CSS 애니메이션(duration = total)로 자동 fade out
        html = f"""
        <div class="fade-line" style="animation-duration:{total}s;">
            {line.replace("\n","<br>")}
        </div>
        """
        box.markdown(html, unsafe_allow_html=True)
        time.sleep(total + gap)
        box.empty()


# =========================
# 스타일(CSS)
# =========================
st.markdown(
    """
<style>
.stApp {
  background: radial-gradient(circle at 20% 20%, #141414 0%, #060606 55%, #000 100%);
  color: #e6e6e6;
}
h1, h2, h3 { letter-spacing: 0.5px; }

/* 카드 */
.block {
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  padding: 18px 18px;
  border-radius: 14px;
  box-shadow: 0 10px 35px rgba(0,0,0,0.35);
}

/* 경고 */
.warn { color:#ff6b6b; font-weight:800; }

/* 버튼 */
.stButton>button{
  width:100%;
  border-radius:12px;
  border:1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color:#f1f1f1;
}
.stButton>button:hover{
  border:1px solid rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.10);
}

/* 페이드 텍스트 */
@keyframes fadeOutSlow {
  0%   { opacity: 0; transform: translateY(2px); }
  8%   { opacity: 1; transform: translateY(0); }
  70%  { opacity: 1; }
  100% { opacity: 0; }
}
.fade-line{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 1.07rem;
  line-height: 1.65;
  white-space: pre-wrap;
  animation-name: fadeOutSlow;
  animation-timing-function: ease-in-out;
}

/* GAME OVER 빨간 깜빡임 */
@keyframes redFlicker {
  0%   { box-shadow: 0 0 0 rgba(255,0,0,0.0); filter: brightness(1); }
  20%  { box-shadow: 0 0 40px rgba(255,0,0,0.25); filter: brightness(1.08); }
  40%  { box-shadow: 0 0 10px rgba(255,0,0,0.10); filter: brightness(1.00); }
  60%  { box-shadow: 0 0 50px rgba(255,0,0,0.32); filter: brightness(1.10); }
  80%  { box-shadow: 0 0 14px rgba(255,0,0,0.12); filter: brightness(1.02); }
  100% { box-shadow: 0 0 0 rgba(255,0,0,0.0); filter: brightness(1); }
}
.gameover {
  margin-top: 14px;
  padding: 18px;
  border-radius: 14px;
  border: 1px solid rgba(255, 80, 80, 0.55);
  background: rgba(120, 0, 0, 0.22);
  text-align: center;
  animation: redFlicker 1.1s infinite;
}
.gameover .title{
  font-size: 2.0rem;
  font-weight: 950;
  letter-spacing: 2px;
  color: #ff4d4d;
  margin-bottom: 6px;
}
.gameover .msg{
  font-size: 1.15rem;
  font-weight: 850;
  line-height: 1.55;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# 상태 초기화
# =========================
ensure_state()

# =========================
# 옵션(사이드바)
# =========================
with st.sidebar:
    st.markdown("### 설정")
    sound_on = st.toggle("🔊 사운드 켜기", value=True)
    fast_mode = st.toggle("⚡ 빠른 연출", value=False)

# 페이드 속도(빠른 모드면 조금 더 빠르게)
HOLD = 1.2 if fast_mode else 1.7
FADE = 1.0 if fast_mode else 1.4
GAP = 0.15 if fast_mode else 0.25

st.title("🕯️ 금지된 방")

# =========================
# 스테이지: INTRO
# =========================
if st.session_state.stage == "intro":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("**이 페이지는 공포 연출(스토리/이미지/사운드)입니다.**")
    st.markdown("불편하면 언제든지 **탈출**을 누르세요.")
    st.markdown("<span class='warn'>※ 점프스케어가 있습니다.</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("들어간다"):
            st.session_state.stage = "warning"
            st.rerun()
    with col2:
        if st.button("나간다(안전)"):
            st.stop()

# =========================
# 스테이지: WARNING (페이드 시퀀스)
# =========================
elif st.session_state.stage == "warning":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown(" ")  # 여백용
    st.markdown("</div>", unsafe_allow_html=True)

    # 사운드(선택)
    if sound_on and WHISPER_AUDIO.exists():
        st.audio(str(WHISPER_AUDIO), autoplay=True)

    if play_once("warning_seq"):
        lines = [
            "문고리가… 돌아가지 않는다.",
            "잠금장치가 ‘딱’ 하고 고정되는 소리.",
            "방 안은 조용한데…",
            "…너 말고 다른 숨소리가 있다.",
            "가까워진다.",
        ]
        fade_sequence(lines, hold=HOLD, fade=FADE, gap=GAP)

    if st.button("주위를 둘러본다"):
        st.session_state.stage = "choose_room"
        st.rerun()

# =========================
# 스테이지: 방 선택 (옵션만)
# =========================
elif st.session_state.stage == "choose_room":
    rooms = [
        "1번 문 — 거울의 방",
        "2번 문 — 타자기의 방",
        "3번 문 — 전화기의 방",
    ]

    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("세 개의 문이 있다.")
    st.markdown("어느 쪽이든… 돌아올 수 있다는 보장은 없다.")
    st.markdown("</div>", unsafe_allow_html=True)

    choice = st.radio("문을 선택해.", rooms, index=0)

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

# =========================
# 스테이지: STORY (방별 긴장감 대본 + 페이드 시퀀스)
# =========================
elif st.session_state.stage == "story":
    room = st.session_state.room or "문"

    scripts = {
        "1번 문 — 거울의 방": [
            "거울이 네 모습을 담는다.",
            "처음엔 정상이다.",
            "…하지만 다음 순간, 거울 속 네가 조금 늦게 따라 한다.",
            "눈을 깜빡였는데 거울 속은 아직 뜨고 있다.",
            "거울 속 네가 입술을 움직인다.",
            "소리는 없는데, 의미는 분명하다.",
            "‘여기… 들어오지 마.’",
        ],
        "2번 문 — 타자기의 방": [
            "낡은 타자기가 책상 위에 있다.",
            "리본도 없고, 잉크도 없다.",
            "그런데도… 자판이 혼자 내려간다.",
            "딱. 딱. 딱.",
            "종이에 글자가 찍힌다.",
            "‘문을 닫아.’",
            "…너는 아직 문을 닫지 않았다.",
        ],
        "3번 문 — 전화기의 방": [
            "전화기가 울린다. 너무 오래된 벨소리.",
            "수화기를 들자, 잡음 뒤로 익숙한 목소리.",
            "…너의 목소리다.",
            "‘지금 내 말 들어.’",
            "‘절대로 뒤돌아보지 마.’",
            "‘그리고… 숨 쉬지 마.’",
        ],
    }

    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown(f"**{room}**")
    st.markdown("</div>", unsafe_allow_html=True)

    seq_key = f"story_seq_{room}"
    if play_once(seq_key):
        fade_sequence(scripts.get(room, ["문이 열렸다."]), hold=HOLD, fade=FADE, gap=GAP)

    if st.button("더 깊이 들어간다"):
        st.session_state.stage = "event"
        st.rerun()

# =========================
# 스테이지: EVENT (랜덤 긴장 이벤트 + 페이드 시퀀스)
# =========================
elif st.session_state.stage == "event":
    room = st.session_state.room or ""
    # 방별로 더 맞는 이벤트가 섞이도록 가중치 느낌으로 리스트 구성
    base_events = [
        "발밑에서 아주 미세하게 진동이 느껴진다.",
        "전등이 꺼졌다 켜진다. 꺼진 동안… 누가 바로 앞에 있었던 것 같다.",
        "숨을 들이마시는 순간, 누가 동시에 들이마신다.",
        "방의 공기가 갑자기 차가워진다. 손가락 끝부터 감각이 흐려진다.",
        "너의 이름을 부르는 소리가 들린다. 가까운 곳에서… 아주 가까운 곳에서.",
    ]
    mirror_events = [
        "거울에 네 등 뒤가 비친다. 그런데 너는 아직 등 뒤를 보지 않았다.",
        "거울 속 네가 손을 든다. 너는 손을 들지 않았다.",
        "거울 표면 안쪽에서 손바닥 자국이 ‘툭’ 하고 튀어나온다.",
    ]
    type_events = [
        "타자기 종이가 스스로 말려 올라간다. 새 종이가 끼워진다.",
        "딱. 딱. 딱. 자판 소리가 네 심장 박자와 맞춰진다.",
        "종이에 새 문장이 찍힌다. ‘너는 이미 늦었어.’",
    ]
    phone_events = [
        "전화선이 없다. 그런데 수화기에서 숨소리가 더 선명해진다.",
        "상대가 말한다. ‘너 지금… 나랑 같은 방에 있어.’",
        "뚝— 끊겼는데도, 통화 중 표시가 꺼지지 않는다.",
    ]

    events = base_events[:]
    if "거울" in room:
        events += mirror_events
    elif "타자기" in room:
        events += type_events
    elif "전화기" in room:
        events += phone_events

    chosen = random.choice(events)

    if play_once("event_seq"):
        fade_sequence(
            [
                chosen,
                "…문 손잡이를 잡는 순간, 손잡이가 먼저 ‘잡는다’.",
                "손이 빠지지 않는다.",
            ],
            hold=HOLD,
            fade=FADE,
            gap=GAP,
        )

    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("문을 당긴다"):
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

# =========================
# 스테이지: JUMPSCARE (이미지 + 빨간 깜빡임 + 버튼 누르면 처음으로)
# =========================
elif st.session_state.stage == "jumpscare":
    st.markdown("<div class='block'>", unsafe_allow_html=True)

    # 점프스케어는 1회만 표시
    if not st.session_state.screamed:
        time.sleep(0.2)
        if JUMPSCARE_IMG.exists():
            st.image(str(JUMPSCARE_IMG), use_container_width=True)
        else:
            st.markdown("### 👁️")
            st.markdown("*(assets/jumpscare.png 가 없어 대체 연출 중)*")
        st.session_state.screamed = True

    st.markdown("</div>", unsafe_allow_html=True)

    # GAME OVER 느낌(빨간 깜빡임)
    st.markdown(
        """
        <div class="gameover">
          <div class="title">GAME OVER</div>
          <div class="msg">당신은 죽었습니다.<br>안타깝네요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음으로 돌아가기"):
            reset_game()
            st.rerun()
    with col2:
        if st.button("종료(탈출)"):
            st.session_state.stage = "escape"
            st.rerun()

# =========================
# 스테이지: ESCAPE
# =========================
elif st.session_state.stage == "escape":
    st.markdown("<div class='block'>", unsafe_allow_html=True)
    st.markdown("### ✅ 탈출 성공")
    st.markdown("조금 불편했다면 물 한 잔 마시고, 눈을 쉬게 해줘.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("처음으로"):
        reset_game()
        st.rerun()
