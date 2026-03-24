"""
Weekly Efficiency Tracker Generator (replaces Dustin's Weekly Operations Tracker)
Computes labor efficiency by department from JobBOSS time entries vs estimated hours.

Efficiency = Estimated Hours / Actual Hours (>1.0 means ahead of estimate)
Broken out by department: Finishing, Fit, Pre-Fab, Shipping.
"""
import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'JOBBOSS_DATA')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')

# Map JobBOSS work centers to Dustin's department buckets
WC_TO_DEPT = {
    'FINISHING': 'Finishing',
    'FIT': 'Fit',
    'FIT TEAM 1': 'Fit',
    'FIT TEAM 2': 'Fit',
    'FIT TEAM 3': 'Fit',
    'PRE FAB': 'Pre-Fab',
    'DETAIL': 'Pre-Fab',
    'BUILD': 'Pre-Fab',
    'SHIPPING': 'Shipping',
    'MOVE TANK': 'Shipping',
    'WELD': 'Fit',
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    time_entries = pd.read_csv(os.path.join(DATA_DIR, 'time_entries.csv'),
                               parse_dates=['Work_Date'], low_memory=False)
    ops = pd.read_csv(os.path.join(DATA_DIR, 'job_operations.csv'), low_memory=False)

    # Map work centers to departments
    time_entries['Department'] = time_entries['WC'].map(WC_TO_DEPT)
    time_entries = time_entries[time_entries['Department'].notna()].copy()

    # Build estimated hours lookup: job+sequence -> est_total_hrs
    est_lookup = ops.set_index(['Job', 'Sequence'])['Est_Total_Hrs'].to_dict()
    time_entries['Est_Hrs'] = time_entries.apply(
        lambda r: est_lookup.get((r['Job'], r['Sequence']), 0), axis=1)

    # Actual hours per entry
    time_entries['Act_Hrs'] = time_entries['Act_Setup_Hrs'].fillna(0) + time_entries['Act_Run_Hrs'].fillna(0)

    # Week bucket (Monday start)
    time_entries['Week_Of'] = time_entries['Work_Date'].dt.to_period('W-SUN').apply(lambda p: p.start_time)

    # Filter to recent data (current year and prior year)
    cutoff = f'{datetime.now().year - 1}-01-01'
    time_entries = time_entries[time_entries['Work_Date'] >= cutoff]

    # Aggregate by week + department
    weekly = time_entries.groupby(['Week_Of', 'Department']).agg(
        Est_Hrs=('Est_Hrs', 'sum'),
        Act_Hrs=('Act_Hrs', 'sum')
    ).reset_index()
    weekly['Efficiency'] = (weekly['Est_Hrs'] / weekly['Act_Hrs']).round(2)
    weekly.loc[weekly['Act_Hrs'] == 0, 'Efficiency'] = None

    # Pivot to get departments as columns
    pivot = weekly.pivot_table(index='Week_Of', columns='Department',
                               values='Efficiency', aggfunc='first')
    pivot = pivot.sort_index()

    # Add total efficiency (weighted)
    totals = time_entries.groupby('Week_Of').agg(
        Est_Hrs=('Est_Hrs', 'sum'),
        Act_Hrs=('Act_Hrs', 'sum')
    )
    totals['Total'] = (totals['Est_Hrs'] / totals['Act_Hrs']).round(2)
    pivot['Total'] = totals['Total']

    # Rolling averages
    pivot['4 Week Avg'] = pivot['Total'].rolling(4, min_periods=1).mean().round(4)
    pivot['8 Week Avg'] = pivot['Total'].rolling(8, min_periods=1).mean().round(4)

    # Add year/month/week columns
    pivot = pivot.reset_index()
    pivot.insert(0, 'Year', pivot['Week_Of'].dt.year)
    # Show month label only on first week of each month
    prev_months = pivot['Week_Of'].dt.month.shift(1)
    pivot.insert(2, 'Month', pivot['Week_Of'].apply(lambda d: d.strftime('%b')))
    pivot.loc[pivot['Week_Of'].dt.month == prev_months, 'Month'] = ''
    pivot.insert(3, 'Week', range(1, len(pivot) + 1))

    # Rename Week_Of
    pivot = pivot.rename(columns={'Week_Of': 'Week of'})

    # Reorder columns
    dept_cols = [c for c in ['Finishing', 'Fit', 'Pre-Fab', 'Shipping'] if c in pivot.columns]
    ordered = ['Year', 'Week of', 'Month', 'Week'] + dept_cols + ['Total', '4 Week Avg', '8 Week Avg']
    pivot = pivot[[c for c in ordered if c in pivot.columns]]

    # --- YTD Summary (like the Efficiency tracker top-level) ---
    current_year = datetime.now().year
    ytd_time = time_entries[time_entries['Work_Date'].dt.year == current_year]
    ytd_summary = ytd_time.groupby('Department').agg(
        Est_Hrs=('Est_Hrs', 'sum'),
        Act_Hrs=('Act_Hrs', 'sum')
    )
    ytd_summary['YTD Efficiency'] = (ytd_summary['Est_Hrs'] / ytd_summary['Act_Hrs']).round(2)

    # Write output
    outfile = os.path.join(OUT_DIR, 'Weekly_Efficiency_Tracker.xlsx')
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        pivot.to_excel(writer, sheet_name='Weekly Data', index=False)
        ytd_summary.to_excel(writer, sheet_name='YTD Summary')

        for sn in writer.sheets:
            ws = writer.sheets[sn]
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 20)

    print(f"Generated: {outfile}")
    print(f"  {len(pivot)} weeks of data")
    print(f"\nYTD Efficiency by Department:")
    print(ytd_summary['YTD Efficiency'].to_string())
    print(f"\nRecent weeks:")
    print(pivot.tail(5).to_string())


if __name__ == '__main__':
    main()
