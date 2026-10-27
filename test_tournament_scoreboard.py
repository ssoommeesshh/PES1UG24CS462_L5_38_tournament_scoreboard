"""Regression checks for scoreboard behavior and security boundaries."""

import contextlib
import io
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import tournament_scoreboard as scoreboard


class ScoreboardTests(unittest.TestCase):
    """Exercise real match outcomes and the repaired helper boundaries."""

    def setUp(self):
        scoreboard.teams.clear()
        scoreboard.matches.clear()

    def test_rosters_are_independent(self):
        scoreboard.add_team("A")
        scoreboard.add_team("B")
        scoreboard.teams["A"]["players"].append("Alice")
        self.assertEqual(scoreboard.teams["B"]["players"], [])
        roster = ["Bob"]
        scoreboard.add_team("C", roster)
        roster.append("Charlie")
        self.assertEqual(scoreboard.teams["C"]["players"], ["Bob"])

    def test_home_away_and_draw_results(self):
        for home, away, expected in [(2, 1, "home"), (0, 2, "away"),
                                     (1, 1, "draw")]:
            with self.subTest(home=home, away=away):
                self.assertEqual(scoreboard.match_result(home, away), expected)

    def test_match_statistics(self):
        scoreboard.add_team("A")
        scoreboard.add_team("B")
        scoreboard.record_match("A", "B", 2, 1)
        scoreboard.record_match("A", "B", 0, 3)
        scoreboard.record_match("A", "B", 1, 1)
        for name in ("A", "B"):
            stats = scoreboard.teams[name]
            self.assertEqual([stats[key] for key in
                              ("played", "won", "drawn", "lost")],
                             [3, 1, 1, 1])
            self.assertEqual(scoreboard.points(name), 4)
        self.assertEqual(scoreboard.goal_difference("A"), -2)
        self.assertEqual(scoreboard.goal_difference("B"), 2)
        self.assertEqual(scoreboard.league_table(), ["B", "A"])
        self.assertEqual(len(scoreboard.matches), 3)

    def test_top_two_for_small_leagues(self):
        self.assertFalse(scoreboard.is_top_two("Missing"))
        scoreboard.add_team("A")
        self.assertTrue(scoreboard.is_top_two("A"))
        self.assertFalse(scoreboard.is_top_two("Missing"))

    def test_demo_matches_original_and_resets(self):
        baseline = Path("reports/before/demo_output.txt").read_text()
        for _ in range(2):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                scoreboard.main()
            self.assertEqual(output.getvalue().splitlines()[1:],
                             baseline.splitlines()[1:])
            self.assertIn(output.getvalue().splitlines()[0],
                          ("Toss: Heads", "Toss: Tails"))

    def test_secure_coin_uses_both_valid_outcomes(self):
        for outcome in ("Heads", "Tails"):
            with patch.object(scoreboard.secrets, "choice",
                              return_value=outcome) as choice:
                self.assertEqual(scoreboard.toss_coin(), outcome)
                choice.assert_called_once_with(["Heads", "Tails"])

    def test_temporary_file_exists_and_can_be_reopened(self):
        path = Path(scoreboard.table_file_path())
        try:
            self.assertTrue(path.is_file())
            self.assertEqual(path.suffix, ".json")
            path.write_text("{}")
            self.assertEqual(path.read_text(), "{}")
        finally:
            path.unlink()

    def test_publish_rejects_shell_and_option_injection(self):
        with patch.object(scoreboard.subprocess, "run") as run:
            for server in ("host;whoami", "host&&whoami", "-oProxyCommand=x",
                           "host name", "host/path", "user@host", "", "$(id)"):
                with self.subTest(server=server):
                    with self.assertRaises(ValueError):
                        scoreboard.publish_table(server)
            run.assert_not_called()

    def test_publish_uses_safe_arguments(self):
        with patch.object(scoreboard.shutil, "which", return_value="/bin/scp"):
            with patch.object(scoreboard.subprocess, "run") as run:
                scoreboard.publish_table("scores.example.com")
                run.assert_called_once_with(
                    ["/bin/scp", "-o", "BatchMode=yes", "-o",
                     "StrictHostKeyChecking=yes", "table.json",
                     "scores.example.com:/var/www/"],
                    shell=False, check=True, timeout=30,
                )

    def test_missing_scp_is_explicit(self):
        with patch.object(scoreboard.shutil, "which", return_value=None):
            with self.assertRaises(FileNotFoundError):
                scoreboard.publish_table("example.com")

    def test_publish_propagates_transfer_failure(self):
        with patch.object(scoreboard.shutil, "which", return_value="/bin/scp"):
            with patch.object(scoreboard.subprocess, "run",
                              side_effect=subprocess.CalledProcessError(
                                  1, ["/bin/scp"])):
                with self.assertRaises(subprocess.CalledProcessError):
                    scoreboard.publish_table("example.com")


if __name__ == "__main__":
    unittest.main()
