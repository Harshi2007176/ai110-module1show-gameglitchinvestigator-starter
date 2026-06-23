from logic_utils import (
    check_guess,
    hint_for,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# ---------------------------------------------------------------------------
# check_guess — returns string outcome
# ---------------------------------------------------------------------------

def test_winning_guess():
    assert check_guess(50, 50) == "Win"

def test_guess_too_high():
    assert check_guess(60, 50) == "Too High"

def test_guess_too_low():
    assert check_guess(40, 50) == "Too Low"


# ---------------------------------------------------------------------------
# hint_for — guards against the inverted Higher/Lower bug
# ---------------------------------------------------------------------------

# FIX: Added these hint_for tests after Claude agent flagged the inverted Higher/Lower hints
# in the original app.py — locks the correct outcome→hint mapping so the bug can't sneak back.
def test_hint_too_high_says_lower():
    # Regression: guess > secret must tell the player to go LOWER, not HIGHER.
    assert hint_for("Too High") == "📉 Go LOWER!"

def test_hint_too_low_says_higher():
    assert hint_for("Too Low") == "📈 Go HIGHER!"

def test_hint_win():
    assert hint_for("Win") == "🎉 Correct!"

def test_hint_unknown_outcome_empty():
    assert hint_for("Bogus") == ""


# ---------------------------------------------------------------------------
# get_range_for_difficulty
# ---------------------------------------------------------------------------

def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)

def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)

def test_range_hard():
    assert get_range_for_difficulty("Hard") == (1, 50)

def test_range_unknown_defaults():
    assert get_range_for_difficulty("???") == (1, 100)


# ---------------------------------------------------------------------------
# parse_guess
# ---------------------------------------------------------------------------

def test_parse_valid_int():
    assert parse_guess("42") == (True, 42, None)

def test_parse_float_truncates():
    assert parse_guess("42.9") == (True, 42, None)

def test_parse_empty():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."

def test_parse_none():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert err == "Enter a guess."

def test_parse_non_numeric():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert err == "That is not a number."


# ---------------------------------------------------------------------------
# update_score
# ---------------------------------------------------------------------------

def test_score_win_first_attempt():
    # points = 100 - 10 * (1 + 1) = 80
    assert update_score(0, "Win", attempt_number=1) == 80

def test_score_win_floor_at_10():
    # large attempt_number → would go negative; clamp to 10
    assert update_score(0, "Win", attempt_number=20) == 10

def test_score_too_high_even_attempt_adds_5():
    assert update_score(0, "Too High", attempt_number=2) == 5

def test_score_too_high_odd_attempt_subtracts_5():
    assert update_score(0, "Too High", attempt_number=3) == -5

def test_score_too_low_subtracts_5():
    assert update_score(0, "Too Low", attempt_number=1) == -5

def test_score_unknown_outcome_unchanged():
    assert update_score(42, "Other", attempt_number=1) == 42
