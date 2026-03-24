"""
Released Jobs Tracker Generator (replaces April's Released Jobs.xlsx)
Reads JobBOSS CSV exports and produces a per-tank milestone tracker.

Each row = one active/released job.
Each milestone column = a fabrication step, scored by completion status from Job_Operation.
"""
import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'JOBBOSS_DATA')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')

# --- Milestone mapping ---
# Maps April's spreadsheet columns to JobBOSS operation description patterns.
# Each milestone can match multiple operation descriptions (searched with str.contains).
MILESTONES = [
    ("Recv Plate",                  ["Receive Material", "RECEIVE MATERIALS"]),
    ("Head(s) Rcvd",                ["UT Top & Bottom Heads", "Wrap Top & Bottom Heads"]),
    ("Pipe & Flange Rcvd",          ["Cut Nozzle Pipe and Clean", "Build Flanges"]),
    ("Receive Special Item(s)",     ["Roll Pipe-Internal Coil", "Fab Internal Coil"]),
    ("Materials Inspected",         ["UT Shells", "UT Components", "UT Top & Bottom Heads"]),
    ("Cut Parts on Plasma",         ["Cut Parts on Burn Table"]),
    ("Form Internal Coil",          ["Roll Pipe-Internal Coil", "Fab Internal Coil"]),
    ("Shell(s) Rolled",             ["Roll Shell, Tack-Weld I/S", "ROLL SHELLS", "Tack Shell Courses"]),
    ("Skirt Rolled",                ["Bld Skirt, Roll & Tack", "Roll Skirt Shells"]),
    ("Roll Repads",                 ["Roll Repads-Drill & Tap", "Build Repads for Nozzles"]),
    ("Build Supports",              ["Build Supports", "Install Support Parts"]),
    ("Nozzle(s) Made",              ["Build Nozzles-Weld"]),
    ("Build Top and/or Bottom",     ["Build Top Head/Cone", "Build Bottom Head/Cone",
                                     "Fit Top to Shell", "Fit Bottom Head to Shell"]),
    ("Build Manway",                ["Make Manway Parts", "Brn MW Neck, Clean, Bevel"]),
    ("Make Ladders/Handrail/Platform", ["Cut, Build Ladder Parts", "Cut, Build Handrail Parts",
                                        "Cut, Build Platform Parts", "Build Ladder-Weld",
                                        "Build Handrail-Weld", "Build Platform-Weld"]),
    ("Weld Cone(s)",                ["Build Top Head/Cone", "Build Bottom Head/Cone"]),
    ("Fit Ladders/Handrail/Platform", ["Fit Ladder, I&W Clips", "Fit Handrail, I&W Clips",
                                        "Fit Platform, I&W Clips", "FIT LADDER HANDRL PLATFRM"]),
    ("QA Inspect L/H/P",           ["QC Inspection - Final & L", "QC Inspection - Final"]),
    ("Weld Shell Seams",            ["Weld all Outside Seams", "WELD SHELL COURSES"]),
    ("Weld Top To Shell",           ["Fit Top to Shell-Weld", "Weld top to shell",
                                     "FIT TOP TO SHELL & WELD"]),
    ("Weld Bottom To Shell",        ["Fit Bottom Head to Shell", "FIT BTM TO SHELL & WELD"]),
    ("Weld Tank Support(s)",        ["Install Support Parts", "Weld rings, lugs, suppts"]),
    ("Install Nozzles",             ["Set Nozzles in Shell", "Weld Shell Nozz & M/Ws",
                                     "Set Nozzles & Lugs - Top", "Set Nozzles - Bottom Head"]),
    ("Install Special External",    ["Install Insul/Vac Rg-Weld", "Install Insul/Vac Rings",
                                     "Install Body Flg-Shell"]),
    ("Install Special Internal",    ["Install Internal Parts", "Install Internal Coil/Spt",
                                     "Install Baffles-Weld"]),
    ("Test",                        ["Test Tank", "HYDRO/AIR/DYE PEN TEST", "Dye Pen Test"]),
    ("Clean & Prep",                ["Clean Tank Complete", "Clean & Prep Parts", "CLEAN TANK"]),
    ("Sandblast / Paint",           ["Blast & Paint", "Sandblast Parts/Plates", "Move to Paint Area"]),
    ("Ship to Galv L/H/P",         ["Take Parts - Galvanizers"]),
    ("Recv from Galv L/H/P",       ["P/U Parts - Galvanizers"]),
    ("Take parts to Machine Shop",  ["Take Parts - Machine Shop"]),
    ("Recv Parts from Machine Shop",["P/U Parts - Machine Shop"]),
    ("Arrange Truck / Load",        ["Load on Truck", "LOAD ON TRUCK", "Prepare Tank for Shipment"]),
]


