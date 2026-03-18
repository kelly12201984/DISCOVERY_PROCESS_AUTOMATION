# JobBOSS Integration Implementation Guide
## OTTO → JobBOSS Automation for Savannah Tank & Equipment

**Purpose:** Implementation-ready XML structures, SQL statements, and field maps for automating pressure vessel manufacturing workflows from OTTO into JobBOSS.

**Sources:** JobBOSS XML SDK Developer's Guide (63 pages), JobBOSS Data Dictionary v18.2 (108 pages)

---

## Table of Contents

1. [JobAddRq — Complete Structure](#1-jobaddrq--complete-structure)
2. [Material Requirements on Jobs (BOM Push)](#2-material-requirements-on-jobs-bom-push)
3. [Purchase Order Creation (Direct SQL)](#3-purchase-order-creation-direct-sql)
4. [TimeEntryAddRq — Shop Floor Labor Logging](#4-timeentryaddreq--shop-floor-labor-logging)
5. [Dashboard Queries — Active Jobs, % Complete, Hours, Materials](#5-dashboard-queries)
6. [Full SDK Write Capability Audit](#6-full-sdk-write-capability-audit)

---

## 1. JobAddRq — Complete Structure

The SDK supports creating a full job with routing AND bill of materials in a **single atomic request** via nested elements. If any nested element fails, the entire job creation rolls back.

### Complete XML Example — Pressure Vessel Job

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-JOB-20260317-001</TransactionId>
    <RequestType>JobAddRq</RequestType>
    <RequestData>
      <JobAddRq>
        <!-- === JOB HEADER === -->
        <Job>26-0147</Job>                          <!-- varchar(10) PK — ST&E job number -->
        <Customer>DATACOOL</Customer>                <!-- varchar(10) FK to Customer table -->
        <Ship_To>DATACOOL-MAIN</Ship_To>             <!-- varchar(10) FK to Ship_To table -->
        <Order_Date>2026-03-17</Order_Date>          <!-- datetime -->
        <Ship_Date>2026-06-15</Ship_Date>            <!-- datetime — promised delivery -->
        <Start_Date>2026-03-24</Start_Date>          <!-- datetime — scheduled shop start -->
        <Part_Number>PV-DC-4896-150</Part_Number>    <!-- varchar(30) — vessel part number -->
        <Rev>A</Rev>                                 <!-- varchar(10) — drawing revision -->
        <Description>48x96 150# COOLING VESSEL</Description> <!-- varchar(30) — SHORT, 30 char max -->
        <Order_Quantity>3</Order_Quantity>            <!-- decimal — qty customer ordered -->
        <Make_Quantity>3</Make_Quantity>              <!-- decimal — qty to manufacture -->
        <Status>Active</Status>                      <!-- varchar(20) — Active, Complete, Cancelled, Hold -->
        <Priority>5</Priority>                       <!-- int — 1=highest, 10=lowest -->
        <Price>47500.00</Price>                      <!-- money — unit selling price -->
        <Trade_Currency>USD</Trade_Currency>          <!-- varchar(3) -->
        <Build_To>Stock</Build_To>                   <!-- varchar(10) — Stock or Order -->
        <Ship_Via>COMMON CARRIER</Ship_Via>           <!-- varchar(20) -->
        <Lead_Days>60</Lead_Days>                    <!-- int — manufacturing lead time -->
        <Sales_Code>PV</Sales_Code>                  <!-- varchar(10) — for reporting/categorization -->
        <Drawing>DWG-PV-4896-150-A</Drawing>         <!-- varchar(30) — drawing reference -->
        <Note_Text>ASME Section VIII Div 1. 48"ID x 96"SS. SA-516-70 shell, 2:1 SE heads. Design: 150 PSI @ 400F. MDMT: -20F. Full RT per UW-11(a)(5)(b). Code stamp required. 3rd party AI by Hartford Steam Boiler. Data center cooling application — glycol service. Customer PO: DC-2026-0892.</Note_Text>

        <!-- === ROUTING (OPERATIONS) === -->

        <!-- Op 10: Layout & Cutting -->
        <OperationAdd>
          <Work_Center>CUT</Work_Center>             <!-- varchar(10) FK to Work_Center table -->
          <Operation_Service>LAYOUT-CUT</Operation_Service> <!-- varchar(30) FK to Operation_Service -->
          <Sequence>10</Sequence>                    <!-- smallint — operation sequence number (PK with Job) -->
          <Est_Setup_Hrs>2.0</Est_Setup_Hrs>         <!-- decimal -->
          <Est_Run_Hrs>8.0</Est_Run_Hrs>             <!-- decimal — total run hours for full qty -->
          <Est_Run_Qty>3</Est_Run_Qty>               <!-- decimal — qty this op produces -->
          <Note_Text>Layout shell courses and head blanks per DWG-PV-4896-150-A. Plasma cut shell plates. Verify material certs SA-516-70 before cutting.</Note_Text>
        </OperationAdd>

        <!-- Op 20: Rolling -->
        <OperationAdd>
          <Work_Center>ROLL</Work_Center>
          <Operation_Service>ROLL-SHELL</Operation_Service>
          <Sequence>20</Sequence>
          <Est_Setup_Hrs>1.5</Est_Setup_Hrs>
          <Est_Run_Hrs>12.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>Roll shell courses to 48" ID. Check roundness with templates — max 1% deviation per UG-80.</Note_Text>
        </OperationAdd>

        <!-- Op 30: Fit-Up -->
        <OperationAdd>
          <Work_Center>FIT</Work_Center>
          <Operation_Service>FIT-VESSEL</Operation_Service>
          <Sequence>30</Sequence>
          <Est_Setup_Hrs>2.0</Est_Setup_Hrs>
          <Est_Run_Hrs>24.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>Fit shells, heads, nozzles per drawing. Tack weld. Verify nozzle projections and orientations. Check all dimensions before welding.</Note_Text>
        </OperationAdd>

        <!-- Op 40: Welding -->
        <OperationAdd>
          <Work_Center>WELD</Work_Center>
          <Operation_Service>WELD-ASME</Operation_Service>
          <Sequence>40</Sequence>
          <Est_Setup_Hrs>1.0</Est_Setup_Hrs>
          <Est_Run_Hrs>48.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>Weld per WPS. All long seams and circ seams full pen. Nozzle welds per detail. Full RT required UW-11(a)(5)(b). Log welder ID and WPS for each seam in MDR.</Note_Text>
        </OperationAdd>

        <!-- Op 50: NDE / Radiography -->
        <OperationAdd>
          <Work_Center>NDE</Work_Center>
          <Operation_Service>RT-EXAM</Operation_Service>
          <Sequence>50</Sequence>
          <Est_Setup_Hrs>0.5</Est_Setup_Hrs>
          <Est_Run_Hrs>16.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>Full RT per UW-51. All long seams and circ seams. Acceptance per UW-52 Table UW-52. RT film reader report required for data book.</Note_Text>
        </OperationAdd>

        <!-- Op 60: PWHT (if required) -->
        <OperationAdd>
          <Work_Center>PWHT</Work_Center>
          <Operation_Service>STRESS-RELIEF</Operation_Service>
          <Sequence>60</Sequence>
          <Est_Setup_Hrs>2.0</Est_Setup_Hrs>
          <Est_Run_Hrs>8.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>PWHT per UCS-56. 1100F +/- 50F, 1 hr/inch. Chart recorder required. Thermocouple placement per Code.</Note_Text>
        </OperationAdd>

        <!-- Op 70: Hydrostatic Test -->
        <OperationAdd>
          <Work_Center>TEST</Work_Center>
          <Operation_Service>HYDRO-TEST</Operation_Service>
          <Sequence>70</Sequence>
          <Est_Setup_Hrs>1.0</Est_Setup_Hrs>
          <Est_Run_Hrs>6.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>Hydro per UG-99. Test pressure 195 PSI (1.3x MAWP). Hold 30 min. AI witness required. Document on Form U-1.</Note_Text>
        </OperationAdd>

        <!-- Op 80: Final Finish / Paint -->
        <OperationAdd>
          <Work_Center>FINISH</Work_Center>
          <Operation_Service>BLAST-PAINT</Operation_Service>
          <Sequence>80</Sequence>
          <Est_Setup_Hrs>1.0</Est_Setup_Hrs>
          <Est_Run_Hrs>10.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>SSPC-SP6 blast. Prime with inorganic zinc. Topcoat per customer spec. Nameplate and NB stamp after AI sign-off.</Note_Text>
        </OperationAdd>

        <!-- Op 90: Ship -->
        <OperationAdd>
          <Work_Center>SHIP</Work_Center>
          <Operation_Service>LOAD-SHIP</Operation_Service>
          <Sequence>90</Sequence>
          <Est_Setup_Hrs>0.5</Est_Setup_Hrs>
          <Est_Run_Hrs>4.0</Est_Run_Hrs>
          <Est_Run_Qty>3</Est_Run_Qty>
          <Note_Text>Load on flatbed. Saddle supports required. Data book with: U-1, MTRs, WPS/PQR, RT reports, hydro chart, PWHT chart. Ship to customer site.</Note_Text>
        </OperationAdd>

        <!-- === BILL OF MATERIALS (nested in JobAddRq) === -->
        <!-- Sequence field links material to the operation that consumes it -->

        <!-- Shell Plate -->
        <MaterialRequirementAdd>
          <Material>SA516-70-0.75</Material>          <!-- varchar(30) FK to Material table -->
          <Description>SA-516-70 3/4" PLATE</Description> <!-- varchar(30) -->
          <Est_Qty>1800.00</Est_Qty>                  <!-- decimal — lbs for plate -->
          <Est_Unit_Cost>1.85</Est_Unit_Cost>          <!-- money — $/lb -->
          <Sequence>10</Sequence>                      <!-- links to Op 10 (Layout & Cut) -->
          <Vendor>METALS-INC</Vendor>                  <!-- varchar(10) FK to Vendor table -->
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>   <!-- B=Buy (purchase), P=Pick from stock -->
        </MaterialRequirementAdd>

        <!-- 2:1 Semi-Elliptical Heads -->
        <MaterialRequirementAdd>
          <Material>HEAD-48-SE-075</Material>
          <Description>48"ID 2:1 SE HEAD 3/4"</Description>
          <Est_Qty>6.00</Est_Qty>                      <!-- 2 heads x 3 vessels -->
          <Est_Unit_Cost>2850.00</Est_Unit_Cost>       <!-- each -->
          <Sequence>30</Sequence>                      <!-- links to Op 30 (Fit-Up) -->
          <Vendor>CONREX</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MaterialRequirementAdd>

        <!-- Nozzles (example: 6" 150# WN flange nozzle) -->
        <MaterialRequirementAdd>
          <Material>NOZZ-6-150-WN</Material>
          <Description>6" 150# WN NOZZLE ASSY</Description>
          <Est_Qty>12.00</Est_Qty>                     <!-- 4 nozzles x 3 vessels -->
          <Est_Unit_Cost>485.00</Est_Unit_Cost>
          <Sequence>30</Sequence>
          <Vendor>BELFAB</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MaterialRequirementAdd>

        <!-- Flanges (example: 6" 150# RF WN) -->
        <MaterialRequirementAdd>
          <Material>FLG-6-150-RFWN</Material>
          <Description>6" 150# RF WN FLANGE A105</Description>
          <Est_Qty>12.00</Est_Qty>
          <Est_Unit_Cost>145.00</Est_Unit_Cost>
          <Sequence>30</Sequence>
          <Vendor>BELFAB</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MaterialRequirementAdd>

        <!-- Gaskets -->
        <MaterialRequirementAdd>
          <Material>GSKT-6-150-RF-SW</Material>
          <Description>6" 150# RF SPIRAL WOUND</Description>
          <Est_Qty>12.00</Est_Qty>
          <Est_Unit_Cost>28.50</Est_Unit_Cost>
          <Sequence>30</Sequence>
          <Vendor>LAMONS</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MaterialRequirementAdd>

        <!-- Bolting -->
        <MaterialRequirementAdd>
          <Material>BOLT-6-150-B7</Material>
          <Description>3/4x4.25 B7/2H STUD SET</Description>
          <Est_Qty>24.00</Est_Qty>                     <!-- 8 bolts x 3 vessels (one nozzle set) -->
          <Est_Unit_Cost>3.75</Est_Unit_Cost>
          <Sequence>30</Sequence>
          <Vendor>FASTENAL</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MaterialRequirementAdd>

        <!-- Weld Wire / Consumables -->
        <MaterialRequirementAdd>
          <Material>WELD-E7018-125</Material>
          <Description>E7018 1/8" ELECTRODE</Description>
          <Est_Qty>300.00</Est_Qty>                    <!-- lbs -->
          <Est_Unit_Cost>2.45</Est_Unit_Cost>
          <Sequence>40</Sequence>                      <!-- links to Op 40 (Welding) -->
          <Vendor>LINCOLN</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MaterialRequirementAdd>

        <!-- Misc: RT Film (via MiscMaterialRequirementAdd for non-inventoried items) -->
        <MiscMaterialRequirementAdd>
          <Description>RT FILM AND PROCESSING</Description>
          <Est_Qty>1.00</Est_Qty>
          <Est_Unit_Cost>1200.00</Est_Unit_Cost>       <!-- lump sum per lot -->
          <Sequence>50</Sequence>                      <!-- links to Op 50 (NDE) -->
          <Vendor>MISTRAS</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MiscMaterialRequirementAdd>

        <!-- Paint -->
        <MiscMaterialRequirementAdd>
          <Description>BLAST/PRIME/TOPCOAT MATL</Description>
          <Est_Qty>1.00</Est_Qty>
          <Est_Unit_Cost>850.00</Est_Unit_Cost>
          <Sequence>80</Sequence>                      <!-- links to Op 80 (Finish) -->
          <Vendor>SHERWIN</Vendor>
          <Pick_Buy_Indicator>B</Pick_Buy_Indicator>
        </MiscMaterialRequirementAdd>

        <!-- === ADDITIONAL CHARGES === -->
        <AdditionalChargeAdd>
          <Charge_Description>3RD PARTY AI INSPECTION</Charge_Description>
          <Est_Charge_Amt>3500.00</Est_Charge_Amt>
          <Charge_Type>Subcontract</Charge_Type>
        </AdditionalChargeAdd>

        <AdditionalChargeAdd>
          <Charge_Description>NB REGISTRATION FEE</Charge_Description>
          <Est_Charge_Amt>175.00</Est_Charge_Amt>
          <Charge_Type>Other</Charge_Type>
        </AdditionalChargeAdd>

      </JobAddRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

### Field Reference — Job Header

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `Job` | varchar(10) | **YES** | Primary key. ST&E format: `YY-NNNN` |
| `Customer` | varchar(10) | **YES** | FK to Customer table. Must exist first. |
| `Order_Date` | datetime | **YES** | Date order was received |
| `Ship_Date` | datetime | Recommended | Promised delivery date |
| `Part_Number` | varchar(30) | Recommended | Your vessel part number |
| `Rev` | varchar(10) | Optional | Drawing revision |
| `Description` | varchar(30) | Recommended | **30 char limit — keep it SHORT** |
| `Order_Quantity` | decimal | **YES** | Customer ordered qty |
| `Make_Quantity` | decimal | **YES** | Qty to manufacture |
| `Status` | varchar(20) | **YES** | `Active`, `Complete`, `Cancelled`, `Hold` |
| `Priority` | int | Optional | 1=highest, 10=lowest |
| `Price` | money | Optional | Unit selling price |
| `Trade_Currency` | varchar(3) | Optional | `USD` |
| `Ship_To` | varchar(10) | Optional | FK to Ship_To table |
| `Start_Date` | datetime | Optional | Planned shop start |
| `Build_To` | varchar(10) | Optional | `Stock` or `Order` |
| `Ship_Via` | varchar(20) | Optional | Carrier/method |
| `Lead_Days` | int | Optional | Manufacturing lead time |
| `Sales_Code` | varchar(10) | Optional | Reporting category |
| `Drawing` | varchar(30) | Optional | Drawing reference number |
| `Note_Text` | text | Optional | Unlimited notes — put ASME details here |
| `Top_Lvl_Job` | varchar(10) | Optional | Parent job for sub-assemblies |
| `Source` | varchar(10) | Optional | Where job originated |

### Field Reference — OperationAdd (nested)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `Work_Center` | varchar(10) | **YES** | FK to Work_Center. Must exist. |
| `Operation_Service` | varchar(30) | **YES** | FK to Operation_Service. Must exist. |
| `Sequence` | smallint | **YES** | Operation sequence # (10, 20, 30...). PK with Job. |
| `Est_Setup_Hrs` | decimal | Recommended | Estimated setup hours |
| `Est_Run_Hrs` | decimal | Recommended | Estimated total run hours |
| `Est_Run_Qty` | decimal | Recommended | Expected output qty for this op |
| `Note_Text` | text | Optional | Operation instructions |

### Field Reference — MaterialRequirementAdd (nested)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `Material` | varchar(30) | **YES** | FK to Material table. Must exist. |
| `Description` | varchar(30) | Recommended | Material description (30 char limit) |
| `Est_Qty` | decimal | **YES** | Estimated quantity needed |
| `Est_Unit_Cost` | money | Recommended | Cost per unit |
| `Sequence` | smallint | Recommended | Links to which operation consumes this material |
| `Vendor` | varchar(10) | Optional | FK to Vendor table — preferred supplier |
| `Pick_Buy_Indicator` | varchar(1) | **YES** | `P` = pick from stock, `B` = buy/purchase |

### Field Reference — MiscMaterialRequirementAdd (nested)

For non-inventoried items (subcontract services, consumables you don't track as stock items):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `Description` | varchar(30) | **YES** | No Material FK needed — just a description |
| `Est_Qty` | decimal | **YES** | Quantity |
| `Est_Unit_Cost` | money | Recommended | Cost per unit |
| `Sequence` | smallint | Recommended | Links to operation |
| `Vendor` | varchar(10) | Optional | FK to Vendor table |
| `Pick_Buy_Indicator` | varchar(1) | Recommended | Usually `B` for misc items |

### Field Reference — AdditionalChargeAdd (nested)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `Charge_Description` | varchar(30) | **YES** | Description of charge |
| `Est_Charge_Amt` | money | **YES** | Estimated charge amount |
| `Charge_Type` | varchar(20) | Recommended | Category (e.g., `Subcontract`, `Other`, `Freight`) |

### Critical Implementation Notes — JobAddRq

1. **Atomic transaction**: If ANY nested element fails (bad Work_Center FK, bad Material FK, etc.), the ENTIRE job creation rolls back — no partial jobs.
2. **Master data must exist first**: Work_Center, Operation_Service, Material, Vendor, Customer records must all exist before referencing them. Use the SDK's `WorkCenterAddRq`, `MaterialAddRq`, `VendorAddRq`, `CustomerAddRq` to create them if needed.
3. **Description is 30 chars max**: This catches people. `"48"ID x 96"SS 150# 2:1 SE HEAD COOLING VESSEL"` won't fit. Use abbreviations.
4. **Job number is 10 chars max**: `26-0147` fits. `2026-PV-0147` doesn't.
5. **Sequence numbers are the BOM↔Routing link**: A `MaterialRequirementAdd` with `<Sequence>30</Sequence>` means that material is consumed at Operation 30 (Fit-Up). This drives material timing in scheduling.

---

## 2. Material Requirements on Jobs (BOM Push)

### How OTTO Should Push the BOM

OTTO calculates the complete bill of materials for each pressure vessel. The BOM push is done **inside the JobAddRq** as shown above — there is NO separate "BOM Add" request. Materials are nested directly in the job creation.

### BOM Categories and How They Map

| OTTO BOM Category | SDK Element | Material Table Entry Needed? |
|---|---|---|
| Shell plate (SA-516-70, SA-240-304, etc.) | `MaterialRequirementAdd` | YES — create with `MaterialAddRq` |
| Heads (2:1 SE, F&D, hemispherical) | `MaterialRequirementAdd` | YES |
| Nozzles / pipe | `MaterialRequirementAdd` | YES |
| Flanges (WN, SO, blind) | `MaterialRequirementAdd` | YES |
| Gaskets (spiral wound, ring joint) | `MaterialRequirementAdd` | YES |
| Bolting (B7 studs, 2H nuts) | `MaterialRequirementAdd` | YES |
| Weld consumables | `MaterialRequirementAdd` | YES |
| Subcontract NDE (RT, UT, MT, PT) | `MiscMaterialRequirementAdd` | NO — description only |
| PWHT (if subcontracted) | `MiscMaterialRequirementAdd` | NO |
| Paint / blast materials | `MiscMaterialRequirementAdd` | NO |
| 3rd party inspection | `AdditionalChargeAdd` | NO — it's a charge, not material |
| NB registration | `AdditionalChargeAdd` | NO |
| Freight | `AdditionalChargeAdd` | NO |

### Setting Up Material Master Records

Before OTTO can reference materials in `MaterialRequirementAdd`, they must exist in the Material table. Use the SDK to create them:

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-MAT-001</TransactionId>
    <RequestType>MaterialAddRq</RequestType>
    <RequestData>
      <MaterialAddRq>
        <Material>SA516-70-0.75</Material>        <!-- varchar(30) PK -->
        <Description>SA-516-70 3/4" PLATE</Description>  <!-- varchar(30) -->
        <Type>Raw Material</Type>                  <!-- varchar(20) -->
        <Pick_Buy_Indicator>B</Pick_Buy_Indicator> <!-- B=Buy, P=Pick -->
        <Stocking_UM>LB</Stocking_UM>             <!-- varchar(4) — unit of measure -->
        <Lead_Days>14</Lead_Days>                  <!-- int — typical lead time -->
        <Last_Unit_Cost>1.85</Last_Unit_Cost>      <!-- money -->
      </MaterialAddRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

### OTTO's One-Shot Job+BOM Creation Workflow

```
1. OTTO completes vessel estimate
2. User clicks "Send to JobBOSS"
3. OTTO code:
   a. Query JobBOSS for existing Material records (MaterialQueryRq)
   b. Create any missing Material records (MaterialAddRq for each)
   c. Create any missing Vendor records (VendorAddRq for each)
   d. Build the JobAddRq XML with ALL nested elements:
      - OperationAdd for each routing step
      - MaterialRequirementAdd for each inventoried BOM line
      - MiscMaterialRequirementAdd for each non-inventoried BOM line
      - AdditionalChargeAdd for inspection, NB fees, freight
   e. Submit single JobAddRq → JobBOSS creates everything atomically
   f. Parse response for success/failure
```

### Linking Materials to POs After Job Creation

Once the job exists with `Pick_Buy_Indicator = 'B'` materials, you need Purchase Orders. The SDK **does NOT** have a PurchaseOrderAddRq. See Section 3 for the direct SQL approach.

After PO creation, update `Material_Req.PO_Detail` to link the BOM line to the PO line:

```sql
-- Link material requirement to PO line after PO creation
UPDATE Material_Req
SET PO_Detail = @NewPODetailId
WHERE Job = '26-0147'
  AND Material = 'SA516-70-0.75';
```

---

## 3. Purchase Order Creation (Direct SQL)

### The SDK Gap

**There is no `PurchaseOrderAddRq` in the JobBOSS XML SDK.** Purchase Orders must be created via direct SQL INSERT into the `PO_Header` and `PO_Detail` tables.

### Table Structure — PO_Header

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `PO_Number` | varchar(10) | **PK** | Your PO number. Must be unique. |
| `Vendor` | varchar(10) | **YES** | FK to Vendor table |
| `Status` | varchar(20) | **YES** | `Open`, `Closed`, `Cancelled` |
| `Order_Date` | datetime | **YES** | Date PO is created |
| `Ship_Via` | varchar(20) | Optional | Shipping method |
| `Note_Text` | text | Optional | PO notes/instructions |
| `Trade_Currency` | varchar(3) | Optional | `USD` |
| `Confirming` | bit | Optional | Is this a confirming PO? Default 0 |
| `Tax_Code` | varchar(10) | Optional | Tax code |
| `Tax_Rate` | decimal | Optional | Tax percentage |
| `Freight` | money | Optional | Freight charges |
| `Printed` | bit | Optional | Has PO been printed? Default 0 |
| `Last_Updated` | datetime | **YES** | Timestamp — use GETDATE() |
| `Print_Date` | datetime | Optional | When PO was last printed |

### Table Structure — PO_Detail

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `PO_Detail` | int (identity) | **PK** | Auto-increment — do NOT specify on INSERT |
| `PO_Number` | varchar(10) | **YES** | FK to PO_Header |
| `Line` | smallint | **YES** | Line number (1, 2, 3...) |
| `Material` | varchar(30) | Optional | FK to Material table (if buying a tracked material) |
| `Job` | varchar(10) | Optional | FK to Job table — which job this material is for |
| `Description` | varchar(30) | **YES** | Line item description |
| `Order_Qty` | decimal | **YES** | Quantity ordered |
| `Recv_Qty` | decimal | **YES** | Quantity received (start at 0) |
| `Unit_Cost` | money | **YES** | Price per unit |
| `Pick_Buy_Indicator` | varchar(1) | Optional | `B` |
| `Promised_Date` | datetime | Recommended | Vendor's promised delivery date |
| `Status` | varchar(20) | **YES** | `Open`, `Received`, `Closed` |
| `Material_Req` | int | Optional | FK back to Material_Req.Material_Req (links PO line to job BOM line) |
| `Last_Updated` | datetime | **YES** | Timestamp |
| `Tax` | money | Optional | Tax amount for this line |
| `Note_Text` | text | Optional | Line item notes |
| `Due_Date` | datetime | Optional | Required-by date |

### Complete SQL Example — PO for Pressure Vessel Materials

```sql
-- ============================================================
-- Create PO for SA-516-70 plate and heads from METALS-INC
-- for Job 26-0147 (48x96 150# Cooling Vessels, qty 3)
-- ============================================================

BEGIN TRANSACTION;

-- Step 1: Get next PO number (your numbering logic)
DECLARE @PONumber VARCHAR(10) = 'PO-26-0089';

-- Step 2: Insert PO Header
INSERT INTO PO_Header (
    PO_Number,
    Vendor,
    Status,
    Order_Date,
    Ship_Via,
    Note_Text,
    Trade_Currency,
    Confirming,
    Printed,
    Last_Updated
)
VALUES (
    @PONumber,
    'METALS-INC',          -- FK to Vendor table
    'Open',                -- Status
    GETDATE(),             -- Order_Date
    'COMMON CARRIER',      -- Ship_Via
    'Job 26-0147. SA-516-70 plate for 48x96 150# cooling vessels (qty 3). MUST include MTRs. Material must be normalized per SA-20. Heat numbers required.',
    'USD',
    0,                     -- Not confirming
    0,                     -- Not yet printed
    GETDATE()
);

-- Step 3: Insert PO Detail lines

-- Line 1: Shell plate
INSERT INTO PO_Detail (
    PO_Number, Line, Material, Job, Description,
    Order_Qty, Recv_Qty, Unit_Cost, Pick_Buy_Indicator,
    Promised_Date, Status, Last_Updated, Note_Text
)
VALUES (
    @PONumber, 1, 'SA516-70-0.75', '26-0147', 'SA-516-70 3/4" PLATE',
    1800.00, 0, 1.85, 'B',
    '2026-04-07', 'Open', GETDATE(),
    'Normalized. MTRs required. Ship to Savannah Tank yard.'
);

-- Capture the auto-generated PO_Detail ID
DECLARE @PlateDetailId INT = SCOPE_IDENTITY();

-- Line 2: 2:1 SE Heads (from same vendor or different PO)
INSERT INTO PO_Detail (
    PO_Number, Line, Material, Job, Description,
    Order_Qty, Recv_Qty, Unit_Cost, Pick_Buy_Indicator,
    Promised_Date, Status, Last_Updated, Note_Text
)
VALUES (
    @PONumber, 2, 'HEAD-48-SE-075', '26-0147', '48"ID 2:1 SE HEAD 3/4"',
    6.00, 0, 2850.00, 'B',
    '2026-04-21', 'Open', GETDATE(),
    'SA-516-70 material. Must include head form report and MTR.'
);

DECLARE @HeadDetailId INT = SCOPE_IDENTITY();

-- Step 4: Link PO lines back to Material_Req records (bidirectional FK)

-- Link plate material requirement to PO line
UPDATE Material_Req
SET PO_Detail = @PlateDetailId
WHERE Job = '26-0147'
  AND Material = 'SA516-70-0.75'
  AND Sequence = 10;

-- Link head material requirement to PO line
UPDATE Material_Req
SET PO_Detail = @HeadDetailId
WHERE Job = '26-0147'
  AND Material = 'HEAD-48-SE-075'
  AND Sequence = 30;

-- Also update PO_Detail to point back to Material_Req
UPDATE PO_Detail
SET Material_Req = (
    SELECT Material_Req FROM Material_Req
    WHERE Job = '26-0147' AND Material = 'SA516-70-0.75' AND Sequence = 10
)
WHERE PO_Detail = @PlateDetailId;

UPDATE PO_Detail
SET Material_Req = (
    SELECT Material_Req FROM Material_Req
    WHERE Job = '26-0147' AND Material = 'HEAD-48-SE-075' AND Sequence = 30
)
WHERE PO_Detail = @HeadDetailId;

COMMIT TRANSACTION;
```

### PO Numbering Strategy

JobBOSS does not auto-generate PO numbers. Your code must manage this. Options:

```sql
-- Option 1: Sequential with prefix
SELECT 'PO-' + RIGHT('00' + CAST(YEAR(GETDATE()) % 100 AS VARCHAR), 2) + '-' +
       RIGHT('0000' + CAST(ISNULL(MAX(CAST(RIGHT(PO_Number, 4) AS INT)), 0) + 1 AS VARCHAR), 4)
FROM PO_Header
WHERE PO_Number LIKE 'PO-' + RIGHT('00' + CAST(YEAR(GETDATE()) % 100 AS VARCHAR), 2) + '-%';

-- Result: PO-26-0089, PO-26-0090, etc.
```

### Receiving Against POs (Direct SQL)

When materials arrive, update the receiving quantities:

```sql
-- Receive 1800 lbs of plate against PO line
UPDATE PO_Detail
SET Recv_Qty = Recv_Qty + 1800.00,
    Status = CASE WHEN (Recv_Qty + 1800.00) >= Order_Qty THEN 'Received' ELSE 'Open' END,
    Last_Updated = GETDATE()
WHERE PO_Detail = @PlateDetailId;

-- If all lines received, close the PO header
UPDATE PO_Header
SET Status = 'Closed',
    Last_Updated = GETDATE()
WHERE PO_Number = @PONumber
  AND NOT EXISTS (
    SELECT 1 FROM PO_Detail
    WHERE PO_Number = @PONumber AND Status = 'Open'
  );
```

---

## 4. TimeEntryAddRq — Shop Floor Labor Logging

For tablet-based shop floor labor entry. Workers clock time against specific jobs and operations.

### Complete XML Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-TIME-20260317-001</TransactionId>
    <RequestType>TimeEntryAddRq</RequestType>
    <RequestData>
      <TimeEntryAddRq>
        <Employee>JSMITH</Employee>              <!-- varchar(10) FK to Employee table -->
        <Job>26-0147</Job>                       <!-- varchar(10) FK to Job table -->
        <Suffix>40</Suffix>                      <!-- smallint — maps to Job_Operation.Sequence (Op 40 = Welding) -->
        <Work_Date>2026-04-15</Work_Date>        <!-- datetime — date work was performed -->
        <Setup_Hrs>0.00</Setup_Hrs>              <!-- decimal — setup hours (0 if just running) -->
        <Run_Hrs>8.50</Run_Hrs>                  <!-- decimal — run hours worked -->
        <Good_Qty>1</Good_Qty>                   <!-- decimal — qty of good parts produced -->
        <Scrap_Qty>0</Scrap_Qty>                 <!-- decimal — qty scrapped -->
        <Work_Center>WELD</Work_Center>           <!-- varchar(10) FK to Work_Center table -->
      </TimeEntryAddRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

### Field Reference — TimeEntryAddRq

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `Employee` | varchar(10) | **YES** | FK to Employee table. Worker's ID. |
| `Job` | varchar(10) | **YES** | FK to Job table |
| `Suffix` | smallint | **YES** | **This is the operation Sequence number**, not a job suffix. `40` = Op 40 (Welding). |
| `Work_Date` | datetime | **YES** | Date the work was performed |
| `Setup_Hrs` | decimal | **YES** | Hours spent on setup (can be 0) |
| `Run_Hrs` | decimal | **YES** | Hours spent running/producing |
| `Good_Qty` | decimal | Recommended | Good parts produced this entry |
| `Scrap_Qty` | decimal | Recommended | Parts scrapped this entry |
| `Work_Center` | varchar(10) | Recommended | FK to Work_Center — should match the operation's work center |

### Batch Time Entry Example (Multiple Workers, One Shift)

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-TIME-BATCH-20260415</TransactionId>
    <RequestType>TimeEntryAddRq</RequestType>
    <RequestData>
      <!-- Welder 1 on vessel welding -->
      <TimeEntryAddRq>
        <Employee>JSMITH</Employee>
        <Job>26-0147</Job>
        <Suffix>40</Suffix>
        <Work_Date>2026-04-15</Work_Date>
        <Setup_Hrs>0.00</Setup_Hrs>
        <Run_Hrs>8.50</Run_Hrs>
        <Good_Qty>0</Good_Qty>
        <Scrap_Qty>0</Scrap_Qty>
        <Work_Center>WELD</Work_Center>
      </TimeEntryAddRq>

      <!-- Welder 2 on same operation -->
      <TimeEntryAddRq>
        <Employee>MJONES</Employee>
        <Job>26-0147</Job>
        <Suffix>40</Suffix>
        <Work_Date>2026-04-15</Work_Date>
        <Setup_Hrs>0.00</Setup_Hrs>
        <Run_Hrs>8.50</Run_Hrs>
        <Good_Qty>0</Good_Qty>
        <Scrap_Qty>0</Scrap_Qty>
        <Work_Center>WELD</Work_Center>
      </TimeEntryAddRq>

      <!-- Fitter on fit-up for different vessel -->
      <TimeEntryAddRq>
        <Employee>BWILSON</Employee>
        <Job>26-0148</Job>
        <Suffix>30</Suffix>
        <Work_Date>2026-04-15</Work_Date>
        <Setup_Hrs>1.00</Setup_Hrs>
        <Run_Hrs>7.00</Run_Hrs>
        <Good_Qty>1</Good_Qty>
        <Scrap_Qty>0</Scrap_Qty>
        <Work_Center>FIT</Work_Center>
      </TimeEntryAddRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

**CRITICAL**: In batch mode, if ANY TimeEntryAddRq in the batch fails (bad Employee, bad Job, bad Suffix), ALL entries in the batch roll back. For reliability on the shop floor, consider submitting each time entry individually rather than batching — a single worker's typo shouldn't wipe out everyone's entries.

### Data Stored in Job_Operation_Time Table

Each successful `TimeEntryAddRq` creates a row in `Job_Operation_Time`:

| Column | Source |
|--------|--------|
| `Job` | From request |
| `Suffix` | From request (maps to `Job_Operation.Sequence`) |
| `Employee` | From request |
| `Work_Date` | From request |
| `Setup_Hrs` | From request |
| `Run_Hrs` | From request |
| `Good_Qty` | From request |
| `Scrap_Qty` | From request |
| `Work_Center` | From request |
| `Overtime_Hrs` | Not settable via SDK — defaults to 0 |
| `Note_Text` | Not settable via SDK |
| `Activity` | Auto-populated by JobBOSS |

The SDK also **auto-updates** `Job_Operation` actuals:
- `Act_Setup_Hrs` += `Setup_Hrs`
- `Act_Run_Hrs` += `Run_Hrs`
- `Act_Run_Qty` += `Good_Qty`

This means you don't need to manually update operation actuals — time entry does it automatically.

### Tablet UI Workflow

```
1. Worker scans badge → Employee ID
2. Worker scans job traveler barcode → Job number
3. Worker selects operation from list → Suffix (Sequence)
4. Worker enters hours (or clock in/out calculated)
5. Worker enters qty completed and scrap
6. Tablet builds TimeEntryAddRq XML
7. Submit individually (NOT batch) for reliability
8. Show success/failure immediately on screen
```

---

## 5. Dashboard Queries

All dashboards read directly from SQL Server. These queries give you everything needed for a production management dashboard.

### Query 1: Active Jobs with % Complete (by Hours)

```sql
SELECT
    j.Job,
    j.Customer,
    j.Part_Number,
    j.Description,
    j.Order_Quantity,
    j.Status,
    j.Order_Date,
    j.Ship_Date,
    DATEDIFF(day, GETDATE(), j.Ship_Date) AS Days_Until_Ship,

    -- Estimated hours (total across all operations)
    SUM(jo.Est_Setup_Hrs + jo.Est_Run_Hrs) AS Total_Est_Hours,

    -- Actual hours logged
    SUM(jo.Act_Setup_Hrs + jo.Act_Run_Hrs) AS Total_Act_Hours,

    -- % Complete by hours
    CASE
        WHEN SUM(jo.Est_Setup_Hrs + jo.Est_Run_Hrs) = 0 THEN 0
        ELSE ROUND(
            SUM(jo.Act_Setup_Hrs + jo.Act_Run_Hrs) * 100.0 /
            SUM(jo.Est_Setup_Hrs + jo.Est_Run_Hrs), 1)
    END AS Pct_Complete_Hours,

    -- Hours variance (negative = over estimate)
    SUM(jo.Est_Setup_Hrs + jo.Est_Run_Hrs) - SUM(jo.Act_Setup_Hrs + jo.Act_Run_Hrs) AS Hours_Remaining,

    -- Price and revenue info
    j.Price,
    j.Price * j.Order_Quantity AS Total_Revenue

FROM Job j
INNER JOIN Job_Operation jo ON j.Job = jo.Job
WHERE j.Status = 'Active'
GROUP BY j.Job, j.Customer, j.Part_Number, j.Description,
         j.Order_Quantity, j.Status, j.Order_Date, j.Ship_Date, j.Price
ORDER BY j.Ship_Date ASC;
```

### Query 2: Job Detail — Operations with Estimated vs Actual

```sql
SELECT
    jo.Job,
    jo.Sequence AS Op_Number,
    jo.Work_Center,
    jo.Operation_Service,
    jo.Status AS Op_Status,

    -- Setup hours
    jo.Est_Setup_Hrs,
    jo.Act_Setup_Hrs,
    jo.Est_Setup_Hrs - jo.Act_Setup_Hrs AS Setup_Variance,

    -- Run hours
    jo.Est_Run_Hrs,
    jo.Act_Run_Hrs,
    jo.Est_Run_Hrs - jo.Act_Run_Hrs AS Run_Variance,

    -- Quantities
    jo.Est_Run_Qty,
    jo.Act_Run_Qty,

    -- Schedule
    jo.Sched_Start,
    jo.Sched_End,
    jo.Act_Start,
    jo.Act_End,

    -- Operation status indicator
    CASE
        WHEN jo.Status = 'Complete' THEN 'DONE'
        WHEN jo.Act_Run_Hrs > 0 THEN 'IN PROGRESS'
        ELSE 'NOT STARTED'
    END AS Progress_Status,

    -- Notes
    jo.Note_Text

FROM Job_Operation jo
WHERE jo.Job = '26-0147'
ORDER BY jo.Sequence;
```

### Query 3: Material Status per Job — What's Ordered, What's Received

```sql
SELECT
    mr.Job,
    mr.Sequence AS For_Operation,
    mr.Material,
    mr.Description,
    mr.Est_Qty,
    mr.Est_Unit_Cost,
    mr.Est_Qty * mr.Est_Unit_Cost AS Est_Total_Cost,
    mr.Act_Qty,
    mr.Act_Unit_Cost,
    mr.Pick_Buy_Indicator,
    mr.Status AS Material_Status,
    mr.Vendor,

    -- PO information (if linked)
    pd.PO_Number,
    pd.Line AS PO_Line,
    pd.Order_Qty AS PO_Order_Qty,
    pd.Recv_Qty AS PO_Recv_Qty,
    pd.Promised_Date AS PO_Promised_Date,
    pd.Status AS PO_Line_Status,

    -- Material receipt status
    CASE
        WHEN mr.Pick_Buy_Indicator = 'P' THEN 'PICK FROM STOCK'
        WHEN pd.PO_Number IS NULL THEN 'NEEDS PO'
        WHEN pd.Recv_Qty >= pd.Order_Qty THEN 'RECEIVED'
        WHEN pd.Recv_Qty > 0 THEN 'PARTIAL (' + CAST(pd.Recv_Qty AS VARCHAR) + '/' + CAST(pd.Order_Qty AS VARCHAR) + ')'
        ELSE 'ON ORDER - DUE ' + CONVERT(VARCHAR(10), pd.Promised_Date, 101)
    END AS Receipt_Status

FROM Material_Req mr
LEFT JOIN PO_Detail pd ON mr.PO_Detail = pd.PO_Detail
WHERE mr.Job = '26-0147'
ORDER BY mr.Sequence, mr.Material;
```

### Query 4: Next Operation per Job (What's the Bottleneck?)

```sql
SELECT
    j.Job,
    j.Customer,
    j.Part_Number,
    j.Description,
    j.Ship_Date,
    DATEDIFF(day, GETDATE(), j.Ship_Date) AS Days_Until_Ship,

    -- Next incomplete operation
    next_op.Sequence AS Next_Op_Number,
    next_op.Work_Center AS Next_Work_Center,
    next_op.Operation_Service AS Next_Operation,
    next_op.Est_Setup_Hrs + next_op.Est_Run_Hrs AS Next_Op_Est_Hours,
    next_op.Sched_Start AS Next_Op_Sched_Start,
    next_op.Note_Text AS Next_Op_Notes

FROM Job j
CROSS APPLY (
    SELECT TOP 1
        jo.Sequence, jo.Work_Center, jo.Operation_Service,
        jo.Est_Setup_Hrs, jo.Est_Run_Hrs, jo.Sched_Start, jo.Note_Text
    FROM Job_Operation jo
    WHERE jo.Job = j.Job
      AND jo.Status <> 'Complete'
    ORDER BY jo.Sequence
) next_op
WHERE j.Status = 'Active'
ORDER BY j.Ship_Date ASC;
```

### Query 5: Work Center Load — Hours Remaining by Department

```sql
SELECT
    jo.Work_Center,
    COUNT(DISTINCT jo.Job) AS Active_Jobs,

    -- Total remaining hours in queue
    SUM(
        CASE WHEN jo.Status <> 'Complete'
        THEN (jo.Est_Setup_Hrs + jo.Est_Run_Hrs) - (jo.Act_Setup_Hrs + jo.Act_Run_Hrs)
        ELSE 0 END
    ) AS Remaining_Hours,

    -- Jobs waiting (not started yet)
    SUM(CASE WHEN jo.Act_Run_Hrs = 0 AND jo.Act_Setup_Hrs = 0 AND jo.Status <> 'Complete' THEN 1 ELSE 0 END) AS Waiting_Jobs,

    -- Jobs in progress
    SUM(CASE WHEN (jo.Act_Run_Hrs > 0 OR jo.Act_Setup_Hrs > 0) AND jo.Status <> 'Complete' THEN 1 ELSE 0 END) AS InProgress_Jobs,

    -- Earliest ship date in queue (most urgent)
    MIN(j.Ship_Date) AS Earliest_Ship_Date

FROM Job_Operation jo
INNER JOIN Job j ON jo.Job = j.Job
WHERE j.Status = 'Active'
GROUP BY jo.Work_Center
ORDER BY Remaining_Hours DESC;
```

### Query 6: Estimated vs Actual Cost Summary per Job

```sql
SELECT
    j.Job,
    j.Customer,
    j.Part_Number,
    j.Description,
    j.Price * j.Order_Quantity AS Total_Revenue,

    -- Labor cost (estimated)
    SUM(jo.Est_Setup_Hrs * jo.Setup_Labor_Rate + jo.Est_Run_Hrs * jo.Run_Labor_Rate) AS Est_Labor_Cost,

    -- Labor cost (actual)
    SUM(jo.Act_Setup_Hrs * jo.Setup_Labor_Rate + jo.Act_Run_Hrs * jo.Run_Labor_Rate) AS Act_Labor_Cost,

    -- Material cost (estimated)
    mat.Est_Material_Cost,

    -- Material cost (actual)
    mat.Act_Material_Cost,

    -- Additional charges (estimated)
    ac.Est_Charges,

    -- Margin calculation
    j.Price * j.Order_Quantity
        - SUM(jo.Act_Setup_Hrs * jo.Setup_Labor_Rate + jo.Act_Run_Hrs * jo.Run_Labor_Rate)
        - ISNULL(mat.Act_Material_Cost, 0)
        - ISNULL(ac.Act_Charges, 0) AS Current_Margin

FROM Job j
INNER JOIN Job_Operation jo ON j.Job = jo.Job
LEFT JOIN (
    SELECT Job,
           SUM(Est_Qty * Est_Unit_Cost) AS Est_Material_Cost,
           SUM(Act_Qty * Act_Unit_Cost) AS Act_Material_Cost
    FROM Material_Req
    GROUP BY Job
) mat ON j.Job = mat.Job
LEFT JOIN (
    SELECT Job,
           SUM(Est_Charge_Amt) AS Est_Charges,
           SUM(Act_Charge_Amt) AS Act_Charges
    FROM Additional_Charge
    GROUP BY Job
) ac ON j.Job = ac.Job
WHERE j.Job = '26-0147'
GROUP BY j.Job, j.Customer, j.Part_Number, j.Description, j.Price, j.Order_Quantity,
         mat.Est_Material_Cost, mat.Act_Material_Cost, ac.Est_Charges, ac.Act_Charges;
```

### Query 7: Delivery Schedule

```sql
SELECT
    d.Job,
    j.Customer,
    j.Part_Number,
    j.Description,
    d.Delivery_Date,
    d.Promised_Quantity,
    d.Shipped_Quantity,
    d.Remaining_Quantity,
    d.Status AS Delivery_Status,
    DATEDIFF(day, GETDATE(), d.Delivery_Date) AS Days_Until_Due,
    CASE
        WHEN d.Shipped_Quantity >= d.Promised_Quantity THEN 'SHIPPED'
        WHEN GETDATE() > d.Delivery_Date THEN 'OVERDUE'
        WHEN DATEDIFF(day, GETDATE(), d.Delivery_Date) <= 7 THEN 'DUE THIS WEEK'
        WHEN DATEDIFF(day, GETDATE(), d.Delivery_Date) <= 14 THEN 'DUE IN 2 WEEKS'
        ELSE 'ON SCHEDULE'
    END AS Urgency

FROM Delivery d
INNER JOIN Job j ON d.Job = j.Job
WHERE j.Status = 'Active'
ORDER BY d.Delivery_Date ASC;
```

---

## 6. Full SDK Write Capability Audit

### What the SDK CAN Write (Complete List)

| Request Type | Purpose | Nested Elements |
|---|---|---|
| **JobAddRq** | Create jobs with full routing + BOM | `OperationAdd`, `MaterialRequirementAdd`, `MiscMaterialRequirementAdd`, `AdditionalChargeAdd` |
| **JobModRq** | Modify existing job fields | Can update Status, Ship_Date, Priority, Note_Text, Description, and other job header fields |
| **TimeEntryAddRq** | Log shop floor labor | Auto-updates Job_Operation actuals |
| **SalesOrderAddRq** | Create sales orders | `OrderLineAdd` (with line items linking to jobs) |
| **QuoteAddRq** | Create quotes/estimates | `QuoteOperationAdd`, `QuoteMaterialAdd` |
| **CustomerAddRq** | Create customer records | — |
| **CustomerModRq** | Modify customer records | — |
| **VendorAddRq** | Create vendor records | — |
| **MaterialAddRq** | Create material master records | — |
| **StockItemAddRq** | Create stock/inventory items | — |
| **WorkCenterAddRq** | Create work centers | — |
| **ServiceOperationAddRq** | Create operation service definitions | — |

### What the SDK CAN Query

| Request Type | Purpose |
|---|---|
| **CustomerQueryRq** | Look up customer records |
| **VendorQueryRq** | Look up vendor records |
| **MaterialQueryRq** | Look up material master records |
| **JobQueryRq** | Look up job records |

### What the SDK CANNOT Do (Confirmed Gaps)

| Need | SDK Support | Workaround |
|---|---|---|
| **Create Purchase Orders** | NO `PurchaseOrderAddRq` | Direct SQL INSERT into `PO_Header` + `PO_Detail` (see Section 3) |
| **Receive against POs** | NO | Direct SQL UPDATE on `PO_Detail.Recv_Qty` |
| **Create/modify invoices** | NO | Direct SQL or handle in JobBOSS UI |
| **Modify time entries** | NO `TimeEntryModRq` | Direct SQL UPDATE/DELETE on `Job_Operation_Time` |
| **Delete jobs** | NO `JobDelRq` | Use `JobModRq` to set Status = 'Cancelled' |
| **Create employees** | NO `EmployeeAddRq` | Direct SQL INSERT into `Employee` table or JobBOSS UI |
| **Modify operations on existing jobs** | NO `OperationModRq` | Direct SQL UPDATE on `Job_Operation` |
| **Attachments/documents** | NO | File system or direct SQL (Attachment table if exists) |
| **Scheduling** | NO | JobBOSS has its own scheduler; can read `Sched_Start`/`Sched_End` via SQL |
| **Overtime hours** | NOT in TimeEntryAddRq | Direct SQL INSERT/UPDATE on `Job_Operation_Time.Overtime_Hrs` |

### SalesOrderAddRq — Complete XML Example

For creating a sales order from an OTTO estimate that was approved by the customer:

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-SO-20260317-001</TransactionId>
    <RequestType>SalesOrderAddRq</RequestType>
    <RequestData>
      <SalesOrderAddRq>
        <Sales_Order>SO-26-0147</Sales_Order>     <!-- varchar(10) PK -->
        <Customer>DATACOOL</Customer>              <!-- varchar(10) FK -->
        <Order_Date>2026-03-17</Order_Date>        <!-- datetime -->
        <Ship_Date>2026-06-15</Ship_Date>          <!-- datetime -->
        <Ship_Via>COMMON CARRIER</Ship_Via>        <!-- varchar(20) -->
        <Note_Text>Customer PO: DC-2026-0892. ASME Section VIII Div 1 pressure vessels for data center cooling. Net 30 terms.</Note_Text>

        <!-- Line item linking to job -->
        <OrderLineAdd>
          <Part_Number>PV-DC-4896-150</Part_Number>  <!-- varchar(30) -->
          <Description>48x96 150# COOLING VESSEL</Description> <!-- varchar(30) -->
          <Order_Qty>3</Order_Qty>                    <!-- decimal -->
          <Unit_Price>47500.00</Unit_Price>            <!-- money -->
          <Job>26-0147</Job>                          <!-- varchar(10) FK — links SO line to job -->
        </OrderLineAdd>
      </SalesOrderAddRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

### JobModRq — Update Job Status/Fields

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-JOBMOD-001</TransactionId>
    <RequestType>JobModRq</RequestType>
    <RequestData>
      <JobModRq>
        <Job>26-0147</Job>                        <!-- Required — identifies which job to modify -->
        <Status>Complete</Status>                  <!-- Change status -->
        <Ship_Date>2026-06-20</Ship_Date>         <!-- Update ship date if delayed -->
        <Note_Text>Completed 6/18. All NDE acceptable. Hydro passed. AI signed off. NB stamped. Data book shipped with vessels.</Note_Text>
      </JobModRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

### QuoteAddRq — Create Quote from OTTO Estimate

```xml
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>OTTO-QUOTE-001</TransactionId>
    <RequestType>QuoteAddRq</RequestType>
    <RequestData>
      <QuoteAddRq>
        <Quote>Q-26-0203</Quote>                  <!-- varchar(10) PK -->
        <Customer>DATACOOL</Customer>              <!-- varchar(10) FK -->
        <Description>48x96 150# COOLING VESSELS</Description>  <!-- varchar(30) -->

        <!-- Quote routing -->
        <QuoteOperationAdd>
          <Work_Center>CUT</Work_Center>
          <Operation_Service>LAYOUT-CUT</Operation_Service>
          <Sequence>10</Sequence>
          <Est_Setup_Hrs>2.0</Est_Setup_Hrs>
          <Est_Run_Hrs>8.0</Est_Run_Hrs>
        </QuoteOperationAdd>

        <QuoteOperationAdd>
          <Work_Center>ROLL</Work_Center>
          <Operation_Service>ROLL-SHELL</Operation_Service>
          <Sequence>20</Sequence>
          <Est_Setup_Hrs>1.5</Est_Setup_Hrs>
          <Est_Run_Hrs>12.0</Est_Run_Hrs>
        </QuoteOperationAdd>

        <!-- ... additional operations ... -->

        <!-- Quote materials -->
        <QuoteMaterialAdd>
          <Material>SA516-70-0.75</Material>
          <Description>SA-516-70 3/4" PLATE</Description>
          <Est_Qty>1800.00</Est_Qty>
          <Est_Unit_Cost>1.85</Est_Unit_Cost>
        </QuoteMaterialAdd>

        <QuoteMaterialAdd>
          <Material>HEAD-48-SE-075</Material>
          <Description>48"ID 2:1 SE HEAD 3/4"</Description>
          <Est_Qty>6.00</Est_Qty>
          <Est_Unit_Cost>2850.00</Est_Unit_Cost>
        </QuoteMaterialAdd>

        <!-- ... additional materials ... -->

      </QuoteAddRq>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

---

## SDK Session Management

Every SDK interaction requires a session. Sessions consume a JobBOSS license seat.

### CreateSession / CloseSession

```xml
<!-- Open session -->
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>SESSION-001</TransactionId>
    <RequestType>CreateSession</RequestType>
    <RequestData>
      <CreateSession>
        <UserName>OTTO_INTEGRATION</UserName>
        <Password>********</Password>
        <Company>SAVANNAH_TANK</Company>
      </CreateSession>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>

<!-- Response contains SessionId to use in subsequent requests -->

<!-- Close session when done — ALWAYS close to release the license seat -->
<?xml version="1.0" encoding="utf-8"?>
<JBXMLRequest>
  <RequestEnvelope>
    <TransactionId>SESSION-END</TransactionId>
    <RequestType>CloseSession</RequestType>
    <RequestData>
      <CloseSession>
        <SessionId>{session-id-from-create}</SessionId>
      </CloseSession>
    </RequestData>
  </RequestEnvelope>
</JBXMLRequest>
```

### COM Object Usage (C# / VB.NET)

```csharp
// The SDK works through a COM object provided by Jbinterface.exe
// Must be registered and running on the machine

Type jbType = Type.GetTypeFromProgID("JBInterface.JBRequestProcessor");
dynamic processor = Activator.CreateInstance(jbType);

// Submit XML and get response
string response = processor.ProcessRequest(xmlRequestString);

// Parse response XML for success/failure
// Response contains <ResponseCode> and <ResponseMessage>
```

### Session Best Practices

1. **Open session → do all work → close session** in a single logical operation
2. **Don't hold sessions open** for extended periods — they consume license seats
3. **Always close sessions in a finally block** to prevent license seat leaks
4. **One session per integration run** — batch your operations within a single session
5. **Batch rollback**: If you submit multiple requests in one batch and ANY fails, ALL roll back

---

## End-to-End Automation Sequence: OTTO → JobBOSS

```
OTTO Estimate Complete
        │
        ▼
┌─────────────────────────────────┐
│  1. CreateSession               │  SDK
│     Open COM connection         │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  2. Check/Create Master Data    │  SDK
│     - CustomerAddRq (if new)    │
│     - VendorAddRq (if new)      │
│     - MaterialAddRq (if new)    │
│     - WorkCenterAddRq (if new)  │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  3. QuoteAddRq (optional)       │  SDK
│     Create formal quote with    │
│     routing + materials from    │
│     OTTO estimate               │
└─────────┬───────────────────────┘
          │
          ▼  (Customer approves quote)
          │
┌─────────────────────────────────┐
│  4. SalesOrderAddRq             │  SDK
│     Create SO linked to job     │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  5. JobAddRq                    │  SDK
│     Create job with:            │
│     - All OperationAdd          │
│     - All MaterialRequirementAdd│
│     - All MiscMaterialReqAdd    │
│     - All AdditionalChargeAdd   │
│     (Single atomic transaction) │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  6. CloseSession                │  SDK
│     Release license seat        │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  7. Create Purchase Orders      │  DIRECT SQL
│     INSERT PO_Header            │
│     INSERT PO_Detail            │
│     UPDATE Material_Req links   │
│     (For all Buy items)         │
└─────────┬───────────────────────┘
          │
          ▼  (Production begins)
          │
┌─────────────────────────────────┐
│  8. TimeEntryAddRq              │  SDK (ongoing)
│     Shop floor tablet labor     │
│     logging against jobs/ops    │
└─────────┬───────────────────────┘
          │
          ▼  (Throughout production)
          │
┌─────────────────────────────────┐
│  9. Dashboard Queries           │  DIRECT SQL (read-only)
│     Active jobs, % complete,    │
│     est vs actual, materials,   │
│     work center load            │
└─────────┬───────────────────────┘
          │
          ▼  (Job complete)
          │
┌─────────────────────────────────┐
│  10. JobModRq                   │  SDK
│      Set Status = 'Complete'    │
└─────────────────────────────────┘
```

---

## Quick Reference: Connection Details

| Item | Value |
|------|-------|
| COM ProgID | `JBInterface.JBRequestProcessor` |
| Executable | `Jbinterface.exe` (must be running) |
| Database | SQL Server (direct connection for queries + PO writes) |
| License | Each `CreateSession` consumes one seat |
| Machine | DESKTOP-L114GHS (per installation email 3/16/2026) |
