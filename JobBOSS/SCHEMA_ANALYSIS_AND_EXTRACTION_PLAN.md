# JobBOSS Schema Analysis & Data Extraction Plan

> Generated: 2026-03-24
> Source: `JOBBOSS_SCHEMA_EDA.csv` — 142 tables from SQL Server via SSMS 22
> Context: 11 tables already exported to `/JOBBOSS_DATA/*.csv`

---

## Schema Summary

| Metric | Value |
|--------|-------|
| Total tables | 142 |
| Tables with data (rows > 0) | 99 |
| Empty tables (0 rows) | 43 |
| Total rows across all tables | ~1,140,000 |
| Largest table | Change_History (231,972 rows) |
| Most complex table | Job_Operation (108 columns) |

---

## What We Have vs What Exists

### Already Exported (11 tables)

| Our CSV | Maps To Schema Table | Our Rows | Schema Rows | Schema Columns | Gap |
|---------|---------------------|----------|-------------|----------------|-----|
| time_entries.csv | Job_Operation_Time | 149,507 | 149,541 | 38 | We have 20 of 38 columns |
| job_operations.csv | Job_Operation | 64,559 | 64,559 | 108 | We have 26 of 108 columns |
| jobs.csv | Job | 1,758 | 1,770 | 96 | We have 35 of 96 columns |
| purchase_orders.csv | PO_Header | 12,044 | 12,049 | 30 | We have 8 of 30 columns |
| materials.csv | Material | 1,436 | 7,508 | 53 | **Aggregate summary, not raw table** |
| deliveries.csv | Delivery | 1,343 | 1,344 | 26 | We have 8 of 26 columns |
| vendors.csv | Vendor | 778 | 778 | 22 | We have 4 of 22 columns |
| customers.csv | Customer | 388 | 388 | 29 | We have 7 of 29 columns |
| employees.csv | Employee | 278 | 279 | 26 | We have 12 of 26 columns |
| operations.csv | Operation | 208 | 208 | 16 | We have 6 of 16 columns |
| work_centers.csv | Work_Center | 31 | 31 | 47 | We have 12 of 47 columns |

**Key findings:**
- Our exports are **column-limited** — most tables have 2-4x more columns than we extracted
- **materials.csv is a derived summary**, not the raw Material table (1,436 vs 7,508 rows)
- Row counts match closely, confirming clean extraction

---

## Critical Missing Tables

### Tier 1: HIGH PRIORITY — Fill Known Data Gaps

These tables directly address gaps identified in the existing Data Profile & Cleaning Plan.

| Table | Rows | Columns | Why We Need It |
|-------|------|---------|----------------|
| **Material_Req** | 39,650 | 57 | **Job-level material requirements** — fills the gap that materials.csv is aggregate-only. Links materials to specific jobs and operations. 3 FKs, 2 indexed. |
| **Material_Trans** | 218,168 | 39 | **Material transactions** — actual receipt/issue/transfer records. The transactional counterpart to Material_Req. 2nd largest table. |
| **PO_Detail** | 46,509 | 38 | **PO line items** — our PO export only has headers (8 columns). This has quantities, costs, due dates per line. |
| **Invoice_Header** | 2,100 | 35 | **Revenue/billing data** — we have cost data (labor, materials, POs) but ZERO revenue data. This is critical for profitability analysis. |
| **Invoice_Detail** | 5,494 | 44 | **Invoice line items** — links invoices back to jobs, quantities, unit prices. |
| **Additional_Charge** | 6,079 | 23 | **Extra charges on jobs** — freight, setup fees, etc. Affects true job cost. |
| **SO_Detail** | 0 | 48 | Empty — Sales Orders not used (confirms direct job-entry workflow) |
| **SO_Header** | 0 | 27 | Empty — confirms no SO module usage |

### Tier 2: MEDIUM PRIORITY — Enrich Existing Analysis

