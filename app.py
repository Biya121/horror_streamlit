import streamlit as st
import time
from pathlib import Path

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="금지된 방",
    page_icon="🕯️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ASSETS = Path(__file__).parent / "assets"
JUMPSCARE_IMG = ASSETS / "jumpscare.png"

# =========================
# 스타일 (완전 블랙)
# =========================
st.markdown("""
<style>
header, footer, .stDecoration {display:none;}
.stApp { background-color: #000000; color: #ffffff; }

.typing {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 1.05rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

button {
  background-color: #000000 !important;
  color: #ffffff !important;
  border: 1px solid #444444 !important;
  border-radius: 6px !important;
}
button:hover {
  border-color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 상태 초기화
# =========================
if "stage" not in st.session_state:
    st.session_state.stage = "intro"
if "lines" not in st.session_state:
    st.session_state.lines = []
if "room_count" not in st.session_state:
    st.session_state.room_count = 0
if "dead" not in st.session_state:
    st.session_state.dead = False


# =========================
# 유틸
# =========================
def type_line(text, speed=0.03):
    """한 줄 타이핑 후 누적 (최대 5줄)"""
    box = st.empty()
    current = ""
    for ch in text:
        current += ch
        box.markdown(
            "<div class='typing'>" + "<br>".join(st.session_state.lines + [current]) + "</div>",
            unsafe_allow_html=True
        )
        time.sleep(speed)

    st.session_state.lines.append(text)
    if len(st.session_state.lines) > 5:
        st.session_state.lines.pop(0)


def clear_and_rerun(next_stage):
    st.session_state.stage = next_stage
    st.rerun()


# =========================
# 화면 렌더
# =========================
st.markdown("<div class='typing'>" + "<br>".join(st.session_state.lines) + "</div>", unsafe_allow_html=True)
st.write("")

# =========================
# INTRO
# =========================
if st.session_state.stage == "intro":
    type_line("문이 닫혔다.")
    type_line("잠금장치는 안쪽에 있다.")
    type_line("이 집은, 선택을 기억한다.")

    if st.button("계속"):
        clear_and_rerun("choose")

# =========================
# 방 선택
# =========================
elif st.session_state.stage == "choose":
    type_line("세 개의 방이 있다.")
    type_line("한 번 들어간 방은, 너를 평가한다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("거울의 방"):
            clear_and_rerun("mirror")
    with col2:
        if st.button("피의 방"):
            clear_and_rerun("blood")
    with col3:
        if st.button("어둠의 방"):
            clear_and_rerun("dark")

# =========================
# 거울의 방
# =========================
elif st.session_state.stage == "mirror":
    type_line("거울 앞에 섰다.")
    type_line("너의 움직임이, 아주 조금 늦게 따라온다.")
    type_line("눈을 깜빡였는데, 거울 속은 아직이다.")

    if st.button("눈을 마주친다"):
        clear_and_rerun("judge")

# =========================
# 피의 방
# =========================
elif st.session_state.stage == "blood":
    type_line("바닥이 끈적하다.")
    type_line("마르지 않은 피가, 숨 쉬듯 움직인다.")
    type_line("이 방은 이미 값을 받았다.")

    if st.button("뒤돌아선다"):
        clear_and_rerun("judge")

# =========================
# 어둠의 방
# =========================
elif st.session_state.stage == "dark":
    type_line("아무것도 보이지 않는다.")
    type_line("하지만, 네가 보인다는 건 느껴진다.")
    type_line("여긴 숨는 곳이 아니다.")

    if st.button("한 발 내딛는다"):
        clear_and_rerun("judge")

# =========================
# 판정
# =========================
elif st.session_state.stage == "judge":
    type_line("집이 판단하고 있다.")
    type_line("네 선택은 충분히 솔직했다.")

    if st.button("다음"):
        clear_and_rerun("end")

# =========================
# 엔딩 + 점프스케어
# =========================
elif st.session_state.stage == "end":
    type_line("이 집은 약속을 지킨다.")
    type_line("이제, 너의 차례다.")

    time.sleep(0.4)

    if JUMPSCARE_IMG.exists():
        st.image(str(JUMPSCARE_IMG), use_container_width=True)

    st.markdown("""
    <div style="text-align:center; margin-top:16px;">
    GAME OVER<br>당신은 선택했다.
    </div>
    """, unsafe_allow_html=True)
