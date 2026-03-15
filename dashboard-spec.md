# CrossFit Open 2025 Scrollytelling Dashboard — Visualization Specification

## Overview

A scrollytelling dashboard built with SvelteKit + Scrollama that lets athletes enter their CrossFit Open 2025 scores and compare their performance against 113K+ men and 90K+ women worldwide.

**Tech stack:** SvelteKit 2.x · Svelte 5 · D3 (scale, shape, array, format) · Scrollama 3 · Canvas API
**Data:** 11 precomputed JSON files in `static/data/`

---

## User Input

Before the scrollytelling begins, the user fills in:

| Field | Type | Notes |
|-------|------|-------|
| Gender | Toggle | Men / Women |
| Age | Number (14–65) | Auto-mapped to 8 age brackets |
| WOD 1 score | Reps + Rx/Scaled | 25.1 — reps only |
| WOD 2 score | Reps or MM:SS + Rx/Scaled | 25.2 — reps if incomplete, time if finished |
| WOD 3 score | Reps or MM:SS + Rx/Scaled | 25.3 — same as 25.2 |

**Age brackets:** 16–17, 18–24, 25–29, 30–34, 35–39, 40–44, 45–49, 50+

Derived stats are computed reactively:
- Per-WOD percentile via interpolation between precomputed p1–p99 breakpoints
- Overall percentile = average of valid WOD percentiles
- Age-group percentile = same logic using bracket-specific breakpoints

---

## Scrollytelling Layout

- Desktop: sticky chart column (right) + scroll steps column (left, 40% width)
- Mobile: stacked, each step min-height 40vh
- Scrollama threshold: 45% of viewport
- 8 steps total (Step 0–7), chart swaps on each step trigger

---

## Step 0 — Overall Ranking

**Component:** `PercentileGauge`
**Chart type:** Animated semicircular arc gauge (SVG, 300×170 viewBox)

**What it shows:**
- User's overall percentile across all 3 WODs vs. the full gender division
- "Better than ~X of Y athletes" below the gauge
- "Top X%" animated counter in the center (1200ms cubic-out easing)

**Color coding:**
| Range | Color |
|-------|-------|
| 90%+ | Green |
| 70–89% | Lime |
| 50–69% | Yellow |
| 30–49% | Orange |
| <30% | Red |

**Data:** `$stats.overallPercentile`, `meta[gender].total_athletes`

---

## Step 1 — Age Group Ranking

**Component:** `PercentileGauge` (same as Step 0)
**Chart type:** Animated semicircular arc gauge

**What it shows:**
- User's percentile recomputed within their specific age bracket
- Subtitle shows "Age X / Bracket label"
- Often differs significantly from overall ranking

**Data:** `$stats.ageGroupPercentile`, `$ageBracket`, `percentiles[gender]` (bracket-specific breakpoints)

---

## Step 2 — Age Group Box Plot (WOD 1 / 25.1)

**Component:** `BoxPlot`
**Chart type:** SVG box-and-whisker plot, one box per age bracket (8 total)

**What it shows:**
- Score distribution spread per age bracket on WOD 1
- User's score overlaid as a highlighted dot on their bracket

**Visual details:**
- Whiskers: p10–p90 (1.5px lines with horizontal caps)
- Box: p25–p75 (semi-transparent fill, 1.5px border, 3px radius)
- Median: p50 horizontal line (2.5px)
- User dot: 6px circle, white 2px stroke, gold color on their bracket
- Bracket colors: 8 distinct (indigo → blue → pink → red → orange → yellow → green → cyan)
- For time-scored WODs: y-axis is inverted (lower time = better)

**Axes:**
- X: Age bracket labels (10px font)
- Y: Score range, 5 ticks, `d3.scaleLinear().nice()`
- Horizontal gridlines at y-ticks (0.3 opacity)

**Data:** `age_distributions[gender].wod_1` → `{n, p5, p10, p25, p50, p75, p90, p95}` per bracket
**Sample size** shown at bottom per bracket

---

## Step 3 — WOD 1 (25.1) Score Distribution

**Component:** `DistributionHistogram`
**Chart type:** SVG bar chart (histogram)

**What it shows:**
- Distribution of all athlete scores for 25.1 in user's division + tier (Rx or Scaled)
- User's score marked with a vertical dashed line + label
- User's bin highlighted in amber; all others in indigo

**Visual details:**
- Bars: pre-binned `{lo, hi, count}` tuples (50 bins), 2px rounded corners
- User bin: amber (`--highlight`), full opacity
- Other bins: indigo (`--accent`), 0.7 opacity
- User marker: 2.5px dashed vertical line (6–3 dash pattern), label above

