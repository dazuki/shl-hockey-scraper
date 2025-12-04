# Project Memory: SHL Hockey Scraper

## Project Overview
Python web scraper that extracts current SHL (Swedish Hockey League) standings from sportstatistik.nu and outputs structured JSON data.

## How It Works

### Data Flow
```
1. load_existing_standings() → Load current standings.json if exists
2. fetch_page() → HTTP GET to sportstatistik.nu/hockey/shl/tabell
3. parse_standings() → Extract first table (Total standings), parse 14 team rows
4. compare_standings() → Compare old vs new, detect changes
5. generate_commit_message() → Create concise update message from changes
6. save_to_json() → Write JSON with change tracking, only if changes detected or file missing
7. git_commit_and_push() → Auto-commit and push using generated message
```

### Technical Details
- **Library**: BeautifulSoup4 + requests (static HTML parsing)
- **Target**: Total standings table only (not Home/Away)
- **Table Structure**: 11 columns per row (no explicit position column - derived from row index)
- **Output**: API-ready JSON with metadata, 14 teams × 16 fields each (12 scraped + 4 calculated)
- **Season Detection**: Auto-calculated based on date (Sept-April SHL calendar)
- **Calculated Stats**: win%, PPG, GPG, games remaining (computed from scraped values)
- **Comparison Logic**: Detects position/stat changes, ignores calculated fields
- **Smart Updates**: Only overwrites file when changes detected
- **Change Tracking**: update_message (commit msg) + changes array embedded in JSON

### Columns Extracted
**Scraped values:**
```
position (1-14, derived)
team (string)
games_played, wins, ties, losses, ot_wins, ot_losses, goals_for, goals_against, goal_diff, points (integers)
```

**Calculated fields:**
```
win_percentage (float, 2 decimals) = (wins / games_played) × 100
points_per_game (float, 2 decimals) = points / games_played
goals_per_game (float, 2 decimals) = goals_for / games_played
games_remaining (integer) = 52 - games_played
```

### Error Handling
- Network errors: ConnectionError, Timeout, HTTPError
- Parsing errors: Missing table, malformed rows (skip with warning)
- File I/O errors: Write failures
- All errors print to stderr, exit code 1 on failure

## Project Structure
```
shl-hockey-scraper/
├── scraper.py          # Main script (375 lines)
├── run_scraper.sh      # Cronjob-compatible bash wrapper
├── requirements.txt    # requests==2.31.0, beautifulsoup4==4.12.2
├── README.md          # User-facing docs
├── CLAUDE.md          # This file - project memory for Claude
├── .gitignore         # Excludes venv/, *.json, __pycache__/
├── venv/              # Python virtual environment (gitignored)
├── standings.json     # Generated output (gitignored)
└── cron.log           # Cronjob output log (optional, gitignored)
```

## Implementation History

### Completed
1. ✅ Project structure created (fresh directory)
2. ✅ requirements.txt with pinned dependencies
3. ✅ scraper.py with 3 main functions:
   - `fetch_page(url)` - HTTP request with 10s timeout
   - `parse_standings(html)` - BeautifulSoup table parsing
   - `save_to_json(data, filename)` - JSON serialization
4. ✅ README.md with setup/usage instructions
5. ✅ .gitignore for Python project
6. ✅ Bug fix: Corrected column count from 12→11 (no position column in HTML)
7. ✅ Tested against live website - successfully extracted 14 teams
8. ✅ Smart comparison system - only update file when changes detected:
   - `load_existing_standings(filename)` - Load existing JSON
   - `compare_standings(old, new)` - Detect position/stat changes
   - Modified `main()` to skip save when no changes
   - Reports specific changes to stdout (position shifts, stat updates)
9. ✅ Cronjob wrapper script:
   - `run_scraper.sh` - Bash wrapper with absolute paths for cron compatibility
   - Activates venv, runs scraper, logs with timestamps
   - Proper exit code handling for monitoring
10. ✅ Descriptive JSON keys:
   - Replaced abbreviations with descriptive names (1-2 words)
   - `gp`→`games_played`, `w`→`wins`, `t`→`ties`, `l`→`losses`
   - `otw`→`ot_wins`, `otl`→`ot_losses`, `g`→`goals_for`, `ga`→`goals_against`
   - `diff`→`goal_diff`, `p`→`points`
