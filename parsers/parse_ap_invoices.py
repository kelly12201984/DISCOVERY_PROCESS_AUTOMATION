"""
Parser for AP_InvoiceRegister.xml — JobBOSS Crystal Report XML export.

Extracts accounts payable invoice data from the AP Invoice Register report.
Covers all vendor invoices and credit memos with amounts, dates, and status.

Output: CSV with one row per invoice/credit memo.
"""

import xml.etree.ElementTree as ET
import csv
import json
import sys
import os
from collections import Counter

NS = {"cr": "urn:crystal-reports:schemas:report-detail"}

ENTRY_DATE_FIELD = 'GroupName ({@Grp1}, "daily")'
# Handle XML-escaped version too
ENTRY_DATE_FIELD_ESCAPED = 'GroupName ({@Grp1}, &quot;daily&quot;)'

INVOICE_FIELDS = {
    "{AP_InvoiceRegister_ttx.Vendor}": "vendor_code",
    "{AP_InvoiceRegister_ttx.Name}": "vendor_name",
    "{AP_InvoiceRegister_ttx.Type}": "type",
    "{AP_InvoiceRegister_ttx.Document}": "document",
    "{AP_InvoiceRegister_ttx.Discount_Amt}": "discount_amount",
    "{AP_InvoiceRegister_ttx.Status}": "status",
    "{AP_InvoiceRegister_ttx.Document_Date}": "document_date",
    "{@Grp3Sum}": "gross_amount",
}

TOTAL_FIELDS = {
    "{@RptSum}": "total_gross_amount",
    "{#RTTotDiscount}": "total_discount",
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


def parse_ap_invoices(xml_path):
    """Parse AP_InvoiceRegister.xml and return list of invoice records + report totals."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    invoices = []

    for group1 in root.findall(".//cr:Group[@Level='1']", NS):
        # Get entry date from Level 1 GroupHeader
        entry_date = ""
        gh1 = group1.find("cr:GroupHeader", NS)
        if gh1 is not None:
            for field in gh1.iter(f"{{{NS['cr']}}}Field"):
                field_name = field.get("FieldName", "")
                if "Grp1" in field_name and "daily" in field_name:
                    value_el = field.find(f"{{{NS['cr']}}}Value")
                    entry_date = value_el.text.strip() if value_el is not None and value_el.text else ""

        # Drill into Level 3 groups for individual invoices
        for group3 in group1.findall(".//cr:Group[@Level='3']", NS):
            gh3 = group3.find("cr:GroupHeader", NS)
            if gh3 is None:
                continue

            invoice = {"entry_date": entry_date}
            invoice.update(_extract_fields(gh3, INVOICE_FIELDS))

            if invoice.get("vendor_code"):
                invoices.append(invoice)

    # Report footer totals
    totals = {}
    report_footer = root.find(".//cr:ReportFooter", NS)
    if report_footer is not None:
        totals = _extract_fields(report_footer, TOTAL_FIELDS)

    return invoices, totals


def to_csv(invoices, output_path):
    """Write parsed invoices to CSV."""
    fieldnames = [
        "entry_date", "vendor_code", "vendor_name", "type", "document",
        "document_date", "gross_amount", "discount_amount", "status",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(invoices)


def to_json(invoices, totals, output_path):
    """Write parsed data to JSON."""
    data = {
        "report": "AP_InvoiceRegister",
        "source": "JobBOSS 18.2 Crystal Report XML Export",
        "company": "Savannah Tank & Equipment Corp.",
        "totals": totals,
        "invoice_count": len(invoices),
        "invoices": invoices,
    }
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def summarize(invoices, totals):
    """Print summary statistics."""
    types = Counter(i.get("type", "Unknown") for i in invoices)
    vendors = set(i.get("vendor_code", "") for i in invoices if i.get("vendor_code"))

    vendor_totals = {}
    for inv in invoices:
        code = inv.get("vendor_code", "")
        name = inv.get("vendor_name", "")
        try:
            amt = float(inv.get("gross_amount", 0) or 0)
        except (ValueError, TypeError):
            amt = 0
        if code not in vendor_totals:
            vendor_totals[code] = {"name": name, "total": 0, "count": 0}
        vendor_totals[code]["total"] += amt
        vendor_totals[code]["count"] += 1

    top_vendors = sorted(vendor_totals.items(), key=lambda x: x[1]["total"], reverse=True)

    print("=" * 60)
    print("  AP_InvoiceRegister — AP Invoice Register Report")
    print("  Savannah Tank & Equipment Corp.")
    print("=" * 60)
    print(f"  Total invoice items:     {len(invoices):,}")
    print(f"  Unique vendors:          {len(vendors):,}")
    print(f"  Grand total (gross):     ${totals.get('total_gross_amount', 'N/A')}")
    print(f"  Total discounts:         ${totals.get('total_discount', 'N/A')}")
    print()
    print("  Document Types:")
    for doc_type, count in types.most_common():
        label = "Invoice" if doc_type == "INV" else "Credit Memo" if doc_type == "CM" else doc_type
        print(f"    {label:<20} {count:>6}")
    print()
    print("  Top 5 Vendors by Total Amount:")
    for code, info in top_vendors[:5]:
        print(f"    {info['name'][:30]:<32} ${info['total']:>12,.2f}  ({info['count']} items)")
    print("=" * 60)


if __name__ == "__main__":
    xml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "JobBOSS", "AP_InvoiceRegister.xml"
    )
    output_dir = os.path.join(os.path.dirname(__file__), "..", "parsed_data")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing {xml_path}...")
    invoices, totals = parse_ap_invoices(xml_path)
    print(f"Extracted {len(invoices)} invoice items.")

    csv_path = os.path.join(output_dir, "ap_invoices.csv")
    json_path = os.path.join(output_dir, "ap_invoices.json")

    to_csv(invoices, csv_path)
    to_json(invoices, totals, json_path)
    summarize(invoices, totals)

    print(f"\nOutput: {csv_path}")
    print(f"Output: {json_path}")
