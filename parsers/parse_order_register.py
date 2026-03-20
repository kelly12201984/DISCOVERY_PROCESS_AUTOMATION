"""
Parser for OP_OrderRegister.xml — JobBOSS Crystal Report XML export.

Extracts order data from the Order Register report.
Covers all jobs/sales orders with pricing, status, customer, and dates.

Output: CSV with one row per order.
"""

import xml.etree.ElementTree as ET
import csv
import json
import sys
import os
from collections import Counter

NS = {"cr": "urn:crystal-reports:schemas:report-detail"}

DETAIL_FIELDS = {
    "{op_orderregister_ttx.Job}": "job",
    "{op_orderregister_ttx.Part_Number}": "part_number",
    "{op_orderregister_ttx.Rev}": "rev",
    "{op_orderregister_ttx.Order_Quantity}": "order_quantity",
    "{op_orderregister_ttx.Unit_Price}": "unit_price",
    "{op_orderregister_ttx.Total_Price}": "total_price",
    "{op_orderregister_ttx.Status}": "status",
    "{@CustLine1}": "customer",
    "{@CustLine2}": "customer_line2",
    "{op_orderregister_ttx.Order_Date}": "order_date",
    "{op_orderregister_ttx.Description}": "description",
    "{op_orderregister_ttx.Sales_Rep}": "sales_rep",
    "{op_orderregister_ttx.sOrderUnit}": "order_unit",
    "{op_orderregister_ttx.NetShipped}": "net_shipped",
    "{op_orderregister_ttx.Price_UofM}": "price_uom",
    "{op_orderregister_ttx.Job_Revision}": "job_revision",
}

TOTAL_FIELDS = {
    "Sum ({op_orderregister_ttx.Total_Price})": "total_extended_price",
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


def parse_order_register(xml_path):
    """Parse OP_OrderRegister.xml and return list of order records + report totals."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    orders = []

    for group in root.findall(".//cr:Group[@Level='1']", NS):
        details = group.find(".//cr:Details[@Level='2']", NS)
        if details is None:
            continue

        order = _extract_fields(details, DETAIL_FIELDS)
        if order.get("job"):
            orders.append(order)

    totals = {}
    report_footer = root.find(".//cr:ReportFooter", NS)
    if report_footer is not None:
        totals = _extract_fields(report_footer, TOTAL_FIELDS)

    return orders, totals


def to_csv(orders, output_path):
    """Write parsed orders to CSV."""
    fieldnames = [
        "job", "status", "customer", "order_date", "part_number",
        "description", "rev", "order_quantity", "unit_price", "total_price",
        "net_shipped", "order_unit", "price_uom", "sales_rep",
        "customer_line2", "job_revision",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(orders)


def to_json(orders, totals, output_path):
    """Write parsed data to JSON."""
    data = {
        "report": "OP_OrderRegister",
        "source": "JobBOSS 18.2 Crystal Report XML Export",
        "company": "Savannah Tank & Equipment Corp.",
        "totals": totals,
        "order_count": len(orders),
        "orders": orders,
    }
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def summarize(orders, totals):
    """Print summary statistics."""
    statuses = Counter(o.get("status", "Unknown") for o in orders)
    customers = set(o.get("customer", "") for o in orders if o.get("customer"))

    dates = [o.get("order_date", "") for o in orders if o.get("order_date")]
    dates_sorted = sorted(dates) if dates else []

    priced = []
    for o in orders:
        try:
            priced.append((float(o.get("total_price", 0) or 0), o.get("job", ""), o.get("customer", "")))
        except (ValueError, TypeError):
            pass
    priced.sort(reverse=True)

    print("=" * 60)
    print("  OP_OrderRegister — Order Register Report")
    print("  Savannah Tank & Equipment Corp.")
    print("=" * 60)
    print(f"  Total orders:            {len(orders):,}")
    print(f"  Unique customers:        {len(customers):,}")
    print(f"  Grand total (ext price): ${totals.get('total_extended_price', 'N/A')}")
    print(f"  Date range:              {dates_sorted[0] if dates_sorted else 'N/A'} to {dates_sorted[-1] if dates_sorted else 'N/A'}")
    print()
    print("  Status Breakdown:")
    for status, count in statuses.most_common():
        print(f"    {status:<20} {count:>6}")
    print()
    print("  Top 5 Orders by Price:")
    for price, job, customer in priced[:5]:
        print(f"    {job:<12} {customer:<20} ${price:>12,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    xml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "JobBOSS", "OP_OrderRegister.xml"
    )
    output_dir = os.path.join(os.path.dirname(__file__), "..", "parsed_data")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing {xml_path}...")
    orders, totals = parse_order_register(xml_path)
    print(f"Extracted {len(orders)} orders.")

    csv_path = os.path.join(output_dir, "order_register.csv")
    json_path = os.path.join(output_dir, "order_register.json")

    to_csv(orders, csv_path)
    to_json(orders, totals, json_path)
    summarize(orders, totals)

    print(f"\nOutput: {csv_path}")
    print(f"Output: {json_path}")
