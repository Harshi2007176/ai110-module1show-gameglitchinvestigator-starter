# Bug Analysis: Why a guess of 99 says "Go HIGHER" instead of "Go LOWER"

## Symptom

Input `99` into the guessing game. Expected behavior: hint tells the player to go **lower** (since 99 is near the ceiling of the 1–100 range and almost always above the secret). Actual behavior: hint tells the player to go **higher**.

## Root Cause

There are **two interacting bugs** in `app.py`. Both push the displayed hint in the wrong direction for an input of 99, which is why the glitch feels so consistent at that value.

### Bug 1 — Swapped hint messages (primary cause)

Location: `app.py:32-47`, inside `check_guess(guess, secret)`.

```python
if guess > secret:
    return "Too High", "📈 Go HIGHER!"   # outcome correct, message wrong
else:
    return "Too Low",  "📉 Go LOWER!"    # outcome correct, message wrong
```

Walk-through for `guess = 99`, `secret = 42`:

1. `99 > 42` evaluates to `True`.
2. The function returns the outcome `"Too High"` — which is internally correct.
3. But the **message paired with that outcome** is `"📈 Go HIGHER!"` — the displayed hint contradicts the outcome.
4. `app.py:166` renders that message to the player via `st.warning(message)`. Player reads "Go HIGHER" and guesses an even bigger number.

The `"Too Low"` branch is swapped the same way (says "Go LOWER" when it should say "Go HIGHER"). The internal outcome labels are right; only the human-facing hint strings are mismatched. This matches the README line: *"the hints lie to you."*

### Bug 2 — Secret type-coerced to `str` on even attempts (amplifier)

Location: `app.py:158-161`.

```python
if st.session_state.attempts % 2 == 0:
    secret = str(st.session_state.secret)
else:
    secret = st.session_state.secret
```

On every even attempt the secret is passed to `check_guess` as a **string** while `guess` stays an `int`. Inside `check_guess` at `app.py:36-47`:

1. `guess > secret` becomes `int > str`, which raises `TypeError` in Python 3.
2. The `except TypeError` block runs: `g = str(guess)`, then both sides are compared as **strings**.
3. String comparison is **lexicographic**, not numeric. `"99" > "100"` is `True` because the character `'9'` is greater than `'1'`. So a guess of 99 against a secret of 100 is wrongly classified as `"Too High"`.
4. Bug 1 then mislabels the displayed hint as "Go HIGHER".

So on odd attempts only Bug 1 fires; on even attempts both bugs stack.

### Why the bug is loudest at 99

99 sits at the very top of the `1..100` Normal range, so `99 > secret` is true in almost every game (≈98% of secrets). That means the outcome `"Too High"` fires nearly every time, and Bug 1 reliably mistranslates it as "Go HIGHER" — pushing the player toward 100, where there is no headroom left. The same logical bug exists for low guesses, but it doesn't feel as broken because the numeric "wall" is farther away.

## How to Fix

| File | Lines | Change |
|------|-------|--------|
| `app.py` | 32–47 | Swap the message strings in `check_guess` so `"Too High"` pairs with `"📉 Go LOWER!"` and `"Too Low"` pairs with `"📈 Go HIGHER!"`. Delete the `try/except TypeError` block — it only exists to mask Bug 2. |
| `app.py` | 158–161 | Delete the `attempts % 2 == 0` branch. Always pass `st.session_state.secret` as an `int`. |
| `logic_utils.py` | 15–21 | Move the fixed `check_guess` here. **Note:** `tests/test_game_logic.py` expects `check_guess` to return a **single string** outcome (`"Win"`, `"Too High"`, `"Too Low"`), not a `(outcome, message)` tuple. Refactor the signature accordingly and let `app.py` derive the hint from the outcome on its side. |

While refactoring, also move `get_range_for_difficulty`, `parse_guess`, and `update_score` from `app.py` into `logic_utils.py` (their stubs already exist there) — README step 4 requires it.

## Verification Steps

1. Run `pytest tests/` — all 3 tests in `test_game_logic.py` should pass.
2. Run `python -m streamlit run app.py`. Open **Developer Debug Info** to see the secret. Guess a number higher than the secret → hint should now say "Go LOWER". Guess lower → hint should say "Go HIGHER". Guess the secret → win + balloons.
3. Test across both an even and an odd attempt count to confirm no `TypeError` and no lexicographic boundary glitches at 9 → 10 or 99 → 100.
