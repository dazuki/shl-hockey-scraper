#!/usr/bin/env python3
"""
SHL Hockey Standings Scraper
Scrapes the Total standings table from sportstatistik.nu and saves to JSON.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup


# Constants
URL = "https://sportstatistik.nu/hockey/shl/tabell"
OUTPUT_FILE = "standings.json"
TIMEOUT = 10
TOTAL_GAMES_IN_SEASON = 52  # SHL regular season
API_VERSION = "1.0.0"


def get_current_season() -> str:
    """
    Calculate current SHL season based on date.

    SHL season runs September to April.
    Returns season in format "YYYY-YYYY" (e.g., "2024-2025").
    """
    now = datetime.now()
    year = now.year
    month = now.month

    # Sep-Dec: current year / next year
    # Jan-Aug: previous year / current year
    if month >= 9:
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"


def fetch_page(url: str) -> Optional[str]:
    """
    Fetch HTML content from URL.

    Args:
        url: Target URL to fetch

    Returns:
        HTML content as string, or None if request fails
    """
    try:
        print(f"Fetching SHL standings from {url}...")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to server", file=sys.stderr)
        return None
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {TIMEOUT} seconds", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed: {e}", file=sys.stderr)
        return None


def parse_standings(html: str) -> Optional[List[Dict]]:
    """
    Parse the Total standings table from HTML.

    Args:
        html: HTML content containing standings tables

    Returns:
        List of team standings as dictionaries, or None if parsing fails
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Find all tables - we need the first one (Total standings)
        tables = soup.find_all('table')

        if not tables:
            print("Error: No tables found on page", file=sys.stderr)
            return None

        # Get first table (Total standings)
        table = tables[0]
        rows = table.find_all('tr')

        if len(rows) < 2:
            print("Error: Table has insufficient rows", file=sys.stderr)
            return None

        standings = []

        # Skip header row (first row), parse data rows
        for position, row in enumerate(rows[1:], start=1):
            cells = row.find_all('td')

            # Expect 11 columns: team, games_played, wins, ties, losses, ot_wins, ot_losses,
            # goals_for, goals_against, goal_diff, points
            if len(cells) < 11:
                print(f"Warning: Skipping row with {len(cells)} cells (expected 11)", file=sys.stderr)
                continue

            try:
                team_data = {
                    "position": position,
                    "team": cells[0].get_text(strip=True),
                    "games_played": int(cells[1].get_text(strip=True)),
                    "wins": int(cells[2].get_text(strip=True)),
                    "ties": int(cells[3].get_text(strip=True)),
                    "losses": int(cells[4].get_text(strip=True)),
                    "ot_wins": int(cells[5].get_text(strip=True)),
                    "ot_losses": int(cells[6].get_text(strip=True)),
                    "goals_for": int(cells[7].get_text(strip=True)),
                    "goals_against": int(cells[8].get_text(strip=True)),
                    "goal_diff": int(cells[9].get_text(strip=True)),
                    "points": int(cells[10].get_text(strip=True))
                }

                # Add calculated fields
                gp = team_data["games_played"]
                team_data["win_percentage"] = round((team_data["wins"] / gp * 100) if gp > 0 else 0.0, 2)
                team_data["points_per_game"] = round((team_data["points"] / gp) if gp > 0 else 0.0, 2)
                team_data["goals_per_game"] = round((team_data["goals_for"] / gp) if gp > 0 else 0.0, 2)
                team_data["games_remaining"] = TOTAL_GAMES_IN_SEASON - gp

                standings.append(team_data)
            except (ValueError, AttributeError) as e:
                print(f"Warning: Failed to parse row data: {e}", file=sys.stderr)
                continue

        if not standings:
            print("Error: No valid standings data extracted", file=sys.stderr)
            return None

        print(f"Found {len(standings)} teams in Total standings table")
        return standings

    except Exception as e:
        print(f"Error: Failed to parse HTML: {e}", file=sys.stderr)
        return None


def load_existing_standings(filename: str) -> Optional[List[Dict]]:
    """
    Load existing standings from JSON file.

    Args:
        filename: Path to JSON file

    Returns:
        List of standings or None if file doesn't exist/invalid
    """
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('standings')
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Could not read existing file: {e}", file=sys.stderr)
        return None


