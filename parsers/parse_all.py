#!/usr/bin/env python3
"""
OTTO Data Pipeline — JobBOSS Crystal Report XML Parser
Savannah Tank & Equipment Corp. — Discovery Engagement

Parses all three Monday reports that Dustin currently pulls manually:
  1. LR_TimeAudit.xml    — Labor hours by job (11 years of data)
  2. OP_OrderRegister.xml — All orders with pricing and status
  3. AP_InvoiceRegister.xml — Accounts payable invoices and credit memos

Outputs structured CSV and JSON files to parsed_data/ directory.

Usage:
    python parse_all.py                          # Parse from default JobBOSS/ directory
    python parse_all.py /path/to/xml/directory   # Parse from custom path
"""

import os
import sys
import time

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(__file__))

from parse_time_audit import parse_time_audit, to_csv as ta_csv, to_json as ta_json, summarize as ta_summary
from parse_order_register import parse_order_register, to_csv as or_csv, to_json as or_json, summarize as or_summary
from parse_ap_invoices import parse_ap_invoices, to_csv as ap_csv, to_json as ap_json, summarize as ap_summary


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, "..", "JobBOSS")
    output_dir = os.path.join(base_dir, "..", "parsed_data")
    os.makedirs(output_dir, exist_ok=True)

    print()
    print("=" * 60)
    print("  OTTO Data Pipeline — JobBOSS Report Parser")
    print("  Savannah Tank & Equipment Corp.")
    print("  Discovery Engagement — Kelly Arseneau")
    print("=" * 60)
    print()

    reports = [
        {
            "name": "Time Audit (Labor)",
            "file": "LR_TimeAudit.xml",
            "parser": parse_time_audit,
            "csv_fn": ta_csv,
            "json_fn": ta_json,
            "summary_fn": ta_summary,
            "csv_name": "time_audit.csv",
            "json_name": "time_audit.json",
            "data_key": "jobs",
        },
        {
            "name": "Order Register",
            "file": "OP_OrderRegister.xml",
            "parser": parse_order_register,
            "csv_fn": or_csv,
            "json_fn": or_json,
            "summary_fn": or_summary,
            "csv_name": "order_register.csv",
            "json_name": "order_register.json",
            "data_key": "orders",
        },
        {
            "name": "AP Invoice Register",
            "file": "AP_InvoiceRegister.xml",
            "parser": parse_ap_invoices,
            "csv_fn": ap_csv,
            "json_fn": ap_json,
            "summary_fn": ap_summary,
            "csv_name": "ap_invoices.csv",
            "json_name": "ap_invoices.json",
            "data_key": "invoices",
        },
    ]

    results = []
    total_start = time.time()

    for report in reports:
        xml_path = os.path.join(xml_dir, report["file"])
        if not os.path.exists(xml_path):
            print(f"  SKIPPED: {report['file']} not found at {xml_path}")
            continue

        start = time.time()
        print(f"  Parsing {report['name']}...")
        records, totals = report["parser"](xml_path)
        elapsed = time.time() - start

        csv_path = os.path.join(output_dir, report["csv_name"])
        json_path = os.path.join(output_dir, report["json_name"])

        report["csv_fn"](records, csv_path)
        report["json_fn"](records, totals, json_path)

        results.append({
            "name": report["name"],
            "records": len(records),
            "elapsed": elapsed,
            "csv_path": csv_path,
            "json_path": json_path,
        })

        print(f"  -> {len(records):,} records in {elapsed:.1f}s")
        print()
        report["summary_fn"](records, totals)
        print()

    total_elapsed = time.time() - total_start

    print()
    print("=" * 60)
    print("  Pipeline Complete")
    print("=" * 60)
    print(f"  Reports parsed:    {len(results)}")
    print(f"  Total records:     {sum(r['records'] for r in results):,}")
    print(f"  Total time:        {total_elapsed:.1f}s")
    print(f"  Output directory:  {output_dir}")
    print()
    print("  Files generated:")
    for r in results:
        print(f"    {r['csv_path']}")
        print(f"    {r['json_path']}")
    print()
    print("  These files are ready for OTTO to consume.")
    print("=" * 60)


if __name__ == "__main__":
    main()
