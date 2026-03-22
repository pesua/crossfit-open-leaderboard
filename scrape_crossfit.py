#!/usr/bin/env python3
"""
Scrape the 2026 CrossFit Open leaderboard and save to CSV.

API: https://c3po.crossfit.com/api/leaderboards/v2/competitions/open/2026/leaderboards
No authentication required. Page size is fixed at 50 rows.
"""

import argparse
import csv
import sys
import time

import requests

BASE_URL = "https://c3po.crossfit.com/api/leaderboards/v2/competitions/open/2026/leaderboards"

DIVISIONS = {
    1: "men",
    2: "women",
}

BASE_PARAMS = {
    "view": 0,       # Open Leaderboard
    "region": 0,     # Worldwide
    "scaled": 0,     # Rx'd
    "sort": 0,       # Overall
}

DELAY_BETWEEN_PAGES = 2  # seconds — be gentle


def fetch_page(page: int, division: int) -> dict:
    params = {**BASE_PARAMS, "division": division, "page": page}
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_csv_row(row: dict, num_workouts: int) -> dict:
    entrant = row["entrant"]
    out = {
        "overall_rank": row["overallRank"],
        "overall_score": row["overallScore"],
        "competitor_id": entrant["competitorId"],
        "name": entrant["competitorName"],
        "age": entrant["age"],
        "country": entrant["countryOfOriginName"],
        "country_code": entrant["countryOfOriginCode"],
        "region": entrant["regionName"],
        "affiliate": entrant["affiliateName"],
        "height": entrant["height"],
        "weight": entrant["weight"],
    }

    scores = {s["ordinal"]: s for s in row.get("scores", [])}
    for i in range(1, num_workouts + 1):
        s = scores.get(i, {})
        out[f"wod_{i}_rank"] = s.get("rank", "")
        out[f"wod_{i}_score"] = s.get("scoreDisplay", "")
        out[f"wod_{i}_scaled"] = "scaled" if s.get("scaled") == "1" else "rx"
        out[f"wod_{i}_video"] = "yes" if s.get("video") == "1" else "no"

    return out


def scrape_division(division_id: int, label: str):
    output_file = f"crossfit_open_2026_{label}.csv"

    print(f"\n=== {label.upper()} (division {division_id}) ===", flush=True)
    print("Fetching page 1 ...", flush=True)
    data = fetch_page(1, division_id)
    total_pages = data["pagination"]["totalPages"]
    total_competitors = data["pagination"]["totalCompetitors"]
    num_workouts = len(data.get("ordinals", []))

    print(f"Total competitors: {total_competitors}")
    print(f"Total pages: {total_pages}  (50 per page)")
    print(f"Workouts: {num_workouts}")
    print(f"Delay between requests: {DELAY_BETWEEN_PAGES}s\n", flush=True)

    first_row = build_csv_row(data["leaderboardRows"][0], num_workouts)
    fieldnames = list(first_row.keys())

    rows_written = 0
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in data["leaderboardRows"]:
            writer.writerow(build_csv_row(row, num_workouts))
            rows_written += 1

        MAX_PAGES = 0
        last_page = min(total_pages, MAX_PAGES) if MAX_PAGES > 0 else total_pages
        for page in range(2, last_page + 1):
            time.sleep(DELAY_BETWEEN_PAGES)
            try:
                data = fetch_page(page, division_id)
            except requests.RequestException as e:
                print(f"  Error on page {page}: {e} — retrying in 5s ...")
                time.sleep(5)
                try:
                    data = fetch_page(page, division_id)
                except requests.RequestException as e2:
                    print(f"  Failed again on page {page}: {e2} — skipping.")
                    continue

            for row in data["leaderboardRows"]:
                writer.writerow(build_csv_row(row, num_workouts))
                rows_written += 1

            if page % 50 == 0 or page == last_page:
                print(f"  Page {page}/{total_pages}  ({rows_written} rows written)", flush=True)

    print(f"Done! {rows_written} rows saved to {output_file}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Scrape CrossFit Open 2026 leaderboard")
    parser.add_argument(
        "--division",
        choices=list(DIVISIONS.values()),
        nargs="+",
        default=list(DIVISIONS.values()),
        help="Division(s) to scrape (default: all)",
    )
    args = parser.parse_args()

    selected = {k: v for k, v in DIVISIONS.items() if v in args.division}
    for division_id, label in selected.items():
        scrape_division(division_id, label)


if __name__ == "__main__":
    main()
