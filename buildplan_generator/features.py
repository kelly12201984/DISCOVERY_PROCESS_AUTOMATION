"""
Extract features from each historical job for similarity matching.

Feature vector per job:
  - total_est_hours: overall job estimate
  - total_act_hours: overall actual
  - n_operations: how many ops in routing
  - n_ops_with_hours: ops that have estimated hours > 0
  - op_presence: binary vector — which of the ~208 master ops are present
  - wc_hours: hours allocated per work center
  - has_manway, has_skirt, has_ladder, has_jacket, has_coil, has_baffles,
    has_cladding, has_platform: boolean flags from operation presence
  - tank_type: classified from description text
"""
import re
import pandas as pd
import numpy as np
from config import (
    CLEAN_JOBS, CLEAN_OPS, OPERATIONS_CSV,
    JOB_FEATURES, ROUTING_CATALOG, DATA_DIR
)

# Op-code ranges that signal tank features
FEATURE_OPS = {
    "has_manway":   [".115", ".120", ".125", ".130", ".135", ".140"],
    "has_skirt":    [".175", ".180", ".185", ".500", ".510", ".515", ".520", ".530", ".540", ".545"],
    "has_ladder":   [".262", ".265", ".270"],
    "has_handrail": [".272", ".275", ".280", ".282"],
    "has_platform": [".285", ".290", ".292", ".295"],
    "has_jacket":   [".477", ".478", ".479", ".700", ".705", ".710", ".711"],
    "has_coil":     [".250", ".580", ".590", ".635"],
    "has_baffles":  [".215", ".220", ".225", ".230", ".625"],
    "has_cladding": [".145", ".147"],
    "has_dip_tubes": [".110", ".735", ".740"],
    "has_stiffeners": [".235", ".375", ".475"],
    "has_body_flange": [".325", ".326", ".382", ".383", ".482", ".483"],
}

TANK_PATTERNS = {
    "storage_tank":  r"storage\s+tank|bulk\s+storage",
    "buffer_tank":   r"buffer\s+tank",
    "dissolving_tank": r"dissolving|smelt",
    "reactor":       r"reactor|cstr|packed\s+bed",
    "separator":     r"separator|stripper",
    "surge_tank":    r"surge\s+tank",
    "flash_tank":    r"flash\s+tank",
    "dryer_plate":   r"dryer\s+plate",
    "handrail_ladder": r"handrail|ladder",
    "heat_exchanger": r"exchanger|heater|cooler",
    "vessel":        r"vessel|pressure",
    "tank":          r"tank",
}


def classify_tank_type(desc: str) -> str:
    if not isinstance(desc, str):
        return "unknown"
    desc_lower = desc.lower()
    for ttype, pattern in TANK_PATTERNS.items():
        if re.search(pattern, desc_lower):
            return ttype
    return "other"


def extract_features(jobs: pd.DataFrame, ops: pd.DataFrame) -> pd.DataFrame:
    """Build feature table: one row per job."""
    # Get all unique op codes from operations
    all_op_codes = sorted(ops["Description"].dropna().unique())  # not ideal, use Sequence+Description

    # Work center hour totals per job
    wc_hours = ops.groupby(["Job", "Work_Center"])["Est_Total_Hrs"].sum().unstack(fill_value=0)
    wc_hours.columns = [f"wc_hrs_{c.replace(' ', '_').lower()}" for c in wc_hours.columns]

    # Operation-level features per job
    op_stats = ops.groupby("Job").agg(
        n_operations=("Sequence", "count"),
        n_ops_with_hours=("Est_Total_Hrs", lambda x: (x > 0).sum()),
        total_est_hrs=("Est_Total_Hrs", "sum"),
        total_act_hrs=("Act_Total_Hrs", "sum") if "Act_Total_Hrs" in ops.columns else ("Est_Total_Hrs", "sum"),
    )

    # Boolean feature flags from operation descriptions
    desc_lower = ops.copy()
    desc_lower["desc_lower"] = desc_lower["Description"].fillna("").str.lower()

    for feat, op_keywords in FEATURE_OPS.items():
        # Check if any of the op codes for this feature appear in the job's operations
        # We match on description substrings since op codes vary between JobBOSS and build plans
        mask = ops.groupby("Job").apply(
            lambda g: any(
                any(kw.replace(".", "").lower() in str(row.get("Description", "")).lower()
                    or str(row.get("Sequence", "")) == kw.replace(".", "")
                    for kw in op_keywords)
                for _, row in g.iterrows()
            )
        )
        op_stats[feat] = mask

    # Join with job-level data
    job_info = jobs.set_index("Job")[
        ["Customer", "Description", "Status", "Order_Date", "Total_Price",
         "Est_Total_Hrs", "Act_Total_Hrs"]
    ].rename(columns={"Est_Total_Hrs": "job_est_hrs", "Act_Total_Hrs": "job_act_hrs"})

    job_info["tank_type"] = job_info["Description"].apply(classify_tank_type)

    features = job_info.join(op_stats, how="inner").join(wc_hours, how="left").fillna(0)

    return features.reset_index()


def build_routing_catalog(ops: pd.DataFrame) -> pd.DataFrame:
    """Build the master routing catalog: for each operation description,
    count how many jobs use it and the distribution of hours."""
    catalog = ops.groupby(["Work_Center", "Description"]).agg(
        job_count=("Job", "nunique"),
        mean_est_hrs=("Est_Total_Hrs", "mean"),
        median_est_hrs=("Est_Total_Hrs", "median"),
        std_est_hrs=("Est_Total_Hrs", "std"),
        mean_act_hrs=("Act_Total_Hrs", "mean") if "Act_Total_Hrs" in ops.columns else ("Est_Total_Hrs", "mean"),
        median_act_hrs=("Act_Total_Hrs", "median") if "Act_Total_Hrs" in ops.columns else ("Est_Total_Hrs", "median"),
    ).reset_index()

    catalog = catalog.sort_values("job_count", ascending=False)
    return catalog


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading cleaned data...")
    jobs = pd.read_csv(CLEAN_JOBS)
    ops = pd.read_csv(CLEAN_OPS, low_memory=False)

    # Only use jobs with actual routing
    jobs_with_ops = set(ops["Job"].unique())
    jobs = jobs[jobs["Job"].isin(jobs_with_ops)]
    print(f"  Jobs with operations: {len(jobs)}")

    print("\nExtracting features...")
    features = extract_features(jobs, ops)
    print(f"  Feature table: {features.shape[0]} jobs x {features.shape[1]} columns")
    print(f"  Tank types: {features['tank_type'].value_counts().to_dict()}")

    features.to_csv(JOB_FEATURES, index=False)
    print(f"  Saved: {JOB_FEATURES}")

    print("\nBuilding routing catalog...")
    catalog = build_routing_catalog(ops)
    print(f"  Catalog: {len(catalog)} unique (work_center, description) pairs")
    print(f"  Top 15 most common operations:")
    for _, row in catalog.head(15).iterrows():
        print(f"    [{row['Work_Center']:12s}] {row['Description']:50s}  "
              f"({row['job_count']} jobs, med_est={row['median_est_hrs']:.1f}h)")

    catalog.to_csv(ROUTING_CATALOG, index=False)
    print(f"  Saved: {ROUTING_CATALOG}")


if __name__ == "__main__":
    main()
