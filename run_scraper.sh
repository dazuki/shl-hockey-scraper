#!/bin/bash

# Get script directory (works even when called from cron)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment
source venv/bin/activate || exit 1

# Run scraper with timestamp
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running SHL scraper..."
python scraper.py
EXIT_CODE=$?

# Log exit status
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Completed successfully"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Failed with exit code $EXIT_CODE" >&2
fi

exit $EXIT_CODE