11. ✅ API-ready enhancements:
   - Added top-level metadata: `api_version`, `season`, `data_source`, `total_games_in_season`
   - `get_current_season()` - Auto-detect season from date (Sept-April calendar)
   - Per-team calculated fields: `win_percentage`, `points_per_game`, `goals_per_game`, `games_remaining`
   - Updated comparison logic to ignore calculated fields (only compare scraped values)
   - Constants: `TOTAL_GAMES_IN_SEASON=52`, `API_VERSION="1.0.0"`
12. ✅ Change tracking in JSON:
   - `generate_commit_message(changes)` - Extract commit message generation logic
   - Added `update_message` field - same message used in git commits
   - Added `changes` array - detailed list of all changes detected
   - Enables API consumers to fetch change history without git access
   - Values: `null`/`[]` on initial creation, populated on updates

### Key Implementation Decisions
- **Position derivation**: Use `enumerate(rows[1:], start=1)` since no explicit column
- **Single script**: No need for modules/packages (simple utility)
- **No async**: Single table, small dataset - requests library sufficient
- **API-ready output**: Rich metadata + calculated stats for direct consumption
- **Season auto-detection**: Date-based logic (month >= 9 = current/next year)
- **Calculated fields**: Computed after parsing, not stored separately
- **Comparison logic**: Only compare scraped values, ignore calculated/derived fields
- **Print-based logging**: Lightweight, no logging library needed
- **Team name lookup**: Dict-based comparison for O(1) lookup vs linear search
- **Change tracking**: Embedded in JSON for API consumers, mirroring git commit messages

## JSON Output Format
```json
{
  "api_version": "1.0.0",
  "timestamp": "2025-12-04T10:15:32.123456",
  "season": "2025-2026",
  "league": "SHL",
  "table_type": "Total",
  "data_source": "https://sportstatistik.nu/hockey/shl/tabell",
  "total_games_in_season": 52,
  "teams_count": 14,
  "update_message": "Frölunda HC: games_played 22→23, wins 18→19",
  "changes": [
    "Frölunda HC: games_played 22→23, wins 18→19, goals_for 74→77, points 54→57"
  ],
  "standings": [
    {
      "position": 1,
      "team": "Frölunda HC",
      "games_played": 23,
      "wins": 19,
      "ties": 0,
      "losses": 4,
      "ot_wins": 0,
      "ot_losses": 0,
      "goals_for": 77,
      "goals_against": 33,
      "goal_diff": 44,
      "points": 57,
      "win_percentage": 82.61,
      "points_per_game": 2.48,
      "goals_per_game": 3.35,
      "games_remaining": 29
    },
    ...
  ]
}
```

## Usage
```bash
# Setup (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run scraper
python scraper.py

# Output scenarios:
# 1. No existing file: Creates standings.json
# 2. No changes: Prints "No changes detected", file not modified
# 3. Changes detected: Reports changes, updates standings.json
```

### Example Output
```
# First run
Fetching SHL standings from https://sportstatistik.nu/hockey/shl/tabell...
Found 14 teams in Total standings table
No existing standings.json - creating new file
Saved 14 standings to standings.json
Done!

# Second run (no changes)
Fetching SHL standings from https://sportstatistik.nu/hockey/shl/tabell...
Found 14 teams in Total standings table
No changes detected - standings.json not modified
Done!

# Run with changes
Fetching SHL standings from https://sportstatistik.nu/hockey/shl/tabell...
Found 14 teams in Total standings table

3 change(s) detected:
  - Frölunda HC: pos 1 → 2
  - Skellefteå AIK: pos 2 → 1
  - Luleå HF: games_played 23→24, wins 14→15, goals_for 67→70, goals_against 55→57, goal_diff 12→13, points 44→47

Saved 14 standings to standings.json
Done!
```

## Known Limitations
- Assumes static HTML (no JavaScript rendering)
- Scrapes Total table only (ignores Home/Away)
- Only keeps current standings (no historical data)
- No pagination handling (assumes single-page table)

## Automation
**Cronjob setup**: Use `run_scraper.sh` for scheduled execution
```bash
# Example: hourly scraping with logging
0 * * * * /home/dazuki/shl-hockey-scraper/run_scraper.sh >> /home/dazuki/shl-hockey-scraper/cron.log 2>&1
```

## Future Considerations
- Store historical data (append vs overwrite)
- Add Home/Away table options
- CLI arguments for output file/table selection
- Data validation (ensure 14 teams, reasonable stats)

## Last Updated
2025-12-04 - Added change tracking to JSON: update_message + changes array matching git commit format
