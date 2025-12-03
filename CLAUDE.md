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
5. save_to_json() → Write JSON only if changes detected or file missing
```

### Technical Details
- **Library**: BeautifulSoup4 + requests (static HTML parsing)
- **Target**: Total standings table only (not Home/Away)
- **Table Structure**: 11 columns per row (no explicit position column - derived from row index)
- **Output**: JSON with timestamp, league info, 14 teams × 12 fields each
- **Comparison Logic**: Detects position changes, stat changes, team additions/removals
- **Smart Updates**: Only overwrites file when changes detected

### Columns Extracted
```
position (1-14, derived)
team (string)
gp, w, t, l, otw, otl, g, ga, diff, p (all integers)
```

### Error Handling
- Network errors: ConnectionError, Timeout, HTTPError
- Parsing errors: Missing table, malformed rows (skip with warning)
- File I/O errors: Write failures
- All errors print to stderr, exit code 1 on failure

## Project Structure
```
shl-hockey-scraper/
├── scraper.py          # Main script (193 lines)
├── requirements.txt    # requests==2.31.0, beautifulsoup4==4.12.2
├── README.md          # User-facing docs
├── CLAUDE.md          # This file - project memory for Claude
├── .gitignore         # Excludes venv/, *.json, __pycache__/
├── venv/              # Python virtual environment (gitignored)
└── standings.json     # Generated output (gitignored)
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

### Key Implementation Decisions
- **Position derivation**: Use `enumerate(rows[1:], start=1)` since no explicit column
- **Single script**: No need for modules/packages (simple utility)
- **No async**: Single table, small dataset - requests library sufficient
- **Metadata in JSON**: Timestamp helps validate data freshness
- **Print-based logging**: Lightweight, no logging library needed
- **Comparison before write**: Avoid unnecessary file writes, report changes to stdout
- **Team name lookup**: Dict-based comparison for O(1) lookup vs linear search

## JSON Output Format
```json
{
  "timestamp": "2025-12-03T15:29:34.148967",
  "league": "SHL",
  "table_type": "Total",
  "teams_count": 14,
  "standings": [
    {
      "position": 1,
      "team": "Frölunda HC",
      "gp": 23,
      "w": 19,
      "t": 0,
      "l": 4,
      "otw": 0,
      "otl": 0,
      "g": 77,
      "ga": 33,
      "diff": 44,
      "p": 57
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
  - Luleå HF: gp 23→24, w 14→15, g 67→70, ga 55→57, diff 12→13, p 44→47

Saved 14 standings to standings.json
Done!
```

## Known Limitations
- Assumes static HTML (no JavaScript rendering)
- Scrapes Total table only (ignores Home/Away)
- Only keeps current standings (no historical data)
- No scheduling/automation (manual execution)
- No pagination handling (assumes single-page table)

## Future Considerations
- Add cron job for automated scraping
- Store historical data (append vs overwrite)
- Add Home/Away table options
- CLI arguments for output file/table selection
- Data validation (ensure 14 teams, reasonable stats)

## Last Updated
2025-12-03 - Added smart comparison system to prevent unnecessary file writes
