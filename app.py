# app.py
# Streamlit horror text adventure: "루시의 달콤살벌 데이트!"
# Requirements covered:
# - Title screen: pink polka dot, centered cute header, two buttons
# - Stage flow (8 stages): sticky-note message -> choices (1~4) + occasional extra choices
# - Progressively darker atmosphere (CSS based on darkness)
# - Minimal UI: text + buttons + optional images (placeholder ready)
# - Choice buttons disappear after selection (state + rerun)
# - Log: typewriter-ish reveal + stacked lines (max 5)
# - Game over: show jumpscare.png (kept as-is)

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any

import streamlit as st

# ----------------------------
# Helpers: UI + State
# ----------------------------

def init_state():
    ss = st.session_state
    if "scene" not in ss:
        ss.scene = "title"  # title | note | choose | outcome | gameover | ending
    if "stage" not in ss:
        ss.stage = 1
    if "darkness" not in ss:
        ss.darkness = 0  # 0..8
    if "flags" not in ss:
        ss.flags = {
            "checked_door": False,
            "looked_window": False,
            "stayed_home": False,
            "ignored_warnings": 0,
        }
    if "log" not in ss:
        ss.log = []
    if "last_choice" not in ss:
        ss.last_choice = None
    if "stage_choice_locked" not in ss:
        ss.stage_choice_locked = False
    if "pending_text" not in ss:
        ss.pending_text = ""  # for typewriter reveal
    if "gameover_reason" not in ss:
        ss.gameover_reason = ""
    if "ending_key" not in ss:
        ss.ending_key = ""

def push_log(line: str):
    ss = st.session_state
    ss.log.append(line)
    # keep only last 5
    ss.log = ss.log[-5:]

def typewriter(line: str, speed: float = 0.012):
    """Typewriter-like reveal. Keeps the revealed line as one log entry at the end."""
    # Streamlit reruns make "true" typewriter tricky; we do a single-run reveal with placeholder.
    placeholder = st.empty()
    out = ""
    for ch in line:
        out += ch
        placeholder.markdown(f"<div class='log-line'>{escape_html(out)}</div>", unsafe_allow_html=True)
        time.sleep(speed)
    placeholder.empty()
    push_log(line)

def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#039;")
    )

