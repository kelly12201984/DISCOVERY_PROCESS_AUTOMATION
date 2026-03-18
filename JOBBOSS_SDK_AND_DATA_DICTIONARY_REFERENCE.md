# JobBOSS SDK & Data Dictionary — Technical Reference
**Savannah Tank & Equipment — Discovery Document**
**Date:** March 17, 2026

---

## Purpose

This document consolidates all findings from the JobBOSS XML SDK Developer's Guide and the JobBOSS Data Dictionary (v18.2) to serve as a reference for integration planning, automation development, and system understanding. It is intended to be shared with engineering/technical stakeholders evaluating how to connect external tools (scheduling, estimation, dashboards, etc.) with the JobBOSS ERP system.

---

## Part 1: JobBOSS XML SDK

### 1.1 Architecture Overview

- **Protocol:** XML request/response pattern over COM (Component Object Model)
- **COM Object:** `JBRequestProcessor` (provided by `Jbinterface.exe`)
- **XML Engine:** Microsoft XML Core Services (MSXML) 4.0
- **Database Support:** Microsoft Access and Microsoft SQL Server
- **Installation:** Automatically installed with JobBOSS client software
- **Licensing:** Session-based — each SDK session consumes a JobBOSS seat license

### 1.2 Authentication & Session Management

```
1. CreateSession(username, password) → returns Session ID
2. Use Session ID in all subsequent XML requests
3. CloseSession() → releases the seat license (CRITICAL — must always close)
```

- All XML requests require a valid Session ID
- Invalid or expired Session IDs trigger errors
- The SDK operates against the currently logged-in database
- **Always close sessions** to avoid consuming seat licenses unnecessarily

### 1.3 XML Document Structure

```xml
<JBXML>
  <JBXMLRequest>
    <!-- One or more functional request elements -->
    <CustomerAddRq>...</CustomerAddRq>
    <JobQueryRq>...</JobQueryRq>
  </JBXMLRequest>
</JBXML>
```

Response:
```xml
<JBXML>
  <JBXMLRespond>
    <!-- One or more functional response elements -->
    <CustomerAddRs>...</CustomerAddRs>
    <JobQueryRs>...</JobQueryRs>
  </JBXMLRespond>
</JBXML>
```

**Important:** Elements must be in the specified order — out-of-order elements cause processing failures.

### 1.4 Date/Time Format

ISO Standard: `YYYY-MM-DDThh:mm:ss`
- Example: `2026-03-17T14:30:00`
- The "T" is a literal character
- All time components (hh, mm, ss) must be present when the field type is Date

### 1.5 Special Character Encoding

| Character | XML Encoding |
|-----------|-------------|
| `&` | `&amp;` |
| `'` | `&apos;` |
| `"` | `&quot;` |
| `>` | `&gt;` |
| `<` | `&lt;` |

### 1.6 Supported Operations

Every supported entity has up to five operations:

| Operation | Tag Suffix | Description |
|-----------|-----------|-------------|
| **Add** | `AddRq` / `AddRs` | Create a new record |
| **Modify** | `ModRq` / `ModRs` | Update an existing record |
| **Delete** | `DelRq` / `DelRs` | Remove a record |
| **Query** | `QueryRq` / `QueryRs` | Retrieve a single record by ID |
| **List Query** | `ListQueryRq` / `ListQueryRs` | Retrieve multiple records with filters |

### 1.7 Supported Entities (Business Objects)

| Entity | Add | Modify | Delete | Query | List Query |
|--------|-----|--------|--------|-------|------------|
| **Job** | Yes | Yes | Yes | Yes | Yes |
| **Customer** | Yes | Yes | Yes | Yes | Yes |
| **Vendor** | Yes | Yes | Yes | Yes | Yes |
| **Material** | Yes | Yes | Yes | Yes | Yes |
| **Stock Item** | Yes | Yes | Yes | Yes | Yes |
| **Service Operation** | Yes | Yes | Yes | Yes | Yes |
| **Work Center** | Yes | Yes | Yes | Yes | Yes |
| **Sales Order** | Yes | Yes | Yes | Yes | Yes |
| **Quote** | Yes | Yes | Yes | Yes | Yes |
| **Time Entry** | Yes | Yes | Yes | Yes | Yes |
| **Department** | Yes | Yes | Yes | Yes | Yes |
| **Reference** | Yes | Yes | Yes | Yes | Yes |
| **Customer Type** | Yes | Yes | Yes | Yes | Yes |
| **Tax Code** | Yes | Yes | Yes | Yes | Yes |
| **Ship Via** | Yes | Yes | Yes | Yes | Yes |
| **Alloy** | Yes | Yes | Yes | Yes | Yes |
| **Material Class** | Yes | Yes | Yes | Yes | Yes |
| **Discount Level** | Yes | Yes | Yes | Yes | Yes |
| **Terms** | Yes | Yes | Yes | Yes | Yes |
| **Currency** | Yes | Yes | Yes | Yes | Yes |
| **Sales Code** | Yes | Yes | Yes | Yes | Yes |
| **Location Type** | Yes | Yes | Yes | Yes | Yes |
| **Warehouse** | Yes | Yes | Yes | Yes | Yes |
| **Additional Cost** | Yes | Yes | Yes | Yes | Yes |
| **Standard Text** | Yes | Yes | Yes | Yes | Yes |

