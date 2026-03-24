"""
Master Schedule Generator (replaces April's MASTER SCHEDULE.xlsx)
Produces a week-by-week Gantt-style view of all active jobs,
showing which phase each job is in during each week.
"""
import pandas as pd
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'JOBBOSS_DATA')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')

# Phase detection based on operation descriptions
PHASE_PATTERNS = [
    ('PRE-FAB',     ['Receive Material', 'Cut Parts', 'Roll Shell', 'Build Nozzle',
                     'Clean & Prep Parts', 'BI, SQ', 'Roll Pipe', 'Roll Repad',
                     'Bld Skirt', 'Fab Misc', 'Build Support', 'Build Top',
                     'Build Bottom', 'Cut Nozzle']),
    ('FABRICATION', ['Set Nozzle', 'Weld Shell', 'Weld all Outside', 'Weld Nozzle',
                     'Weld top', 'Install Nozzle', 'Install Internal', 'Install Support',
                     'Fit Top', 'Fit Bottom', 'Install Baffle', 'Weld Skirt',
                     'Fit Ladder', 'Fit Handrail', 'Fit Platform', 'Move Tank']),
    ('TESTING',     ['Test Tank', 'HYDRO', 'Dye Pen', 'ASME Inspection', 'QC Inspection - Test']),
    ('CLEANING',    ['Clean Tank', 'Inspect Tank', 'Prepare Tank']),
    ('PAINT',       ['Blast & Paint', 'Sandblast', 'Move to Paint', 'QC Inspection - Paint']),
    ('SHIPPING',    ['Load on Truck', 'LOAD ON TRUCK', 'Prepare Tank for Shipment']),
]


def get_job_phase(job_ops):
    """Determine current phase of a job based on its operations."""
    if job_ops.empty:
        return 'UNKNOWN'

    sorted_ops = job_ops.sort_values('Sequence', ascending=False)

    # Walk backwards from end: find the last completed or in-progress operation
    for _, op in sorted_ops.iterrows():
        if op['Status'] in ('C', 'S') or (op.get('Run_Pct_Complete', 0) or 0) > 0:
            desc = str(op.get('Description', ''))
            for phase_name, patterns in PHASE_PATTERNS:
                if any(p.lower() in desc.lower() for p in patterns):
                    return phase_name
            break

    # Default: check how far along we are
    total = len(job_ops)
    completed = len(job_ops[job_ops['Status'] == 'C'])
    pct = completed / total if total > 0 else 0
    if pct == 0:
        return 'NOT STARTED'
    if pct < 0.3:
        return 'PRE-FAB'
    if pct < 0.7:
        return 'FABRICATION'
    return 'TESTING'


def generate_week_columns(start_date, num_weeks=24):
    """Generate Monday-based week column headers."""
    # Snap to Monday
    start = start_date - timedelta(days=start_date.weekday())
    return [start + timedelta(weeks=i) for i in range(num_weeks)]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = pd.read_csv(os.path.join(DATA_DIR, 'jobs.csv'),
                       parse_dates=['Order_Date', 'Sched_Start', 'Sched_End'],
                       low_memory=False)
    ops = pd.read_csv(os.path.join(DATA_DIR, 'job_operations.csv'), low_memory=False)
    customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
    deliveries = pd.read_csv(os.path.join(DATA_DIR, 'deliveries.csv'),
                             parse_dates=['Promised_Date', 'Shipped_Date'])

    cust_map = dict(zip(customers['Customer'], customers['Name']))

    # Active jobs only
    active = jobs[jobs['Status'].isin(['Active', 'Released', 'Hold'])].copy()
    active = active.sort_values('Sched_End')

    # Generate week columns spanning from 2 weeks ago to 22 weeks out
    today = datetime.now()
    weeks = generate_week_columns(today - timedelta(weeks=2), num_weeks=24)

    rows = []
    for _, job in active.iterrows():
        job_num = job['Job']
        job_ops = ops[ops['Job'] == job_num].copy()
        current_phase = get_job_phase(job_ops)

        row = {
            'Customer': cust_map.get(job['Customer'], job['Customer']),
            'Description': job.get('Description', ''),
            'Job #': job_num,
            'Tank Dimensions': '',  # Not in JobBOSS — manual field
            'Planned Ship Week': job['Sched_End'].strftime('%Y-%m-%d') if pd.notna(job['Sched_End']) else '',
            'PO Recvd': job['Order_Date'].strftime('%Y-%m-%d') if pd.notna(job['Order_Date']) else '',
        }

        # Fill week columns: show phase during active weeks
        sched_start = job['Sched_Start'] if pd.notna(job['Sched_Start']) else None
        sched_end = job['Sched_End'] if pd.notna(job['Sched_End']) else None

        for week_start in weeks:
            week_end = week_start + timedelta(days=6)
            col_name = week_start.strftime('%m/%d')

            if sched_start and sched_end:
                if week_start.date() <= sched_end.date() and week_end.date() >= sched_start.date():
                    # This week overlaps the job's schedule — show phase
                    # Estimate phase by position within schedule
                    total_days = max((sched_end - sched_start).days, 1)
                    days_in = max((week_start - sched_start).days, 0)
                    pct_through = days_in / total_days

                    if pct_through < 0.2:
                        row[col_name] = 'PRE-FAB'
                    elif pct_through < 0.6:
                        row[col_name] = 'FABRICATION'
                    elif pct_through < 0.8:
                        row[col_name] = 'TESTING'
                    elif pct_through < 0.95:
                        row[col_name] = 'CLEANING'
                    else:
                        row[col_name] = 'SHIPPING'

                    # Override current week with actual phase
                    if week_start.date() <= today.date() <= week_end.date():
                        row[col_name] = current_phase
                else:
                    row[col_name] = ''
            else:
                row[col_name] = ''

        rows.append(row)

    df = pd.DataFrame(rows)

    # Write to Excel with separate sheets for certified vs non-certified
    outfile = os.path.join(OUT_DIR, 'Master_Schedule.xlsx')
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        # All active jobs on one sheet
        df.to_excel(writer, sheet_name='Schedule', index=False)

        ws = writer.sheets['Schedule']
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 18)

    print(f"Generated: {outfile}")
    print(f"  {len(df)} active jobs across {len(weeks)} weeks")
    print(f"  Week range: {weeks[0].strftime('%m/%d/%Y')} to {weeks[-1].strftime('%m/%d/%Y')}")
    print(f"\nSample:")
    print(df.head(5)[['Customer', 'Job #', 'Planned Ship Week']].to_string())


if __name__ == '__main__':
    main()
