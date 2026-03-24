"""
Master Schedule Generator (replaces April's MASTER SCHEDULE.xlsx)
Produces a week-by-week Gantt-style view of all active jobs,
showing which phase each job is in during each week.

Built from ACTUAL operation progress data — not Sched_Start/Sched_End
(which are empty in JobBOSS).  Projects future weeks by estimating
remaining hours per phase and converting to calendar weeks using a
shop-hours-per-week constant.
"""
import pandas as pd
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'JOBBOSS_DATA')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')

SHOP_HOURS_PER_WEEK = 200  # approximate shop capacity per job (adjustable)

# Phases in production order, with keywords that map operations to phases
PHASES = [
    ('PRE-FAB',     ['Receive Material', 'UT Top', 'UT Bottom', 'UT Shell',
                     'Cut Parts', 'Cut Nozzle', 'Clean & Prep', 'Roll Shell',
                     'Roll Pipe', 'Roll Repad', 'Roll Rim', 'Build Nozzle',
                     'Make Manway', 'Build Hatch', 'Build Door', 'Bld Skirt',
                     'Bld Lift Lugs', 'Bld Grd Lugs', 'B&C parts',
                     'BI, SQ', 'Fab Misc', 'Build Support', 'Build Top',
                     'Build Bottom', 'Misc Fabrication', 'Drill', 'Punch',
                     'Build Flange']),
    ('FABRICATION', ['S/U and Build', 'Set Nozzle', 'Weld Shell', 'Weld Nozzle',
                     'Weld top', 'Weld bottom', 'Weld all', 'Weld ring',
                     'Weld Skirt', 'Weld Shell Nozz',
                     'Install Nozzle', 'Install Internal', 'Install Support',
                     'Install Insul', 'Install Vac', 'Install Baffle',
                     'Install Body Flg', 'Install Bottom Stiff',
                     'Install Top Stiff', 'Install Lift Lugs',
                     'Fit Top', 'Fit Bottom', 'Fit Ladder', 'Fit Handrail',
                     'Fit Platform', 'I&W Bottom', 'I&W Top',
                     'L/O Top', 'L/O Bottom', 'Move Tank',
                     'Tack-Weld', 'Roll Shell, Tack']),
    ('TESTING',     ['Test Tank', 'HYDRO', 'Dye Pen', 'ASME Inspection',
                     'QC Inspection - Test', 'QC Inspection - Internal',
                     'QC Inspection -Top', 'QC Inspection']),
    ('CLEANING',    ['Clean Tank', 'Prepare Tank', 'Move to Paint',
                     'QC Inspection - Sandblast', 'Sandblast']),
    ('PAINT',       ['Blast & Paint', 'Paint', 'QC Inspection - Paint']),
    ('SHIPPING',    ['Load on Truck', 'LOAD ON TRUCK', 'Check BOM', 'Pack Parts',
                     'QC Inspection - Final', 'Prepare Tank for Shipment']),
]

PHASE_NAMES = [p[0] for p in PHASES]


def classify_operation(desc):
    """Map an operation description to a phase name."""
    desc_lower = str(desc).lower()
    for phase_name, keywords in PHASES:
        if any(kw.lower() in desc_lower for kw in keywords):
            return phase_name
    return None


