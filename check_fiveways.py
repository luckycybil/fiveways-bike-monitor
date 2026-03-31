#!/usr/bin/env python3
"""
Fiveways Bike Monitor
Checks Beryl bike availability at Fiveways (station 7307) and appends to fiveways_log.csv.
Designed to run daily via GitHub Actions.
"""

import urllib.request
import json
import csv
import os
from datetime import datetime, timezone

# --- Config ---
STATION_ID = "7307"
STATION_NAME = "Fiveways"
STATUS_URL = "https://beryl-gbfs-production.web.app/v2_2/Brighton/station_status.json"
LOG_FILE = "fiveways_log.csv"


def fetch_station_status():
    """Fetch live station status from Beryl's GBFS feed."""
    with urllib.request.urlopen(STATUS_URL, timeout=10) as response:
        data = json.loads(response.read().decode())
    for station in data["data"]["stations"]:
        if station["station_id"] == STATION_ID:
            return station
    raise ValueError(f"Station {STATION_ID} not found in feed")


def log_result(station):
    """Append a row to the CSV log file."""
    file_exists = os.path.exists(LOG_FILE)
    now = datetime.now(timezone.utc)  # GitHub Actions runs in UTC

    bikes = station["num_bikes_available"]
    docks = station["num_docks_available"]
    available = "YES" if bikes > 0 else "NO"

    row = {
        "date": now.strftime("%Y-%m-%d"),
        "time_utc": now.strftime("%H:%M"),
        "bikes_available": bikes,
        "docks_available": docks,
        "bike_available_yn": available,
    }

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"[{row['date']} {row['time_utc']} UTC] {STATION_NAME}: "
          f"{bikes} bike(s) available, {docks} dock(s) free — logged to {LOG_FILE}")


def main():
    try:
        station = fetch_station_status()
        log_result(station)
    except Exception as e:
        now = datetime.now(timezone.utc)
        print(f"[{now.strftime('%Y-%m-%d %H:%M')} UTC] ERROR: {e}")
        raise  # Re-raise so GitHub Actions marks the run as failed


if __name__ == "__main__":
    main()
