# JobBOSS Data Exports

CSV extracts from the PRODUCTION database on DC2 for EDA.
To refresh: `python export_jobboss.py`

## Files

| File | Rows | Description |
|------|------|-------------|
| `jobs.csv` | 1,758 | All jobs (2014–2026) with est/actual hours, labor, material, price |
| `job_operations.csv` | 64,559 | Every routing step on every job with est vs actual hours and costs |
| `time_entries.csv` | 149,507 | Every time entry (who, when, what job, what operation, hours, rate) |
| `employees.csv` | 278 | All employees with hourly rates, department, hire date, status |
| `customers.csv` | 388 | Customers with job counts and total revenue |
| `work_centers.csv` | 31 | Shop floor and indirect work centers with rates and burden |
| `operations.csv` | 208 | Master operation definitions (routing step library) |
| `materials.csv` | 1,436 | Materials with usage counts and estimated costs |
| `purchase_orders.csv` | 12,044 | PO headers with vendor, dates, line counts, estimated totals |
| `vendors.csv` | 778 | Vendors with PO counts |
| `deliveries.csv` | 1,343 | Delivery records with promised/shipped dates and quantities |

## Quick Start (pandas)

```python
import pandas as pd

jobs = pd.read_csv('JOBBOSS_DATA/jobs.csv', parse_dates=['Order_Date','Sched_Start','Sched_End'])
ops = pd.read_csv('JOBBOSS_DATA/job_operations.csv')
time = pd.read_csv('JOBBOSS_DATA/time_entries.csv', parse_dates=['Work_Date'])
emps = pd.read_csv('JOBBOSS_DATA/employees.csv', parse_dates=['Hire_Date'])
```

## Key Relationships

- `jobs.Job` → `job_operations.Job` → `time_entries.Job` (1:many:many)
- `time_entries.Employee` → `employees.Employee`
- `time_entries.WC` → `work_centers.Work_Center`
- `jobs.Customer` → `customers.Customer`
- `purchase_orders.Vendor` → `vendors.Vendor`
