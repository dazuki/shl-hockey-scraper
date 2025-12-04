# SHL Hockey Scraper

Python scraper for extracting SHL (Swedish Hockey League) standings from sportstatistik.nu.

## Features

- Scrapes Total standings table (14 teams)
- Extracts all available columns with descriptive names
- API-ready JSON output with metadata and calculated stats
- Auto-calculated season detection (Sept-April SHL calendar)
- Per-team calculated fields: win%, PPG, GPG, games remaining
- Smart comparison - only updates file when changes detected
- Reports specific changes (position shifts, stat updates) to stdout
- **Change tracking embedded in JSON** - update message + detailed changes array
- Auto-commits and pushes changes to git with descriptive messages
- Error handling for network and parsing failures

## Setup

### 1. Create virtual environment
```bash
python3 -m venv venv
```

### 2. Activate virtual environment
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python scraper.py
```

### Behavior

- **First run**: Creates `standings.json` with scraped data
- **No changes**: Prints "No changes detected" and doesn't modify file
- **Changes detected**: Reports specific changes and updates `standings.json`

### Example Output

```
# No changes
Fetching SHL standings from https://sportstatistik.nu/hockey/shl/tabell...
Found 14 teams in Total standings table
No changes detected - standings.json not modified
Done!

# Changes detected
Fetching SHL standings from https://sportstatistik.nu/hockey/shl/tabell...
Found 14 teams in Total standings table

3 change(s) detected:
  - Frölunda HC: pos 1 → 2
  - Skellefteå AIK: pos 2 → 1
  - Luleå HF: games_played 23→24, wins 14→15, goals_for 67→70, goals_against 55→57, goal_diff 12→13, points 44→47

Saved 14 standings to standings.json
Done!
```

## Automated Scheduling

Use `run_scraper.sh` for cronjob execution. Script includes:
- Absolute paths (cron-compatible)
- Virtual environment activation
- Timestamped logging
- Exit code handling

### Setup Cronjob

```bash
crontab -e
```

Add one of these entries:

```bash
# Every hour
0 * * * * /home/dazuki/shl-hockey-scraper/run_scraper.sh >> /home/dazuki/shl-hockey-scraper/cron.log 2>&1

# Every 30 minutes
*/30 * * * * /home/dazuki/shl-hockey-scraper/run_scraper.sh >> /home/dazuki/shl-hockey-scraper/cron.log 2>&1

# Daily at 8 AM
0 8 * * * /home/dazuki/shl-hockey-scraper/run_scraper.sh >> /home/dazuki/shl-hockey-scraper/cron.log 2>&1
```

Output logged to `cron.log` with timestamps.

## Output Format

### Top-level Metadata
- `api_version`: Schema version for tracking format changes
- `timestamp`: ISO 8601 timestamp of data fetch
- `season`: Auto-detected season (e.g., "2024-2025")
- `league`: League identifier ("SHL")
- `table_type`: Standings type ("Total")
- `data_source`: Source URL
- `total_games_in_season`: Regular season game count (52)
- `teams_count`: Number of teams
- `update_message`: Concise commit message describing changes (null on initial creation)
- `changes`: Array of detailed change descriptions (empty array on initial creation)

### Team Fields
**Scraped values:**
- `position`, `team`, `games_played`, `wins`, `ties`, `losses`
- `ot_wins`, `ot_losses`, `goals_for`, `goals_against`, `goal_diff`, `points`

**Calculated fields:**
- `win_percentage`: (wins / games_played) × 100
- `points_per_game`: points / games_played
- `goals_per_game`: goals_for / games_played
- `games_remaining`: 52 - games_played

### Example JSON

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
    }
  ]
}
```

## Dependencies

- requests 2.31.0
- beautifulsoup4 4.12.2

## Source

Data scraped from: https://sportstatistik.nu/hockey/shl/tabell
