"""
Parser for LR_TimeAudit.xml — JobBOSS Crystal Report XML export.

Extracts labor hours by job from the Employee Time Audit report.
This is one of three reports Dustin pulls every Monday at Savannah Tank.

Output: CSV with one row per job containing labor hours, overtime, and scrap data.
"""

import xml.etree.ElementTree as ET
import csv
import json
import sys
import os

NS = {"cr": "urn:crystal-reports:schemas:report-detail"}

# Map FieldName attributes to our output field names
HEADER_FIELDS = {
    "{LR_TimeAudit_TTX.Job}": "job",
    "{LR_TimeAudit_TTX.Part_Number}": "part_number",
    "{LR_TimeAudit_TTX.Make_Quantity}": "make_quantity",
    "{LR_TimeAudit_TTX.Customer}": "customer",
}

FOOTER_FIELDS = {
    "Sum ({LR_TimeAudit_TTX.Labor_Hrs}, {@GH1})": "labor_hrs",
    "Sum ({LR_TimeAudit_TTX.OT_Hrs}, {@GH1})": "ot_hrs",
    "Sum ({@Detail_Labor_Setup}, {@GH1})": "labor_setup",
    "Sum ({@Detail_Labor_Run}, {@GH1})": "labor_run",
    "Sum ({@Detail_OT_Setup}, {@GH1})": "ot_setup",
    "Sum ({@Detail_OT_Run}, {@GH1})": "ot_run",
    "Sum ({LR_TimeAudit_TTX.Act_Scrap_Qty}, {@GH1})": "scrap_qty",
    "Sum ({@Detail_Scrap_Run}, {@GH1})": "scrap_run",
    "Sum ({@Detail_Scrap_Setup}, {@GH1})": "scrap_setup",
}

TOTAL_FIELDS = {
    "Sum ({LR_TimeAudit_TTX.Labor_Hrs})": "total_labor_hrs",
    "Sum ({LR_TimeAudit_TTX.OT_Hrs})": "total_ot_hrs",
    "Sum ({@Detail_Labor_Setup})": "total_labor_setup",
    "Sum ({@Detail_Labor_Run})": "total_labor_run",
    "Sum ({@Detail_OT_Setup})": "total_ot_setup",
    "Sum ({@Detail_OT_Run})": "total_ot_run",
}


def _extract_fields(element, field_map):
    """Extract fields from an XML element using FieldName attribute mapping."""
    result = {}
    for field in element.iter(f"{{{NS['cr']}}}Field"):
        field_name = field.get("FieldName", "")
        if field_name in field_map:
            value_el = field.find(f"{{{NS['cr']}}}Value")
            value = value_el.text.strip() if value_el is not None and value_el.text else ""
            result[field_map[field_name]] = value
    return result


def parse_time_audit(xml_path):
    """Parse LR_TimeAudit.xml and return list of job records + report totals."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    jobs = []

    for group in root.findall(".//cr:Group[@Level='1']", NS):
        job = {}

        header = group.find("cr:GroupHeader", NS)
        if header is not None:
            job.update(_extract_fields(header, HEADER_FIELDS))

        footer = group.find("cr:GroupFooter", NS)
        if footer is not None:
            job.update(_extract_fields(footer, FOOTER_FIELDS))

        if job.get("job"):
            jobs.append(job)

    # Report footer totals
    totals = {}
    report_footer = root.find(".//cr:ReportFooter", NS)
    if report_footer is not None:
        totals = _extract_fields(report_footer, TOTAL_FIELDS)

    return jobs, totals


def to_csv(jobs, output_path):
    """Write parsed jobs to CSV."""
    fieldnames = [
        "job", "part_number", "customer", "make_quantity",
        "labor_hrs", "labor_setup", "labor_run",
        "ot_hrs", "ot_setup", "ot_run",
        "scrap_qty", "scrap_run", "scrap_setup",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(jobs)


def to_json(jobs, totals, output_path):
    """Write parsed data to JSON."""
    data = {
        "report": "LR_TimeAudit",
        "source": "JobBOSS 18.2 Crystal Report XML Export",
        "company": "Savannah Tank & Equipment Corp.",
        "totals": totals,
        "job_count": len(jobs),
        "jobs": jobs,
    }
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def summarize(jobs, totals):
    """Print summary statistics."""
    oh_jobs = [j for j in jobs if j.get("job", "").startswith("OH")]
    prod_jobs = [j for j in jobs if not j.get("job", "").startswith("OH")]
    customers = set(j.get("customer", "") for j in prod_jobs if j.get("customer"))

    oh_labor = sum(float(j.get("labor_hrs", 0) or 0) for j in oh_jobs)
    prod_labor = sum(float(j.get("labor_hrs", 0) or 0) for j in prod_jobs)
    total_labor = oh_labor + prod_labor

    buffer_jobs = [j for j in jobs if "buffer" in j.get("part_number", "").lower()]
    buffer_labor = sum(float(j.get("labor_hrs", 0) or 0) for j in buffer_jobs)

    # Median and average labor hours
    labor_values = sorted(float(j.get("labor_hrs", 0) or 0) for j in jobs)
    avg_labor = total_labor / len(jobs) if jobs else 0
    median_labor = labor_values[len(labor_values) // 2] if labor_values else 0

    print("=" * 60)
    print("  LR_TimeAudit — Employee Time Audit Report")
    print("  Savannah Tank & Equipment Corp.")
    print("=" * 60)
    print(f"  Total jobs:              {len(jobs):,}")
    print(f"  Production jobs:         {len(prod_jobs):,}")
    print(f"  Overhead (OH) jobs:      {len(oh_jobs):,}")
    print(f"  Unique customers:        {len(customers):,}")
    print(f"  Total labor hours:       {totals.get('total_labor_hrs', 'N/A'):>12}")
    print(f"  Total overtime hours:    {totals.get('total_ot_hrs', 'N/A'):>12}")
    print(f"  Avg labor hrs/job:       {avg_labor:>12,.0f}")
    print(f"  Median labor hrs/job:    {median_labor:>12,.0f}")
    print(f"  Production labor hrs:    {prod_labor:>12,.2f}")
    print(f"  Overhead labor hrs:      {oh_labor:>12,.2f}")
    if total_labor > 0:
        print(f"  OH % of total:           {oh_labor / total_labor * 100:>11.1f}%")
    print(f"  Buffer tank jobs:        {len(buffer_jobs):,}")
    print(f"  Buffer tank labor hrs:   {buffer_labor:>12,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    xml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "JobBOSS", "LR_TimeAudit.xml"
    )
    output_dir = os.path.join(os.path.dirname(__file__), "..", "parsed_data")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing {xml_path}...")
    jobs, totals = parse_time_audit(xml_path)
    print(f"Extracted {len(jobs)} jobs.")

    csv_path = os.path.join(output_dir, "time_audit.csv")
    json_path = os.path.join(output_dir, "time_audit.json")

    to_csv(jobs, csv_path)
    to_json(jobs, totals, json_path)
    summarize(jobs, totals)

    print(f"\nOutput: {csv_path}")
    print(f"Output: {json_path}")
