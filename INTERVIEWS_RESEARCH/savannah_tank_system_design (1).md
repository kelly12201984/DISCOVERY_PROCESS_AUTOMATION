# Savannah Tank & Equipment — System & Data Design
## Source of Truth for Automation and Data Engineering

**Prepared by:** Kelly Fletcher, Savannah Intelligence Systems LLC
**Date:** March 24, 2026
**Status:** Discovery Draft — Week 2 of 3

---

## 1. High-Level Domain Model / ERD

### Core Entities and Relationships

```
                         ┌──────────────┐
                         │   CUSTOMER   │
                         │──────────────│
                         │ customer_id  │
                         │ name         │
                         │ contacts[]   │
                         └──────┬───────┘
                                │ 1:many
                    ┌───────────┴───────────┐
                    │                       │
              ┌─────▼──────┐         ┌──────▼───────┐
              │   QUOTE    │         │   DOCUMENT   │
              │────────────│         │──────────────│
              │ quote_id   │         │ doc_id       │
              │ tank_specs │         │ type (dwg,   │
              │ est_hours  │         │  cert, BOM,  │
              │ est_matl$  │         │  UDR1, etc.) │
              │ price      │         │ version      │
              │ status     │         │ job_id (FK)  │
              │ xml_file   │         │ file_path    │
              └─────┬──────┘         └──────────────┘
                    │ WON (1:many tanks per quote)
              ┌─────▼──────┐
              │    TANK    │
              │────────────│
              │ tank_id    │
              │ quote_id   │
              │ job_id     │
              │ type       │
              │ diameter   │
              │ height     │
              │ material   │
              │ orientation│
              │ code (ASME/│
              │  API 650)  │
              └─────┬──────┘
                    │ 1:1
              ┌─────▼──────┐
              │    JOB     │◄──────────────────────────────┐
              │────────────│                               │
              │ job_id     │                               │
              │ job_number │   ┌────────────┐              │
              │ tank_id    │   │  EMPLOYEE  │              │
              │ customer_id│   │────────────│              │
              │ status     │   │ emp_id     │              │
              │ order_date │   │ emp_number │              │
              │ sched_end  │   │ name       │              │
              │ price      │   │ department │              │
              └──┬──┬──┬───┘   │ hire_date  │              │
                 │  │  │       │ status     │              │
     ┌───────────┘  │  └────┐  │ pay_rate   │              │
     │              │       │  └─────┬──────┘              │
     ▼              ▼       ▼        │                     │
┌─────────┐  ┌──────────┐  ┌────────▼───────┐   ┌────────┴────────┐
│  BUILD  │  │ MATERIAL │  │  TIME_ENTRY    │   │ PURCHASE_ORDER  │
│  PLAN   │  │   _REQ   │  │────────────────│   │─────────────────│
│─────────│  │──────────│  │ time_id        │   │ po_id           │
│ plan_id │  │ req_id   │  │ employee_id    │   │ job_id          │
│ job_id  │  │ job_id   │  │ job_id         │   │ vendor_id       │
│ ops[]   │  │ material │  │ operation_id   │   │ status          │
│         │  │ quantity  │  │ work_center_id │   │ order_date      │
│         │  │ vendor_id │  │ setup_hrs      │   │ due_date        │
│         │  │ po_id     │  │ run_hrs        │   │ ship_method     │
│         │  │ status    │  │ ot_hrs         │   │ fob_terms       │
└────┬────┘  └──────────┘  │ date           │   └────────┬────────┘
     │                     └────────────────┘            │
     │ 1:many                                            │ 1:many
┌────▼──────────┐    ┌──────────────┐          ┌────────▼────────┐
│ JOB_OPERATION │    │ WORK_CENTER  │          │   PO_DETAIL     │
│───────────────│    │──────────────│          │─────────────────│
│ job_op_id     │    │ wc_id        │          │ line_id         │
│ job_id        │    │ name         │          │ po_id           │
│ operation_id  │    │ type (direct/│          │ material_id     │
│ work_center_id│◄───│  indirect)   │          │ job_id          │
│ sequence      │    │ department   │          │ qty_ordered     │
│ est_hours     │    │ setup_rate   │          │ qty_received    │
│ actual_hours  │    │ run_rate     │          │ unit_cost       │
│ pct_complete  │    └──────────────┘          │ status          │
│ status        │                              └─────────────────┘
└───────────────┘
                         ┌──────────────┐
                         │   VENDOR     │
              ┌──────────│──────────────│
              │          │ vendor_id    │
              │          │ name         │
              │          │ contacts[]   │
              │          │ materials[]  │
              │          │ lead_times   │
              │          └──────────────┘
              │
     ┌────────▼─────────┐    ┌──────────────────┐
     │    INVOICE       │    │   INSPECTION     │
     │──────────────────│    │──────────────────│
     │ invoice_id       │    │ insp_id          │
     │ vendor_id        │    │ job_id           │
     │ po_id            │    │ type (QC, ASME,  │
     │ amount           │    │  customer, NDE)  │
     │ status           │    │ operation_id     │
     │ received_date    │    │ result           │
     │ payment_status   │    │ inspector        │
     └──────────────────┘    │ date             │
                             └──────────────────┘

     ┌──────────────────┐
     │  WELD_PROCEDURE  │
     │──────────────────│
     │ wps_id           │
     │ process          │
     │ base_metals      │
     │ thickness_range  │
     │ pqr_ref          │
     └────────┬─────────┘
              │ assigned to
     ┌────────▼─────────┐
     │  WELD_RECORD     │
     │──────────────────│
     │ weld_id          │
     │ job_id           │
     │ wps_id           │
     │ welder_id (FK)   │
     │ joint_location   │
     │ nde_result       │
     │ status           │
     └──────────────────┘
```

