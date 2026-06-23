# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- When I first ran the game, it appeared to load correctly, but bugs became clear as soon as I started playing.
- The hints were backwards — guessing higher than the secret number showed "Go Higher" instead of "Go Lower", and vice versa.
- The "New Game" button did nothing when clicked, requiring a full page refresh to start over.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|  99   |go lower           |go higher        |none                    |
|  66   |ho high            |go lower         |none                    |
| Clicked "New Game" button | Game resets | Nothing happens, must refresh page | none |
| Clicked "Submit Guess" | Guess added to history immediately | Must click submit twice | none |
| Double submit due to history bug | 1 attempt counted | 2 attempts counted | none |

---

## 2. How did you use AI as a teammate?

I used Claude Code in agent mode as my main coding teammate, plus ChatGPT for quick "why is Streamlit doing this" questions.

**Correct suggestion.** When I asked Claude to focus on one bug, it pointed at `check_guess` in `app.py` and said the "Go HIGHER!" / "Go LOWER!" hints were swapped. `guess > secret` was returning "Go HIGHER!" when it should say "Go LOWER!". I verified this by playing the game with the Developer Debug Info expander open: I could see the secret was 42, I typed 80, and the app told me to "Go HIGHER!", which was clearly wrong. After Claude flipped the message, I retested with secret=42 and guess=80 and got the correct "Go LOWER!" hint. I also locked the fix in with a pytest case (`test_hint_too_high_says_lower`) that asserts `hint_for("Too High") == "📉 Go LOWER!"` so the bug can't regress.

**Incorrect / misleading suggestion.** During the refactor, Claude moved `check_guess` into `logic_utils.py` and dropped the original `TypeError` fallback branch, but it left the `if attempts % 2 == 0: secret = str(...)` glitch in `handle_submission`. That combination silently introduced a regression: on every even-numbered guess the app would now crash with `TypeError: '>' not supported between 'int' and 'str'` instead of silently misbehaving. I caught it by re-reading the diff before committing and noticing the fallback was gone while the str-cast wasn't: Claude even called it out in its summary, but only because I prompted it for one. The lesson: an AI saying "tests pass" only proves what the tests cover; the str-cast path had no test, so green pytest was misleading.

---

## 3. Debugging and testing your fixes

I treated a bug as "really fixed" only after both a manual play-through and a pytest assertion agreed. For the inverted hints I opened the Developer Debug Info panel to peek at the secret, then guessed deliberately above and below it (e.g. secret=42, guesses 80 and 10) and confirmed the hints now said "Go LOWER!" and "Go HIGHER!" in the right direction. For the logic refactor I ran `python3 -m pytest tests/ -v`, which initially printed `22 passed in 0.02s`: the new `test_hint_too_high_says_lower` and `test_hint_too_low_says_higher` cases were the ones that specifically protected the bug I had just fixed, so seeing them green meant the regression couldn't quietly come back. Claude helped me design the test suite: I asked it to generate tests for `check_guess`, `hint_for`, `get_range_for_difficulty`, `parse_guess`, and `update_score`, and it suggested edge cases I wouldn't have thought of (empty input, `None`, the score floor at 10 for late wins). Reading those tests also helped me understand the score formula better: I had to trace `100 - 10 * (attempt_number + 1)` by hand to confirm the expected values were right.

---

## 4. What did you learn about Streamlit and state?

The biggest thing I learned is that Streamlit reruns the entire script from top to bottom every time the user does almost anything: clicks a button, types in a box, toggles a checkbox. So if I write `secret = random.randint(1, 100)` at module scope, a new secret gets picked on every interaction and the game becomes unwinnable. The way to keep a value alive across reruns is `st.session_state` — it's a dict-like object that survives reruns, so you guard initialization with `if "secret" not in st.session_state: st.session_state.secret = ...` and only write to it inside event handlers. The way I'd explain it to a friend: imagine every click reloads the page, and `session_state` is the only suitcase you're allowed to carry across the reload. Anything not in the suitcase gets recreated from scratch.

---

## 5. Looking ahead: your developer habits

**Habit I want to keep.** Writing a pytest case the moment I fix a bug, even a one-line one. The inverted hint was a five-character change, but I added `test_hint_too_high_says_lower` and `test_hint_too_low_says_higher` immediately after so the bug literally cannot come back without a red test. That tiny extra step turned "I think it works" into "the suite will yell if I'm wrong." I also want to keep the habit of scoping my AI prompts: when I told Claude "focus on one problem and prompt me before moving forward" it did way better work than the earlier turn where I asked it to "refactor everything."

**Thing I would do differently.** I'd diff the AI's output against my last known-good state before accepting it, every single time. During the refactor Claude removed the `TypeError` fallback from `check_guess` while leaving the `secret = str(...)` line in `handle_submission`, which silently introduced a crash on even-numbered guesses. Tests still passed because that path wasn't covered. If I had done a careful `git diff` before committing instead of trusting "22 passed," I would have caught it immediately.

**How this changed my view of AI-generated code.** AI is genuinely faster than me at the mechanical parts — extracting functions, writing test boilerplate, generating commit messages — but it has zero intuition for which lines of existing code are *load-bearing*. Green tests prove what the tests cover, not that the code works; I have to be the one who decides what "works" means and where the holes in the test suite are.
