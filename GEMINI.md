# SHL Hockey Scraper - Project Context

## Project Overview
This project is a Python-based web scraper that extracts current SHL (Swedish Hockey League) standings from `sportstatistik.nu` and outputs structured, API-ready JSON data.

**Key Features:**
*   **Source:** Scrapes the "Total" standings table from `https://sportstatistik.nu/hockey/shl/tabell`.
*   **Output:** Generates `standings.json` with metadata (season, timestamp, change logs) and calculated fields.
*   **Smart Updates:** Only updates the output file and triggers changes if actual data shifts are detected.
*   **Change Tracking:** Embeds `update_message` (git-style commit msg) and a detailed `changes` array directly into the JSON.
*   **Automation:** Includes `run_scraper.sh` for cronjob execution.

## Technical Details

### Data Flow
1.  `load_existing_standings()`: Load current `standings.json` if it exists.
2.  `fetch_page()`: HTTP GET with 10s timeout to source URL.
3.  `parse_standings()`: BeautifulSoup extraction of the first table (14 team rows).
4.  `compare_standings()`: Compare old vs new data, detecting position/stat changes.
5.  `generate_commit_message()`: Create concise update message from detected changes.
6.  `save_to_json()`: Write JSON only if changes detected or file is missing.
7.  `git_commit_and_push()`: Auto-commit/push using the generated message.

### Core Logic & Constants
*   **Constants:** `TOTAL_GAMES_IN_SEASON = 52`, `API_VERSION = "1.0.0"`.
*   **Season Detection:** Auto-calculated based on a Sept-April calendar.
*   **Positioning:** Positions (1-14) are derived from row index as they aren't explicit in the HTML.
*   **Comparison:** Uses O(1) dictionary-based lookup for team comparison. Only compares scraped values, ignoring calculated/derived fields.

### Data Fields
**Scraped Values:**
`position`, `team`, `games_played`, `wins`, `ties`, `losses`, `ot_wins`, `ot_losses`, `goals_for`, `goals_against`, `goal_diff`, `points`.

**Calculated Fields:**
*   `win_percentage`: `(wins / games_played) * 100`
*   `points_per_game`: `points / games_played`
*   `goals_per_game`: `goals_for / games_played`
*   `games_remaining`: `52 - games_played`

## Building and Running

### Prerequisites
*   Python 3 & `pip`

### Setup
1.  **Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  **Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Execution
*   **Manual:** `python scraper.py`
*   **Automated (Cron):** `./run_scraper.sh`
    *   Example cron (hourly): `0 * * * * /path/to/run_scraper.sh >> cron.log 2>&1`

## Development Conventions
*   **Single Script:** All logic resides in `scraper.py` (approx. 375 lines).
*   **No Async:** Static HTML source makes `requests` sufficient.
*   **Error Handling:** Connection, Timeout, HTTP, and Parsing errors print to stderr and exit with code 1.
*   **Artifacts:** `standings.json` is machine-generated; do not edit manually.

## Future Considerations
*   Add historical data tracking (currently overwrites).
*   Include Home/Away table options.
*   Implement CLI arguments for table selection.