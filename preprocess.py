#!/usr/bin/env python3
"""
Preprocess CrossFit Open 2025 CSV data into slim JSON files for the dashboard.

Reads:  crossfit_open_2025_men.csv, crossfit_open_2025_women.csv
Writes: dashboard/static/data/*.json
"""

import argparse
import csv
import json
import math
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd

PERCENTILES = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 96, 97, 98, 99]
AGE_BRACKETS = ["16-17", "18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50+"]
SCATTER_SAMPLE = 5000

# Set by main() after argument parsing
OUT_DIR: Path = Path("dashboard/static/data/2025")
year: int = 2025


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_height_cm(val: str) -> float | None:
    if not val or not val.strip():
        return None
    val = val.strip()
    if val.endswith("cm"):
        return float(val.replace("cm", "").strip())
    if val.endswith("in"):
        return round(float(val.replace("in", "").strip()) * 2.54, 1)
    return None


def parse_weight_kg(val: str) -> float | None:
    if not val or not val.strip():
        return None
    val = val.strip()
    if val.endswith("kg"):
        return float(val.replace("kg", "").strip())
    if val.endswith("lb"):
        return round(float(val.replace("lb", "").strip()) * 0.453592, 1)
    return None


def get_age_bracket(age: int) -> str:
    if age <= 17:
        return "16-17"
    if age <= 24:
        return "18-24"
    if age <= 29:
        return "25-29"
    if age <= 34:
        return "30-34"
    if age <= 39:
        return "35-39"
    if age <= 44:
        return "40-44"
    if age <= 49:
        return "45-49"
    return "50+"


def parse_score_numeric(score_str: str):
    """Return (numeric_value, score_type) or (None, None)."""
    if not score_str or not score_str.strip():
        return None, None
    clean = score_str.split(" - ")[0].strip()
    if "reps" in clean:
        try:
            return int(clean.replace("reps", "").strip()), "reps"
        except ValueError:
            return None, None
    m = re.match(r"^(\d{1,2}):(\d{2})$", clean)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)), "time"
    return None, None


# ---------------------------------------------------------------------------
# Load and clean
# ---------------------------------------------------------------------------

def load_and_clean(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype=str).fillna("")

    # Drop DNS (no scores on any WOD)
    has_score = (df["wod_1_score"].ne("")) | (df["wod_2_score"].ne("")) | (df["wod_3_score"].ne(""))
    df = df[has_score].copy()

    # Numeric conversions
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0).astype(int)
    df["overall_rank"] = pd.to_numeric(df["overall_rank"], errors="coerce")
    df["overall_score"] = pd.to_numeric(df["overall_score"], errors="coerce")

    # Height / weight
    df["height_cm"] = df["height"].apply(parse_height_cm)
    df["weight_kg"] = df["weight"].apply(parse_weight_kg)

    # Age bracket
    df["age_bracket"] = df["age"].apply(get_age_bracket)

    # Per-WOD parsing
    for wod in [1, 2, 3]:
        col_score = f"wod_{wod}_score"
        col_scaled = f"wod_{wod}_scaled"
        col_rank = f"wod_{wod}_rank"

        df[col_rank] = pd.to_numeric(df[col_rank], errors="coerce")

        parsed = df[col_score].apply(lambda s: parse_score_numeric(s))
        df[f"wod_{wod}_numeric"] = parsed.apply(lambda x: x[0])
        df[f"wod_{wod}_type"] = parsed.apply(lambda x: x[1])
        df[f"wod_{wod}_is_scaled"] = df[col_scaled].eq("scaled")

    return df


# ---------------------------------------------------------------------------
# Output generators
# ---------------------------------------------------------------------------

def compute_percentile_breakpoints(series: pd.Series) -> dict:
    """Compute percentile breakpoints for a numeric series, dropping NaN."""
    vals = series.dropna().values
    if len(vals) < 10:
        return None
    result = {"n": int(len(vals)), "min": float(np.min(vals)), "max": float(np.max(vals))}
    for p in PERCENTILES:
        result[f"p{p}"] = float(np.percentile(vals, p))
    return result