def compare_standings(old: List[Dict], new: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Compare old and new standings, report differences.

    Args:
        old: Previous standings
        new: New standings

    Returns:
        Tuple of (has_changes, list_of_change_messages)
    """
    changes = []

    # Check if team count changed
    if len(old) != len(new):
        changes.append(f"Team count changed: {len(old)} → {len(new)}")
        return True, changes

    # Build lookup by team name
    old_by_team = {team['team']: team for team in old}
    new_by_team = {team['team']: team for team in new}

    # Check for new/removed teams
    old_teams = set(old_by_team.keys())
    new_teams = set(new_by_team.keys())

    if old_teams != new_teams:
        added = new_teams - old_teams
        removed = old_teams - new_teams
        if added:
            changes.append(f"New teams: {', '.join(added)}")
        if removed:
            changes.append(f"Removed teams: {', '.join(removed)}")
        return True, changes

    # Check position and stat changes
    for i, new_team in enumerate(new, start=1):
        team_name = new_team['team']
        old_team = old_by_team[team_name]

        # Position change
        if old_team['position'] != new_team['position']:
            changes.append(f"{team_name}: pos {old_team['position']} → {new_team['position']}")

        # Stat changes (only compare raw scraped values, not calculated fields)
        stat_changes = []
        for key in ['games_played', 'wins', 'ties', 'losses', 'ot_wins', 'ot_losses',
                    'goals_for', 'goals_against', 'goal_diff', 'points']:
            if old_team.get(key) != new_team.get(key):
                stat_changes.append(f"{key} {old_team[key]}→{new_team[key]}")

        if stat_changes:
            changes.append(f"{team_name}: {', '.join(stat_changes)}")

    return len(changes) > 0, changes


def save_to_json(data: List[Dict], filename: str) -> bool:
    """
    Save standings data to JSON file.

    Args:
        data: List of team standings dictionaries
        filename: Output file path

    Returns:
        True if save successful, False otherwise
    """
    try:
        output = {
            "api_version": API_VERSION,
            "timestamp": datetime.now().isoformat(),
            "season": get_current_season(),
            "league": "SHL",
            "table_type": "Total",
            "data_source": URL,
            "total_games_in_season": TOTAL_GAMES_IN_SEASON,
            "teams_count": len(data),
            "standings": data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(data)} standings to {filename}")
        return True

    except IOError as e:
        print(f"Error: Failed to write file: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: Failed to save JSON: {e}", file=sys.stderr)
        return False


def git_commit_and_push(changes: List[str]) -> bool:
    """
    Commit and push standings.json changes to git.

    Args:
        changes: List of change descriptions from compare_standings

    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate concise commit message
        if len(changes) == 1:
            msg = changes[0]
        else:
            # Check for position changes
            pos_changes = [c for c in changes if ' pos ' in c]
            if pos_changes:
                msg = pos_changes[0] if len(pos_changes) == 1 else f"{len(pos_changes)} pos changes"
            else:
                msg = f"{len(changes)} teams updated"

        # Add and commit
        subprocess.run(['git', 'add', OUTPUT_FILE], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', msg], check=True, capture_output=True)

        # Push to remote
        result = subprocess.run(['git', 'push'], check=True, capture_output=True, text=True)
        print(f"Pushed to remote: {msg}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Warning: Git operation failed: {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False
    except Exception as e:
        print(f"Warning: Failed to commit/push: {e}", file=sys.stderr)
        return False


def main():
    """Main execution function."""
    # Load existing standings
    existing = load_existing_standings(OUTPUT_FILE)

    # Fetch page
    html = fetch_page(URL)
    if html is None:
        sys.exit(1)

    # Parse standings
    standings = parse_standings(html)
    if standings is None:
        sys.exit(1)

    # Compare with existing
    if existing is not None:
        has_changes, changes = compare_standings(existing, standings)

        if not has_changes:
            print("No changes detected - standings.json not modified")
            print("Done!")
            return

        # Report changes
        print(f"\n{len(changes)} change(s) detected:")
        for change in changes:
            print(f"  - {change}")
        print()

        # Save to JSON
        success = save_to_json(standings, OUTPUT_FILE)
        if not success:
            sys.exit(1)

        # Commit and push changes
        git_commit_and_push(changes)

    else:
        print("No existing standings.json - creating new file")
        # Save to JSON
        success = save_to_json(standings, OUTPUT_FILE)
        if not success:
            sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
