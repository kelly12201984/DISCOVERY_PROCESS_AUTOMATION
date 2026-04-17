"""
Build Plan Generator — main entry point.

Usage:
    python generate.py <job_number>
    python generate.py 089-25              # generate plan for existing job (backtest)
    python generate.py --new --desc "STORAGE TANK" --est-hours 400
    python generate.py --backtest 20       # backtest last 20 completed jobs

Outputs an Excel build plan to buildplan_generator/output/
"""
import argparse
import sys
from pathlib import Path
import pandas as pd

import config
from config import CLEAN_JOBS, CLEAN_OPS, PARSED_BUILD_PLANS, JOB_FEATURES, DATA_DIR
from similarity import JobSimilarityEngine
from predict_hours import HoursPredictor
from excel_writer import write_build_plan

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def load_operations_master():
    """Load the master operation list from parsed build plans (preferred)
    or fall back to JobBOSS operations."""
    if PARSED_BUILD_PLANS.exists():
        bp = pd.read_csv(PARSED_BUILD_PLANS)
        master = bp.drop_duplicates(subset=["op_code"]).sort_values("op_code")
        return master[["op_code", "work_center", "description", "section"]].copy()

    from config import OPERATIONS_CSV
    ops = pd.read_csv(OPERATIONS_CSV)
    ops = ops.rename(columns={"Operation": "op_code", "Work_Center": "work_center",
                                "Description": "description"})
    ops["section"] = ""
    return ops


def _load_ops_with_codes():
    """Load Operations.csv which has actual op codes per job operation."""
    ops_file = config.JOBBOSS_DIR / "Operations.csv"
    if not ops_file.exists():
        return None
    # No header in this file: Job, Sequence, Operation, Description, Work_Center, Est_Hrs, Act_Hrs, Status, Date
    df = pd.read_csv(ops_file, header=None, encoding="utf-8-sig",
                     names=["Job", "Sequence", "op_code", "Description",
                            "Work_Center", "Est_Total_Hrs", "Act_Total_Hrs",
                            "Status", "Sched_Start"])
    return df


_OPS_WITH_CODES = None

def get_ops_with_codes():
    global _OPS_WITH_CODES
    if _OPS_WITH_CODES is None:
        _OPS_WITH_CODES = _load_ops_with_codes()
    return _OPS_WITH_CODES


def get_job_routing(job_no: str, clean_ops: pd.DataFrame) -> pd.DataFrame:
    """Get the actual routing for a specific job, using Operations.csv for op codes."""
    # Try Operations.csv first (has actual op codes)
    ops_coded = get_ops_with_codes()
    if ops_coded is not None:
        job_ops = ops_coded[ops_coded["Job"] == job_no].sort_values("Sequence").copy()
        if not job_ops.empty:
            rows = []
            for _, op in job_ops.iterrows():
                code = str(op["op_code"]).strip()
                if code == "nan" or code == "NULL":
                    code = f".S{op['Sequence']:03d}"
                if not code.startswith("."):
                    code = "." + code
                rows.append({
                    "op_code": code,
                    "work_center": str(op["Work_Center"]).strip().upper()
                        if str(op["Work_Center"]) != "NULL" else "",
                    "description": str(op["Description"]).strip()
                        if str(op["Description"]) != "NULL" else "",
                    "est_hours": float(op["Est_Total_Hrs"]) if pd.notna(op["Est_Total_Hrs"]) else 0,
                    "section": "",
                    "notes": "",
                })
            return pd.DataFrame(rows)

    # Fallback: use clean_ops and match descriptions to master op codes
    job_ops = clean_ops[clean_ops["Job"] == job_no].sort_values("Sequence").copy()
    if job_ops.empty:
        return pd.DataFrame()

    master = load_operations_master()
    valid = master.dropna(subset=["description"])
    desc_to_op = dict(zip(
        valid["description"].str.lower().str.strip(),
        valid["op_code"]
    ))

    rows = []
    for _, op in job_ops.iterrows():
        desc = str(op["Description"]).strip()
        desc_lower = desc.lower()
        op_code = desc_to_op.get(desc_lower, "")
        if not op_code:
            for master_desc, code in desc_to_op.items():
                if isinstance(master_desc, str) and master_desc[:25] == desc_lower[:25]:
                    op_code = code
                    break
        if not op_code:
            op_code = f".S{op['Sequence']:03d}"
        rows.append({
            "op_code": op_code,
            "work_center": str(op["Work_Center"]).strip().upper(),
            "description": desc,
            "est_hours": float(op.get("Est_Total_Hrs", 0)),
            "section": "",
            "notes": "",
        })
    return pd.DataFrame(rows)


