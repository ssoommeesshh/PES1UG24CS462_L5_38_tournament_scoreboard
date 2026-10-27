# Static analysis findings

Original line numbers refer to commit `c9ef096`.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Bandit B605 | Security, high | 71 | Untrusted server text is concatenated into a shell command. | Validate a hostname/IPv4 address and pass fixed SCP arguments to subprocess.run with shell=False; resolve the executable, check exit status, enforce host-key verification and a timeout. |
| Bandit B306 | Security, medium | 66 | mktemp only chooses a name, allowing a race before creation. | Use mkstemp to atomically create a private file and close its descriptor. The caller must delete the returned file after use. |
| Bandit B105 | Security, low | 6 | A demo password is embedded in source. | Remove the unused credential; the scoreboard has no authentication feature. |
| Bandit B311 | Randomness, low | 61 | The coin toss uses the standard pseudo-random generator. | Use secrets.choice for an unpredictable toss. |

## Reviewed subprocess warnings

The safe replacement still triggers Bandit B404 (subprocess import) and B603 (process execution), which flag subprocess use even without a shell. Two narrow inline exceptions cover only those warnings. The actual B605 injection issue is fixed: the destination accepts only letters, digits, dots and hyphens and must begin with a letter or digit; no user text is interpreted by a shell. SCP uses its normal trusted executable search path and verifies known host keys. The executable and local environment must be trusted. These exceptions are visible in the Bandit report; no global checks or severity levels are disabled.
