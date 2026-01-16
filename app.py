# app.py
# "루시의 달콤살벌 데이트!" - Streamlit Horror Text Adventure
#
# Changes in this version:
# 1) Stage-specific ominous banner text (not统一).
# 2) If extra (ominous) choices + outfit choices appear together, user must choose BOTH before proceeding.
#    - We store both selections, then show ONE combined outcome screen.
# 3) When atmosphere is dark, button font color becomes RED for readability.

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any

import streamlit as st


# ----------------------------
# State
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

    # For combined selection flow (extra + outfit)
    if "picked_extra" not in ss:
        ss.picked_extra = None  # Option or None
    if "picked_outfit" not in ss:
        ss.picked_outfit = None  # Option or None

    if "last_outcome" not in ss:
        ss.last_outcome = ""  # string shown on outcome scene only
    if "gameover_reason" not in ss:
        ss.gameover_reason = ""
    if "ending_key" not in ss:
        ss.ending_key = ""


def reset_game():
    ss = st.session_state
    ss.scene = "title"
    ss.stage = 1
    ss.darkness = 0
    ss.flags = {
        "checked_door": False,
        "looked_window": False,
        "stayed_home": False,
        "ignored_warnings": 0,
    }
    ss.picked_extra = None
    ss.picked_outfit = None
    ss.last_outcome = ""
    ss.gameover_reason = ""
    ss.ending_key = ""


def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#039;")
    )


# ----------------------------
# Theme
# ----------------------------