### 1.8 Query Filters

- Wildcard support using `%` (percent) symbol
- Filter types: `IDFilter`, `NameFilter`, `TypeFilter`
- **Performance warning:** Large result sets without filters cause performance degradation — always use filters

### 1.9 Error Handling

| Error Code | Meaning |
|------------|---------|
| `0` | Success |
| `1` | Business logic error (e.g., customer not found, over credit limit, duplicate record) |
| `2` | COM object failure |

**Transaction Behavior:** If a request contains multiple operations (e.g., 3 CustomerAddRq elements) and any single one fails, the **entire batch is rolled back** — none of the records are committed.

### 1.10 Calculated Fields Available in Responses

These are computed by JobBOSS and returned read-only in query responses:
- `EstimatedTotalHours`
- `EstimatedTotalTime`
- `ActualTotalTime`
- `RemainingTotalTime`
- `EstimatedTotalCost`
- `ActualTotalCost`

### 1.11 Sample Code (Visual Basic)

```vb
Public Sub ProcessXMLRequests()
    ' 1. Create COM object
    Set oJBReqProc = CreateObject("JBRequestProcessor")

    ' 2. Create MSXML DOM documents
    Set oXMLReq = CreateObject("MSXML2.DOMDocument")
    Set oXMLResp = CreateObject("MSXML2.DOMDocument")

    ' 3. Load XML request from file
    oXMLReq.Load "C:\request.xml"

    ' 4. Process request — returns XML response string
    strResponse = oJBReqProc.ProcessRequest(oXMLReq.xml)

    ' 5. Load response into DOM
    oXMLResp.loadXML strResponse

    ' 6. Save response to file
    oXMLResp.Save "C:\response.xml"

    ' 7. ALWAYS close session to release license
    oJBReqProc.CloseSession
End Sub
```

---

## Part 2: JobBOSS Data Dictionary (v18.2)

### 2.1 Core Tables — Jobs & Production

#### Job Table (Primary)
The central table for all manufacturing work.

| Field | Type | Description |
|-------|------|-------------|
| Job | Key | Job number (e.g., "025-25") |
| Order_Date | Date | When the job was entered |
| Order_Qty | Numeric | Quantity ordered |
| Make_Qty | Numeric | Quantity to manufacture |
| Status | Text | **Pending, Active, Hold, Complete, Closed, Template** |
| Customer | FK | Links to Customer table |
| Ship_Via | FK | Shipping method |
| Various cost fields | Numeric | Estimated and actual costs |
| Various time fields | Numeric | Estimated and actual hours |

**Job Completion Rules (v8.1+):**
- Automatically completes when `Shipped_Qty >= Order_Qty`
- OR when `Transferred_Qty + Shipped_Qty >= Make_Qty`
- Does NOT auto-complete on routing completion alone

#### Job_Operation Table (Routing)
Defines the sequence of operations (routing steps) for each job.

| Field | Type | Description |
|-------|------|-------------|
| Job | FK | Links to Job table (referential integrity enforced) |
| Sequence | Numeric | Operation order |
| Work_Center | FK | Links to Work Center |
| Service | FK | Links to Service Operation |
| Setup_Hours | Numeric | Estimated setup time |
| Run | Numeric | Run time per unit |
| Status | Text | Operation status |

#### Bill_Of_Jobs Table (Assembly Relationships)
Maintains parent-child relationships between jobs.