| Table | Rows | Columns | Why We Need It |
|-------|------|---------|----------------|
| **Delivery** (full) | 1,344 | 26 | Re-extract with all 26 columns (we only have 8). Includes Packlist, Invoice links, Returned_Quantity, NCP_Quantity. |
| **Packlist_Header** | 1,106 | 18 | Packing lists — links deliveries to invoices and shipping details. |
| **Packlist_Detail** | 1,570 | 36 | Line-item detail for packing lists. |
| **Source** | 60,749 | 31 | Links PO lines, job operations, and material requirements. Key junction table. |
| **Quote** | 29 | 31 | Quoting data — small but useful for quote-to-job conversion analysis. |
| **Quote_Qty** | 29 | 35 | Quote quantity breakdowns. |
| **Bill_Of_Jobs** | 198 | 13 | **Parent-child job relationships** — this could resolve the 110 orphaned sub-assembly jobs we identified! |
| **Change_History** | 231,972 | 22 | Audit trail — largest table. Useful for understanding schedule changes, date shifts. |

### Tier 3: REFERENCE DATA — Small but Useful

| Table | Rows | Columns | Why We Need It |
|-------|------|---------|----------------|
| **Contact** | 383 | 16 | Customer/vendor contacts |
| **Address** | 2,524 | 22 | Geographic data for customers/vendors |
| **Shift** | 2 | 16 | **Resolves the GUID-to-shift-name mapping** we identified in employees.csv |
| **User_Values** | 515 | 16 | Custom field values (linked by many tables) |
| **Account** | 177 | 7 | GL account chart — needed if we analyze financials |
| **Fiscal_Period** | 168 | 7 | Period definitions for financial analysis |
| **Status_Definitions** | 29 | 5 | Decodes status codes |
| **User_Code** | 241 | 13 | Custom lookup values |

---

## Tables We Can Skip

### Empty Tables (43 tables, 0 rows)
These modules are not in use: Sales Orders (SO_*), Stock Items, Attendance, Serialization, Customer_Part, Transaction_Data/Detail, etc.

### Low-Value Tables
- **Change_History** (231,972 rows) — largest table but purely audit. Defer unless investigating specific date change patterns.
- **Journal_Entry** (146,937 rows) — GL journal entries. Only needed for deep financial reconciliation.
- **AP_*/** tables — Accounts Payable detail. Defer unless analyzing vendor payment patterns.
- **ACH_*/** tables — Electronic payment configuration. Infrastructure only.
- **Report/RptPref** — Report configuration metadata.
- **CA_ProjectedCashFlow** — Cash flow projections (463 rows, internal tool).

---

## Recommended Extraction Priority

### Phase 1: Re-extract with Full Columns (fix column gaps)

These are tables we already have but with missing columns:

```sql
-- 1. Jobs - full 96 columns (we have 35)
SELECT * FROM Job ORDER BY Order_Date DESC;

-- 2. Job_Operation - full 108 columns (we have 26)
SELECT * FROM Job_Operation ORDER BY Job, Sequence;

-- 3. Job_Operation_Time - full 38 columns (we have 20)
SELECT * FROM Job_Operation_Time ORDER BY Work_Date DESC;

-- 4. Employee - full 26 columns (we have 12)
SELECT * FROM Employee ORDER BY Employee;

-- 5. Customer - full 29 columns (we have 7)
SELECT * FROM Customer ORDER BY Customer;

-- 6. Vendor - full 22 columns (we have 4)
SELECT * FROM Vendor ORDER BY Vendor;

-- 7. Work_Center - full 47 columns (we have 12)
SELECT * FROM Work_Center ORDER BY Work_Center;

-- 8. PO_Header - full 30 columns (we have 8)
SELECT * FROM PO_Header ORDER BY Order_Date DESC;

-- 9. Operation - full 16 columns (we have 6)
SELECT * FROM Operation ORDER BY Operation;

-- 10. Delivery - full 26 columns (we have 8)
SELECT * FROM Delivery ORDER BY Delivery;
```

### Phase 2: Extract New Critical Tables