def write_percentiles(df: pd.DataFrame, gender: str):
    """Write percentile breakpoints for overall + each WOD, by age bracket."""
    out = {}

    # Overall rank percentiles (lower rank = better)
    out["overall"] = {"all": compute_percentile_breakpoints(df["overall_rank"])}
    for bracket in AGE_BRACKETS:
        sub = df[df["age_bracket"] == bracket]
        bp = compute_percentile_breakpoints(sub["overall_rank"])
        if bp:
            out["overall"][bracket] = bp

    # Per-WOD score percentiles, split by rx/scaled and score type (reps vs time)
    for wod in [1, 2, 3]:
        key = f"wod_{wod}"
        out[key] = {"rx": {}, "scaled": {}}
        for tier, is_scaled in [("rx", False), ("scaled", True)]:
            sub = df[df[f"wod_{wod}_is_scaled"] == is_scaled]
            sub = sub[sub[f"wod_{wod}_numeric"].notna()]
            for stype in ["reps", "time"]:
                stype_sub = sub[sub[f"wod_{wod}_type"] == stype]
                if len(stype_sub) < 10:
                    continue
                out[key][tier][stype] = {}
                bp = compute_percentile_breakpoints(stype_sub[f"wod_{wod}_numeric"])
                if bp:
                    out[key][tier][stype]["all"] = bp
                for bracket in AGE_BRACKETS:
                    bsub = stype_sub[stype_sub["age_bracket"] == bracket]
                    bp_bracket = compute_percentile_breakpoints(bsub[f"wod_{wod}_numeric"])
                    if bp_bracket:
                        out[key][tier][stype][bracket] = bp_bracket

    path = OUT_DIR / f"percentiles.{gender}.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"  Written {path} ({path.stat().st_size:,} bytes)", flush=True)


def write_distributions(df: pd.DataFrame, gender: str):
    """Write histogram bins for overall rank and each WOD score."""
    out = {}
    n_bins = 50

    # Overall rank distribution
    vals = df["overall_rank"].dropna().values
    counts, edges = np.histogram(vals, bins=n_bins)
    out["overall_rank"] = {
        "bins": [
            {"lo": round(float(edges[i]), 1), "hi": round(float(edges[i + 1]), 1), "count": int(counts[i])}
            for i in range(n_bins)
        ],
        "domain": [float(edges[0]), float(edges[-1])],
        "n": int(len(vals)),
    }

    # Per-WOD distributions
    for wod in [1, 2, 3]:
        key = f"wod_{wod}"
        out[key] = {}

        for tier, is_scaled in [("rx", False), ("scaled", True)]:
            sub = df[(df[f"wod_{wod}_is_scaled"] == is_scaled) & df[f"wod_{wod}_numeric"].notna()]
            if len(sub) < 10:
                continue

            # Split by score type for WOD 2/3 (time finishers vs time-capped reps)
            for stype in sub[f"wod_{wod}_type"].unique():
                svals = sub[sub[f"wod_{wod}_type"] == stype][f"wod_{wod}_numeric"].values.astype(float)
                if len(svals) < 10:
                    continue
                counts, edges = np.histogram(svals, bins=n_bins)
                label = f"{tier}_{stype}" if stype else tier
                out[key][label] = {
                    "bins": [
                        {"lo": round(float(edges[i]), 1), "hi": round(float(edges[i + 1]), 1), "count": int(counts[i])}
                        for i in range(n_bins)
                    ],
                    "domain": [float(edges[0]), float(edges[-1])],
                    "n": int(len(svals)),
                    "score_type": stype,
                }

    path = OUT_DIR / f"distributions.{gender}.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"  Written {path} ({path.stat().st_size:,} bytes)", flush=True)


def write_age_distributions(df: pd.DataFrame, gender: str):
    """Write per-WOD percentile breakpoints of raw scores by age bracket (Rx only)."""
    out = {}
    age_pctiles = [5, 10, 25, 50, 75, 90, 95]  # fewer for age breakdowns
    for wod in [1, 2, 3]:
        key = f"wod_{wod}"
        out[key] = {}
        rx = df[(~df[f"wod_{wod}_is_scaled"]) & df[f"wod_{wod}_numeric"].notna()]
        for bracket in AGE_BRACKETS:
            sub = rx[rx["age_bracket"] == bracket]
            vals = sub[f"wod_{wod}_numeric"].dropna().values.astype(float)
            if len(vals) < 10:
                continue
            bp = {"n": int(len(vals))}
            for p in age_pctiles:
                bp[f"p{p}"] = round(float(np.percentile(vals, p)), 1)
            out[key][bracket] = bp

    path = OUT_DIR / f"age_distributions.{gender}.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"  Written {path} ({path.stat().st_size:,} bytes)", flush=True)