### Key Relationships Summary

- **Customer** → many Quotes → many Tanks → 1:1 Job each
- **Job** → many Job_Operations (the build plan / routing)
- **Job** → many Time_Entries (actual labor logged per operation)
- **Job** → many Material_Reqs → linked to PO_Details
- **Job** → many Purchase_Orders (per vendor, can span multiple jobs)
- **Job** → many Inspections (QC hold points throughout fabrication)
- **Job** → many Documents (drawings, BOMs, certs, UDR-1, etc.)
- **Job** → many Weld_Records → linked to Weld_Procedures and Employees
- **Employee** → many Time_Entries (daily, per operation per job)
- **Work_Center** → many Job_Operations (PRE FAB, FIT, FINISHING, etc.)
- **Vendor** → many POs → many PO_Details → many Invoices

### Entity Notes

- **TANK** is a concept OTTO owns that JobBOSS doesn't have — JobBOSS sees Jobs, not Tanks. The Tank entity carries the engineering specs (from XML), the Job carries the production/financial data.
- **BUILD_PLAN** bridges the estimate world and the production world. Currently an Excel template; target state is auto-generated from tank specs + historical actuals.
- **WELD_PROCEDURE / WELD_RECORD** may already live in Codeware ShopFloor — discovery needed with John to confirm. If so, these entities exist but in a separate system.
- **DOCUMENT** is intentionally broad — drawings, BOMs, certified drawings, UDR-1 forms, customer certs, QC packages all live here with a type discriminator.

---

## 2. Current-State vs. Target-State Process Maps

### 2A. Sales / Estimating

**Current State:**
1. Customer sends RFQ via email → Chris receives
2. Chris runs COMPRESS calc → exports XML
3. Chris opens OTTO → uploads XML → OTTO extracts specs and generates estimate
4. Chris reviews estimate, adjusts pricing → generates proposal PDF
5. Chris sends proposal to customer
6. If won → Chris creates job in JobBOSS manually, creates job folder on P drive manually
7. Sherri sets up job in JobBOSS for financial tracking (before Nick can purchase)

**Pain Points:** Job creation in JobBOSS is manual. Job folder creation is manual. No automatic handoff from OTTO quote to JobBOSS job. Estimate doesn't get updated post-PO.

**Target State:**
1. RFQ email → OTTO auto-classifies and extracts (already built for Chris)
2. OTTO parses XML → generates estimate with ML-calibrated hours (trained on 149K historical time entries, not padded sales hours)
3. Chris reviews and sends proposal
4. If won → OTTO auto-creates job in JobBOSS via SQL, auto-creates P drive folder structure, auto-generates U-DR-1 from XML data, triggers engineering and procurement workflows
5. Estimate-to-actual feedback loop runs continuously, improving predictions

---

### 2B. Engineering