def generate_for_job(job_no: str, engine: JobSimilarityEngine,
                     predictor: HoursPredictor, k: int = 5) -> tuple[Path, float]:
    """Generate a build plan for a specific job number.
    Returns (output_path, total_predicted_hours)."""
    clean_ops = pd.read_csv(CLEAN_OPS, low_memory=False)
    clean_jobs = pd.read_csv(CLEAN_JOBS)

    # Get job info
    job_info = clean_jobs[clean_jobs["Job"] == job_no]
    if job_info.empty:
        print(f"Warning: Job {job_no} not in cleaned jobs, searching raw ops...")
        job_desc = "Unknown"
        total_est = 0
    else:
        job_desc = str(job_info.iloc[0].get("Description", "Unknown"))
        total_est = float(job_info.iloc[0].get("Est_Total_Hrs", 0))

    # Get routing for this job
    routing = get_job_routing(job_no, clean_ops)
    if routing.empty:
        print(f"No operations found for job {job_no}. Using master template.")
        routing = load_operations_master()
        routing["est_hours"] = 0
        routing["notes"] = ""

    # Find similar jobs
    try:
        siblings = engine.find_similar(job_no=job_no, k=k)
        sibling_jobs = siblings["Job"].tolist()
        print(f"Found {len(sibling_jobs)} similar jobs: {sibling_jobs}")
        for _, s in siblings.iterrows():
            print(f"  {s['Job']:10s} | {str(s.get('Description','')):40s} | "
                  f"Est:{s.get('total_est_hrs',0):6.0f}h | dist={s['similarity_distance']:.2f}")
    except ValueError:
        print(f"Job {job_no} not in feature table, using description-based fallback")
        sibling_jobs = []

    # Predict hours
    if sibling_jobs:
        predictions = predictor.predict_from_siblings(sibling_jobs, routing)
    else:
        predictions = routing.copy()
        predictions["predicted_hours"] = predictions["est_hours"]
        predictions["confidence"] = "none"
        predictions["sibling_range"] = "no siblings"
        predictions["source_jobs"] = ""
        predictions["n_sources"] = 0

    # Write Excel
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{job_no} GENERATED BUILD PLAN.xlsx"
    write_build_plan(predictions, job_no, job_desc, sibling_jobs,
                     output_path, total_est=total_est)

    # Print summary
    total_predicted = predictions["predicted_hours"].sum()
    high_conf = (predictions["confidence"] == "high").sum()
    med_conf = (predictions["confidence"] == "medium").sum()
    low_conf = (predictions["confidence"].isin(["low", "none"])).sum()
    print(f"\nGenerated: {output_path}")
    print(f"  Operations: {len(predictions)}")
    print(f"  Total predicted hours: {total_predicted:.1f}")
    print(f"  Original estimate: {total_est:.1f}")
    print(f"  Confidence: {high_conf} high, {med_conf} medium, {low_conf} low/none")

    return output_path, total_predicted


def backtest(n_jobs: int, engine: JobSimilarityEngine,
             predictor: HoursPredictor) -> pd.DataFrame:
    """Generate plans for the last N completed jobs, compare predicted vs actual."""
    clean_jobs = pd.read_csv(CLEAN_JOBS)

    # Get completed jobs with actual hours, sorted by date
    completed = clean_jobs[
        (clean_jobs["Status"].isin(["Complete", "Closed"])) &
        (clean_jobs["Act_Total_Hrs"] > 10) &
        (~clean_jobs["Description"].fillna("").str.contains("BUFFER TANK.*OF 224", case=False))
    ].sort_values("Order_Date", ascending=False).head(n_jobs)

    print(f"\n{'='*80}")
    print(f"BACKTESTING: Generating plans for {len(completed)} recent completed jobs")
    print(f"{'='*80}\n")

    results = []
    for _, job in completed.iterrows():
        job_no = job["Job"]
        actual_hrs = job["Act_Total_Hrs"]
        est_hrs = job["Est_Total_Hrs"]

        try:
            path, predicted_total = generate_for_job(job_no, engine, predictor)

            est_error = abs(est_hrs - actual_hrs) / actual_hrs * 100 if actual_hrs > 0 else 0
            pred_error = abs(predicted_total - actual_hrs) / actual_hrs * 100 if actual_hrs > 0 else 0

            results.append({
                "job": job_no,
                "description": job["Description"],
                "actual_hrs": actual_hrs,
                "estimated_hrs": est_hrs,
                "predicted_hrs": predicted_total,
                "est_error_pct": est_error,
                "pred_error_pct": pred_error,
                "improved": pred_error < est_error,
            })

            print(f"  {job_no}: actual={actual_hrs:.0f}h, est={est_hrs:.0f}h "
                  f"({est_error:.0f}% off), pred={predicted_total:.0f}h "
                  f"({pred_error:.0f}% off) {'✓ BETTER' if pred_error < est_error else ''}")

        except Exception as e:
            print(f"  {job_no}: ERROR — {e}")

    if results:
        df = pd.DataFrame(results)
        print(f"\n{'='*80}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*80}")
        print(f"Jobs tested: {len(df)}")
        print(f"Average estimation error:  {df['est_error_pct'].mean():.1f}%")
        print(f"Average prediction error:  {df['pred_error_pct'].mean():.1f}%")
        print(f"Predictions better than estimates: {df['improved'].sum()}/{len(df)}")
        print(f"Median estimation error:  {df['est_error_pct'].median():.1f}%")
        print(f"Median prediction error:  {df['pred_error_pct'].median():.1f}%")

        df.to_csv(DATA_DIR / "backtest_results.csv", index=False)
        print(f"\nDetailed results: {DATA_DIR / 'backtest_results.csv'}")

        return df

    return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="Savannah Tank Build Plan Generator")
    parser.add_argument("job", nargs="?", help="Job number to generate plan for (e.g., 089-25)")
    parser.add_argument("--new", action="store_true", help="New job (not in JobBOSS yet)")
    parser.add_argument("--desc", help="Job description for new jobs")
    parser.add_argument("--est-hours", type=float, help="Estimated total hours for new jobs")
    parser.add_argument("--backtest", type=int, metavar="N",
                        help="Backtest on last N completed jobs")
    parser.add_argument("-k", type=int, default=5, help="Number of similar jobs to use")
    args = parser.parse_args()

    # Initialize engine and predictor
    print("Loading similarity engine...")
    engine = JobSimilarityEngine()
    print("Loading hours predictor...")
    predictor = HoursPredictor()

    if args.backtest:
        backtest(args.backtest, engine, predictor)
    elif args.job:
        generate_for_job(args.job, engine, predictor, k=args.k)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