| Field | Type | Description |
|-------|------|-------------|
| Parent_Job | FK | Assembly (parent) job |
| Component_Job | FK | Child job |
| Relationship_Type | Text | **Component** (parts needed), **Release** (job release), **Split** (sent ahead) |
| Relationship_Qty | Numeric | Quantity of component needed |
| Root_Job | FK | Top-level parent in assembly hierarchy (v8.0+) |

### 2.2 Core Tables — Customers & Contacts

#### Customer Table

| Field | Type | Description |
|-------|------|-------------|
| Customer | Key | Customer ID |
| Name | C45 | Customer name (expanded from C30 in v11.2) |
| Type | Text | **Active, Inactive, Prospect** |
| Credit_Limit | Numeric | Credit limit |
| Current_Balance | Numeric | Current AR balance |
| Ship_Via | FK | Default shipping method |
| Lead_Days | Numeric | Default lead time |
| Customer_Since | Date | Relationship start date |

#### Address Table
Supports multiple address types per customer/vendor.

| Field | Type | Description |
|-------|------|-------------|
| Address_Name | Text | Address label |
| Line1, Line2 | Text | Street address |
| City, State, Zip | Text | Location |
| Country | C50 | Country (expanded from C20 in v11.3) |
| Default flags | Bit | Position 1: Default Main, Position 2: Default Bill/Remit, Position 3: Default Ship To |
| Billable | Flag | Can be used for billing |
| Shippable | Flag | Can be used for shipping |

#### Contact Table

| Field | Type | Description |
|-------|------|-------------|
| ContactKey | Long Int | Primary key |
| Name, Title | Text | Contact info |
| Phone, Fax, Email | Text | Communication |
| Customer | FK | Links to Customer |
| Vendor | FK | Links to Vendor |
| Status | Text | Active / Inactive |
| Default_Invoice_Contact | Flag | Default for invoicing |

### 2.3 Core Tables — Materials & Inventory

#### Material Table

| Field | Type | Description |
|-------|------|-------------|
| Material | Key | Material ID |
| Type | Char | **R** (Raw Stock), **H** (Hardware), **S** (Supplies), **F** (Finished Goods) |
| Description | Text | Material description |
| Standard_Cost | Numeric | Standard cost |
| Average_Cost | Numeric | Average cost |
| Last_Cost | Numeric | Most recent purchase cost |
| Sell_Price | Numeric | Selling price |
| Reorder_Point | Numeric | Minimum stock trigger |
| Lead_Days | Numeric | Procurement lead time |
| Default_Location | FK | Default warehouse location |
| Purchase_Unit | Text | Unit of measure for purchasing |
| Cost_Unit | Text | Unit of measure for costing |
| Stock_Unit | Text | Unit of measure for inventory |

### 2.4 Core Tables — Financials

#### AP_Document Table (Accounts Payable)

| Field | Type | Description |
|-------|------|-------------|
| Status | Text | **Posted, Unposted, Hold** |
| Type | Text | **INV** (Invoice), **CM** (Credit Memo) |
| Vendor | FK | Links to Vendor |
| Document_Number | Text | Vendor invoice number |
| Original_Amount | Numeric | Original document amount |
| Open_Amount | Numeric | Remaining balance |
| Due_Date | Date | Payment due date |
| Terms | FK | Payment terms |
| Conversion_Rate | Numeric | Currency exchange rate |

#### Invoice_Header & Invoice_Detail Tables

| Field | Type | Description |
|-------|------|-------------|
| Status | Text | **Posted, Unposted** |
| Quantity | Numeric | Line item quantity |
| Unit_Price | Numeric | Price per unit |
| GL_Account | FK | General ledger account |
| Job | FK | Links to Job (if job-related) |
| Commission_Included | Flag | Sales commission in price (v11.11+) |

**Currency Note:** Invoice Detail stores values in *trading currency*; Invoice Header stores values in *base currency*.

#### Additional_Charge Table

| Field | Type | Description |
|-------|------|-------------|
| Job | FK | Links to Job |
| Description | Text | Charge description |
| Est_Price | Numeric | Estimated price |
| Act_Price | Numeric | Actual price |
| Job_Revenue | Flag | Counts as job revenue |
| Commissionable | Flag | Eligible for commission |

### 2.5 Supporting Tables

#### Employee Table

| Field | Type | Description |
|-------|------|-------------|
| Type | Text | **Shop, Sales, Other** |
| Status | Text | **Active, Inactive** |
| Class | Char | **I** (Independent), **E** (Employee) |
| Hourly_Rate | Numeric | Pay rate |
| Commission_Pct | Numeric | Commission percentage (Sales type only) |
| Department | FK | Department assignment |
| Supervisor | FK | Supervisor reference |
| Hire_Date | Date | Start date |
| Shift | FK | Assigned shift |