def compute_milestone_status(job_ops_df, patterns):
    """Given a job's operations and a list of description patterns, return a status value.

    Returns:
      2 = all matching ops complete (Status='C' or Run_Pct_Complete=100)
      1 = at least one matching op started (Status='S' or Run_Pct_Complete > 0)
      0 = not started or no matching ops found
    """
    mask = job_ops_df['Description'].str.strip().isin([p.strip() for p in patterns])
    matched = job_ops_df[mask]
    if matched.empty:
        return ''  # operation not on this job's routing
    statuses = matched['Status'].tolist()
    pcts = matched['Run_Pct_Complete'].fillna(0).tolist()
    if all(s == 'C' or p >= 100 for s, p in zip(statuses, pcts)):
        return 2  # complete
    if any(s == 'S' or p > 0 for s, p in zip(statuses, pcts)):
        return 1  # in progress
    return 0  # not started


def categorize_job(row, pct):
    """Assign On Track / @ Risk / On Hold based on status and progress."""
    if row.get('Status') == 'Hold':
        return 'On Hold'
    if pd.isna(row.get('Sched_End')):
        return ''
    days_left = (row['Sched_End'] - pd.Timestamp.now()).days
    if pct >= 0.7 or days_left > 14:
        return 'On Track'
    return '@ Risk'


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = pd.read_csv(os.path.join(DATA_DIR, 'jobs.csv'),
                       parse_dates=['Order_Date', 'Sched_Start', 'Sched_End', 'Released_Date'],
                       low_memory=False)
    ops = pd.read_csv(os.path.join(DATA_DIR, 'job_operations.csv'), low_memory=False)
    customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))

    # Filter to active/released jobs only
    active_jobs = jobs[jobs['Status'].isin(['Active', 'Released'])].copy()
    active_jobs = active_jobs.sort_values('Sched_End')

    # Build customer name lookup
    cust_map = dict(zip(customers['Customer'], customers['Name']))

    rows = []
    for _, job in active_jobs.iterrows():
        job_num = job['Job']
        job_ops = ops[ops['Job'] == job_num].copy()

        # Count total operations and completed ones
        total_ops = len(job_ops)
        completed_ops = len(job_ops[(job_ops['Status'] == 'C') | (job_ops['Run_Pct_Complete'] >= 100)])
        pct_complete = completed_ops / total_ops if total_ops > 0 else 0

        row = {
            'Job #': job_num,
            'Customer': cust_map.get(job['Customer'], job['Customer']),
            'Category': categorize_job(job, pct_complete),
            'Ship Date': job['Sched_End'].strftime('%Y-%m-%d') if pd.notna(job['Sched_End']) else '',
            'Progress': round(pct_complete, 2),
            'Complete': completed_ops,
        }

        # Add milestone columns
        for milestone_name, patterns in MILESTONES:
            row[milestone_name] = compute_milestone_status(job_ops, patterns)

        rows.append(row)

    df = pd.DataFrame(rows)

    # Write to Excel
    outfile = os.path.join(OUT_DIR, 'Released_Jobs_Tracker.xlsx')
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='By Tank', index=False)

        # Auto-size columns
        ws = writer.sheets['By Tank']
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 25)

    print(f"Generated: {outfile}")
    print(f"  {len(df)} active jobs, {len(MILESTONES)} milestone columns")
    print(f"\nLegend: 2=Complete, 1=In Progress, 0=Not Started, blank=N/A for this job")
    print(f"\nSample:")
    print(df.head(5)[['Job #', 'Customer', 'Category', 'Ship Date', 'Progress']].to_string())


if __name__ == '__main__':
    main()