```sql
-- 11. Material (RAW - not the aggregate we currently have)
SELECT * FROM Material ORDER BY Material;

-- 12. Material Requirements (job-level material data)
SELECT * FROM Material_Req ORDER BY Job, Material_Req;

-- 13. Material Transactions
SELECT * FROM Material_Trans ORDER BY Material_Trans_Date DESC;

-- 14. PO Line Items
SELECT * FROM PO_Detail ORDER BY PO, Line;

-- 15. Invoice Headers
SELECT * FROM Invoice_Header ORDER BY Document_Date DESC;

-- 16. Invoice Line Items
SELECT * FROM Invoice_Detail ORDER BY Document, Document_Line;

-- 17. Additional Charges
SELECT * FROM Additional_Charge ORDER BY Job;

-- 18. Bill of Jobs (parent-child relationships)
SELECT * FROM Bill_Of_Jobs ORDER BY Parent_Job, Component_Job;

-- 19. Source (PO-Job-Material junction)
SELECT * FROM Source ORDER BY Source;
```

### Phase 3: Reference Data

```sql
-- 20. Shift (resolves employee GUID issue)
SELECT * FROM Shift;

-- 21. Contacts
SELECT * FROM Contact ORDER BY Customer, Vendor;

-- 22. Addresses
SELECT * FROM Address ORDER BY Customer, Vendor;

-- 23. User Values (custom fields)
SELECT * FROM User_Values ORDER BY User_Values;

-- 24. Quotes
SELECT * FROM Quote ORDER BY Quote;

-- 25. Status Definitions
SELECT * FROM Status_Definitions;

-- 26. Packlist Headers
SELECT * FROM Packlist_Header ORDER BY Packlist_Date DESC;

-- 27. Packlist Details
SELECT * FROM Packlist_Detail ORDER BY Packlist;
```

---

## Immediate Quick Wins

These small queries would resolve specific issues from the Data Profile RIGHT NOW:

### 1. Resolve Employee Shift GUIDs
```sql
-- Maps the GUID shift values in Employee to readable names
SELECT e.Employee, e.First_Name, e.Last_Name,
       s.Shift_Name, s.OT_Rate, s.DT_Rate,
       s.Daily_OT_Threshold, s.Weekly_OT_Threshold
FROM Employee e
LEFT JOIN Shift s ON e.Shift = s.Shift
WHERE e.Status = 'Active';
```

### 2. Resolve Orphaned Sub-Assembly Jobs
```sql
-- Check if Bill_Of_Jobs explains the 110 orphaned job_operations
SELECT boj.Parent_Job, boj.Component_Job, boj.Relationship_Type,
       j.Status as Parent_Status, j.Part_Number
FROM Bill_Of_Jobs boj
LEFT JOIN Job j ON boj.Parent_Job = j.Job
ORDER BY boj.Parent_Job;
```

### 3. Revenue Data for Job Profitability
```sql
-- Get invoice totals per job for profitability analysis
SELECT id.Job,
       COUNT(DISTINCT ih.Document) as Invoice_Count,
       SUM(id.Amount) as Total_Invoiced,
       MIN(ih.Document_Date) as First_Invoice,
       MAX(ih.Document_Date) as Last_Invoice
FROM Invoice_Detail id
JOIN Invoice_Header ih ON id.Document = ih.Document
WHERE id.Job IS NOT NULL
GROUP BY id.Job
ORDER BY Total_Invoiced DESC;
```

---

## Data Volume Estimates for Full Extraction

| Phase | Tables | Est. Rows | Est. CSV Size |
|-------|--------|-----------|---------------|
| Phase 1 (re-extract) | 10 | ~230,000 | ~80 MB |
| Phase 2 (new critical) | 9 | ~376,000 | ~120 MB |
| Phase 3 (reference) | 8 | ~5,500 | ~2 MB |
| **Total** | **27** | **~611,000** | **~202 MB** |

> Note: Material_Trans (218K rows) and Job_Operation_Time (150K rows) are the bulk of the size. If storage is a concern, these can be filtered to recent years (e.g., WHERE date >= '2020-01-01').

---

## Next Steps

1. **Start with Phase 2, query #18 (Bill_Of_Jobs)** — only 198 rows, immediately resolves the orphaned jobs mystery
2. **Run Quick Win #1 (Shift mapping)** — 2 rows, immediately fixes the employee GUID issue
3. **Extract Invoice_Header + Invoice_Detail** — unlocks revenue/profitability analysis
4. **Extract Material_Req** — fills the biggest data gap (job-level material costs)
5. Re-extract existing tables with full columns as time permits
