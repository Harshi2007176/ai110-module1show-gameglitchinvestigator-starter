# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Game purpose.** A Streamlit number-guessing game: the app picks a secret number in a difficulty-dependent range (Easy 1–20, Normal 1–100, Hard 1–50), the player has a fixed number of attempts to guess it, and the game gives a "Too High / Too Low" hint after each guess plus a running score.

**Bugs found.**
- `check_guess` returned the wrong direction — `guess > secret` said "Go HIGHER!" instead of "Go LOWER!", making the game effectively unwinnable.
- `check_guess` returned a `(outcome, message)` tuple, which broke the existing `tests/test_game_logic.py` (the tests assert equality against the bare string `"Win"` / `"Too High"` / `"Too Low"`).
- All game logic lived at module scope in `app.py` tangled with Streamlit calls, so nothing was unit-testable and `logic_utils.py` was a stub raising `NotImplementedError`.
- On every even attempt, `handle_submission` cast the secret to a string before calling `check_guess`, which silently corrupted comparisons (a deliberate "glitch" left intact per the README's warning).
- `New Game` button only reset `attempts` and `secret`; it didn't reset `score`, `status`, or `history`.

**Fixes applied.**
- Swapped the hint mapping so "Too High" → "📉 Go LOWER!" and "Too Low" → "📈 Go HIGHER!".
- Moved pure logic (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`) into `logic_utils.py`; `check_guess` now returns only the outcome string and a new `hint_for(outcome)` helper maps it to the UI message.
- Split `app.py` into `render_*` helpers + `main()` so each section (sidebar, debug, controls, submit handler) reads as one concern.
- Expanded `tests/test_game_logic.py` from 3 to 22 cases covering the hint regression, range lookup, parsing edge cases (empty / `None` / non-numeric / float-truncation), and the score formula (including the late-win floor at 10).

## 📸 Demo Walkthrough

A sample game on Normal difficulty (range 1–100). Open the "Developer Debug Info" expander to follow along with the secret value.

1. App loads. Sidebar shows **Difficulty: Normal**, **Range: 1 to 100**, **Attempts allowed: 8**. Score is `0`, attempts is `1`, status is `playing`.
2. Open **Developer Debug Info** — the secret for this run is `42`.
3. Enter `40` in "Enter your guess:" and click **Submit Guess 🚀**. App shows `📈 Go HIGHER!`, history becomes `[40]`, attempts becomes `2`, score goes to `-5` (Too Low subtracts 5).
4. Enter `70` and submit. App shows `📉 Go LOWER!`, attempts becomes `3`, history is `[40, 70]`. (Score behavior on even attempts is intentionally glitchy per the original spec.)
5. Enter `42` and submit. App shows `🎉 Correct!`, fires `st.balloons()`, sets status to `won`, and displays "You won! The secret was 42. Final score: ...".
6. Click **New Game 🔁** to start a fresh round with a new secret in the same range.

**Screenshot** *(optional)*: not included — the textual walkthrough above covers the same ground.

## 🧪 Test Results

```
$ python3 -m pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/harshinibondila/ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.14.0
collected 22 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  4%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  9%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 13%]
tests/test_game_logic.py::test_hint_too_high_says_lower PASSED           [ 18%]
tests/test_game_logic.py::test_hint_too_low_says_higher PASSED           [ 22%]
tests/test_game_logic.py::test_hint_win PASSED                           [ 27%]
tests/test_game_logic.py::test_hint_unknown_outcome_empty PASSED         [ 31%]
tests/test_game_logic.py::test_range_easy PASSED                         [ 36%]
tests/test_game_logic.py::test_range_normal PASSED                       [ 40%]
tests/test_game_logic.py::test_range_hard PASSED                         [ 45%]
tests/test_game_logic.py::test_range_unknown_defaults PASSED             [ 50%]
tests/test_game_logic.py::test_parse_valid_int PASSED                    [ 54%]
tests/test_game_logic.py::test_parse_float_truncates PASSED              [ 59%]
tests/test_game_logic.py::test_parse_empty PASSED                        [ 63%]
tests/test_game_logic.py::test_parse_none PASSED                         [ 68%]
tests/test_game_logic.py::test_parse_non_numeric PASSED                  [ 72%]
tests/test_game_logic.py::test_score_win_first_attempt PASSED            [ 77%]
tests/test_game_logic.py::test_score_win_floor_at_10 PASSED              [ 81%]
tests/test_game_logic.py::test_score_too_high_even_attempt_adds_5 PASSED [ 86%]
tests/test_game_logic.py::test_score_too_high_odd_attempt_subtracts_5 PASSED [ 90%]
tests/test_game_logic.py::test_score_too_low_subtracts_5 PASSED          [ 95%]
tests/test_game_logic.py::test_score_unknown_outcome_unchanged PASSED    [100%]

============================== 22 passed in 0.02s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
