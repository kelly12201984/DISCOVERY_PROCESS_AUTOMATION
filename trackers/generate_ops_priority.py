"""
Ops Priority List Generator (replaces Dustin's Ops - Priority List.xlsx)
Produces a prioritized list of active jobs sorted by ship date with shop status.
"""
import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'JOBBOSS_DATA')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')


def derive_shop_status(job_ops):
    """Derive a human-readable shop status from the job's operation routing."""
    if job_ops.empty:
        return 'No operations'

    sorted_ops = job_ops.sort_values('Sequence')
    completed = sorted_ops[sorted_ops['Status'] == 'C']
    started = sorted_ops[sorted_ops['Status'] == 'S']
    open_ops = sorted_ops[sorted_ops['Status'] == 'O']

    # Find the current phase by looking at what's in progress
    in_progress = sorted_ops[(sorted_ops['Status'] == 'S') |
                             ((sorted_ops['Run_Pct_Complete'] > 0) & (sorted_ops['Run_Pct_Complete'] < 100))]

    if len(completed) == len(sorted_ops):
        return 'Fab complete, ready to ship'

    # Check for test/inspection phase
    test_ops = sorted_ops[sorted_ops['Description'].str.contains(
        'Test|HYDRO|Dye Pen', case=False, na=False)]
    test_complete = test_ops[test_ops['Status'] == 'C']
    test_started = test_ops[test_ops['Status'].isin(['S', 'C'])]

    inspection_ops = sorted_ops[sorted_ops['Description'].str.contains(
        'ASME|QC Inspection', case=False, na=False)]

    clean_ops = sorted_ops[sorted_ops['Description'].str.contains(
        'Clean|Prep|Paint|Blast', case=False, na=False)]

    ship_ops = sorted_ops[sorted_ops['Description'].str.contains(
        'Load on Truck|Prepare.*Ship|Shipping', case=False, na=False)]

    # Determine phase
    if not ship_ops.empty and all(ship_ops['Status'] == 'C'):
        return 'Shipped'
    if not clean_ops.empty and any(clean_ops['Status'].isin(['S', 'C'])):
        if not test_ops.empty and all(test_ops['Status'] == 'C'):
            return 'Fab complete, testing complete, cleaning/prep'
        return 'Cleaning and prep in progress'
    if not test_ops.empty and any(test_ops['Status'].isin(['S', 'C'])):
        if all(test_ops['Status'] == 'C'):
            return 'Fab complete, testing complete'
        return 'Testing in progress'
    if not inspection_ops.empty and any(inspection_ops['Description'].str.contains('Fab', na=False)):
        fab_insp = inspection_ops[inspection_ops['Description'].str.contains('Fab', na=False)]
        if any(fab_insp['Status'].isin(['S', 'C'])):
            return 'Fabrication near complete, QC inspection'

    # Fall back to describing current ops
    if not in_progress.empty:
        current_descs = in_progress['Description'].tolist()
        # Summarize
        if any('Shell' in d or 'Roll' in d for d in current_descs):
            return 'Shell fabrication in progress'
        if any('Nozzle' in d or 'Weld' in d for d in current_descs):
            return 'Fit and weld in progress'
        if any('Cut' in d or 'Burn' in d for d in current_descs):
            return 'Cutting/pre-fab in progress'
        return f'In progress: {current_descs[0][:40]}'

    pct = len(completed) / len(sorted_ops) * 100
    return f'In fabrication ({pct:.0f}% ops complete)'


def needs_galvanizing(job_ops):
    """Check if job has galvanizing operations."""
    galv = job_ops[job_ops['Description'].str.contains('Galvaniz', case=False, na=False)]
    return 'YES' if not galv.empty else 'NO'


def needs_painting(job_ops):
    """Check if job has painting operations."""
    paint = job_ops[job_ops['Description'].str.contains('Paint|Blast', case=False, na=False)]
    return 'YES' if not paint.empty else 'NO'


def estimate_fab_complete_date(job, job_ops):
    """Estimate fabrication completion date from operation schedule."""
    # Look at the test operation's scheduled start as proxy for fab complete
    test_ops = job_ops[job_ops['Description'].str.contains(
        'Test|HYDRO', case=False, na=False)]
    if not test_ops.empty:
        dates = pd.to_datetime(test_ops['Sched_Start'], errors='coerce').dropna()
        if not dates.empty:
            return dates.min().strftime('%Y-%m-%d')
    return ''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = pd.read_csv(os.path.join(DATA_DIR, 'jobs.csv'),
                       parse_dates=['Order_Date', 'Sched_Start', 'Sched_End'],
                       low_memory=False)
    ops = pd.read_csv(os.path.join(DATA_DIR, 'job_operations.csv'), low_memory=False)
    customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
    cust_map = dict(zip(customers['Customer'], customers['Name']))

    # Active jobs sorted by ship date (priority order)
    active = jobs[jobs['Status'].isin(['Active', 'Released', 'Hold'])].copy()
    active = active.sort_values('Sched_End')

    rows = []
    for priority, (_, job) in enumerate(active.iterrows(), 1):
        job_num = job['Job']
        job_ops = ops[ops['Job'] == job_num].copy()

        row = {
            'Priority': priority,
            'Job #': job_num,
            'Customer': cust_map.get(job['Customer'], job['Customer']),
            'Description': job.get('Description', ''),
            'MOC': job.get('Part_Number', ''),  # Material of Construction often in Part_Number
            'Fab Comp / Test Date': estimate_fab_complete_date(job, job_ops),
            'Ship Date': job['Sched_End'].strftime('%Y-%m-%d') if pd.notna(job['Sched_End']) else '',
            'Shop Status': derive_shop_status(job_ops),
            'Galv': needs_galvanizing(job_ops),
            'Galv Status': '',
            'Paint': needs_painting(job_ops),
            'Paint Status': '',
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    outfile = os.path.join(OUT_DIR, f'Ops_Priority_List_{datetime.now().strftime("%m-%d-%y")}.xlsx')
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        ws = writer.sheets['Sheet1']
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)

    print(f"Generated: {outfile}")
    print(f"  {len(df)} jobs prioritized by ship date")
    print(f"\nTop 10:")
    print(df.head(10)[['Priority', 'Job #', 'Customer', 'Ship Date', 'Shop Status']].to_string())


if __name__ == '__main__':
    main()
