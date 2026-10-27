"""Maintain a football league scoreboard and run a sample tournament."""

import os
import re
import secrets
import shutil
# Required for shell-free SCP execution; reviewed in issues.md.
import subprocess  # nosec B404
import tempfile

POINTS = {"win": 3, "draw": 1, "loss": 0}
teams = {}
matches = []


def add_team(team_name, players=None):
    """Register a team with its own copy of the player roster."""
    teams[team_name] = {
        "played": 0, "won": 0, "drawn": 0, "lost": 0,
        "gf": 0, "ga": 0,
        "players": list(players) if players is not None else [],
    }


def match_result(home_goals, away_goals):
    """Return home, away or draw according to the two scores."""
    if home_goals > away_goals:
        return "home"
    if home_goals < away_goals:
        return "away"
    return "draw"


def record_match(home, away, home_goals, away_goals):
    """Update both registered teams and append a match to the history."""
    result = match_result(home_goals, away_goals)
    sides = ((home, home_goals, away_goals), (away, away_goals, home_goals))
    for team, scored, conceded in sides:
        teams[team]["played"] += 1
        teams[team]["gf"] += scored
        teams[team]["ga"] += conceded
    if result == "draw":
        teams[home]["drawn"] += 1
        teams[away]["drawn"] += 1
    else:
        winner, loser = (home, away) if result == "home" else (away, home)
        teams[winner]["won"] += 1
        teams[loser]["lost"] += 1
    matches.append((home, away, home_goals, away_goals))


def points(team_name):
    """Calculate league points from wins and draws."""
    stats = teams[team_name]
    return stats["won"] * POINTS["win"] + stats["drawn"] * POINTS["draw"]


def goal_difference(team_name):
    """Return goals scored minus goals conceded."""
    return teams[team_name]["gf"] - teams[team_name]["ga"]


def league_table():
    """Rank teams by points, breaking ties with goal difference."""
    return sorted(teams, key=lambda t: (points(t), goal_difference(t)),
                  reverse=True)


def is_top_two(team_name):
    """Check top-two membership, including leagues with fewer teams."""
    return team_name in league_table()[:2]


def toss_coin():
    """Return an unpredictable Heads or Tails result."""
    return secrets.choice(["Heads", "Tails"])


def table_file_path():
    """Create a private JSON file; the caller must remove it after use."""
    descriptor, path = tempfile.mkstemp(suffix=".json")
    os.close(descriptor)
    return path


def publish_table(server):
    """Upload table.json to a validated host using verified SSH keys."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", server):
        raise ValueError("server must be a hostname or IPv4 address")
    executable = shutil.which("scp")
    if executable is None:
        raise FileNotFoundError("scp executable is not installed")
    # B603: validated hostname, resolved executable, fixed arguments, no shell.
    subprocess.run(  # nosec B603
        [executable, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
         "table.json", f"{server}:/var/www/"],
        shell=False, check=True, timeout=30,
    )


def main():
    """Reset the scoreboard and demonstrate a four-match tournament."""
    teams.clear()
    matches.clear()
    for name in ["Royal Strikers", "City Rovers", "Lake United"]:
        add_team(name)
    add_team("Hill Warriors")
    print("Toss:", toss_coin())
    record_match("Royal Strikers", "City Rovers", 2, 1)
    record_match("Lake United", "Hill Warriors", 0, 0)
    record_match("City Rovers", "Lake United", 3, 2)
    record_match("Hill Warriors", "Royal Strikers", 1, 1)
    print("Pos Team Played Won Drawn Lost Pts")
    for pos, name in enumerate(league_table(), 1):
        stats = teams[name]
        print(pos, name, stats["played"], stats["won"], stats["drawn"],
              stats["lost"], points(name))  # one row per team
    print("Is City Rovers in the top two?", is_top_two("City Rovers"))
    print("Matches played:", len(matches))


if __name__ == "__main__":
    main()
