"""
Missing POs Tracker Generator (replaces John's Missing POs For Certified Jobs List.xlsx)
Identifies jobs that have material requirements without corresponding POs,
or POs that are still open/unissued.

Requires: po_detail.csv and material_reqs.csv (run export_jobboss.py to generate).
Falls back to purchase_orders.csv if detailed exports aren't available.
"""
import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'JOBBOSS_DATA')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = pd.read_csv(os.path.join(DATA_DIR, 'jobs.csv'), low_memory=False)
    pos = pd.read_csv(os.path.join(DATA_DIR, 'purchase_orders.csv'), low_memory=False)

    # Check if we have detailed PO data
    po_detail_path = os.path.join(DATA_DIR, 'po_detail.csv')
    mat_req_path = os.path.join(DATA_DIR, 'material_reqs.csv')

    has_detail = os.path.exists(po_detail_path)
    has_mat_req = os.path.exists(mat_req_path)

    active_jobs = jobs[jobs['Status'].isin(['Active', 'Released', 'Hold'])]

    if has_detail:
        # PO line items — note: PO_Detail has no Job column, so we filter by status only
        po_detail = pd.read_csv(po_detail_path, low_memory=False)

        # Open/unissued PO lines (can't filter by job since PO_Detail lacks Job linkage)
        active_po_detail = po_detail[
            po_detail['Status'].isin(['Open', 'Unissued', 'Partial'])
        ].copy()

        rows = []
        for _, line in active_po_detail.iterrows():
            rows.append({
                'PO #': line['PO'],
                'Line': line.get('Line', ''),
                'Vendor': line.get('Vendor_Name', line.get('Vendor', '')),
                'Order Qty': line.get('Order_Quantity', ''),
                'Est Amount': line.get('Est_Ext_Amount', ''),
                'Certs Required': line.get('Certs_Required', ''),
                'Status': line.get('Status', ''),
                'Due Date': line.get('Due_Date', ''),
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values(['PO #'])
        print(f"Using PO detail data: {len(df)} open PO lines on active jobs")

    else:
        # Fallback: use PO headers to flag jobs with open POs
        # This is less granular but still useful
        print("NOTE: po_detail.csv not found. Run export_jobboss.py to get detailed PO data.")
        print("Using PO headers (less granular).\n")

        open_pos = pos[pos['Status'] == 'Open'].copy()

        # We don't have job linkage in PO headers, so list all open POs
        # and cross-reference with active job timelines
        rows = []
        for _, po in open_pos.iterrows():
            rows.append({
                'PO #': po['PO'],
                'Vendor': po.get('Vendor_Name', po.get('Vendor', '')),
                'Status': po['Status'],
                'Order Date': po.get('Order_Date', ''),
                'Due Date': po.get('Due_Date', ''),
                'Line Count': po.get('Line_Count', ''),
                'Est Total': po.get('Est_Total', ''),
            })

        df = pd.DataFrame(rows)
        print(f"Found {len(df)} open POs (no job linkage without po_detail.csv)")

    if has_mat_req:
        # Also check for material requirements without POs
        mat_reqs = pd.read_csv(mat_req_path, low_memory=False)
        active_mat = mat_reqs[mat_reqs['Job'].isin(active_jobs['Job'])].copy()
        # Buy items that are still open (not received/closed)
        missing = active_mat[
            (active_mat['Pick_Buy'] == 'B') &
            (active_mat['Status'].isin(['O', 'U', '']))  # Open or Unissued
        ]
        if not missing.empty:
            missing_rows = []
            for _, m in missing.iterrows():
                missing_rows.append({
                    'Job #': m['Job'],
                    'Material': m.get('Material', ''),
                    'Description': m.get('Description', ''),
                    'Est Qty': m.get('Est_Qty', ''),
                    'Status': 'NO PO ISSUED',
                })
            missing_df = pd.DataFrame(missing_rows)
            print(f"\nFound {len(missing_df)} material requirements with no PO issued")
        else:
            missing_df = pd.DataFrame()
    else:
        missing_df = pd.DataFrame()

    # Write output
    outfile = os.path.join(OUT_DIR, f'Missing_POs_Tracker.xlsx')
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        if not df.empty:
            df.to_excel(writer, sheet_name='Open POs', index=False)
        if not missing_df.empty:
            missing_df.to_excel(writer, sheet_name='No PO Issued', index=False)

        for sn in writer.sheets:
            ws = writer.sheets[sn]
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 30)

    print(f"\nGenerated: {outfile}")


if __name__ == '__main__':
    main()
