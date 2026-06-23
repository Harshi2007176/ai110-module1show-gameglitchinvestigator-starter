def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIX: Original app.py had both "Too High" and "Too Low" returning "Go LOWER!", making the game unwinnable.
# Collaborated with Claude in agent mode: it spotted the reversed hint direction, then refactored the
# message lookup into this dict so the outcome → hint mapping is explicit and easy to audit.
HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}


# FIX: Original returned a (outcome, message) tuple, which broke tests expecting a plain string.
# Collaborated with Claude in agent mode: it narrowed check_guess to outcome only and moved
# hint text into HINT_MESSAGES so tests/test_game_logic.py pass.
def check_guess(guess, secret):
    """
    Compare guess to secret and return outcome string.

    Returns: "Win", "Too High", or "Too Low"
    """
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


# FIX: New helper added during refactor (suggested by Claude agent) to keep UI strings out of
# pure logic — app.py calls hint_for(outcome) instead of unpacking a tuple from check_guess.
def hint_for(outcome: str) -> str:
    """Return the user-facing hint message for an outcome."""
    return HINT_MESSAGES.get(outcome, "")


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