**Current State:**
1. India team receives job assignment (email/Splashtop)
2. Engineer opens COMPRESS → runs/updates calculations → exports XML3D
3. Engineer manually creates Inventor model from scratch (3 days per drawing)
4. Engineer manually creates 2D AutoCAD drawings from Inventor model
5. Nick/Rutang review drawings against calcs — check nozzle schedules, dimensions, specs by reading XML and drawing side by side
6. Drawings sent to customer for certification (email, manual tracking)
7. Customer returns certified (or "approved as noted") → April tracks as checkbox
8. Nick manually builds BOM in Excel from certified drawings — calculates pipe lengths, plate sizes
9. Nick manually creates preliminary BOM (stock check by walking to shop), then final BOM with PO numbers

**Pain Points:** 3-day manual drawing process. No automated verification of drawings against calcs. BOM built manually from drawings with hand calculations. Drawing certification tracked as binary checkbox. COMPRESS can't model internals. India engineer already trying to automate XML→Inventor but stuck on Python bugs. David purchased Inventor add-on that's unused. CWI evaluated and doesn't meet needs.

**Target State:**
1. OTTO XML3D parser extracts all structured parameters from COMPRESS
2. Parameters feed Inventor iLogic → auto-generates 3D model + 2D drawings (1 day instead of 3 — 67% reduction, exceeds David's 30% target)
3. Engineers add internals (baffles, coils) via iLogic with a few clicks (specs from customer datasheet)
4. OTTO drawing verification: compares all drawing table data against XML for pressure boundary components, against datasheet for internals — shows matches (green) and mismatches (red)
5. Engineer reviews verification report, accepts → OTTO sends to customer for certification
6. Customer certification tracked with full lifecycle (draft → sent → returned → certified/approved as noted)
7. Smart BOM auto-generated from drawing + XML + datasheet, presented for engineer review (human-in-the-loop)
8. Accepted BOM → auto-generates vendor RFQs grouped by material type, routed to preferred vendors from vendor list

---

### 2C. Procurement

**Current State:**
1. Nick builds BOM in Excel from certified drawings
2. Groups materials by type → copy/paste into emails → sends RFQs to 2-3 vendors
3. Vendor quotes return via email (all different formats)
4. Nick compares quotes manually (price, lead time) — vendor preference knowledge in his head
5. Nick creates PO in JobBOSS line-by-line (class → filter → scroll → select material → enter length/qty → assign job number → enter unit cost from vendor quote)
6. Nick exports PO as PDF → saves to job folder → replies to vendor email with PO attached
7. Vendor sends acknowledgement → Nick updates BOM with PO number and delivery date
8. Cross-job consolidation (buying for 3+ jobs on one PO to save shipping) — entirely in Nick's head
9. PO follow-up every ~15 days via JobBOSS open requirements report → manual email/call to vendors
10. Receiving closes line items in JobBOSS when materials arrive (partial shipments common)

**Pain Points:** BOM data entered twice (Excel then JobBOSS). PO entry is tedious click-by-click. Cross-job optimization is tribal knowledge. Vendor comparison is manual. Follow-up is ad hoc. JobBOSS has RFQ module but Nick doesn't use it (too many clicks). Wrong vendor or missing GL codes on POs cause downstream errors for Sherri.

**Target State:**
1. Smart BOM from engineering feeds procurement directly
2. OTTO auto-generates RFQs from BOM, grouped by material type, sent to preferred vendors
3. Vendor quotes parsed by OTTO (AI extraction from email attachments — same pattern as RFQ intake)
4. OTTO presents comparison matrix: vendor × line item × price × lead time
5. Nick selects winning vendor per line item → OTTO auto-generates PO in JobBOSS via SQL
6. OTTO surfaces cross-job consolidation opportunities ("3 other active jobs need 8" Sch 40 pipe — combine?")
7. Auto follow-up: POs past expected delivery date trigger reminder emails
8. Open PO dashboard visible to Nick, Sherri, and receiving

---

### 2D. Production

**Current State:**
1. Dustin receives job info verbally at kick-off + from his own tracking
2. Sherri manually enters build plan (30-40 operations) into JobBOSS from Excel template
3. Dustin schedules jobs using Excel (not JobBOSS scheduling module)
4. Workers fill out handwritten paper timesheets daily
5. Scott manually enters timesheets into JobBOSS (~2 hrs/day)
6. Dustin prints 3 JobBOSS reports every Monday (16+ pages), manually calculates totals
7. Dustin prepares Priority List in Excel — 20 active jobs with status narrative
8. Dustin presents at PM meeting from printed reports + Priority List
9. No real-time job status visibility — April walks the floor, Dustin checks manually

**Pain Points:** Build plan manual entry. Handwritten timesheets → manual data entry. Monday prep is hours of printing/calculating. Multiple overlapping trackers. No scheduling in JobBOSS. 5x volume growth broke all manual processes. Scott's data entry is the #1 bottleneck at scale.

**Target State:**
1. Build plan auto-generated from ML model (tank specs → predicted hours per operation) or from estimate → human review → push to JobBOSS routing
2. Traveler scanning (JobBOSS Data Collection module — already licensed) replaces handwritten timesheets — scan operation barcode, enter hours, done
3. Real-time job status visible to everyone (operation progress, hours consumed vs. estimated)
4. Monday reports auto-compile from JobBOSS SQL — efficiency, time audit, job status delivered as dashboard or auto-emailed PDF
5. Dustin's Priority List auto-populated from job data + schedule
6. PM meeting becomes 15-minute decision session instead of 60-minute data review

---

### 2E. Quality Control

**Current State:** (Partially known — John interview 3/25-26)
1. John tracks QC inspections, MTRs, test reports in spreadsheets
2. ASME hold points exist as operations in JobBOSS routing but status tracking is manual
3. Drawing certification tracked by April as checkbox
4. Customer inspection scheduling is manual
5. Post-shipment QC package assembled manually
6. Codeware ShopFloor exists — usage status unknown
7. John not present at kick-off meetings — finds out about new jobs unclear how

**Pain Points:** Unknown depth until interview. Suspected: welder qualification tracking manual, NDE scheduling manual, QC documentation assembly manual, no integration between ShopFloor and JobBOSS.

**Target State:**
1. If ShopFloor is functional → activate/expand its use (weld procedure management, welder tracking, QC dashboard, U-Form generation, shop traveler with weld assignments)
2. If ShopFloor is not functional → evaluate whether OTTO QC module or ShopFloor activation is the better path
3. Inspection hold points in JobBOSS routing trigger notifications to John when a job reaches that operation
4. QC package auto-assembled from documents attached to job (MTRs, test reports, inspection reports, as-built drawings)
5. Welder qualification tracking with proactive alerts for expiring certifications

---

### 2F. Office / HR / AP (Sherri)

**Current State:**
1. **Indeed recruiting:** Per-candidate: open Indeed → read resume → download → save PDF to P drive → type name in spreadsheet → print → hand to hiring manager. $75/day/posting. No screening questions on postings.
2. **AP invoices:** Email to apinvoice@ → print attachment → file in Outlook vendor folder → match to receiving paperwork (physical stack) → match to PO in JobBOSS → enter invoice in JobBOSS AP → print check → David signs → stuff/stamp/mail
3. **New hire onboarding:** Same data entered in Access DB (employee number) + JobBOSS (timesheet) + Paychecks Flex (payroll). Plus badge assignment, E-Verify (3-day deadline), Georgia New Hires.
4. **Build plan entry:** 208-row Excel template → manually enter 30-40 active operations per job into JobBOSS routing
5. **Payroll:** Working well — badge clock-in → Paychecks Flex auto-calculates. Pain is everything around payroll, not payroll itself.
6. **Time clock:** 3 employees clock in early, Sherri manually adjusts punches. Paychecks Flex rule limitation.

**Pain Points:** Indeed is #1 pain — drowning in unqualified applicants. Triple data entry for onboarding. AP is all paper-based matching. Build plan entry is significant recurring data entry. Sherri is a single point of failure for too many processes.

**Target State:**
1. **Indeed:** Multiple user logins (hiring managers review own candidates). OTTO job posting optimizer (paste JD → screening questions + qualifications + title). AI resume screener per department (generalize existing Dustin app). Bulk resume download + auto-file.
2. **AP:** Power Automate auto-files invoice email attachments to vendor folders + auto-prints. OTTO extracts invoice data and auto-matches to JobBOSS PO. Flags partial receipts and missing receiving.
3. **Onboarding:** Single-entry form → writes to JobBOSS + Access (or eliminate Access). Digital checklist with E-Verify deadline tracking.
4. **Build plan:** Auto-generated (see Production section). Sherri never enters routing manually.
5. **Receiving:** Open PO dashboard from JobBOSS data (same report Nick runs manually every 15 days).

---

## 3. Starter Dimensional Model / Analytics Backbone

### Bus Matrix

| Business Process | Customer | Tank | Job | Employee | Work Center | Time (Date) | Material | Vendor | Operation | Department |
|---|---|---|---|---|---|---|---|---|---|---|
| **Quotes** | ✓ | ✓ | | | | ✓ | ✓ | | | |
| **Jobs** | ✓ | ✓ | ✓ | | | ✓ | | | | |
| **Production Ops** | | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ | ✓ |
| **Time Tracking** | | | ✓ | ✓ | ✓ | ✓ | | | ✓ | |
| **QC / NDE** | ✓ | ✓ | ✓ | ✓ | | ✓ | | | ✓ | |
| **Purchasing** | | | ✓ | | | ✓ | ✓ | ✓ | | |
| **AP / Invoicing** | | | ✓ | | | ✓ | | ✓ | | |

### Priority Fact Tables (Phase 1)

#### FactTimeEntry (implement first — most data, most impact)

- **Grain:** One row per employee per operation per job per day
- **Source:** JobBOSS `Job_Operation_Time` table (149,507 existing rows)
- **Dimension FKs:** employee_id, job_id, operation_id, work_center_id, date_id
- **Measures:** setup_hours, run_hours, overtime_hours, total_hours
- **Derived:** actual_vs_estimated_pct (joined to Job_Operation.est_hours)
- **Why first:** Enables Dustin's Monday reports to auto-generate, validates 85% factor, feeds ML model for build plan prediction, surfaces work center efficiency trends

#### FactJobOperation (implement second — the build plan backbone)

- **Grain:** One row per operation per job
- **Source:** JobBOSS `Job_Operation` table (64,559 existing rows)
- **Dimension FKs:** job_id, operation_id, work_center_id, date_id (start/end)
- **Measures:** estimated_hours, actual_hours (aggregated from FactTimeEntry), pct_complete, status
- **Derived:** efficiency_pct (actual/estimated), hours_remaining
- **Why second:** Powers real-time job status dashboard (RAG status for PM meeting), build plan accuracy analysis, scheduling

#### FactPurchaseOrder (implement third — connects procurement to finance)

- **Grain:** One row per PO line item
- **Source:** JobBOSS `PO_Detail` table (46,496 existing rows)
- **Dimension FKs:** po_id, job_id, vendor_id, material_id, date_id (order, due, received)
- **Measures:** qty_ordered, qty_received, unit_cost, total_cost, days_to_receive
- **Derived:** receipt_status (full/partial/pending), on_time_flag, cost_vs_estimate
- **Why third:** Powers open PO dashboard for receiving, vendor performance scoring, material cost trending, AP invoice matching

### Shared Dimensions

- **DimDate** — standard date dimension (day, week, month, quarter, year, fiscal period)
- **DimEmployee** — emp_id, name, department, hire_date, status, employee_number
- **DimJob** — job_id, job_number, customer, tank_type, material, diameter, status, order_date
- **DimWorkCenter** — wc_id, name, type (direct/indirect), department
- **DimOperation** — op_id, code, description, work_center, numbering_system (old/new)
- **DimMaterial** — material_id, description, class, specification, unit_of_measure
- **DimVendor** — vendor_id, name, location, preferred_materials, payment_terms
- **DimCustomer** — customer_id, name, contacts, job_count, revenue_total

---

## 4. Implementation-Oriented Roadmap

### Phase 1: Foundation (Weeks 1-8) — "Turn on what you already own"

**1A. Traveler Scanning Activation**
- Problem: Scott enters handwritten timesheets 2 hrs/day. Error-prone, doesn't scale.
- Data: JobBOSS Data Collection module (licensed, not configured)
- Entities: Time_Entry, Job_Operation, Employee, Work_Center
- Benefits: Scott (500 hrs/yr saved), Dustin (real-time data), April (job status visibility)
- Effort: 3-4 weeks (hardware procurement + JobBOSS configuration + training)

**1B. Monday Report Automation**
- Problem: Dustin prints 16 pages, manually calculates totals every Monday
- Data: FactTimeEntry + FactJobOperation (SQL queries against JobBOSS)
- Entities: Job, Job_Operation, Time_Entry, Work_Center, Employee
- Benefits: Dustin (hours saved weekly), PM meeting prep eliminated
- Effort: 2-3 weeks (SQL queries + report template + scheduling)

**1C. AP Invoice Auto-File**
- Problem: Sherri manually prints/files every invoice email attachment
- Data: Power Automate connected to apinvoice@savannahtank.com + P drive
- Entities: Invoice, Vendor
- Benefits: Sherri (2.5 hrs/week saved)
- Effort: 1-2 weeks (Power Automate flow configuration)

### Phase 2: Quick Wins (Weeks 4-16) — "Eliminate obvious re-entry"

**2A. Build Plan → JobBOSS Routing Automation**
- Problem: Sherri manually enters 30-40 operations per job from Excel template
- Data: Build plan Excel → JobBOSS Job_Operation table via SQL
- Entities: Job, Job_Operation, Work_Center, Operation
- Benefits: Sherri (significant time per job), data quality improvement
- Effort: 3-4 weeks

**2B. Job Creation Pipeline (OTTO → JobBOSS)**
- Problem: Quote won → manual job creation in JobBOSS, manual folder creation on P drive
- Data: OTTO quote data → JobBOSS Job table + P drive folder structure
- Entities: Quote, Tank, Job, Customer
- Benefits: Chris (time saved), Sherri (no longer gates Nick's purchasing), error reduction
- Effort: 2-3 weeks

**2C. U-DR-1 Auto-Fill**
- Problem: ASME form manually filled for every job
- Data: OTTO Raw Data extraction (85% coverage) + customer/PO info
- Entities: Tank, Job, Customer, Document
- Benefits: Chris/Rutang (time saved per job), error reduction on compliance form
- Effort: 2 weeks

**2D. Indeed Job Posting Optimizer**
- Problem: Unqualified applicants flooding Indeed at $75/day/posting. No screening questions.
- Data: Job description text → Claude API → structured posting with screening questions, qualifications, title
- Entities: (HR domain, not in core ERD)
- Benefits: Sherri, all hiring managers. Reduce Indeed cost, reduce resume review time.
- Effort: 2-3 weeks

### Phase 3: Engineering Automation (Weeks 8-24) — "The 67% drawing reduction"

**3A. XML3D Parser for Inventor iLogic**
- Problem: Engineers manually draw tanks from scratch (3 days each). India engineer's Python parser has bugs.
- Data: COMPRESS XML3D → structured parameter Excel → Inventor iLogic
- Entities: Tank (specs), Document (drawings)
- Benefits: India engineering team (3 days → 1 day per drawing, 67% reduction)
- Effort: 4-6 weeks (extends OTTO's existing XML parser)

**3B. Drawing Verification**
- Problem: Nick/Rutang manually compare drawing tables against XML calcs
- Data: Drawing table data (extracted) + XML specs + customer datasheet
- Entities: Tank, Document, Inspection (verification as QA step)
- Benefits: Nick/Rutang (catch errors before customer, faster review cycles)
- Effort: 4-6 weeks

**3C. Smart BOM Generation**
- Problem: Nick manually builds BOM from drawings with hand calculations
- Data: Drawing + XML + datasheet + estimate (reference) → draft BOM
- Entities: Material_Req, Tank, Job, Material
- Benefits: Nick (significant time per job), feeds auto-RFQ downstream
- Effort: 4-6 weeks

### Phase 4: Procurement & Analytics (Weeks 16-36) — "Close the loops"

**4A. Auto-RFQ from BOM + Vendor Quote Comparison**
- Problem: Nick copy/pastes BOM to email for vendor RFQs, manually compares different-format quotes
- Data: Accepted BOM → vendor list → email RFQs; vendor responses parsed by AI
- Entities: Material_Req, Vendor, Purchase_Order
- Benefits: Nick (time saved), cross-job consolidation surfaced automatically
- Effort: 6-8 weeks

**4B. Predictive Build Plan Hours (ML Model)**
- Problem: Build plan hours based on padded sales estimates, not actual production data
- Data: 149K historical time entries + tank specs (type, diameter, material, options)
- Entities: FactTimeEntry, FactJobOperation, Tank
- Benefits: More accurate scheduling (Dustin), better quoting calibration (Chris), capacity planning (David)
- Effort: 4-6 weeks (EDA + model training + integration into build plan flow)

**4C. Job Costing Dashboard**
- Problem: Nobody sees estimated vs. actual cost per job in real time
- Data: FactTimeEntry (labor$) + FactPurchaseOrder (material$) + Quote (estimated$)
- Entities: Job, FactTimeEntry, FactPurchaseOrder, Quote
- Benefits: David (margin visibility), Chris (estimating accuracy feedback)
- Effort: 3-4 weeks

---

## 5. Questions and Assumptions

### Assumptions Made

1. **JobBOSS SQL is directly writable** — we can INSERT/UPDATE JobBOSS tables via pyodbc. Assumed based on the COM SDK and direct SQL access confirmed during DB audit. Need to verify write permissions and any trigger/constraint implications.

2. **JobBOSS Data Collection module is activatable without ECI involvement** — assumed it's licensed and just needs configuration. May require ECI support call for initial setup.

3. **ShopFloor integration with COMPRESS is functional** — assumed ST has an active ShopFloor subscription. Usage status completely unknown. This could change the QC roadmap significantly.

4. **Power Automate is available** — ST has M365. Assumed Power Automate is included in their license tier. Need to verify.

5. **The India team's Inventor version supports iLogic** — assumed based on Aalhad's email and existing use of iLogic rules. Need to confirm Inventor version/edition.

6. **Build plan Excel template is standardized** — assumed from the 208-row template examined (Job 004-25). Need to confirm all jobs use this same template vs. variations.

7. **Vendor shortlist on P drive is current and structured** — Nick said it exists and he updates it. Haven't examined it yet.

8. **Paychecks Flex has no API** — assumed from the fact that Sherri enters data manually. May have an API or import capability that could eliminate one of the three onboarding entries.

9. **The INDIA database on DC2 is a separate operational instance** — not a replica or archive. Assumed from DB audit finding of 146 tables with same schema.

10. **Calcs get updated post-PO** — Nick confirmed this in the procurement interview. The XML reflects the final engineering design, not just the initial estimate. This makes XML more authoritative for BOM/verification than originally assumed.

### Clarifying Questions for Stakeholders

1. **John:** Is Codeware ShopFloor actively in use? What parts? Who uses it? Is it connected to your COMPRESS instance?

2. **John:** How do you currently track welder qualifications and continuity? Spreadsheet, ShopFloor, or memory?

3. **John:** What does your QC package look like when you ship a vessel? How long does it take to assemble? How many of those documents could be auto-generated?

4. **Dustin:** What make/model are the robotic welders? How are they programmed (teach pendant vs. offline from CAD)? What's their utilization rate?

5. **Dustin:** Would you trust a system-generated build plan with predicted hours, or would you always want to manually review/adjust? (Adoption question for the ML model.)

6. **David:** What is the Inventor add-on you purchased? What did you expect it to do? Why isn't it being used?

7. **David:** What's the budget envelope for automation tooling (hardware for scanning, software licenses, development)? Is this CapEx or OpEx?

8. **Nick:** What does the iLogic input file format need to look like? Can Aalhad provide a template of what Inventor expects?

9. **Nick:** How many POs per month, roughly? And how many of those are split across multiple jobs? (Quantifies cross-job consolidation opportunity.)

10. **April:** If you had real-time job status from traveler scanning, what would change about how you run the PM meeting? Would you still need the same prep?

11. **Sherri:** How long does build plan entry take per job? (Need the number for ROI calculation.)

12. **Sherri:** Is there a reason the Access employee database can't be retired if employee numbers were managed in JobBOSS or Paychecks Flex?

13. **Roy (IT):** What are the write permissions on the JobBOSS SQL Server? Any restrictions on direct table writes vs. stored procedures?

14. **Roy (IT):** What M365 license tier does ST have? Is Power Automate Premium included, or just the base connector set?

15. **General:** Are there any compliance or regulatory constraints on automating ASME documentation (U-Forms, QC packages, weld records)? Does the Authorized Inspector need to approve any changes to how these are generated?
