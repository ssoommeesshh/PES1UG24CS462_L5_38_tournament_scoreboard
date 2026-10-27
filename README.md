# Lab 5: Static Code Analysis — Sports Tournament Scoreboard

**Your file:** `tournament_scoreboard.py`

Follow the lab handout for the full instructions.

## About the program

A league scoreboard. It registers teams, records match results, keeps played/won/drawn/lost and goal stats, builds a points table sorted by points and goal difference, and does a coin toss.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:

   ```
   python tournament_scoreboard.py
   ```

   It runs a short demonstration and needs no input. Note what it prints, so you can check that it still behaves the same after your fixes.

2. **Install the tools:**

   ```
   python -m pip install pylint bandit flake8
   ```

3. **Run the analysis and save the reports:**

   ```
   python -m pylint tournament_scoreboard.py > pylint_report.txt
   python -m bandit -r tournament_scoreboard.py > bandit_report.txt
   python -m flake8 tournament_scoreboard.py > flake8_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ...   | ...  | ...     | ...         | ...          |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

- `tournament_scoreboard.py`: your cleaned version, with at least 4 issues fixed.
- `issues.md`: the completed issue table.
- `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.


## Completed lab results

| Check | Before | After |
|-------|--------|-------|
| Pylint | 4.75/10 | 10.00/10 |
| Bandit | 1 high, 1 medium, 2 low | No active findings; 2 reviewed subprocess exceptions |
| Flake8 | 4 formatting violations | No violations |
| Regression tests | Not supplied | 11 passed |

Original reports are in `reports/before/`. Final reports, demonstration output and regression results are in `reports/after/`. The three final analysis reports are also at the repository root. See `issues.md` for original line references and fixes, and `reflection.md` for the reflection placeholder. It is intentionally blank until the handout questions are supplied.

### Reproduce the checks

Create and activate a Python virtual environment, then run:

```text
python -m pip install -r requirements-dev.txt
python tournament_scoreboard.py
python -m pylint --persistent=n tournament_scoreboard.py > pylint_report.txt
python -m bandit -r tournament_scoreboard.py -f txt -o bandit_report.txt
python -m flake8 tournament_scoreboard.py > flake8_report.txt
python -m unittest -v test_tournament_scoreboard
```

On standard Windows Python, activate with `venv\Scripts\Activate.ps1`. On this PC, Python is installed through MSYS2, so the environment uses `venv\bin\python.exe`; it can be invoked directly without activation. On Linux/macOS, use `source venv/bin/activate`.

### Helper behavior

Functions and arguments now use snake_case. `table_file_path()` returns an already-created file; its caller must delete it after use. `publish_table(server)` accepts a hostname or IPv4 address, uses the current SSH account and uploads the existing `table.json` to `/var/www/`. It requires SCP on the trusted system PATH, an existing trusted host key and non-interactive SSH credentials. User-qualified destinations and IPv6 are outside this helper's accepted input. No real remote upload was performed during verification.