#### Delivery Table (v11.0+)

| Field | Type | Description |
|-------|------|-------------|
| DeliveryKey | Key | Primary key |
| Packlist | FK | Links to packing list |
| Job | FK | Links to Job |
| Promised_Qty | Numeric | Quantity promised |
| Shipped_Qty | Numeric | Quantity shipped |
| Remaining_Qty | Calculated | Promised - Shipped |
| Requested_Date | Date | Customer requested date |
| Promised_Date | Date | Committed date |
| Shipped_Date | Date | Actual ship date |
| Returned_Qty | Numeric | Returns tracking |

#### Attachment Table

| Field | Type | Description |
|-------|------|-------------|
| Owner_Type | Text | Job, Quote, Customer, Vendor, Material, Employee, PO, etc. |
| File_Type | Text | **File** (attachment) or **Link** (URL) — v11.9+ |
| Print_Attachment | Flag | Include when printing |

**Supported Owner Types:** Job, Quote, JobOperation, MaterialReq, QuoteOperation, QuoteReq, PartSpec, Customer, Vendor, Material, Operation, Employee, POHeader, PODetail, PackList, PackListItem

#### Auto_Number Table

| Field | Type | Description |
|-------|------|-------------|
| Type | Text | Invoice, Job, Quote, PurchaseOrder, SalesOrder, PackList, BOL, Group |
| System_Generated | Flag | Auto-generates on record creation |
| Last_Nbr | Numeric | Next available number |

#### Change_History Table (v9.0+)

Audit trail for PO changes and Job Routing changes (v10.1+).

**Tracked Changes Include:**
- Purchase Orders: Order Qty, Unit Cost, Due Date
- Job Routing: Operation Added/Removed, Status, Setup Hours, Run, Work Center, Vendor, Service, Sequence, Due Date, and more
- Each change records: Old Value, New Value, Change Date, Changed By

#### Bill_Of_Quotes Table

Similar to Bill_Of_Jobs but for quote-level assembly relationships (Parent_Quote ↔ Component_Quote).

#### Breaks Table (v8.1+)

Shift break definitions with start/end times and deduction rules.

#### Cost Table (GL Cost Tracking)

Period-based cost tracking with Budget, MTD, and Period Ending amounts. Created/updated with Journal Entry records.

#### Currency_Def & Currency_Rate Tables

Multi-currency support with exchange rates, effective dates, and formatting preferences.

#### CA_ProjectedCashFlow Table (v11.8+)

Cash flow projections with inflow/outflow tracking, beginning/ending balances.

#### FinPref Table

Financial preferences including fiscal period configuration and default GL accounts.

### 2.6 Key Relationships Map

```
Customer ──────┐
               ├──→ Job ──→ Job_Operation (routing steps)
Sales Order ───┘      │
                      ├──→ Bill_Of_Jobs (assembly hierarchy)
                      ├──→ Material Requirements
                      ├──→ Additional_Charge
                      ├──→ Delivery / Packlist
                      ├──→ Invoice_Detail → Invoice_Header
                      ├──→ Attachment
                      └──→ Change_History

Customer ──→ Address (multiple: Main, Bill, Ship)
Customer ──→ Contact (multiple)

Quote ──→ Bill_Of_Quotes (assembly hierarchy)
Quote ──→ QuoteOperation, QuoteReq

Vendor ──→ AP_Document
Vendor ──→ Address, Contact

Employee ──→ Department, Shift, Breaks
```

### 2.7 System-Wide Patterns

- **Replication Support:** `ObjectID` and `_OID` fields on most tables for multi-site sync
- **Audit Timestamps:** `Last_Updated` and `Created_Time` on critical tables
- **Soft Deletes:** Most entities use Status fields (Active/Inactive) rather than hard deletes
- **Currency Layers:** Base currency vs. Trading currency — careful mapping required
- **Material Types:** 4 base types — R (Raw Stock), H (Hardware), S (Supplies), F (Finished Goods)

---

## Part 3: Integration Considerations for ST&E

### 3.1 What the SDK Can Do for Savannah Tank

Based on ST&E's current processes (spreadsheet-based tracking, manual data entry), the JobBOSS SDK enables:

