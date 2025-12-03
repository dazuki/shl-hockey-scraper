# SHL Hockey Scraper

Python scraper for extracting SHL (Swedish Hockey League) standings from sportstatistik.nu.

## Features

- Scrapes Total standings table (14 teams)
- Extracts all available columns (position, team, GP, W, T, L, OTW, OTL, G, GA, +/-, P)
- Outputs structured JSON with metadata
- Smart comparison - only updates file when changes detected
- Reports specific changes (position shifts, stat updates) to stdout
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
  - Luleå HF: gp 23→24, w 14→15, g 67→70, ga 55→57, diff 12→13, p 44→47

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

```json
{
  "timestamp": "2025-12-03T10:30:45.123456",
  "league": "SHL",
  "table_type": "Total",
  "teams_count": 14,
  "standings": [
    {
      "position": 1,
      "team": "Team Name",
      "gp": 20,
      "w": 15,
      "t": 2,
      "l": 3,
      "otw": 0,
      "otl": 0,
      "g": 95,
      "ga": 65,
      "diff": 30,
      "p": 47
    }
  ]
}
```

## Dependencies

- requests 2.31.0
- beautifulsoup4 4.12.2

## Source

Data scraped from: https://sportstatistik.nu/hockey/shl/tabell