def analyze_job(job_ops):
    """Compute per-phase hours (estimated, actual, remaining) and current phase."""
    if job_ops.empty:
        return None

    sorted_ops = job_ops.sort_values('Sequence')

    # Accumulate hours by phase
    phase_est = {p: 0.0 for p in PHASE_NAMES}
    phase_remaining = {p: 0.0 for p in PHASE_NAMES}
    phase_has_started = {p: False for p in PHASE_NAMES}
    phase_all_done = {p: True for p in PHASE_NAMES}

    current_phase = None

    for _, op in sorted_ops.iterrows():
        est = op['Est_Total_Hrs'] or 0
        pct = (op['Run_Pct_Complete'] or 0) / 100.0
        status = op['Status']
        remaining = est * (1 - pct)

        phase = classify_operation(op.get('Description', ''))
        if phase is None:
            # Assign unclassified ops based on sequence position
            total = len(sorted_ops)
            seq_pct = op['Sequence'] / max(total - 1, 1) if total > 1 else 0
            if seq_pct < 0.25:
                phase = 'PRE-FAB'
            elif seq_pct < 0.65:
                phase = 'FABRICATION'
            elif seq_pct < 0.80:
                phase = 'TESTING'
            elif seq_pct < 0.90:
                phase = 'CLEANING'
            else:
                phase = 'SHIPPING'

        phase_est[phase] += est
        phase_remaining[phase] += remaining

        if status in ('S', 'C') or pct > 0:
            phase_has_started[phase] = True
        if status != 'C' and pct < 100:
            phase_all_done[phase] = False

    # Determine current phase: latest phase that has started but isn't fully done
    for phase in PHASE_NAMES:
        if phase_has_started[phase] and not phase_all_done[phase]:
            current_phase = phase
    # If nothing in progress, find earliest phase with remaining hours
    if current_phase is None:
        for phase in PHASE_NAMES:
            if phase_remaining[phase] > 0:
                current_phase = phase
                break

    total_est = sum(phase_est.values())
    total_remaining = sum(phase_remaining.values())

    return {
        'phase_est': phase_est,
        'phase_remaining': phase_remaining,
        'current_phase': current_phase or 'UNKNOWN',
        'total_est_hrs': total_est,
        'total_remaining_hrs': total_remaining,
        'pct_complete': ((total_est - total_remaining) / total_est * 100) if total_est > 0 else 0,
    }


def project_phase_weeks(analysis, today):
    """Given phase remaining hours, project which weeks each phase occupies.

    Returns a dict: {phase_name: (start_week_date, end_week_date)}
    Current/past phases are anchored to today; future phases follow sequentially.
    """
    if analysis is None:
        return {}

    snap_to_monday = lambda d: d - timedelta(days=d.weekday())
    current_week = snap_to_monday(today)

    phase_weeks = {}
    cursor = current_week  # start projecting from this week

    current_phase = analysis['current_phase']
    hit_current = False

    for phase in PHASE_NAMES:
        remaining = analysis['phase_remaining'][phase]
        est = analysis['phase_est'][phase]

        if est == 0 and remaining == 0:
            continue

        # Phase is fully done — it was in the past
        if remaining == 0:
            # Don't assign week columns for completed phases
            continue

        if phase == current_phase:
            hit_current = True

        if hit_current:
            weeks_needed = max(1, round(remaining / SHOP_HOURS_PER_WEEK))
            start = cursor
            end = cursor + timedelta(weeks=weeks_needed - 1)
            phase_weeks[phase] = (start, end)
            cursor = end + timedelta(weeks=1)

    return phase_weeks


