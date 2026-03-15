# 2025 CrossFit Open — Leaderboard Explorer

Scrape the CrossFit Open leaderboard, preprocess it, and serve an interactive scrollytelling dashboard where athletes can enter their scores and see how they rank worldwide.

## Project Structure

```
scrape_crossfit.py   — Fetch leaderboard data from the CrossFit API → CSV
preprocess.py        — Transform CSVs into optimised JSON for the dashboard
dashboard/           — SvelteKit web app (scrollytelling visualisation)
```

## Pipeline

### 1. Scrape

Fetches athlete data from the public `c3po.crossfit.com` API and saves it as CSV.

```sh
uv sync
uv run scrape_crossfit.py
```

Outputs `crossfit_open_2025_men.csv` and (after editing `PARAMS["division"]`) `crossfit_open_2025_women.csv`.

#### Scraper configuration

| Constant | Description |
|----------|-------------|
| `PARAMS["division"]` | `1` = Men, `2` = Women (see script for all division IDs) |
| `PARAMS["region"]` | `0` = Worldwide, or a specific region ID |
| `PARAMS["scaled"]` | `0` = Rx'd, `1` = Scaled, `2` = Foundations |
| `DELAY_BETWEEN_PAGES` | Seconds between API requests (default: 2) |
| `MAX_PAGES` | Cap page count for testing (`0` = fetch all) |

**API:** `GET https://c3po.crossfit.com/api/leaderboards/v2/competitions/open/2025/leaderboards` — no auth, 50 rows/page.

**CSV columns:** `overall_rank`, `overall_score`, `competitor_id`, `name`, `age`, `country`, `country_code`, `region`, `affiliate`, `height`, `weight`, plus per-workout columns `wod_N_rank`, `wod_N_score`, `wod_N_scaled`, `wod_N_video`.

### 2. Preprocess

Transforms the raw CSVs into slim JSON files consumed by the dashboard.

```sh
uv run preprocess.py
```

Writes to `dashboard/static/data/`:

| File | Contents |
|------|----------|
| `meta.json` | Athlete counts, age brackets, WOD names |
| `percentiles.{men,women}.json` | Percentile breakpoints for overall rank and each WOD, by tier and age bracket |
| `distributions.{men,women}.json` | Histogram bins for overall rank and per-WOD scores |
| `age_distributions.{men,women}.json` | Per-WOD score percentiles broken down by age bracket (Rx only) |
| `scatter_height.{men,women}.json` | Stratified sample of height vs overall rank |
| `scatter_weight.{men,women}.json` | Stratified sample of weight vs overall rank |

### 3. Dashboard

SvelteKit app. Enter your scores to get a personalised breakdown across 8 scrollytelling steps:

1. **Overall percentile** — gauge vs all competitors
2. **Age-group percentile** — same gauge filtered to your bracket
3. **Score vs age groups** — box plot of 25.1 across all age brackets
4. **25.1 distribution** — histogram with your score highlighted
5. **25.2 distribution** — histogram with your score highlighted
6. **25.3 distribution** — histogram with your score highlighted
7. **Score vs height** — scatter plot (optionally coloured by age group)
8. **Score vs weight** — scatter plot

```sh
cd dashboard
npm install      # first time only
npm run dev      # http://localhost:5173
npm run build    # production build → dashboard/build/
```

## Dev Container

Includes a devcontainer config (forwards ports 3000, 5173, 8000, 8080).

```sh
devcontainer up --workspace-folder .
```
