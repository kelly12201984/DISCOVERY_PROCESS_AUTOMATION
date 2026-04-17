"""
Paths and constants for the Build Plan Generator.
All original JOBBOSS_DATA files are READ-ONLY — cleaned outputs go to data/.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBBOSS_DIR = ROOT / "JOBBOSS_DATA"
BUILD_PLANS_DIR = ROOT / "BUILD_PLANS_DRAWINGS" / "MASTER_BUILD_PLANS"
DATA_DIR = Path(__file__).resolve().parent / "data"

# Source CSVs (read-only)
JOBS_CSV = JOBBOSS_DIR / "jobs.csv"
JOB_OPS_CSV = JOBBOSS_DIR / "job_operations.csv"
TIME_ENTRIES_CSV = JOBBOSS_DIR / "time_entries.csv"
OPERATIONS_CSV = JOBBOSS_DIR / "operations.csv"
MATERIALS_CSV = JOBBOSS_DIR / "materials.csv"
MATERIAL_REQS_CSV = JOBBOSS_DIR / "material_reqs.csv"
WORK_CENTERS_CSV = JOBBOSS_DIR / "work_centers.csv"

# Cleaned outputs (written to data/)
CLEAN_JOBS = DATA_DIR / "clean_jobs.csv"
CLEAN_OPS = DATA_DIR / "clean_job_operations.csv"
JOB_FEATURES = DATA_DIR / "job_features.csv"
ROUTING_CATALOG = DATA_DIR / "routing_catalog.csv"
PARSED_BUILD_PLANS = DATA_DIR / "parsed_build_plans.csv"

# Build plan generation defaults
DEFAULT_K_NEIGHBORS = 5
MIN_JOBS_FOR_PREDICTION = 3

# Work center canonical names (build plans use mixed case)
WC_MAP = {
    "prefab": "PRE FAB", "pre fab": "PRE FAB", "PRE FAB": "PRE FAB",
    "fit": "FIT", "FIT": "FIT",
    "weld": "WELD", "WELD": "WELD",
    "detail": "DETAIL", "DETAIL": "DETAIL",
    "build": "BUILD", "BUILD": "BUILD",
    "inspection": "INSPECTION", "INSPECTION": "INSPECTION",
    "finishing": "FINISHING", "FINISHING": "FINISHING",
    "move": "MOVE TANK", "move tank": "MOVE TANK", "MOVE TANK": "MOVE TANK",
    "shipping": "SHIPPING", "SHIPPING": "SHIPPING",
}
