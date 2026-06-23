import random
import streamlit as st

# FIX: Pure game logic was tangled with Streamlit calls in app.py. Worked with Claude in
# agent mode to extract get_range_for_difficulty / parse_guess / check_guess / update_score
# into logic_utils.py so the same functions can be unit-tested via pytest.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    hint_for,
    update_score,
)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def init_session_state(low: int, high: int) -> None:
    defaults = {
        "secret": random.randint(low, high),
        "attempts": 1,
        "score": 0,
        "status": "playing",
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_new_game(low: int, high: int) -> None:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.success("New game started.")
    st.rerun()


# ---------------------------------------------------------------------------
# UI sections
# ---------------------------------------------------------------------------

# FIX: Original app.py rendered all UI at module scope (~70 lines straight). Claude agent split
# it into render_* helpers so each section reads as one concern and main() shows the page flow.
def render_header() -> None:
    st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")
    st.title("🎮 Game Glitch Investigator")
    st.caption("An AI-generated guessing game. Something is off.")


def render_sidebar():
    st.sidebar.header("Settings")
    difficulty = st.sidebar.selectbox(
        "Difficulty",
        list(ATTEMPT_LIMITS.keys()),
        index=1,
    )
    attempt_limit = ATTEMPT_LIMITS[difficulty]
    low, high = get_range_for_difficulty(difficulty)
    st.sidebar.caption(f"Range: {low} to {high}")
    st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
    return difficulty, attempt_limit, low, high


def render_attempts_banner(attempt_limit: int) -> None:
    st.subheader("Make a guess")
    st.info(
        f"Guess a number between 1 and 100. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )


def render_debug_panel(difficulty: str) -> None:
    with st.expander("Developer Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)


def render_controls(difficulty: str):
    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.button("Submit Guess 🚀")
    with col2:
        new_game = st.button("New Game 🔁")
    with col3:
        show_hint = st.checkbox("Show hint", value=True)
    return raw_guess, submit, new_game, show_hint


def render_game_over_message() -> None:
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")


# ---------------------------------------------------------------------------
# Game flow
# ---------------------------------------------------------------------------

def handle_submission(raw_guess: str, attempt_limit: int, show_hint: bool) -> None:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)
    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
        return

    st.session_state.history.append(guess_int)

    if st.session_state.attempts % 2 == 0:
        secret = str(st.session_state.secret)
    else:
        secret = st.session_state.secret

    outcome = check_guess(guess_int, secret)

    # FIX: check_guess now returns only the outcome string (post-refactor with Claude agent),
    # so UI looks up the hint via hint_for() instead of unpacking a tuple.
    if show_hint:
        st.warning(hint_for(outcome))

    st.session_state.score = update_score(
        current_score=st.session_state.score,
        outcome=outcome,
        attempt_number=st.session_state.attempts,
    )

    if outcome == "Win":
        st.balloons()
        st.session_state.status = "won"
        st.success(
            f"You won! The secret was {st.session_state.secret}. "
            f"Final score: {st.session_state.score}"
        )
        return

    if st.session_state.attempts >= attempt_limit:
        st.session_state.status = "lost"
        st.error(
            f"Out of attempts! "
            f"The secret was {st.session_state.secret}. "
            f"Score: {st.session_state.score}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    render_header()
    difficulty, attempt_limit, low, high = render_sidebar()
    init_session_state(low, high)
    render_attempts_banner(attempt_limit)
    render_debug_panel(difficulty)
    raw_guess, submit, new_game, show_hint = render_controls(difficulty)

    if new_game:
        start_new_game(low, high)

    if st.session_state.status != "playing":
        render_game_over_message()
        st.stop()

    if submit:
        handle_submission(raw_guess, attempt_limit, show_hint)

    st.divider()
    st.caption("Built by an AI that claims this code is production-ready.")


main()