def generate_week_columns(start_date, num_weeks=24):
    """Generate Monday-based week column dates."""
    start = start_date - timedelta(days=start_date.weekday())
    return [start + timedelta(weeks=i) for i in range(num_weeks)]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = pd.read_csv(os.path.join(DATA_DIR, 'jobs.csv'),
                       parse_dates=['Order_Date'],
                       low_memory=False)
    ops = pd.read_csv(os.path.join(DATA_DIR, 'job_operations.csv'), low_memory=False)
    customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
    deliveries = pd.read_csv(os.path.join(DATA_DIR, 'deliveries.csv'),
                             parse_dates=['Promised_Date', 'Shipped_Date'])

    cust_map = dict(zip(customers['Customer'], customers['Name']))

    # Active jobs only — exclude jobs with no operations
    active = jobs[jobs['Status'].isin(['Active', 'Released', 'Hold'])].copy()
    jobs_with_ops = ops.groupby('Job')['Sequence'].count()
    active = active[active['Job'].isin(jobs_with_ops.index)]

    today = datetime.now()
    weeks = generate_week_columns(today - timedelta(weeks=2), num_weeks=24)

    rows = []
    for _, job in active.iterrows():
        job_num = job['Job']
        job_ops = ops[ops['Job'] == job_num].copy()
        analysis = analyze_job(job_ops)
        if analysis is None:
            continue

        # Get delivery info if available
        job_del = deliveries[deliveries['Job'] == job_num]
        promised = ''
        if not job_del.empty and job_del['Promised_Date'].notna().any():
            promised = job_del['Promised_Date'].dropna().iloc[0].strftime('%Y-%m-%d')

        row = {
            'Customer': cust_map.get(job['Customer'], job['Customer']),
            'Job #': job_num,
            'Description': job.get('Description', ''),
            'Total $': job.get('Total_Price', 0),
            'PO Recvd': job['Order_Date'].strftime('%Y-%m-%d') if pd.notna(job['Order_Date']) else '',
            'Promised Date': promised,
            'Current Phase': analysis['current_phase'],
            '% Complete': round(analysis['pct_complete'], 1),
            'Est Hrs': round(analysis['total_est_hrs'], 0),
            'Remaining Hrs': round(analysis['total_remaining_hrs'], 0),
        }

        # Project phases onto week columns
        phase_schedule = project_phase_weeks(analysis, today)

        for week_start in weeks:
            col_name = week_start.strftime('%m/%d')
            row[col_name] = ''
            for phase_name, (ps, pe) in phase_schedule.items():
                if ps <= week_start <= pe:
                    row[col_name] = phase_name
                    break

        rows.append(row)

    df = pd.DataFrame(rows)

    # Sort by remaining hours descending (biggest jobs first)
    df = df.sort_values('Remaining Hrs', ascending=False).reset_index(drop=True)

    # Write to Excel with formatting
    outfile = os.path.join(OUT_DIR, 'Master_Schedule.xlsx')
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Schedule', index=False)

        ws = writer.sheets['Schedule']

        # Auto-fit column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 18)

        # Color-code phase cells
        from openpyxl.styles import PatternFill
        phase_colors = {
            'PRE-FAB':     'FFF2CC',   # light yellow
            'FABRICATION': 'D9E2F3',   # light blue
            'TESTING':     'E2EFDA',   # light green
            'CLEANING':    'FCE4D6',   # light orange
            'PAINT':       'E4DFEC',   # light purple
            'SHIPPING':    'D6DCE4',   # light gray
        }

        # Find where week columns start
        header_row = [cell.value for cell in ws[1]]
        week_col_start = None
        for i, h in enumerate(header_row):
            if h and '/' in str(h) and len(str(h)) <= 5:
                week_col_start = i + 1  # 1-indexed
                break

        if week_col_start:
            for row_cells in ws.iter_rows(min_row=2, min_col=week_col_start,
                                          max_col=ws.max_column):
                for cell in row_cells:
                    val = str(cell.value or '')
                    if val in phase_colors:
                        cell.fill = PatternFill(start_color=phase_colors[val],
                                                end_color=phase_colors[val],
                                                fill_type='solid')

    print(f"Generated: {outfile}")
    print(f"  {len(df)} active jobs across {len(weeks)} weeks")
    print(f"  Week range: {weeks[0].strftime('%m/%d/%Y')} to {weeks[-1].strftime('%m/%d/%Y')}")
    print(f"  Shop capacity assumption: {SHOP_HOURS_PER_WEEK} hrs/week per job")
    print()

    # Summary stats
    in_prog = df[df['% Complete'].between(0.1, 99.9)]
    print(f"  In-progress jobs: {len(in_prog)}")
    print(f"  Not started:      {len(df[df['% Complete'] == 0])}")
    print(f"  Total remaining:  {df['Remaining Hrs'].sum():,.0f} hrs")
    print()
    print("Sample (top 10 by remaining hours):")
    sample_cols = ['Customer', 'Job #', 'Current Phase', '% Complete', 'Remaining Hrs']
    print(df.head(10)[sample_cols].to_string(index=False))


if __name__ == '__main__':
    main()