**Axes (600×340 default, margin 24/20/40/50):**
- X: Score range, 6 ticks, formatted as reps (integer) or time (M:SS)
- Y: Count, abbreviated (e.g. "10.5k")
- Horizontal gridlines at y-ticks (0.3 opacity)

**Data:** `distributions[gender].wod_1.{rx|scaled}_reps`
**Selection logic:** tier from user input (Rx/Scaled); 25.1 is always reps

---

## Step 4 — WOD 2 (25.2) Score Distribution

**Component:** `DistributionHistogram` (identical to Step 3)

**What it shows:**
- Same as Step 3 but for 25.2
- 25.2 can be reps (if athlete didn't finish) OR time (if finished) — distribution selected to match user's input

**4 possible distributions:** `rx_reps`, `rx_time`, `scaled_reps`, `scaled_time`

**Data:** `distributions[gender].wod_2.{rx|scaled}_{reps|time}`
**Selection logic:** tier + score type derived from user's 25.2 input format

---

## Step 5 — WOD 3 (25.3) Score Distribution

**Component:** `DistributionHistogram` (identical to Steps 3–4)

**What it shows:**
- Same as Step 4 but for 25.3
- Same reps/time duality as 25.2

**Data:** `distributions[gender].wod_3.{rx|scaled}_{reps|time}`

---

## Step 6 — Score vs. Height Scatter Plot

**Component:** `ScatterCanvas`
**Chart type:** Canvas (dots) + SVG overlay (axes)

**What it shows:**
- Sampled population plotted as height (cm) vs. overall rank
- User dot overlaid in amber with white stroke
- Optional: color dots by age bracket

**Visual details:**
- Population dots: 2px circles, indigo with 0x50 alpha (default) OR 8 bracket colors with 0x80 alpha
- User dot: 8px amber circle, 2.5px white stroke
- High-DPR canvas scaling
- Axes rendered in SVG overlay (5 ticks each axis)

**Axes:**
- X: Height in cm ("165 cm")
- Y: Overall rank (0 → total athletes), labeled "Overall Rank"

**Interaction:**
- Checkbox: "Color by age group" — toggles per-bracket coloring + legend

**Data:** `scatter_height[gender]` → `{ points: [height_cm, rank, ageIdx][], n_sampled, n_total, age_brackets[] }`
**User Y:** `Math.round(total_athletes × (1 − overallPercentile/100))`

---

## Step 7 — Score vs. Weight Scatter Plot

**Component:** `ScatterCanvas` (identical to Step 6)

**What it shows:**
- Same as Step 6 but X-axis is body weight (kg)
- Explores correlation between weight and CrossFit performance

**Axes:**
- X: Weight in kg ("75 kg")
- Y: Overall rank

**Data:** `scatter_weight[gender]` → same structure as height data

---

## Data Files Reference

All files in `dashboard/static/data/`:

| File | Contents |
|------|----------|
| `meta.json` | Athlete counts, WOD names, age bracket labels per gender |
| `percentiles.{men,women}.json` | p1–p99 breakpoints: overall + per-WOD + per-age-bracket |
| `distributions.{men,women}.json` | 50-bin histograms for each WOD × tier × score type |
| `age_distributions.{men,women}.json` | Box plot stats (p5–p95) per age bracket per WOD |
| `scatter_height.{men,women}.json` | Sampled (height, rank, ageIdx) tuples |
| `scatter_weight.{men,women}.json` | Sampled (weight, rank, ageIdx) tuples |

---

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0f172a` | Page background |
| `--bg-secondary` | `#1e293b` | Card backgrounds |
| `--bg-tertiary` | `#334155` | Borders, dividers |
| `--accent` | `#6366f1` | Indigo — population bars/dots |
| `--highlight` | `#f59e0b` | Amber — user marker |

---

## Summary Table

| Step | Title | Chart | Key Feature |
|------|-------|-------|-------------|
| 0 | Overall Ranking | Semicircle gauge | Animated fill, color by percentile |
| 1 | Age Group Ranking | Semicircle gauge | Bracket-specific percentile |
| 2 | Age Comparison | Box plot (8 brackets) | User dot overlay, inverted for time |
| 3 | WOD 1 Distribution | Histogram | User bin + dashed marker |
| 4 | WOD 2 Distribution | Histogram | Reps vs. time variant |
| 5 | WOD 3 Distribution | Histogram | Reps vs. time variant |
| 6 | Height vs. Rank | Canvas scatter | Color-by-age toggle |
| 7 | Weight vs. Rank | Canvas scatter | Color-by-age toggle |