def apply_theme(darkness: int, scene: str):
    """
    darkness: 0 (cute pink) -> 8 (near-black)
    We'll gradually shift background and reduce saturation.
    """
    # clamp
    d = max(0, min(8, int(darkness)))
    # gradient: pink to dark
    # We keep polka dots most visible at low darkness and fade them out.
    bg_base = [
        "#ffe6f3", "#ffd6ee", "#f7c9e6", "#e8b4d4",
        "#c88aa9", "#8a5a70", "#3a2a33", "#141014", "#070607"
    ][d]
    dot_opacity = [0.35, 0.32, 0.28, 0.22, 0.16, 0.10, 0.06, 0.03, 0.02][d]
    text_color = ["#2b1b24", "#2b1b24", "#2b1b24", "#2b1b24", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef"][d]
    card_bg = ["#fff0f8", "#ffe7f4", "#ffe0f0", "#f7d6ea", "#2a2026", "#20171d", "#161017", "#0e0a10", "#0b080d"][d]
    note_bg = ["#ffd9ec", "#ffd0e8", "#ffc4e2", "#ffb9dc", "#3a2a33", "#2a2026", "#20171d", "#161017", "#100b12"][d]
    note_text = ["#2b1b24", "#2b1b24", "#2b1b24", "#2b1b24", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef"][d]

    # Minimal layout container widths
    st.markdown(
        f"""
        <style>
        /* page */
        .stApp {{
          background:
            radial-gradient(circle at 18px 18px, rgba(255,255,255,{dot_opacity}) 2px, transparent 2.5px),
            radial-gradient(circle at 0 0, rgba(255,255,255,{dot_opacity}) 2px, transparent 2.5px),
            {bg_base};
          background-size: 36px 36px;
          color: {text_color};
        }}

        /* center main */
        section.main > div {{
          max-width: 780px;
          padding-top: 32px;
        }}

        /* title */
        .title-wrap {{
          text-align: center;
          margin-top: 10px;
          margin-bottom: 18px;
        }}
        .title {{
          font-size: 42px;
          font-weight: 800;
          letter-spacing: -0.5px;
          line-height: 1.1;
        }}
        .subtitle {{
          margin-top: 8px;
          opacity: 0.9;
          font-size: 14px;
        }}

        /* log */
        .log-box {{
          border-radius: 16px;
          padding: 14px 16px;
          background: rgba(0,0,0,0.12);
          backdrop-filter: blur(6px);
          margin: 14px 0 10px 0;
        }}
        .log-line {{
          font-size: 16px;
          line-height: 1.5;
          margin: 2px 0;
          color: {text_color};
          white-space: pre-wrap;
        }}

        /* sticky note */
        .note {{
          background: {note_bg};
          color: {note_text};
          border-radius: 14px;
          padding: 18px 18px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.18);
          transform: rotate(-0.4deg);
          margin: 10px 0 12px 0;
          border: 1px solid rgba(255,255,255,0.18);
        }}
        .note p {{
          margin: 0;
          font-size: 17px;
          line-height: 1.6;
          white-space: pre-wrap;
        }}

        /* card */
        .card {{
          background: {card_bg};
          border-radius: 16px;
          padding: 14px 14px;
          border: 1px solid rgba(255,255,255,0.14);
          box-shadow: 0 8px 22px rgba(0,0,0,0.16);
        }}
        .muted {{
          opacity: 0.82;
          font-size: 13px;
        }}

        /* buttons */
        div.stButton > button {{
          width: 100%;
          border-radius: 14px;
          padding: 12px 12px;
          font-weight: 700;
          border: 1px solid rgba(255,255,255,0.18);
        }}

        /* remove extra padding top in some scenes */
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_log():
    ss = st.session_state
    lines = ss.log[-5:]
    html = "<div class='log-box'>" + "".join(
        [f"<div class='log-line'>{escape_html(l)}</div>" for l in lines]
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)

def stage_asset_path(stage: int, option_idx: int) -> str:
    # Optional: place images like assets/stage1_1.png etc.
    return os.path.join("assets", f"stage{stage}_{option_idx}.png")

# ----------------------------
# Story Data
# ----------------------------

@dataclass
class Option:
    key: str
    label: str
    outcome: str
    darkness_delta: int = 0
    set_flag: Optional[Callable[[Dict[str, Any]], None]] = None
    add_ignore: int = 0
    game_over: bool = False
    game_over_reason: str = ""

@dataclass
class Stage:
    stage_num: int
    note_text: str
    prompt: str
    options: List[Option] = field(default_factory=list)
    extra_note_flash: Optional[str] = None
    extra_choices: Optional[List[Option]] = None  # shown above outfit options (stage >=2)
    # If stage has special logic when arriving:
    on_enter: Optional[Callable[[Dict[str, Any]], None]] = None

def make_stages() -> Dict[int, Stage]:
    def flag_checked_door(flags): flags["checked_door"] = True
    def flag_looked_window(flags): flags["looked_window"] = True
    def flag_stayed_home(flags): flags["stayed_home"] = True

    stages: Dict[int, Stage] = {}

    stages[1] = Stage(
        1,
        note_text="안녕! 오늘은 정말 중요한 날이야 💕\n데이트 준비를 도와줄래?\n먼저 옷부터 골라보자!",
        prompt="오늘은 테니스를 치러 갈 거니까 🎾\n스포티하면서도 귀여운 룩으로 부탁해!",
        options=[
            Option("1", "1번: 스포티 핑크 셋업", "꺄! 이거 완전 내 스타일이야 💗", darkness_delta=0),
            Option("2", "2번: 화이트 테니스 원피스", "깔끔하고 예쁘다… 오늘은 이걸로 😊", darkness_delta=0),
            Option("3", "3번: 블랙 트랙수트", "음… 조금 강해 보이지만, 괜찮겠지?", darkness_delta=1, add_ignore=1),
            Option("4", "4번: 두꺼운 후드 + 모자", "뭔가 숨기고 싶을 때 입는 옷 같아…", darkness_delta=1, add_ignore=1),
        ],
    )

    stages[2] = Stage(
        2,
        note_text="생각해보니까…\n약속 시간보다 조금 일찍 준비해도 괜찮겠지? 😊\n오늘은 왠지 기분이 좋아.",
        prompt="가벼운 아우터를 입을까 말까 고민 중이야!",
        extra_note_flash="현관 쪽에서… 소리가 난 것 같았어.",
        extra_choices=[
            Option("door_peek", "문을 확인한다", "잠깐… 문고리가 차갑네. 그래도 닫혀 있어.", darkness_delta=1, set_flag=flag_checked_door),
            Option("ignore", "무시한다", "착각이겠지. 귀찮아…", darkness_delta=1, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 리본 달린 바람막이", "귀엽다! 바람이 불어도 괜찮겠어 🎀", darkness_delta=0),
            Option("2", "2번: 가디건 + 테니스 스커트", "따뜻하고 예쁘네. 좋아!", darkness_delta=0),
            Option("3", "3번: 얇은 재킷", "조금… 무겁다. 그래도 입을까?", darkness_delta=1),
            Option("4", "4번: 아우터 안 입기", "괜찮아. 나갈 때만… 빨리 나가면 돼.", darkness_delta=1, add_ignore=1),
        ],
    )

    stages[3] = Stage(
        3,
        note_text="방금 말한 소리 말이야…\n아마 착각이겠지? 😅\n그래도 옷은 제대로 골라야지!",
        prompt="치마가 좋을까? 반바지가 좋을까?",
        extra_choices=[
            Option("door_check", "문을 다시 잠근다", "잠금 소리가 크게 울렸어. 너무 크게…", darkness_delta=1, set_flag=flag_checked_door),
            Option("ignore", "무시하고 고른다", "응. 아무 일도 없을 거야.", darkness_delta=1, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 플리츠 스커트", "움직이기 편하고 귀여워! 💕", darkness_delta=0),
            Option("2", "2번: 테니스 반바지", "가볍고 좋아. 뛰기 딱이야!", darkness_delta=0),
            Option("3", "3번: 너무 긴 스커트", "발목이… 걸릴 것 같아. 괜찮겠지?", darkness_delta=1),
            Option("4", "4번: 이상하게 젖은 옷", "…이 옷, 왜 축축하지?", darkness_delta=2, add_ignore=1),
        ],
    )

    stages[4] = Stage(
        4,
        note_text="아까 문 말이야…\n분명 닫아놨던 것 같은데 🤔\n뭐, 상관없겠지?",
        prompt="오늘 기분에 맞는 색을 골라줘.",
        extra_choices=[
            Option("listen", "문 쪽에 귀를 댄다", "…무슨 소리도 안 나. 너무 조용해.", darkness_delta=2),
            Option("ignore", "무시한다", "응. 귀찮아…", darkness_delta=1, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 핑크 포인트", "역시 핑크지! 오늘은 완벽해 💗", darkness_delta=0),
            Option("2", "2번: 화이트 톤", "깨끗해. 마음이 편해져.", darkness_delta=0),
            Option("3", "3번: 블랙 포인트", "…왜 갑자기 어두운 색이 끌리지?", darkness_delta=1),
            Option("4", "4번: 색이 바랜 옷", "이 옷… 예전부터 있던 건가? 기억이 안 나.", darkness_delta=2, add_ignore=1),
        ],
    )

    stages[5] = Stage(
        5,
        note_text="창문 쪽이 조금… 이상해.\n커튼을 닫아둘까?",
        prompt="액세서리를 고를까? (가벼운 것만!)",
        extra_choices=[
            Option("window", "창문을 본다", "유리 너머로… 뭔가가 지나간 것 같아.", darkness_delta=2, set_flag=flag_looked_window),
            Option("curtain", "커튼을 닫는다", "커튼이 닫히는 소리가, 너무 크게 들려.", darkness_delta=1),
            Option("ignore", "무시한다", "괜찮아. 괜찮아…", darkness_delta=2, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 하트 헤어핀", "귀엽지? 오늘은 내 날이야 💕", darkness_delta=0),
            Option("2", "2번: 테니스 캡", "스포티! 햇빛도 가려주고 좋아.", darkness_delta=0),
            Option("3", "3번: 목을 가리는 초커", "목이… 시려. 왜지?", darkness_delta=2),
            Option("4", "4번: 아무것도 안 한다", "꾸미는 게… 의미가 있을까?", darkness_delta=2, add_ignore=1),
        ],
    )

    stages[6] = Stage(
        6,
        note_text="…\n그냥 집에 있으면 안 될까?\n네가 정해줘.",
        prompt="나갈까? 말까?",
        extra_choices=[
            Option("go_out", "그래도 나간다", "응… 약속은 약속이니까.", darkness_delta=2),
            Option("stay", "집에 남아 있는다", "문을 다시 잠그자. 숨을 크게 쉬자.", darkness_delta=2, set_flag=flag_stayed_home),
        ],
        options=[
            Option("1", "1번: 편한 운동화", "…도망치기 좋겠네.", darkness_delta=2),
            Option("2", "2번: 끈이 많은 신발", "끈이… 자꾸 풀릴 것 같아.", darkness_delta=2, add_ignore=1),
            Option("3", "3번: 너무 작은 신발", "발이 아파. 그래도 참아야 해?", darkness_delta=2, add_ignore=1),
            Option("4", "4번: 맨발", "발소리를… 줄이면 되는 거지?", darkness_delta=3, add_ignore=1),
        ],
    )

    stages[7] = Stage(
        7,
        note_text="방 안에\n다른 숨소리가 있어.",
        prompt="이제 선택은… 옷이 아니야.",
        extra_choices=[
            Option("open", "문을 연다", "문이 열리는 순간, 공기가 바뀐다.", game_over=True, game_over_reason="문 밖에서 누군가 웃고 있었어.", darkness_delta=3),
            Option("lights", "불을 끈다", "깜깜해지자… 더 가까워진다.", game_over=True, game_over_reason="어둠 속에서 네 이름을 불렀어.", darkness_delta=3),
            Option("lock", "문을 잠근다", "딸깍. 하지만 잠금이… 믿음직하지 않아.", darkness_delta=3),
            Option("hold", "숨을 죽인다", "…(숨소리만 남는다)", darkness_delta=2),
        ],
        options=[
            Option("1", "1번: (아무것도) 고르지 않는다", "너무 조용해. 너무…", darkness_delta=2),
            Option("2", "2번: (아무것도) 고르지 않는다", "시간이… 늘어난다.", darkness_delta=2),
            Option("3", "3번: (아무것도) 고르지 않는다", "심장이 시끄럽다.", darkness_delta=2),
            Option("4", "4번: (아무것도) 고르지 않는다", "문고리가… 돌아간다.", darkness_delta=3, add_ignore=1),
        ],
    )

    stages[8] = Stage(
        8,
        note_text="마지막이야.\n끝을 고르자.",
        prompt="루시는… 어디로 가야 할까?",
        extra_choices=[
            Option("end_a", "커튼 뒤에 숨는다", "조용히… 숨을 참는다.", darkness_delta=0),
            Option("end_b", "그대로 나간다", "밖은 조용했다. 너무 조용했다.", darkness_delta=0),
            Option("end_c", "문을 바라본다", "문은… 이미 열려 있었다.", darkness_delta=0),
        ],
        options=[
            Option("1", "1번: (엔딩으로 간다)", "…", darkness_delta=0),
            Option("2", "2번: (엔딩으로 간다)", "…", darkness_delta=0),
            Option("3", "3번: (엔딩으로 간다)", "…", darkness_delta=0),
            Option("4", "4번: (엔딩으로 간다)", "…", darkness_delta=0),
        ],
    )

    return stages

STAGES = make_stages()

# ----------------------------
# Game Flow
# ----------------------------

def reset_game():
    ss = st.session_state
    ss.scene = "title"
    ss.stage = 1
    ss.darkness = 0
    ss.flags = {"checked_door": False, "looked_window": False, "stayed_home": False, "ignored_warnings": 0}
    ss.log = []
    ss.last_choice = None
    ss.stage_choice_locked = False
    ss.pending_text = ""
    ss.gameover_reason = ""
    ss.ending_key = ""

def go_to(scene: str):
    st.session_state.scene = scene
    st.rerun()

def apply_option(option: Option):
    ss = st.session_state
    # apply flags
    if option.set_flag is not None:
        option.set_flag(ss.flags)
    if option.add_ignore:
        ss.flags["ignored_warnings"] += option.add_ignore
    ss.darkness = min(8, ss.darkness + option.darkness_delta)

    ss.last_choice = option.label
    # outcome into log with typewriter
    typewriter(option.outcome, speed=0.010 if ss.darkness < 5 else 0.007)

    # handle game over
    if option.game_over:
        ss.gameover_reason = option.game_over_reason or "…"
        ss.scene = "gameover"
        st.rerun()

def choose_outfit(stage: Stage):
    ss = st.session_state

    # Optional extra choices (above outfit choices)
    if stage.extra_choices:
        st.markdown("<div class='card'><div class='muted'>…선택지가 하나 더 생겼다.</div></div>", unsafe_allow_html=True)
        cols = st.columns(len(stage.extra_choices))
        for i, opt in enumerate(stage.extra_choices):
            with cols[i]:
                # Only show if not locked
                if not ss.stage_choice_locked and st.button(opt.label, key=f"extra_{stage.stage_num}_{opt.key}"):
                    ss.stage_choice_locked = True
                    apply_option(opt)
                    # after outcome, return to choose screen to pick outfit
                    ss.stage_choice_locked = False
                    st.rerun()

        st.markdown("")

    # Outfit prompt
    st.markdown(f"<div class='card'><div class='muted'>{escape_html(stage.prompt)}</div></div>", unsafe_allow_html=True)
    st.markdown("")

    # Outfit options 1..4
    cols = st.columns(2)
    option_cols = [cols[0], cols[1], cols[0], cols[1]]
    for idx, opt in enumerate(stage.options, start=1):
        with option_cols[idx - 1]:
            # Optional image if present
            path = stage_asset_path(stage.stage_num, idx)
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            else:
                # placeholder block
                st.markdown(
                    f"<div class='card'><div style='font-weight:800;'>선택 {idx}</div>"
                    f"<div class='muted'>이미지 자리: assets/stage{stage.stage_num}_{idx}.png</div></div>",
                    unsafe_allow_html=True,
                )
            if not ss.stage_choice_locked:
                if st.button(opt.label, key=f"opt_{stage.stage_num}_{opt.key}"):
                    ss.stage_choice_locked = True
                    apply_option(opt)
                    ss.scene = "outcome"
                    st.rerun()

def compute_ending() -> str:
    flags = st.session_state.flags
    ignored = flags.get("ignored_warnings", 0)
    stayed = flags.get("stayed_home", False)

    # Simple ending logic (tweakable)
    if ignored <= 1 and stayed:
        return "A"  # 조심 + 숨기기
    if ignored >= 4:
        return "C"  # 위험 누적
    return "B"      # 무난하지만 찝찝

def render_title():
    st.markdown(
        """
        <div class="title-wrap">
          <div class="title">루시의 달콤살벌 데이트! 💗</div>
          <div class="subtitle">핑크는 언제나 안전…하다고 믿고 싶지?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💗 데이트 준비 시작하기", key="start_btn"):
            push_log("루시: 안녕! 오늘은 정말 중요한 날이야 💕")
            st.session_state.scene = "note"
            st.session_state.stage = 1
            st.rerun()
    with c2:
        if st.button("❌ 종료하고 나가기", key="exit_btn"):
            st.markdown("<div class='card'>안녕… 다음에 또 놀자 💗</div>", unsafe_allow_html=True)
            st.stop()

def render_note(stage: Stage):
    # flash note line as extra (shows only on note screen)
    flash = ""
    if stage.extra_note_flash and st.session_state.stage >= 2:
        flash = f"\n\n(잠깐) {stage.extra_note_flash}"

    st.markdown(
        f"<div class='note'><p>{escape_html(stage.note_text + flash)}</p></div>",
        unsafe_allow_html=True,
    )

    render_log()

    if st.button("다음으로", key=f"to_choose_{stage.stage_num}"):
        st.session_state.scene = "choose"
        st.rerun()

def render_choose(stage: Stage):
    render_log()
    choose_outfit(stage)

def render_outcome(stage: Stage):
    # After choosing outfit, allow next stage
    render_log()

    if stage.stage_num < 8:
        if st.button("다음 스테이지", key=f"next_stage_{stage.stage_num}"):
            st.session_state.stage += 1
            st.session_state.scene = "note"
            st.session_state.stage_choice_locked = False
            st.rerun()
    else:
        # go to ending
        st.session_state.ending_key = compute_ending()
        st.session_state.scene = "ending"
        st.rerun()

def render_gameover():
    st.markdown("<div class='title-wrap'><div class='title'>…</div></div>", unsafe_allow_html=True)
    render_log()

    # jumpscare
    if os.path.exists("jumpscare.png"):
        st.image("jumpscare.png", use_container_width=True)
    else:
        st.markdown("<div class='card'>jumpscare.png 파일이 폴더에 없어요.</div>", unsafe_allow_html=True)

    reason = st.session_state.gameover_reason or "끝."
    st.markdown(f"<div class='card'><div style='font-weight:800;'>GAME OVER</div><div class='muted'>{escape_html(reason)}</div></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("처음으로", key="go_title"):
            reset_game()
            st.rerun()
    with c2:
        if st.button("다시 도전", key="retry"):
            # retry from stage 1 but keep title scene?
            st.session_state.scene = "note"
            st.session_state.stage = 1
            st.session_state.darkness = 0
            st.session_state.flags = {"checked_door": False, "looked_window": False, "stayed_home": False, "ignored_warnings": 0}
            st.session_state.log = []
            push_log("루시: …다시 시작하자.")
            st.rerun()

def render_ending():
    key = st.session_state.ending_key or "B"
    render_log()

    if key == "A":
        text = "루시는 결국 약속에 가지 않았다.\n밖은 조용했다.\n너무 조용했다."
        title = "ENDING A"
    elif key == "C":
        text = "루시는 옷을 다 골랐다.\n이제… 숨을 곳이 없다."
        title = "ENDING C"
    else:
        text = "“왜 계속 못 들은 척했어?”\n게임이 여기서 끝난다."
        title = "ENDING B"

    st.markdown(
        f"<div class='card'><div style='font-weight:900; font-size:22px;'>{title}</div>"
        f"<div style='margin-top:10px; white-space:pre-wrap;'>{escape_html(text)}</div></div>",
        unsafe_allow_html=True,
    )

    if st.button("처음 화면으로", key="end_to_title"):
        reset_game()
        st.rerun()

# ----------------------------
# App Entry
# ----------------------------

st.set_page_config(page_title="루시의 달콤살벌 데이트!", page_icon="💗", layout="centered")

init_state()
apply_theme(st.session_state.darkness, st.session_state.scene)

# Title / Scene router
scene = st.session_state.scene
stage_num = st.session_state.stage
stage = STAGES.get(stage_num, STAGES[1])

if scene == "title":
    render_title()

elif scene == "note":
    # On stage enter: add a subtle log line only once per stage note entry
    st.markdown("<div class='title-wrap'><div class='title'>💗</div></div>", unsafe_allow_html=True)
    render_note(stage)

elif scene == "choose":
    st.markdown("<div class='title-wrap'><div class='title'>옷장 열기…</div></div>", unsafe_allow_html=True)
    render_choose(stage)

elif scene == "outcome":
    st.markdown("<div class='title-wrap'><div class='title'>…</div></div>", unsafe_allow_html=True)
    render_outcome(stage)

elif scene == "gameover":
    render_gameover()

elif scene == "ending":
    render_ending()

else:
    # fallback
    reset_game()
    st.rerun()