def apply_theme(darkness: int):
    d = max(0, min(8, int(darkness)))

    bg_base = [
        "#ffe6f3", "#ffd6ee", "#f7c9e6", "#e8b4d4",
        "#c88aa9", "#8a5a70", "#3a2a33", "#141014", "#070607"
    ][d]
    dot_opacity = [0.35, 0.32, 0.28, 0.22, 0.16, 0.10, 0.06, 0.03, 0.02][d]
    text_color = ["#2b1b24", "#2b1b24", "#2b1b24", "#2b1b24", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef"][d]
    card_bg = ["#fff0f8", "#ffe7f4", "#ffe0f0", "#f7d6ea", "#2a2026", "#20171d", "#161017", "#0e0a10", "#0b080d"][d]
    note_bg = ["#ffd9ec", "#ffd0e8", "#ffc4e2", "#ffb9dc", "#3a2a33", "#2a2026", "#20171d", "#161017", "#100b12"][d]
    note_text = ["#2b1b24", "#2b1b24", "#2b1b24", "#2b1b24", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef", "#f2e9ef"][d]

    # (3) Button text color rule:
    # When dark enough, use RED text for readability.
    button_text = "#2b1b24" if d < 5 else "#ff2a2a"

    st.markdown(
        f"""
        <style>
        .stApp {{
          background:
            radial-gradient(circle at 18px 18px, rgba(255,255,255,{dot_opacity}) 2px, transparent 2.5px),
            radial-gradient(circle at 0 0, rgba(255,255,255,{dot_opacity}) 2px, transparent 2.5px),
            {bg_base};
          background-size: 36px 36px;
          color: {text_color};
        }}

        section.main > div {{
          max-width: 820px;
          padding-top: 32px;
        }}

        .title-wrap {{
          text-align: center;
          margin-top: 10px;
          margin-bottom: 18px;
        }}
        .title {{
          font-size: 42px;
          font-weight: 900;
          letter-spacing: -0.5px;
          line-height: 1.1;
        }}
        .subtitle {{
          margin-top: 8px;
          opacity: 0.9;
          font-size: 14px;
        }}

        .note {{
          background: {note_bg};
          color: {note_text};
          border-radius: 16px;
          padding: 18px 18px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.18);
          margin: 10px 0 12px 0;
          border: 1px solid rgba(255,255,255,0.18);
        }}
        .note p {{
          margin: 0;
          font-size: 17px;
          line-height: 1.6;
          white-space: pre-wrap;
        }}

        .card {{
          background: {card_bg};
          border-radius: 16px;
          padding: 14px 14px;
          border: 1px solid rgba(255,255,255,0.14);
          box-shadow: 0 8px 22px rgba(0,0,0,0.16);
        }}

        .muted {{
          opacity: 0.85;
          font-size: 13px;
          white-space: pre-wrap;
        }}

        .banner {{
          font-weight: 900;
          letter-spacing: -0.2px;
          white-space: pre-wrap;
        }}

        .outcome {{
          font-size: 18px;
          line-height: 1.7;
          white-space: pre-wrap;
        }}

        /* buttons */
        div.stButton > button {{
          width: 100%;
          border-radius: 14px;
          padding: 12px 12px;
          font-weight: 900;
          border: 1px solid rgba(255,255,255,0.18);
          color: {button_text} !important;     /* force */
        }}

        header, footer {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    extra_choices: Optional[List[Option]] = None
    extra_banner: Optional[str] = None  # stage-specific ominous banner


def stage_asset_path(stage: int, option_idx: int) -> str:
    return os.path.join("assets", f"stage{stage}_{option_idx}.png")


def make_stages() -> Dict[int, Stage]:
    def flag_checked_door(flags): flags["checked_door"] = True
    def flag_looked_window(flags): flags["looked_window"] = True
    def flag_stayed_home(flags): flags["stayed_home"] = True

    s: Dict[int, Stage] = {}

    s[1] = Stage(
        1,
        note_text="안녕! 오늘은 정말 중요한 날이야 💕\n데이트 준비를 도와줄래?\n먼저 옷부터 골라보자!",
        prompt="오늘은 테니스를 치러 갈 거니까 🎾\n스포티하면서도 귀여운 룩으로 부탁해!",
        options=[
            Option("1", "1번: 스포티 셋업", "꺄! 이거 완전 내 스타일이야 💗", darkness_delta=0),
            Option("2", "2번: 테니스 원피스", "깔끔하고 예쁘다… 오늘은 이걸로 😊", darkness_delta=0),
            Option("3", "3번: 트랙수트", "음… 조금 강해 보이지만, 괜찮겠지?", darkness_delta=1, add_ignore=1),
            Option("4", "4번: 두꺼운 후드 + 모자", "뭔가 숨기고 싶을 때 입는 옷 같아…", darkness_delta=1, add_ignore=1),
        ],
    )

    s[2] = Stage(
        2,
        note_text="생각해보니까…\n약속 시간보다 조금 일찍 준비해도 괜찮겠지? 😊\n오늘은 왠지 기분이 좋아.",
        prompt="가벼운 아우터를 입을까 말까 고민 중이야!",
        extra_note_flash="현관 쪽에서… 발소리가 난 것 같았어.",
        extra_banner="방금… 들었어? 되게 기분 나쁘다.",
        extra_choices=[
            Option("door_peek", "문을 확인한다", "잠깐… 문고리가 따뜻해.", darkness_delta=1, set_flag=flag_checked_door),
            Option("ignore", "무시한다", "착각이겠지. 귀찮아…", darkness_delta=1, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 리본 달린 바람막이", "귀엽다! 바람이 불어도 괜찮겠어 🎀", darkness_delta=0),
            Option("2", "2번: 가디건", "따뜻하고 예쁘네. 좋아!", darkness_delta=0),
            Option("3", "3번: 두꺼운 재킷", "조금… 무겁다. 그래도 입을까?", darkness_delta=1),
            Option("4", "4번: 아우터 안 입기", "괜찮아. 별로 춥지도 않았어.", darkness_delta=1, add_ignore=1),
        ],
    )

    s[3] = Stage(
        3,
        note_text="방금 말한 소리 말이야…\n아마 착각이겠지? 😅\n그래도 옷은 제대로 골라야지!",
        prompt="치마가 좋을까? 반바지가 좋을까?",
        extra_banner="계속 문을 쳐다보게 돼. 기분이 나빠.",
        extra_choices=[
            Option("door_check", "문을 다시 잠근다", "일단 잠궜어. 그나마 기분이 나아졌어.", darkness_delta=1, set_flag=flag_checked_door),
            Option("ignore", "무시한다", "응. 아무 일도 없을 거야.", darkness_delta=1, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 플리츠 스커트", "움직이기 편하고 귀여워! 💕", darkness_delta=0),
            Option("2", "2번: 테니스 반바지", "가볍고 좋아. 뛰기 딱이야!", darkness_delta=0),
            Option("3", "3번: 너무 긴 스커트", "발목이… 걸릴 것 같아. 괜찮겠지?", darkness_delta=1),
            Option("4", "4번: 이상하게 젖은 옷", "…이 옷, 왜 축축하지?", darkness_delta=2, add_ignore=1),
        ],
    )

    s[4] = Stage(
        4,
        note_text="아까 문 말이야…\n분명 닫아놨던 것 같은데 🤔\n괜히 기분이 찜찜하네",
        prompt="인스타에 OOTD 스토리 올릴 건데, 테마는 뭘로 할까?",
        extra_banner="계속 어디에서 숨소리가 들리는 것 같아...",
        extra_choices=[
            Option("listen", "문 쪽에 귀를 댄다", "… 갑자기 무슨 소리도 안 나. 너무 조용해.", darkness_delta=2),
            Option("ignore", "무시한다", "응. 귀찮아…", darkness_delta=1, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 핑크 포인트", "역시 핑크지! 오늘은 완벽해 💗", darkness_delta=0),
            Option("2", "2번: 화이트 톤", "깨끗해. 마음이 편해져.", darkness_delta=0),
            Option("3", "3번: 블랙 포인트", "어두운 색이 끌릴 때도 있지.", darkness_delta=1),
            Option("4", "4번: 다 뒤덮인 더러운 색", "진심이야?", darkness_delta=2, add_ignore=1),
        ],
    )

    s[5] = Stage(
        5,
        note_text="창문 쪽이 조금… 이상해.\n커튼을 닫아둘까?",
        prompt="액세서리를 고를까? (가벼운 것만!)",
        extra_banner="안을 훤히 들여다보기 좋은 구도야.\n....이런 불길한 생각은 그만 하고 싶은데.",
        extra_choices=[
            Option("window", "창문을 본다", "유리 너머로… 뭔가가 지나간 것 같아.", darkness_delta=2, set_flag=flag_looked_window),
            Option("curtain", "커튼을 닫는다", "커튼이 닫히는 소리가, 너무 크게 들려.", darkness_delta=1),
            Option("ignore", "무시한다", "괜찮아. 괜찮아…", darkness_delta=2, add_ignore=1),
        ],
        options=[
            Option("1", "1번: 하트 헤어핀", "귀엽지? 오늘은 내 날이야 💕", darkness_delta=0),
            Option("2", "2번: 테니스 캡", "스포티! 햇빛도 가려주고 좋아.", darkness_delta=0),
            Option("3", "3번: 목을 가리는 초커", "왠지 모르게 등골이 오싹해.", darkness_delta=2),
            Option("4", "4번: 아무것도 안 한다", "꾸미는 게… 의미가 있을까?", darkness_delta=2, add_ignore=1),
        ],
    )

    s[6] = Stage(
        6,
        note_text="…\n그냥 집에 있으면 안 될까?\n네가 정해줘.",
        prompt="나갈까? 말까?",
        extra_banner="밖은 공터야.\n그래서 더 잘 보여.",
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

    s[7] = Stage(
        7,
        note_text="방 안에\n다른 숨소리가 있어.",
        prompt="이제 옷이 문제가 아냐.",
        extra_banner="제발제발제발제발제발제발",
        extra_choices=[
            Option("open", "문을 연다", "문이 열리는 순간, 공기가 바뀐다.", game_over=True, game_over_reason="문 밖에서 누군가 웃고 있었어.", darkness_delta=3),
            Option("lights", "불을 끈다", "깜깜해지자… 더 가까워진다.", game_over=True, game_over_reason="어둠 속에서 누군가 내 이름을 불렀어.", darkness_delta=3),
            Option("lock", "문을 잠근다", "잠금이… 믿음직하지 않아.", darkness_delta=3),
            Option("hold", "숨을 죽인다", "…(숨소리만 남는다)", darkness_delta=2),
        ],
        options=[
            Option("1", "1번: (아무것도) 고르지 않는다", "너무 조용해. 너무…", darkness_delta=2),
            Option("2", "2번: (아무것도) 고르지 않는다", "시간이… 늘어난다.", darkness_delta=2),
            Option("3", "3번: (아무것도) 고르지 않는다", "심장이 시끄럽다.", darkness_delta=2),
            Option("4", "4번: (아무것도) 고르지 않는다", "문고리가… 돌아간다.", darkness_delta=3, add_ignore=1),
        ],
    )

    s[8] = Stage(
        8,
        note_text="난 끝이야.",
        prompt="루시는… 어디로 가야 할까?",
        extra_banner="제발제발제발제발제발제발.",
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

    return s


STAGES = make_stages()


# ----------------------------
# Apply option effects (without auto-scene jump)
# ----------------------------

def apply_effects(opt: Option):
    ss = st.session_state
    if opt.set_flag is not None:
        opt.set_flag(ss.flags)
    if opt.add_ignore:
        ss.flags["ignored_warnings"] += opt.add_ignore
    ss.darkness = min(8, ss.darkness + opt.darkness_delta)


def compute_ending() -> str:
    flags = st.session_state.flags
    ignored = flags.get("ignored_warnings", 0)
    stayed = flags.get("stayed_home", False)

    if ignored <= 1 and stayed:
        return "A"
    if ignored >= 4:
        return "C"
    return "B"


def clear_stage_picks():
    st.session_state.picked_extra = None
    st.session_state.picked_outfit = None


def maybe_proceed_to_outcome(stage: Stage):
    """
    Rule:
    - If stage has extra_choices: user MUST pick one extra AND one outfit before moving on.
    - If stage has no extra_choices: only outfit pick is required.
    Once required picks are done, we build a combined outcome message and move to outcome scene.
    """
    ss = st.session_state
    need_extra = stage.extra_choices is not None and len(stage.extra_choices) > 0

    if need_extra and (ss.picked_extra is None or ss.picked_outfit is None):
        return
    if (not need_extra) and (ss.picked_outfit is None):
        return

    # Outcome rule:
    # - If stage has extra choices (ominous + outfit together),
    #   show ONLY the ominous outcome in the outcome scene.
    # - Otherwise (no extra choices), show the outfit outcome.
    need_extra = stage.extra_choices is not None and len(stage.extra_choices) > 0

    if need_extra and ss.picked_extra is not None:
        ss.last_outcome = ss.picked_extra.outcome or "…"
    elif ss.picked_outfit is not None:
        ss.last_outcome = ss.picked_outfit.outcome or "…"
    else:
        ss.last_outcome = "…"

    # If either pick caused game over, go to gameover immediately
    for opt in [ss.picked_extra, ss.picked_outfit]:
        if opt is not None and opt.game_over:
            ss.gameover_reason = opt.game_over_reason or "…"
            ss.scene = "gameover"
            st.rerun()

    ss.scene = "outcome"
    st.rerun()


# ----------------------------
# Renderers
# ----------------------------

def render_title():
    st.markdown(
        """
        <div class="title-wrap">
          <div class="title">루시의 달콤살벌 데이트! 💗</div>
          <div class="subtitle">루시의 데이트 준비를 도와주세요!</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Title image space
    title_img_candidates = ["title.png", os.path.join("assets", "title.png")]
    img_path = next((p for p in title_img_candidates if os.path.exists(p)), None)

    if img_path:
        st.image(img_path, use_container_width=True)
    else:
        st.markdown(
            "<div class='card'><div class='muted'>타이틀 이미지 자리\n- title.png 또는 assets/title.png</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💗 데이트 준비 시작하기", key="start_btn"):
            st.session_state.scene = "note"
            st.session_state.stage = 1
            clear_stage_picks()
            st.rerun()
    with c2:
        if st.button("❌ 종료하고 나가기", key="exit_btn"):
            st.markdown("<div class='card'>안녕… 다음에 또 놀자 💗</div>", unsafe_allow_html=True)
            st.stop()


def render_note(stage: Stage):
    flash = ""
    if stage.extra_note_flash and stage.stage_num >= 2:
        flash = f"\n\n(잠깐) {stage.extra_note_flash}"

    st.markdown(
        f"<div class='note'><p>{escape_html(stage.note_text + flash)}</p></div>",
        unsafe_allow_html=True,
    )

    if st.button("다음으로", key=f"to_choose_{stage.stage_num}"):
        st.session_state.scene = "choose"
        clear_stage_picks()
        st.rerun()


def render_choose(stage: Stage):
    ss = st.session_state

    # Extra choice block (ominous)
    if stage.extra_choices:
        banner = stage.extra_banner or "…"
        st.markdown(
    f"<div class='card'>"
    f"<div class='banner'>{escape_html(banner)}</div>"
    f"</div>",
    unsafe_allow_html=True,
)
        st.markdown("")

        cols = st.columns(len(stage.extra_choices))
        for i, opt in enumerate(stage.extra_choices):
            with cols[i]:
                label = opt.label
                picked = (ss.picked_extra is not None and ss.picked_extra.key == opt.key)
                if st.button(("✅ " if picked else "") + label, key=f"extra_{stage.stage_num}_{opt.key}"):
                    ss.picked_extra = opt
                    apply_effects(opt)
                    maybe_proceed_to_outcome(stage)

        st.markdown("")

    # Outfit prompt
    st.markdown(
        f"<div class='card'><div class='muted'>{escape_html(stage.prompt)}</div>"
        f"<div class='muted' style='margin-top:6px;'>"
        f"{'✅ 옷 선택 완료' if ss.picked_outfit else '옷을 1개 골라줘.'}"
        f"</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # Outfit options 1..4
    cols = st.columns(2)
    slot_cols = [cols[0], cols[1], cols[0], cols[1]]

    for idx, opt in enumerate(stage.options, start=1):
        with slot_cols[idx - 1]:
            path = stage_asset_path(stage.stage_num, idx)
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            else:
                st.markdown(
                    f"<div class='card'><div style='font-weight:900;'>선택 {idx}</div>"
                    f"<div class='muted'>이미지: assets/stage{stage.stage_num}_{idx}.png</div></div>",
                    unsafe_allow_html=True,
                )

            picked = (ss.picked_outfit is not None and ss.picked_outfit.key == opt.key)
            if st.button(("✅ " if picked else "") + opt.label, key=f"opt_{stage.stage_num}_{opt.key}"):
                ss.picked_outfit = opt
                apply_effects(opt)
                maybe_proceed_to_outcome(stage)


def render_outcome():
    # Show ONLY combined outcome
    text = st.session_state.last_outcome or "…"
    st.markdown(
        f"<div class='card'><div class='outcome'>{escape_html(text)}</div></div>",
        unsafe_allow_html=True,
    )

    stage_num = st.session_state.stage

    if stage_num < 8:
        if st.button("다음 스테이지", key=f"next_stage_{stage_num}"):
            st.session_state.stage += 1
            st.session_state.scene = "note"
            st.session_state.last_outcome = ""
            clear_stage_picks()
            st.rerun()
    else:
        st.session_state.ending_key = compute_ending()
        st.session_state.scene = "ending"
        st.session_state.last_outcome = ""
        clear_stage_picks()
        st.rerun()


def render_gameover():
    st.markdown("<div class='title-wrap'><div class='title'>…</div></div>", unsafe_allow_html=True)

    if os.path.exists("jumpscare.png"):
        st.image("jumpscare.png", use_container_width=True)
    else:
        st.markdown("<div class='card'>jumpscare.png 파일이 폴더에 없어요.</div>", unsafe_allow_html=True)

    reason = st.session_state.gameover_reason or "끝."
    st.markdown(
        f"<div class='card'><div style='font-weight:950; font-size:24px;'>GAME OVER</div>"
        f"<div class='muted'>{escape_html(reason)}</div></div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("처음으로", key="go_title"):
            reset_game()
            st.rerun()
    with c2:
        if st.button("다시 도전", key="retry"):
            st.session_state.scene = "note"
            st.session_state.stage = 1
            st.session_state.darkness = 0
            st.session_state.flags = {
                "checked_door": False,
                "looked_window": False,
                "stayed_home": False,
                "ignored_warnings": 0,
            }
            st.session_state.last_outcome = ""
            st.session_state.gameover_reason = ""
            st.session_state.ending_key = ""
            clear_stage_picks()
            st.rerun()


def render_ending():
    key = st.session_state.ending_key or "B"

    if key == "A":
        title = "ENDING A"
        text = "루시는 결국 약속에 가지 않았고, 경찰을 불렀다.\n밖은 비로소 조용해졌다."
    elif key == "C":
        title = "ENDING C"
        text = "“루시, 내  사랑. 왜 계속 못 들은 척했어?”\n“내가 계속 밖에서 기다리고 있었는데.”"
    else:
        title = "ENDING B"
        text = "루시는 끝까지 못 들은 척을 했다. \n하지만 어디에선가, 옷장 쪽에서, 계속... 누군가의 숨소리가 들려 온다."

    st.markdown(
        f"<div class='card'><div style='font-weight:950; font-size:24px;'>{title}</div>"
        f"<div class='outcome' style='margin-top:12px;'>{escape_html(text)}</div></div>",
        unsafe_allow_html=True,
    )

    if st.button("처음 화면으로", key="end_to_title"):
        reset_game()
        st.rerun()


# ----------------------------
# App
# ----------------------------

st.set_page_config(page_title="루시의 달콤살벌 데이트!", page_icon="💗", layout="centered")
init_state()
apply_theme(st.session_state.darkness)

scene = st.session_state.scene
stage_num = st.session_state.stage
stage = STAGES.get(stage_num, STAGES[1])

# Router: render ONLY current scene
if scene == "title":
    render_title()
elif scene == "note":
    render_note(stage)
elif scene == "choose":
    render_choose(stage)
elif scene == "outcome":
    render_outcome()
elif scene == "gameover":
    render_gameover()
elif scene == "ending":
    render_ending()
else:
    reset_game()
    st.rerun()

