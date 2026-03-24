# JobBoss Data Profile & Cleaning Plan

> Generated: 2026-03-23
> Source: `/JOBBOSS_DATA/*.csv` (11 files, ~46 MB total)

---

## Table of Contents

1. [Dataset Overview](#dataset-overview)
2. [File-by-File Profiles](#file-by-file-profiles)
3. [Cross-File Linkage Validation](#cross-file-linkage-validation)
4. [Proposed Data Cleaning Actions](#proposed-data-cleaning-actions)

---

## Dataset Overview

| File | Rows | Columns | Size | Purpose |
|------|------|---------|------|---------|
| time_entries.csv | 149,507 | 20 | 17 MB | Employee labor time logged against jobs |
| job_operations.csv | 64,559 | 26 | 11 MB | Operations/steps within each job |
| jobs.csv | 1,758 | 35 | 502 KB | Master job records with estimates vs actuals |
| purchase_orders.csv | 12,044 | 8 | 1.1 MB | Purchase orders to vendors |
| materials.csv | 1,436 | 6 | 106 KB | Material catalog with aggregate usage |
| deliveries.csv | 1,343 | 8 | 133 KB | Shipment/delivery records |
| vendors.csv | 778 | 4 | 31 KB | Vendor master list |
| customers.csv | 388 | 7 | 27 KB | Customer master list |
| employees.csv | 278 | 12 | 29 KB | Employee master list |
| operations.csv | 208 | 6 | 11 KB | Standard operation templates |
| work_centers.csv | 31 | 12 | 2.4 KB | Work center definitions |

---

## File-by-File Profiles

---

### 1. time_entries.csv

**149,507 rows | 20 columns | 17 MB**

**Columns:** Employee, Work_Date, WC, Act_Setup_Hrs, Act_Run_Hrs, Act_Run_Qty, Act_Scrap_Qty, Overtime_Hrs, Setup_Overtime_Hrs, Overtime_Factor, Run_Labor_Rate, Setup_Labor_Rate, Labor_Burden, Operation_Complete, Rework_Time, Run_Pct_Complete, Entry_Type, Job, Sequence, Op_Description

**Key Stats:**
- 249 unique employees, 18 work centers, 1,533 unique jobs
- Date range: 2015 to 2026-03-20 (with anomalous dates back to 1962)
- 83% production time entries, 17% overhead (OH-* jobs)

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **308 exact duplicate rows** | HIGH | Full row-level duplicates that must be deduplicated |
| **39 impossible dates** | HIGH | 38 rows dated 1962-02-20 (employee MOOSCO, jobs 22-06x), 1 dated 1990-02-20 -- likely should be 2022-02-20 based on job numbers |
| **Extreme outliers in Act_Run_Hrs** | HIGH | Top entry is 1,194.75 hrs on a single row. Top 10 are all employee SAVATA, WC=SHOP, dated 2015-06-28 -- appears to be a bulk correction dump, not real daily entries |
| **Act_Setup_Hrs nearly all zeros** | LOW | 149,502 of 149,507 rows are 0.0 -- setup is not tracked here. Dead column. |
| **Act_Scrap_Qty nearly all zeros** | LOW | Only 3 non-zero values out of 149,507. Dead column. |
| **Setup_Overtime_Hrs nearly all zeros** | LOW | Dead column (setup not tracked) |
| **Entry_Type nearly uniform** | LOW | 149,502 are type 1, only 5 are type 0. Near-zero analytical value. |
| **Op_Description blank 17%** | MEDIUM | 26,702 blanks -- aligns exactly with overhead (OH-) entries, which have no operation description |

**Recommended Splits:**
- **Production vs Overhead**: Separate OH-* job entries (26,702 rows) from production entries (122,805 rows) -- these are analyzed very differently
- Optionally split by year for trend analysis

---

### 2. employees.csv

**278 rows | 12 columns | 29 KB**

**Columns:** Employee, First_Name, Last_Name, Department, Status, Type, Class, Hourly_Rate, Hire_Date, Shift, Work_Center, Last_Updated

**Key Stats:**
- 39 Active, 239 Inactive employees
- Types: 254 Shop, 23 Other, 1 Sales
- Hourly rate: $0.00 - $57.69, mean $21.38

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **Work_Center is 100% blank** | HIGH | All 278 rows have empty Work_Center. Completely dead column. |
| **Department 58% blank** | HIGH | 163 of 278 employees have no department. Only 7 departments defined for the remaining 115. |
| **Shift column contains GUIDs** | MEDIUM | Values are UUIDs like `B168CA62-A0FF-4207-8FD6-9C8AC1ABF6C7` instead of human-readable shift names. 61% blank. |
| **Class is uniform** | LOW | All values are "E". Dead column. |
| **29 employees never appear in time_entries** | LOW | These may be office/non-production staff or truly inactive |

---

### 3. jobs.csv

**1,758 rows | 35 columns | 502 KB**

**Columns:** Job, Customer, Status, Type, Order_Date, Status_Date, Part_Number, Description, Order_Quantity, Make_Quantity, Completed_Quantity, Shipped_Quantity, Est_Total_Hrs, Act_Total_Hrs, Est_Labor, Act_Labor, Est_Material, Act_Material, Est_Service, Act_Service, Est_Labor_Burden, Act_Labor_Burden, Est_Machine_Burden, Act_Machine_Burden, Est_GA_Burden, Act_GA_Burden, Unit_Price, Total_Price, Customer_PO, Sched_Start, Sched_End, Lead_Days, Priority, Released_Date, Last_Updated

**Key Stats:**
- Status: 704 Complete, 649 Closed, 405 Active
- Type: 1,649 Regular, 109 Assembly
- Order dates: 2014-02-12 to 2026-03-20

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **Sched_Start 89% blank** | HIGH | 1,565 of 1,758 jobs have no scheduled start date |
| **Sched_End 89% blank** | HIGH | Same -- scheduling data is largely missing |
| **Released_Date 87% blank** | HIGH | 1,536 jobs have no release date |
| **5 dead columns (all zeros)** | MEDIUM | Est_Service, Est_Machine_Burden, Act_Machine_Burden, Est_GA_Burden, Act_GA_Burden are 100% zero |
| **Make_Quantity outlier** | HIGH | One job has Make_Quantity = 799,455 (all others are 1-2). Likely a data entry error. |
| **Part_Number 15% blank** | MEDIUM | 267 jobs have no part number |
| **Description 19% blank** | MEDIUM | 336 jobs have no description |
| **Act_Total_Hrs outlier** | MEDIUM | Max is 16,876.53 hrs (~8 person-years). Needs investigation. |
| **222 jobs with $0 pricing** | MEDIUM | Unit_Price and Total_Price both zero -- could be overhead/internal jobs |

---

### 4. job_operations.csv

**64,559 rows | 26 columns | 11 MB**

**Columns:** Job, Sequence, Work_Center, Description, Est_Setup_Hrs, Est_Run_Hrs, Est_Total_Hrs, Act_Setup_Hrs, Act_Run_Hrs, Est_Setup_Labor, Est_Run_Labor, Act_Setup_Labor, Act_Run_Labor, Est_Labor_Burden, Act_Labor_Burden, Est_Machine_Burden, Act_Machine_Burden, Est_Total_Cost, Act_Total_Cost, Status, Run_Pct_Complete, Setup_Pct_Complete, Due_Date, Sched_Start, Sched_End, Actual_Start

**Key Stats:**
- 1,676 unique jobs, up to 117 sequences per job
- Status: C (Complete) 52,120, O (Open) 10,330, S (Scheduled) 1,904, T (Template) 205
- 29 unique work centers

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **Due_Date 99% blank** | HIGH | 64,555 of 64,559 rows have no due date. Effectively dead. |
| **Sched_Start/End 93% blank** | HIGH | Scheduling data largely missing |
| **Setup columns all near-zero** | LOW | Est_Setup_Hrs, Act_Setup_Hrs, Setup_Pct_Complete -- confirms setup not tracked |
| **Est_Machine_Burden/Est_Total_Cost all zero** | LOW | Dead columns |
| **Act_Run_Hrs outlier: 9,962 hrs** | MEDIUM | Single operation. Needs investigation. |
| **110 orphaned jobs** | MEDIUM | 110 jobs (989 rows) exist in job_operations but NOT in the jobs table. These have naming patterns like `15-125_BTM`, `15-112_ADM` -- appear to be sub-assembly suffixed jobs that don't match the parent job format |

---

### 5. deliveries.csv

**1,343 rows | 8 columns | 133 KB**

**Columns:** Job, Promised_Date, Requested_Date, Shipped_Date, Shipped_Quantity, Promised_Quantity, Customer, Description

**Key Stats:**
- 1,089 unique jobs
- Date range: 2015-07-10 to 2026-03-17

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **73 exact duplicate rows** | HIGH | Full row-level duplicates |
| **23 missing Shipped_Date** | LOW | Likely not yet shipped |
| **Description 11% blank** | MEDIUM | 151 rows missing description |
| **69 rows with Shipped_Quantity = 0** | LOW | May represent unshipped deliveries |

---

### 6. materials.csv

**1,436 rows | 6 columns | 106 KB**

**Columns:** Material, Description, Req_Count, Total_Est_Qty, Total_Act_Qty, Total_Est_Cost

**Key Stats:**
- 1,436 unique materials
- Top material by usage: FREIGHT (925 requisitions), HEAD (711), PLT 304L 1/4 X 60 X (638)

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **Floating point artifacts** | MEDIUM | Values like `1106.9999999999995` and `1058.9999999999998` -- need rounding |
| **13 missing descriptions** | LOW | Material codes exist but no description |
| **28 materials with zero actual quantity** | LOW | Estimated but never used |
| **Aggregate-only data** | NOTE | This is a summary table (totals per material), not transactional. No job-level linkage. |

---

### 7. operations.csv

**208 rows | 6 columns | 11 KB**

**Columns:** Operation, Description, Work_Center, Est_Setup_Hrs, Run, Run_Method

**Key Stats:**
- This is a **template/catalog** of standard operations
- All Run_Method = "FixedHrs"
- All Est_Setup_Hrs = 0.0 (confirming setup not used)
- All Run = 0.0

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **Run column is all zeros** | LOW | Standard run hours not defined in templates -- all estimation happens at the job level |
| **Est_Setup_Hrs all zeros** | LOW | Confirms setup not tracked anywhere |
| **This is reference data only** | NOTE | No transactional data here. Used as templates when creating job operations. |

---

### 8. purchase_orders.csv

**12,044 rows | 8 columns | 1.1 MB**

**Columns:** PO, Vendor, Vendor_Name, Status, Order_Date, Due_Date, Line_Count, Est_Total

**Key Stats:**
- Status: 9,965 Closed, 2,078 Open, 1 Unissued
- 340 unique vendors
- Date range: 2015-05-13 to 2026-03-20

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **1,846 POs (15%) have no Vendor code** | HIGH | Vendor and Vendor_Name both blank on ~15% of records |
| **Negative Est_Total values** | MEDIUM | Minimum is -$2,244.36 -- could be credits/returns but needs verification |
| **1,409 POs with $0 estimated total** | MEDIUM | Either blanket POs or missing data |
| **31 POs with zero line items** | LOW | Empty purchase orders |
| **1 due date in 2027** | LOW | Could be legitimate long-lead item or error |

---

### 9. vendors.csv

**778 rows | 4 columns | 31 KB**

**Columns:** Vendor, Name, Status, PO_Count

**Key Stats:**
- 770 Active, 8 Inactive
- Top vendors: NEXAIR LLC (1,419 POs), ROBERT JAMES SALES (729), CHATHAM STEEL (646)

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **8 vendors with blank Names** | LOW | Vendor codes exist but no name |
| **438 vendors (56%) with 0 POs** | MEDIUM | Over half the vendor list has zero purchase orders -- legacy/unused records |
| **Nearly all "Active"** | LOW | Only 8 marked Inactive despite 438 having zero activity |

---

### 10. work_centers.csv

**31 rows | 12 columns | 2.4 KB**

**Columns:** Work_Center, Department, Type, Machines, Operators, Setup_Labor_Rate, Run_Labor_Rate, Labor_Burden, Machine_Burden, GA_Burden, Status, Equipment

**Key Stats:**
- 12 Direct (production), 19 Indirect work centers
- Departments: Fabrication (7), Design (8), FIT teams (3), Office (1), (none) (6), blank (1)
- All Machine_Burden and GA_Burden = 0
- All Equipment = False

**Issues Found:**

| Issue | Severity | Detail |
|-------|----------|--------|
| **6 departments are "(none)"** | LOW | ACADEMY, FAC. MAINT, MAINTENANC, OVERHEAD, REPAIR, SAFETY, SUPERVISN, TRAINING have no department |
| **Machine_Burden/GA_Burden all zero** | LOW | Dead columns |
| **Equipment all False** | LOW | Dead column |
| **Indirect WCs have $0 rates** | NOTE | By design -- indirect work centers don't accrue direct labor costs |
| **Labor_Burden = 230.0 for all Direct WCs** | NOTE | Flat rate across all direct centers. This is a simplification. |
| **13 work centers exist in table but never appear in time_entries** | NOTE | These are design/engineering workflow steps (DRAWINGS, DWG APPROV, PREL BOM, etc.) -- tracked at job_operations level but not in time entries |

---

## Cross-File Linkage Validation

| Relationship | Status | Detail |
|---|---|---|
| time_entries.Employee -> employees.Employee | CLEAN | All 249 time entry employees exist in employees table |
| time_entries.Job -> jobs.Job | CLEAN | All 1,533 time entry jobs exist in jobs table |
| time_entries.WC -> work_centers.Work_Center | CLEAN | All 18 work centers match |
| jobs.Customer -> customers.Customer | CLEAN | All 217 job customers exist in customers table |
| purchase_orders.Vendor -> vendors.Vendor | CLEAN | All 340 PO vendors exist in vendor table |
| deliveries.Job -> jobs.Job | CLEAN | All 1,089 delivery jobs exist in jobs table |
| **job_operations.Job -> jobs.Job** | **BROKEN** | **110 jobs (989 rows) in job_operations have no match in jobs table.** These use suffixed naming (e.g., `15-125_BTM`, `15-112_ADM`, `10-000 BTM`) suggesting sub-assembly breakdowns not reflected in the jobs master. |
| employees -> time_entries | GAP | 29 employees in the employee table never appear in time_entries (likely office/inactive staff) |
| customers -> jobs | GAP | 171 customers (44%) have zero jobs |
| vendors -> purchase_orders | GAP | 438 vendors (56%) have zero POs |

---

## Proposed Data Cleaning Actions

### Priority 1: Critical (Must Fix Before Analysis)

1. **Deduplicate time_entries.csv** -- Remove 308 exact duplicate rows
2. **Deduplicate deliveries.csv** -- Remove 73 exact duplicate rows
3. **Fix impossible dates in time_entries** -- 39 rows with 1962/1990 dates. Likely 2022 based on job numbering (22-xxx). Verify and correct.
4. **Investigate SAVATA bulk entries** -- 10+ rows from 2015-06-28 with 199-1,194 hours each. Determine if these are corrections, data migration artifacts, or errors. Flag or quarantine.
5. **Investigate Make_Quantity = 799,455 in jobs.csv** -- Almost certainly a data entry error (all other values are 1-2).
6. **Resolve 110 orphaned jobs in job_operations** -- Determine the relationship between suffixed jobs (e.g., `15-125_BTM`) and parent jobs. Either add them to the jobs table or map them to parents.

### Priority 2: Data Normalization

7. **Strip timestamps from date columns** -- All date fields include `00:00:00` time components that add noise. Normalize to `YYYY-MM-DD`.
8. **Round floating point artifacts in materials.csv** -- Values like `1106.9999999999995` should be `1107.0`.
9. **Resolve Shift GUIDs in employees.csv** -- Replace UUID values with human-readable shift names.
10. **Standardize Department values** -- `(none)` vs blank vs actual department names. Consolidate.

### Priority 3: Dead Column Removal

11. **time_entries.csv** -- Drop or flag: `Act_Setup_Hrs`, `Act_Scrap_Qty`, `Setup_Overtime_Hrs`, `Setup_Labor_Rate`, `Entry_Type`
12. **employees.csv** -- Drop: `Work_Center` (100% blank), `Class` (uniform "E")
13. **jobs.csv** -- Drop: `Est_Service`, `Est_Machine_Burden`, `Act_Machine_Burden`, `Est_GA_Burden`, `Act_GA_Burden` (all zeros)
14. **job_operations.csv** -- Drop: `Due_Date` (99% blank), setup columns, `Est_Machine_Burden`, `Act_Machine_Burden`, `Est_Total_Cost`
15. **work_centers.csv** -- Drop: `Machine_Burden`, `GA_Burden`, `Equipment` (all zeros/false)

### Priority 4: Subset Splitting

16. **Split time_entries into Production vs Overhead** -- Separate OH-* entries (26,702 rows) from production entries (122,805 rows)
17. **Flag zero-activity customers** -- Mark or separate the 171 customers with no jobs
18. **Flag zero-activity vendors** -- Mark or separate the 438 vendors with no POs

### Priority 5: Data Enrichment

19. **Add derived "Dormant" status to customers** -- Based on Last_Order recency (e.g., no order in 2+ years)
20. **Add Est vs Actual variance columns to jobs.csv** -- For hours, labor, materials to enable cost analysis
21. **Investigate and document blank fields** -- 15% blank Part_Numbers in jobs, 58% blank Departments in employees, 15% blank Vendors in POs

---

## Schema Analysis Update (2026-03-24)

Full schema extracted via `JOBBOSS_SCHEMA_EDA.csv` — 142 tables profiled from SQL Server.

**Key findings from schema analysis:**

- **We have 11 of 142 tables** — and most of our exports are column-limited (e.g., Job has 96 columns, we extracted 35; Job_Operation has 108, we extracted 26)
- **materials.csv is a derived summary, not the raw table** — the real Material table has 7,508 rows and 53 columns. Job-level material data lives in `Material_Req` (39,650 rows) and `Material_Trans` (218,168 rows)
- **Revenue data exists but was not extracted** — `Invoice_Header` (2,100 rows) and `Invoice_Detail` (5,494 rows) contain billing/revenue data needed for profitability analysis
- **Bill_Of_Jobs (198 rows) CONFIRMED resolves the orphaned sub-assembly jobs** — 111 parent jobs break into 198 component jobs using suffixes: `_BTM` (bottom), `_TOP` (top), `_MAN` (manway/shell), `_PRE` (pre-assembly), `_ADM` (admin). This is the tank fabrication assembly hierarchy.
- **Shift table (2 rows) CONFIRMED resolves the employee GUID issue** — `B168CA62...` = "1ST" (first shift), `FFBD432F...` = "DESIGN SCH" (design schedule). Both have 40-hour weekly OT threshold.
- **Invoice data now extracted** — 2,100 invoices, $90.6M total revenue (2014-2026). $2.96M open AR across 38 unpaid invoices. Top customers: ONEACONS ($4.48M), SOLVSPEC ($4.45M), FLOQENGI ($3.40M)
- **Sales Orders module is unused** — SO_Header and SO_Detail are both empty (0 rows), confirming direct job-entry workflow
- **43 tables are completely empty** — significant portions of JobBOSS functionality are not in use

> See `JobBOSS/SCHEMA_ANALYSIS_AND_EXTRACTION_PLAN.md` for the full extraction priority plan with SQL queries.

---

## Notes

- **The data is well-linked overall** -- all primary foreign key relationships (time_entries -> jobs, employees, work_centers; jobs -> customers; POs -> vendors; deliveries -> jobs) are clean with zero orphans.
- **The one broken link** is job_operations -> jobs, where 110 sub-assembly style jobs exist only in operations. The `Bill_Of_Jobs` table (198 rows) likely contains the parent-child mappings that explain these.
- **Setup tracking is not used** -- confirmed across time_entries, job_operations, operations, and work_centers. All setup columns are dead weight.
- **Machine Burden and GA Burden are not used** -- confirmed across all tables. These cost allocation methods are not implemented.
- **The operations.csv file is purely a template catalog** -- no transactional data, all run/setup values are zero. It defines the standard workflow steps.
- **materials.csv is aggregate-only** -- it shows totals per material code, not per-job breakdowns. Job-level material data lives in `Material_Req` (39,650 rows) and `Material_Trans` (218,168 rows).
