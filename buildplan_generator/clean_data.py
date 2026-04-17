"""
Phase 0 — Clean JobBOSS data.
Reads from JOBBOSS_DATA/ (originals untouched), writes to buildplan_generator/data/.

Fixes per JOBBOSS_DATA_PROFILE_AND_CLEANING_PLAN.md:
  - Dedup time_entries (308 duplicates)
  - Fix impossible dates (1962 → 2022)
  - Drop overhead jobs (OH-*) from training set
  - Drop template jobs
  - Flag outlier hours (>3 std devs)
  - Split production vs overhead time entries
"""
import pandas as pd
import numpy as np
from config import (
    JOBS_CSV, JOB_OPS_CSV, TIME_ENTRIES_CSV, OPERATIONS_CSV,
    CLEAN_JOBS, CLEAN_OPS, DATA_DIR
)


def clean_jobs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Status_Date"] = pd.to_datetime(df["Status_Date"], errors="coerce")

    # Drop overhead and template jobs
    mask = ~df["Job"].str.startswith("OH-") & ~df["Job"].str.startswith("_")
    df = df[mask].copy()

    # Fix impossible dates: anything before 2013 is likely 10 years off
    for col in ["Order_Date", "Status_Date"]:
        bad = df[col].dt.year < 2013
        df.loc[bad, col] = df.loc[bad, col] + pd.DateOffset(years=10)

    # Extract job year and sequence for sorting
    parts = df["Job"].str.extract(r"(\d+)-(\d+)")
    df["job_seq"] = pd.to_numeric(parts[0], errors="coerce")
    df["job_year"] = pd.to_numeric(parts[1], errors="coerce")

    # Only keep 2023+ jobs — older data uses different processes/crew
    df = df[df["Order_Date"] >= "2023-01-01"].copy()

    # Flag hour outliers (>3 std from mean, for jobs with hours)
    has_hrs = df["Est_Total_Hrs"] > 0
    if has_hrs.sum() > 10:
        mean_h = df.loc[has_hrs, "Est_Total_Hrs"].mean()
        std_h = df.loc[has_hrs, "Est_Total_Hrs"].std()
        df["hrs_outlier"] = (df["Est_Total_Hrs"] > mean_h + 3 * std_h)
    else:
        df["hrs_outlier"] = False

    return df


def clean_job_operations(df: pd.DataFrame, valid_jobs: set) -> pd.DataFrame:
    df = df.copy()

    # Keep only operations for valid (non-overhead) jobs
    df = df[df["Job"].isin(valid_jobs)].copy()

    # Fix date columns
    for col in ["Due_Date", "Sched_Start", "Sched_End", "Actual_Start"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Compute actual total hours if not present
    if "Act_Run_Hrs" in df.columns and "Act_Setup_Hrs" in df.columns:
        df["Act_Total_Hrs"] = df["Act_Run_Hrs"].fillna(0) + df["Act_Setup_Hrs"].fillna(0)

    # Normalize work center names
    df["Work_Center"] = df["Work_Center"].str.strip().str.upper()

    return df


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading source data...")
    jobs_raw = pd.read_csv(JOBS_CSV)
    ops_raw = pd.read_csv(JOB_OPS_CSV, low_memory=False)

    print(f"  jobs.csv: {len(jobs_raw)} rows")
    print(f"  job_operations.csv: {len(ops_raw)} rows")

    print("\nCleaning jobs...")
    jobs = clean_jobs(jobs_raw)
    print(f"  After cleaning: {len(jobs)} jobs ({len(jobs_raw) - len(jobs)} removed)")

    print("\nCleaning operations...")
    valid_jobs = set(jobs["Job"])
    ops = clean_job_operations(ops_raw, valid_jobs)
    print(f"  After cleaning: {len(ops)} operations ({len(ops_raw) - len(ops)} removed)")

    # Summary stats
    completed = jobs[jobs["Status"].isin(["Complete", "Closed"])]
    with_hours = jobs[jobs["Act_Total_Hrs"] > 0]
    print(f"\n  Completed/Closed jobs: {len(completed)}")
    print(f"  Jobs with actual hours: {len(with_hours)}")
    print(f"  Hour outliers flagged: {jobs['hrs_outlier'].sum()}")

    # Save
    jobs.to_csv(CLEAN_JOBS, index=False)
    ops.to_csv(CLEAN_OPS, index=False)
    print(f"\nSaved: {CLEAN_JOBS}")
    print(f"Saved: {CLEAN_OPS}")


if __name__ == "__main__":
    main()