def write_scatter(df: pd.DataFrame, gender: str, field: str, out_name: str):
    """Write stratified scatter sample for height or weight vs overall rank."""
    col = field  # "height_cm" or "weight_kg"
    valid = df[df[col].notna() & df["overall_rank"].notna()].copy()
    if len(valid) == 0:
        return

    # Stratified sample by age bracket
    points = []
    bracket_counts = valid["age_bracket"].value_counts()
    total_valid = len(valid)
    for bracket in AGE_BRACKETS:
        bsub = valid[valid["age_bracket"] == bracket]
        if len(bsub) == 0:
            continue
        n_sample = max(10, int(SCATTER_SAMPLE * len(bsub) / total_valid))
        sample = bsub.sample(n=min(n_sample, len(bsub)), random_state=42)
        bracket_idx = AGE_BRACKETS.index(bracket)
        for _, row in sample.iterrows():
            points.append([
                round(float(row[col]), 1),
                int(row["overall_rank"]),
                bracket_idx,
            ])

    out = {
        "field": field,
        "age_brackets": AGE_BRACKETS,
        "n_sampled": len(points),
        "n_total": total_valid,
        "points": points,
    }

    path = OUT_DIR / f"{out_name}.{gender}.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"  Written {path} ({path.stat().st_size:,} bytes)", flush=True)


def write_meta(men_df: pd.DataFrame, women_df: pd.DataFrame):
    """Write metadata about the competition."""
    def gender_meta(df: pd.DataFrame, label: str) -> dict:
        total = len(df)
        meta = {
            "label": label,
            "total_athletes": total,
            "age_brackets": AGE_BRACKETS,
            "regions": sorted(df["region"].unique().tolist()),
            "wods": [],
        }
        for wod in [1, 2, 3]:
            rx = df[~df[f"wod_{wod}_is_scaled"] & df[f"wod_{wod}_numeric"].notna()]
            scaled = df[df[f"wod_{wod}_is_scaled"] & df[f"wod_{wod}_numeric"].notna()]
            types = rx[f"wod_{wod}_type"].value_counts().to_dict()
            short_year = str(year)[2:]
            meta["wods"].append({
                "index": wod,
                "name": f"{short_year}.{wod}",
                "rx_count": int(len(rx)),
                "scaled_count": int(len(scaled)),
                "score_types": {k: int(v) for k, v in types.items()},
            })
        return meta

    out = {
        "men": gender_meta(men_df, "Men"),
        "women": gender_meta(women_df, "Women"),
    }
    path = OUT_DIR / "meta.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"  Written {path} ({path.stat().st_size:,} bytes)", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Preprocess CrossFit Open CSV data")
    parser.add_argument("--year", type=int, default=2025, help="Competition year (e.g. 2026)")
    args = parser.parse_args()

    global OUT_DIR, year
    year = args.year
    OUT_DIR = Path(f"dashboard/static/data/{year}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Processing {year} data...", flush=True)

    print("Loading men's data...", flush=True)
    men = load_and_clean(f"crossfit_open_{year}_men.csv")
    print(f"  {len(men)} athletes (after DNS removal)", flush=True)

    print("Loading women's data...", flush=True)
    women = load_and_clean(f"crossfit_open_{year}_women.csv")
    print(f"  {len(women)} athletes (after DNS removal)", flush=True)

    for gender, df in [("men", men), ("women", women)]:
        print(f"\nProcessing {gender}...", flush=True)
        write_percentiles(df, gender)
        write_distributions(df, gender)
        write_age_distributions(df, gender)
        write_scatter(df, gender, field="height_cm", out_name="scatter_height")
        write_scatter(df, gender, field="weight_kg", out_name="scatter_weight")

    print("\nWriting metadata...", flush=True)
    write_meta(men, women)

    # Summary
    total_size = sum(f.stat().st_size for f in OUT_DIR.glob("*.json"))
    print(f"\nDone! {len(list(OUT_DIR.glob('*.json')))} JSON files, {total_size:,} bytes total", flush=True)


if __name__ == "__main__":
    main()
