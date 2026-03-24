"""
JobBOSS Data Export Script
Exports key tables from PRODUCTION database on DC2 to CSV files for EDA.
Run: python export_jobboss.py
"""
import pyodbc
import csv
import os
from datetime import datetime

CONN_STR = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DC2;DATABASE=PRODUCTION;UID=sa;PWD=job1!boss;'
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def export_query(conn, filename, query, description):
    """Export a SQL query to CSV."""
    filepath = os.path.join(OUT_DIR, filename)
    c = conn.cursor()
    c.execute(query)
    cols = [d[0] for d in c.description]
    rows = c.fetchall()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for row in rows:
            w.writerow([str(v) if v is not None else '' for v in row])
    print(f"  {filename}: {len(rows):,} rows ({description})")
    return len(rows)

def main():
    print(f"JobBOSS Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUT_DIR}")
    print()
    conn = pyodbc.connect(CONN_STR)
    total = 0

    # 1. Jobs
    total += export_query(conn, 'jobs.csv', """
        SELECT Job, Customer, Status, Type, Order_Date, Status_Date,
               Part_Number, Description, Order_Quantity, Make_Quantity,
               Completed_Quantity, Shipped_Quantity,
               Est_Total_Hrs, Act_Total_Hrs,
               Est_Labor, Act_Labor, Est_Material, Act_Material,
               Est_Service, Act_Service,
               Est_Labor_Burden, Act_Labor_Burden,
               Est_Machine_Burden, Act_Machine_Burden,
               Est_GA_Burden, Act_GA_Burden,
               Unit_Price, Total_Price, Customer_PO,
               Sched_Start, Sched_End, Lead_Days, Priority,
               Released_Date, Last_Updated
        FROM Job
        WHERE Status != 'Template'
        ORDER BY Order_Date DESC
    """, "All jobs except templates")

    # 2. Job Operations
    total += export_query(conn, 'job_operations.csv', """
        SELECT jo.Job, jo.Sequence, jo.Work_Center, jo.Description,
               jo.Est_Setup_Hrs, jo.Est_Run_Hrs, jo.Est_Total_Hrs,
               jo.Act_Setup_Hrs, jo.Act_Run_Hrs,
               jo.Est_Setup_Labor, jo.Est_Run_Labor,
               jo.Act_Setup_Labor, jo.Act_Run_Labor,
               jo.Est_Labor_Burden, jo.Act_Labor_Burden,
               jo.Est_Machine_Burden, jo.Act_Machine_Burden,
               jo.Est_Total_Cost, jo.Act_Total_Cost,
               jo.Status, jo.Run_Pct_Complete, jo.Setup_Pct_Complete,
               jo.Due_Date, jo.Sched_Start, jo.Sched_End, jo.Actual_Start
        FROM Job_Operation jo
        ORDER BY jo.Job, jo.Sequence
    """, "All job operations with est vs actual")

    # 3. Job Operation Time (the big one)
    total += export_query(conn, 'time_entries.csv', """
        SELECT jot.Employee, jot.Work_Date, jot.WC,
               jot.Act_Setup_Hrs, jot.Act_Run_Hrs,
               jot.Act_Run_Qty, jot.Act_Scrap_Qty,
               jot.Overtime_Hrs, jot.Setup_Overtime_Hrs, jot.Overtime_Factor,
               jot.Run_Labor_Rate, jot.Setup_Labor_Rate, jot.Labor_Burden,
               jot.Operation_Complete, jot.Rework_Time,
               jot.Run_Pct_Complete, jot.Entry_Type,
               jo.Job, jo.Sequence, jo.Description as Op_Description
        FROM Job_Operation_Time jot
        JOIN Job_Operation jo ON jo.Job_Operation = jot.Job_Operation
        ORDER BY jot.Work_Date DESC, jot.Employee
    """, "All time entries joined to job/operation")

    # 4. Employees
    total += export_query(conn, 'employees.csv', """
        SELECT Employee, First_Name, Last_Name, Department, Status, Type, Class,
               Hourly_Rate, Hire_Date, Shift, Work_Center, Last_Updated
        FROM Employee
        ORDER BY Status, Last_Name
    """, "All employees (active + inactive)")

    # 5. Customers
    total += export_query(conn, 'customers.csv', """
        SELECT c.Customer, c.Name, c.Status,
               COUNT(j.Job) as Job_Count,
               SUM(j.Total_Price) as Total_Revenue,
               MIN(j.Order_Date) as First_Order,
               MAX(j.Order_Date) as Last_Order
        FROM Customer c
        LEFT JOIN Job j ON j.Customer = c.Customer AND j.Status != 'Template'
        GROUP BY c.Customer, c.Name, c.Status
        ORDER BY Total_Revenue DESC
    """, "Customers with job counts and revenue")

    # 6. Work Centers
    total += export_query(conn, 'work_centers.csv', """
        SELECT Work_Center, Department, Type, Machines, Operators,
               Setup_Labor_Rate, Run_Labor_Rate,
               Labor_Burden, Machine_Burden, GA_Burden,
               Status, Equipment
        FROM Work_Center
        ORDER BY Work_Center
    """, "All work centers")

    # 7. Operations (master list)
    total += export_query(conn, 'operations.csv', """
        SELECT Operation, Description, Work_Center, Est_Setup_Hrs, Run, Run_Method
        FROM Operation
        ORDER BY Operation
    """, "Operation master definitions")

    # 8. Materials (with usage counts)
    total += export_query(conn, 'materials.csv', """
        SELECT m.Material, m.Description,
               COUNT(mr.Material_Req) as Req_Count,
               SUM(mr.Est_Qty) as Total_Est_Qty,
               SUM(mr.Act_Qty) as Total_Act_Qty,
               SUM(mr.Est_Unit_Cost * mr.Est_Qty) as Total_Est_Cost
        FROM Material m
        LEFT JOIN Material_Req mr ON mr.Material = m.Material
        GROUP BY m.Material, m.Description
        HAVING COUNT(mr.Material_Req) > 0
        ORDER BY Req_Count DESC
    """, "Materials with usage stats")

    # 9. PO Headers
    total += export_query(conn, 'purchase_orders.csv', """
        SELECT po.PO, po.Vendor, v.Name as Vendor_Name,
               po.Status, po.Order_Date, po.Due_Date,
               (SELECT COUNT(*) FROM PO_Detail pd WHERE pd.PO = po.PO) as Line_Count,
               (SELECT SUM(pd.Order_Quantity * pd.Unit_Cost) FROM PO_Detail pd WHERE pd.PO = po.PO) as Est_Total
        FROM PO_Header po
        LEFT JOIN Vendor v ON v.Vendor = po.Vendor
        ORDER BY po.Order_Date DESC
    """, "Purchase order headers with vendor names")

    # 10. Vendors
    total += export_query(conn, 'vendors.csv', """
        SELECT v.Vendor, v.Name, v.Status,
               COUNT(po.PO) as PO_Count
        FROM Vendor v
        LEFT JOIN PO_Header po ON po.Vendor = v.Vendor
        GROUP BY v.Vendor, v.Name, v.Status
        ORDER BY PO_Count DESC
    """, "Vendors with PO counts")

    # 11. Deliveries
    total += export_query(conn, 'deliveries.csv', """
        SELECT d.Job, d.Promised_Date, d.Requested_Date, d.Shipped_Date,
               d.Shipped_Quantity, d.Promised_Quantity,
               j.Customer, j.Description
        FROM Delivery d
        JOIN Job j ON j.Job = d.Job
        ORDER BY d.Promised_Date DESC
    """, "All deliveries with job info")

    # 12. PO Details (line items tied to jobs)
    total += export_query(conn, 'po_detail.csv', """
        SELECT pd.PO, pd.Line, pd.Job, pd.Material, pd.Description,
               pd.Order_Quantity, pd.Unit_Cost, pd.Recv_Quantity,
               pd.Status, pd.Due_Date,
               ph.Vendor, v.Name as Vendor_Name
        FROM PO_Detail pd
        JOIN PO_Header ph ON ph.PO = pd.PO
        LEFT JOIN Vendor v ON v.Vendor = ph.Vendor
        ORDER BY pd.PO DESC, pd.Line
    """, "PO line items with job links and vendor names")

    # 13. Material Requirements (BOM per job)
    total += export_query(conn, 'material_reqs.csv', """
        SELECT mr.Job, mr.Material, mr.Description,
               mr.Est_Qty, mr.Act_Qty, mr.Est_Unit_Cost,
               mr.Pick_Buy, mr.Status, mr.Due_Date,
               mr.PO, mr.Vendor
        FROM Material_Req mr
        ORDER BY mr.Job, mr.Material
    """, "Material requirements (BOM) per job")

    print(f"\nTotal: {total:,} rows exported across all files")
    conn.close()

if __name__ == '__main__':
    main()
