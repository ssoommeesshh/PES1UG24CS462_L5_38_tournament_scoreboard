# Static analysis findings

Original line numbers refer to commit `c9ef096`.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Bandit B605 | Security, high | 71 | Untrusted server text is concatenated into a shell command. | Validate a hostname/IPv4 address and pass fixed SCP arguments to subprocess.run with shell=False; resolve the executable, check exit status, enforce host-key verification and a timeout. |
| Bandit B306 | Security, medium | 66 | mktemp only chooses a name, allowing a race before creation. | Use mkstemp to atomically create a private file and close its descriptor. The caller must delete the returned file after use. |
| Bandit B105 | Security, low | 6 | A demo password is embedded in source. | Remove the unused credential; the scoreboard has no authentication feature. |
| Bandit B311 | Randomness, low | 61 | The coin toss uses the standard pseudo-random generator. | Use secrets.choice for an unpredictable toss. |
| Pylint W0102 | Bug | 11-13 | A list default shares the roster across calls; supplied lists also alias caller state. | Default to None and create a fresh list, copying a supplied roster. |
| Pylint C0103 | Maintainability | 11-71 | Function and argument names use camelCase. | Rename definitions and all call sites to snake_case. |
| Pylint C0114/C0116 | Documentation | 1, 11-74 | Module and functions lack docstrings. | Describe each function and the temporary-file cleanup responsibility. |
| Pylint R1705 | Control flow | 17-22 | elif/else follows a branch that returns. | Use early returns without redundant else branches. |
| Pylint R1714 | Bug and readability | 56-58 | Two indexed comparisons are verbose and can raise IndexError for small leagues. | Test membership in league_table()[:2], which safely handles zero or one team. |
| Flake8 E203 | Formatting | 5 | Extra space before the dictionary colon. | Use normal key: value spacing. |
| Flake8 E302 | Formatting | 60 | Missing second blank line between top-level functions. | Add the required blank line. |
| Flake8 E231 | Formatting | 79 | Missing space after a comma in a match call. | Separate arguments with a comma and space. |
| Flake8 E261 | Formatting | 87 | Inline comment has only one preceding space. | Put two spaces before the comment. |

The roster-copy change also introduced continuation/line-length violations (E128/E501); the final formatting commit expands the dictionary to aligned lines under 79 characters.

The top-two crash is a manual finding exposed while addressing R1714; Pylint did not diagnose the IndexError. An import guard now prevents the demo from running on import, and main resets demo state so repeated runs remain consistent.

## Reviewed subprocess warnings

The safe replacement still triggers Bandit B404 (subprocess import) and B603 (process execution), which flag subprocess use even without a shell. Two narrow inline exceptions cover only those warnings. The actual B605 injection issue is fixed: the destination accepts only letters, digits, dots and hyphens and must begin with a letter or digit; no user text is interpreted by a shell. SCP uses its normal trusted executable search path and verifies known host keys. The executable and local environment must be trusted. These exceptions are visible in the Bandit report; no global checks or severity levels are disabled.


## Final verification

- Pylint 4.1.3: 10.00/10, no messages, exit status 0 (baseline 4.75/10).
- Bandit 1.9.4: no active findings, exit status 0; two reviewed subprocess exceptions above (baseline one high, one medium, two low).
- Flake8 7.4.1: empty report, exit status 0 (baseline four violations).
- Eleven regression tests pass; demo standings match the baseline, excluding the intentionally random toss.
- Reports use the target script, not third-party virtual-environment code. Before reports retain original output; after reports describe the final source.
