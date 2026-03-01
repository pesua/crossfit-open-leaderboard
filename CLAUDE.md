# CLAUDE.md

## Project Overview

CrossFit Games Open leaderboard scraper. Fetches athlete data from the public `c3po.crossfit.com` API and saves it as CSV.

## Key Files

- `scrape_crossfit.py` — Main scraper script
- `cdp_intercept.py` — Chrome DevTools Protocol helper used for API reverse-engineering (not needed at runtime)
- `main.py` — Placeholder entry point (unused)

## API Reference

- **Leaderboard endpoint:** `GET https://c3po.crossfit.com/api/leaderboards/v2/competitions/open/2025/leaderboards`
- **Competition metadata:** `GET https://c3po.crossfit.com/api/competitions/v1/competitions/open/2025?expand[]=controls&expand[]=view0`
- No authentication required
- Fixed page size of 50, 1-indexed pagination
- Division IDs: `1` = Men, `2` = Women, `11` = Team (see scraper for age groups)

## Commands

```sh
uv sync                        # Install dependencies
uv run scrape_crossfit.py      # Run the scraper
```

## Conventions

- Use `uv` for dependency management (not pip)
- All print statements should use `flush=True` for real-time log output
- Respect rate limits: keep `DELAY_BETWEEN_PAGES >= 2` seconds
- CSV files are output artifacts, not checked in