| Use Case | SDK Capability | Current ST&E Process |
|----------|---------------|---------------------|
| **Job creation from estimates** | `JobAddRq` — create jobs with customer, quantities, dates | Manual entry from OTTO estimates |
| **Job status queries** | `JobQueryRq` / `JobListQueryRq` — pull active jobs, filter by status | April's Released Jobs spreadsheet |
| **Customer management** | `CustomerAddRq` / `CustomerQueryRq` | Manual entry |
| **Time entry automation** | `TimeEntryAddRq` — push shop floor hours | Manual data collection |
| **Material/BOM queries** | `MaterialQueryRq` / `StockItemQueryRq` | Manual stock checks |
| **Quote-to-Job conversion** | `QuoteQueryRq` → `JobAddRq` | Manual process |
| **Dashboard data feeds** | `JobListQueryRq` with filters — pull all active jobs, hours, costs | Dustin's Efficiency Tracker spreadsheet |
| **Delivery tracking** | Query Delivery table for promised vs. shipped | Delivery Window spreadsheet |

### 3.2 Key Integration Patterns

1. **Read from JobBOSS → Populate Dashboards**
   - Use `ListQueryRq` with status filters to pull active jobs
   - Calculate efficiency from estimated vs. actual hours
   - Feed into production schedule / capacity planning tools

2. **Write to JobBOSS ← External Systems**
   - OTTO (estimation tool) could create Quotes or Jobs via SDK
   - Shop floor data collection could push Time Entries
   - Customer portal could create Sales Orders

3. **Sync Between JobBOSS ↔ Spreadsheets**
   - Replace manual PM Tracker with automated JobBOSS queries
   - Auto-generate Released Jobs status from Job + Delivery tables
   - Build Plan Log could be auto-populated from Job table

### 3.3 Direct Database Access (Alternative to SDK)

Since ST&E uses SQL Server, direct database queries are also possible for **read-only** reporting:

```sql
-- Example: Active jobs with hours and status
SELECT j.Job, j.Customer, j.Status, j.Order_Qty,
       j.EstimatedTotalHours, j.ActualTotalTime, j.RemainingTotalTime
FROM Job j
WHERE j.Status = 'Active'
ORDER BY j.Order_Date;

-- Example: Job routing with work centers
SELECT jo.Job, jo.Sequence, jo.Work_Center, jo.Setup_Hours, jo.Run
FROM Job_Operation jo
JOIN Job j ON jo.Job = j.Job
WHERE j.Status = 'Active'
ORDER BY jo.Job, jo.Sequence;
```

**Warning:** Direct writes to the database bypass JobBOSS business logic and can corrupt data. Use the SDK for any write operations.

### 3.4 Practical Tips & Gotchas

1. **Session Licenses:** Always close sessions — orphaned sessions consume seat licenses that other users need
2. **Batch Transactions:** If any record in a batch fails, ALL records in that batch are rolled back — design for small batches
3. **Element Order:** XML elements must be in the exact order specified in the SDK guide — out-of-order elements fail silently or with cryptic errors
4. **Filter Everything:** Always use filters on ListQuery requests — unfiltered queries against large tables cause severe performance degradation
5. **Currency Complexity:** Invoice Detail uses trading currency, Invoice Header uses base currency — be careful when aggregating financial data
6. **Job Completion Logic:** Jobs auto-complete based on shipped/transferred quantities, NOT routing completion — don't rely on operation status alone

### 3.5 Installation Context

Per the email from Kelly Arseneau (3/16/2026), JobBOSS is being installed on machine `DESKTOP-L114GHS` via remote installation. This suggests the system is actively being set up or expanded.

---

## Part 4: Recommended Next Steps

1. **Confirm SQL Server access** — Determine if direct read-only database access is available for reporting/dashboards
2. **Identify SDK version** — Confirm which version of the XML SDK is installed and whether it matches the v18.2 data dictionary
3. **Map current spreadsheets to JobBOSS tables** — Determine which manual tracking can be replaced by querying Job, Job_Operation, Delivery, and Employee tables
4. **Prototype a read-only dashboard** — Start with `JobListQueryRq` to pull active jobs and compare estimated vs. actual hours (replaces Efficiency Tracker)
5. **Plan OTTO integration** — Design how the estimation tool will create Quotes or Jobs via SDK
6. **Evaluate session license capacity** — Determine how many concurrent SDK sessions are available without impacting user licenses

---

*Document generated from: JobBOSS XML SDK Developer's Guide, JobBOSS Data Dictionary v18.2, JobBOSS Installation email, and ST&E Discovery Documents.*
