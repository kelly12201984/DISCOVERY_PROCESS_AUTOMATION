# Savannah Tank — Spreadsheet & Manual Log Inventory
## Mapping Manual Artifacts to the Domain Model

**Companion to:** Savannah Tank System Design (domain model, process maps, dimensional model)
**Date:** March 24, 2026
**Status:** Discovery Draft — populated from Week 1-2 interviews; gaps noted for Week 3

---

## 1. Catalog Schema

Every spreadsheet, paper form, or manual log discovered at Savannah Tank gets cataloged with these fields:

| Field | Description |
|---|---|
| **ID** | Catalog reference (SS-001, PF-001, etc.) |
| **Name** | What users call it |
| **Owner** | Primary person who maintains it |
| **Department** | Sales, PM, Engineering, Procurement, Production, QC, Office/HR/AP |
| **Purpose** | What business question it answers or decision it supports |
| **Core Entities** | Which domain model entities it touches (Job, Tank, Employee, Operation, Material, Vendor, etc.) |
| **Source Systems** | Where the data originates (JobBOSS, COMPRESS, OTTO, Paychecks Flex, email, verbal, etc.) |
| **Capture Method** | How data gets in (fully manual, copy-paste, exported report, verbal-then-typed, etc.) |
| **Update Frequency** | Real-time, daily, weekly, per-job, ad-hoc |
| **Consumers** | Who reads/uses this besides the owner |
| **Pain Points** | What's broken, slow, duplicated, or error-prone |
| **Target Solution** | What should replace or feed this (OTTO module, JobBOSS config, ShopFloor, Power Automate, dashboard, elimination) |
| **Roadmap Phase** | Which phase/deliverable from the implementation roadmap |
| **Priority** | High / Medium / Low (based on impact × frequency × pain) |

---

## 2. Interview Script for Spreadsheet Discovery

Use these questions with each stakeholder. Adapt language to the person — Dustin talks differently than Sherri.

### Opening (use with everyone)

- "Walk me through a typical Monday morning. What do you open first on your computer?"
- "What spreadsheets or lists do you keep outside of JobBOSS to track your work?"
- "If your computer died right now, what files would you panic about losing?"
- "Is there anything you track on paper that eventually gets typed into a system?"

### Mapping to entities and processes

- "For each spreadsheet you showed me: where does the data come from? Do you type it from scratch, copy it from another system, or does someone give it to you?"
- "How often do you update it — every day, once a week, or whenever something changes?"
- "Who else looks at this? Does anyone else edit it?"
- "If this spreadsheet disappeared tomorrow, what decision could you no longer make?"
- "Is there anything in here that you also have to enter somewhere else — like JobBOSS, or another tracker?"

### Uncovering hidden artifacts

- "Do you ever print something from JobBOSS or email and then write on it by hand?"
- "Are there any sticky notes, whiteboards, or notebooks you use to track things that should probably be in a system?"
- "When you go to the PM meeting, what do you bring with you? Paper? Laptop? Both?"
- "Does anyone send you a spreadsheet that you have to combine with your own data?"

### Connecting to the dimensional model

- "If I wanted to answer 'how many hours did Job X actually take versus what we estimated,' where would I find that?"
- "If I wanted to know 'which vendor delivered late most often this year,' could you tell me? Where would you look?"
- "If David asked 'what's our gross margin on the last 20 jobs,' who would pull that together and from what?"

---

## 3. Catalog — Known Artifacts

### SS-001: PM Tracker

| Field | Value |
|---|---|
| **Name** | PM Tracker (PM_Tracker_-_Working.xlsx) |
| **Owner** | April |
| **Department** | Project Management |
| **Purpose** | Master project lifecycle tracking: drawing submittals, customer returns, RTR checklist, actual dates, ship dates, shipment checklists, change orders. Answers: "Where is every active job in its lifecycle?" |
| **Core Entities** | Job, Customer, Document (drawings, certs), Tank |
| **Source Systems** | Verbal (kick-off meetings), JobBOSS (job numbers), email (customer responses), physical observation (April walks the floor) |
| **Capture Method** | Fully manual — April types everything, cross-references job folders and JobBOSS |
| **Update Frequency** | Daily (attempts), but depends on other people updating April or April checking herself |
| **Consumers** | April (primary), Chris, David, Dustin (indirectly at PM meeting) |
| **Pain Points** | 11 tabs, maintained since 2019, depends on everyone else providing updates (they don't). Drawing certification is a checkbox with no lifecycle. Dual numbering (ST job # vs. customer tank #) mentally mapped. Hours/week of data entry. |
| **Target Solution** | OTTO Jobs Module — single source of truth replacing this tracker. Real-time status from traveler scanning feeds job progress automatically. Drawing certification becomes a tracked lifecycle. |
| **Roadmap Phase** | Phase 2B (Job Creation Pipeline) + Phase 1A (Traveler Scanning for real-time status) |
| **Priority** | **High** |

---

### SS-002: Master Schedule

| Field | Value |
|---|---|
| **Name** | Master Schedule (MASTER_SCHEDULE.xlsx) |
| **Owner** | April |
| **Department** | Project Management |
| **Purpose** | Gantt-style production schedule showing ~60 active jobs across weekly columns. Answers: "What's the overall shop load and timeline?" |
| **Core Entities** | Job, Customer, Work_Center (implicitly) |
| **Source Systems** | PM Tracker (April's own data), verbal from Dustin, JobBOSS (job dates) |
| **Capture Method** | Manual — April builds and updates from her own PM Tracker and verbal input |
| **Update Frequency** | Weekly (before PM meeting) |
| **Consumers** | April, Dustin, David, Chris |
| **Pain Points** | Overlaps with Dustin's Priority List and Released Jobs tracker. No connection to actual shop floor progress. Schedule dates are aspirational, not data-driven. |
| **Target Solution** | Dashboard powered by FactJobOperation — auto-generated Gantt from JobBOSS job dates + real-time operation progress from traveler scanning |
| **Roadmap Phase** | Phase 1A (Traveler Scanning) + Phase 2B (Job Creation Pipeline) |
| **Priority** | **Medium** |

---

### SS-003: Released Jobs Tracker

| Field | Value |
|---|---|
| **Name** | Released Jobs Tracker |
| **Owner** | April (possibly shared with Dustin) |
| **Department** | Project Management / Production |
| **Purpose** | Tracks ~25 discrete fabrication tasks per job with color-coded status. Answers: "For each released job, what operations are done and what's remaining?" |
| **Core Entities** | Job, Job_Operation, Work_Center |
| **Source Systems** | Verbal from shop floor, physical observation, Dustin's input |
| **Capture Method** | Manual — color-coded status updated by April based on floor checks |
| **Update Frequency** | Daily to weekly |
| **Consumers** | April, Dustin |
| **Pain Points** | Duplicates information that should come from JobBOSS time entries. Manual color-coding instead of data-driven status. |
| **Target Solution** | Eliminated — traveler scanning provides real-time operation status per job. FactJobOperation dashboard replaces this entirely. |
| **Roadmap Phase** | Phase 1A (Traveler Scanning) |
| **Priority** | **High** (elimination candidate) |

---

### SS-004: Dustin's Priority List

| Field | Value |
|---|---|
| **Name** | Priority List |
| **Owner** | Dustin |
| **Department** | Production |
| **Purpose** | Top 20 active jobs ranked by priority with MOC, fab/test date, ship date, detailed shop status narrative, galvanizing/paint specs. Answers: "What should the shop be working on and in what order?" |
| **Core Entities** | Job, Customer, Tank (MOC), Job_Operation |
| **Source Systems** | JobBOSS (job data), Dustin's head (priority ranking, status narrative), April's schedule (ship dates) |
| **Capture Method** | Manual — Dustin builds/updates weekly from a combination of printed JobBOSS reports and floor knowledge |
| **Update Frequency** | Weekly (Monday, before PM meeting) |
| **Consumers** | Dustin, shop leads (Sammy, Scott), April (at PM meeting) |
| **Pain Points** | Priority ranking is tribal knowledge. Status narratives are manually written. Overlaps with April's PM Tracker and Released Jobs. Hours of Monday prep to compile. |
| **Target Solution** | Auto-populated from FactJobOperation + FactTimeEntry — job status from traveler scanning, priority ranking surfaced as a configurable dashboard. Dustin reviews/adjusts rather than builds from scratch. |
| **Roadmap Phase** | Phase 1A (Traveler Scanning) + Phase 1B (Monday Report Automation) |
| **Priority** | **High** |

---

### SS-005: Monday Meeting Reports (3 printed JobBOSS reports)

| Field | Value |
|---|---|
| **Name** | Time Audit Report, Efficiency Report, Job Report |
| **Owner** | Dustin |
| **Department** | Production |
| **Purpose** | Shows hours logged per employee per operation, efficiency percentages by work center, and job status. Answers: "How did we perform last week? Where are we inefficient?" |
| **Core Entities** | Employee, Job, Job_Operation, Time_Entry, Work_Center |
| **Source Systems** | JobBOSS Crystal Reports (3 separate reports) |
| **Capture Method** | Printed from JobBOSS, totals calculated manually (used to use calculator, now uses a helper Excel sheet) |
| **Update Frequency** | Weekly (Monday morning before PM meeting) |
| **Consumers** | Dustin, David, April, Chris (at PM meeting) |
| **Pain Points** | 16+ printed pages (was 3 before volume growth). Manual total calculations. No trend analysis. Takes significant prep time every Monday. |
| **Target Solution** | FactTimeEntry SQL queries → auto-compiled dashboard or emailed PDF. Crystal Reports scheduling as interim. Full dashboard as target. |
| **Roadmap Phase** | Phase 1B (Monday Report Automation) |
| **Priority** | **High** |

---

### SS-006: Build Plan Template

| Field | Value |
|---|---|
| **Name** | Build Plan (e.g., 004-25_Build_Plan.xlsx) |
| **Owner** | Dustin (creates), Sherri (enters into JobBOSS) |
| **Department** | Production / Office |
| **Purpose** | 208-row Excel template listing every possible fabrication operation. Green cells filled per job with estimated hours and notes. Answers: "What operations does this job need and how long should each take?" |
| **Core Entities** | Job, Job_Operation, Work_Center, Operation |
| **Source Systems** | Chris's estimate (hours), Dustin's knowledge (operation selection and notes) |
| **Capture Method** | Manual — Dustin/Chris fill in the template, Sherri re-enters 30-40 active operations into JobBOSS routing |
| **Update Frequency** | Per job (one-time creation, then entered into JobBOSS) |
| **Consumers** | Sherri (enters in JB), Dustin (schedules from it), shop leads (work from it) |
| **Pain Points** | Double data entry (Excel then JobBOSS). Hours based on padded sales estimates, not calibrated actuals. 208 rows to scan for each job. Sherri's entry is an error vector for downstream efficiency data. |
| **Target Solution** | ML-predicted hours from FactTimeEntry historical data → auto-generated build plan based on tank specs → human review → push to JobBOSS routing via SQL. Sherri never touches it. |
| **Roadmap Phase** | Phase 2A (Build Plan Automation) + Phase 4B (Predictive Build Plan ML) |
| **Priority** | **High** |

---

### SS-007: Bill of Materials (BOM)

| Field | Value |
|---|---|
| **Name** | Bill of Materials (Excel, per job — 3 stages: long lead, preliminary, final) |
| **Owner** | Nick |
| **Department** | Engineering / Procurement |
| **Purpose** | Lists all materials needed for a job with quantities, specs, vendors, PO numbers, delivery dates. Answers: "What do we need to buy, from whom, and when will it arrive?" |
| **Core Entities** | Job, Material, Material_Req, Vendor, Purchase_Order |
| **Source Systems** | Drawings (Nick calculates pipe lengths, plate sizes), COMPRESS XML (specs), vendor quotes (pricing, lead times), JobBOSS (PO numbers) |
| **Capture Method** | Manual — Nick builds from drawings with hand calculations, groups by material type, sends RFQs via copy-paste email, updates with PO numbers and dates after ordering |
| **Update Frequency** | Per job — 3 iterations (long lead → preliminary → final) |
| **Consumers** | Nick (primary), Sherri (delivery dates for receiving), Dustin (material availability for scheduling), April (delivery dates for PM Tracker) |
| **Pain Points** | Hand calculations for pipe lengths. Triple iteration. Copy-paste to email for RFQs. Manual vendor comparison. Data re-entered into JobBOSS PO system line by line. Cross-job consolidation is tribal knowledge. |
| **Target Solution** | Smart BOM auto-generated from drawing + XML + datasheet → human review → accepted BOM feeds auto-RFQ and auto-PO creation in JobBOSS |
| **Roadmap Phase** | Phase 3C (Smart BOM) + Phase 4A (Auto-RFQ) |
| **Priority** | **High** |

---

### SS-008: Vendor Shortlist

| Field | Value |
|---|---|
| **Name** | Vendor list (on P drive, Nick's folder) |
| **Owner** | Nick |
| **Department** | Procurement |
| **Purpose** | 2-3 preferred vendors per material type with contact info and sales rep details. Answers: "Who do I send this RFQ to?" |
| **Core Entities** | Vendor, Material |
| **Source Systems** | Nick's experience, periodic updates as reps change |
| **Capture Method** | Manual — Nick maintains and updates |
| **Update Frequency** | Ad-hoc (when reps change jobs, new vendors onboarded) |
| **Consumers** | Nick |
| **Pain Points** | Only Nick uses it. Pricing knowledge not captured (who's cheapest for what is in Nick's head). No performance history (on-time delivery, quality). |
| **Target Solution** | Vendor dimension in analytics model enriched with FactPurchaseOrder data — auto-calculated on-time delivery rate, average price per material class, lead time reliability. Feeds auto-RFQ routing. |
| **Roadmap Phase** | Phase 4A (Auto-RFQ + Vendor Comparison) |
| **Priority** | **Medium** |

---

### SS-009: Sherri's Payroll Prep Spreadsheet

| Field | Value |
|---|---|
| **Name** | Payroll breakdown spreadsheet (Sherri-created) |
| **Owner** | Sherri |
| **Department** | Office / HR |
| **Purpose** | Pre-calculates employee hours from daily timesheets so Monday payroll processing isn't a scramble. Answers: "What are each employee's hours this pay period before I process payroll?" |
| **Core Entities** | Employee, Time_Entry |
| **Source Systems** | Handwritten timesheets (old process), now Paychecks Flex time clock data |
| **Capture Method** | Manual — Sherri transcribed daily, now partially automated via Paychecks Flex badge data |
| **Update Frequency** | Daily (old), now being phased out as Paychecks Flex handles it |
| **Consumers** | Sherri |
| **Pain Points** | Sherri said she's "still doing it but will definitely get away from it" — legacy artifact from before badge clock-in. Redundant now that Paychecks Flex auto-populates hours. |
| **Target Solution** | Eliminate — Paychecks Flex already handles this. Confirm Sherri has stopped using it. |
| **Roadmap Phase** | N/A (self-resolving) |
| **Priority** | **Low** |

---

### SS-010: Indeed Candidate Tracking Spreadsheet

| Field | Value |
|---|---|
| **Name** | Candidate tracking spreadsheet (name unknown) |
| **Owner** | Sherri |
| **Department** | Office / HR |
| **Purpose** | Logs candidate names per open position as Sherri reviews them. Answers: "Who applied and did I review them?" |
| **Core Entities** | (HR domain — not in core ERD) |
| **Source Systems** | Indeed (manual download per candidate), Sherri's review |
| **Capture Method** | Fully manual — Sherri types each candidate name after downloading/reviewing their resume |
| **Update Frequency** | Daily when positions are active |
| **Consumers** | Sherri, hiring managers (receive printed resumes, not the spreadsheet) |
| **Pain Points** | Per-candidate workflow is 15-20 minutes. At 5 open positions with 30+ applicants/week, this is 6-8 hrs/week. No scoring, no filtering, no tracking of hiring manager decisions. |
| **Target Solution** | AI resume screener (OTTO) — bulk download + auto-score + present ranked short list. Hiring managers get Indeed logins for direct review. Spreadsheet replaced by OTTO candidate tracking. |
| **Roadmap Phase** | Phase 2D (Indeed Job Posting Optimizer) + future AI Resume Screener |
| **Priority** | **High** |

---

### SS-011: Microsoft Access Employee Database

| Field | Value |
|---|---|
| **Name** | Employee database (Access, on P drive under Safety folder) |
| **Owner** | Sherri |
| **Department** | Office / HR |
| **Purpose** | Assigns sequential employee numbers, tracks name/address/SSN/start date/status, runs "current employees" query. Answers: "What's the next employee number?" and "Who currently works here?" |
| **Core Entities** | Employee |
| **Source Systems** | Sherri's manual entry from new hire paperwork |
| **Capture Method** | Fully manual — same data also entered in JobBOSS and Paychecks Flex |
| **Update Frequency** | Per new hire |
| **Consumers** | Sherri |
| **Pain Points** | Triple data entry. Built by a former safety manager. Only real purpose is sequential employee number assignment. Legacy artifact. |
| **Target Solution** | Eliminate — assign employee numbers in JobBOSS or Paychecks Flex. Single-entry onboarding form writes to remaining systems. |
| **Roadmap Phase** | Phase 2 (Single-Entry Onboarding) |
| **Priority** | **Medium** |

---

### SS-012: Handwritten Timesheets

| Field | Value |
|---|---|
| **Name** | Paper timesheets (shop floor) |
| **Owner** | Shop employees (fill out), Scott (enters into JobBOSS) |
| **Department** | Production |
| **Purpose** | Records hours worked per employee per operation per job per day. Answers: "Who worked on what, and for how long?" |
| **Core Entities** | Employee, Job, Job_Operation, Time_Entry, Work_Center |
| **Source Systems** | Employee self-report (handwritten) |
| **Capture Method** | Fully manual — handwritten on paper, then Scott re-enters into JobBOSS (~2 hrs/day) |
| **Update Frequency** | Daily |
| **Consumers** | Scott (enters), Dustin (reports from entered data), Sherri (payroll cross-reference) |
| **Pain Points** | 2 hrs/day of Scott's time. Error-prone (handwriting, wrong job numbers, wrong operation codes). Ballooned to 2.5-3 hrs on Vertiv (50 ops/tank). Data entry lag means JobBOSS data is always a day behind. |
| **Target Solution** | Traveler scanning (JobBOSS Data Collection module) — scan operation barcode, enter hours. Eliminates paper and Scott's re-entry entirely. |
| **Roadmap Phase** | Phase 1A (Traveler Scanning) |
| **Priority** | **High** |

---

### SS-013: Dustin's Efficiency Tracker

| Field | Value |
|---|---|
| **Name** | Efficiency Tracker (Excel) |
| **Owner** | Dustin |
| **Department** | Production |
| **Purpose** | Tracks efficiency percentages by work center (target 93%). Answers: "Are we hitting our efficiency targets? Where are we falling short?" |
| **Core Entities** | Work_Center, Job_Operation, Time_Entry |
| **Source Systems** | JobBOSS reports (time audit, efficiency) |
| **Capture Method** | Dustin extracts from printed JobBOSS reports, enters into his own Excel |
| **Update Frequency** | Weekly |
| **Consumers** | Dustin, David |
| **Pain Points** | Manual extraction from printed reports. Current findings: Hydro 62%, Shipping 56% — well below 93% target. Finishing Supervisor position unfilled affects these numbers. No trend analysis over time. |
| **Target Solution** | FactTimeEntry + FactJobOperation → auto-calculated efficiency dashboard with trends by week/month/quarter. Work center efficiency becomes a live metric, not a weekly manual calculation. |
| **Roadmap Phase** | Phase 1B (Monday Report Automation) + Phase 4C (Job Costing Dashboard) |
| **Priority** | **Medium** |

---

### SS-014: Per-Project Customer Schedules

| Field | Value |
|---|---|
| **Name** | Individual project schedules (various Excel files per customer/project) |
| **Owner** | April |
| **Department** | Project Management |
| **Purpose** | Customer-specific schedule trackers for larger or multi-tank projects. Answers: "What did we commit to this customer and are we on track?" |
| **Core Entities** | Job, Customer, Document |
| **Source Systems** | Customer requirements, PM Tracker, verbal from Chris |
| **Capture Method** | Manual — April creates per project, updates from her other trackers |
| **Update Frequency** | Weekly to ad-hoc |
| **Consumers** | April, Chris (customer communication) |
| **Pain Points** | Separate from PM Tracker — April maintains both. Duplicated effort. Customer-facing dates may diverge from internal dates without anyone noticing. |
| **Target Solution** | OTTO Jobs Module customer view — auto-generated schedule from job data, filterable by customer. Customer updates auto-drafted when status changes. |
| **Roadmap Phase** | Phase 2B (Job Creation Pipeline) |
| **Priority** | **Low** |

---

### PF-001: Physical Invoice Stacks (Sherri's Desk)

| Field | Value |
|---|---|
| **Name** | Three physical paper stacks: Invoices Received / Waiting for Backup / Waiting for Invoices |
| **Owner** | Sherri |
| **Department** | Office / AP |
| **Purpose** | Three-way match: invoice ↔ PO ↔ receiving paperwork. Answers: "Can I pay this vendor?" |
| **Core Entities** | Invoice, Purchase_Order, PO_Detail, Vendor, Job |
| **Source Systems** | Email (invoices to apinvoice@), physical delivery (packing slips from shop), JobBOSS (PO data) |
| **Capture Method** | Fully manual — print email attachment, file alphabetically by vendor, match to physical receiving docs |
| **Update Frequency** | Daily |
| **Consumers** | Sherri |
| **Pain Points** | Three physical stacks. Invoice arrives but receiving paperwork missing (or vice versa). Partial shipments create multi-step matching. Upstream PO errors (wrong vendor, missing GL code) block posting. |
| **Target Solution** | Phase 1C (Power Automate auto-file) + Phase 2 (OTTO invoice extraction + auto-match to JobBOSS PO via FactPurchaseOrder). Open PO dashboard replaces "waiting for backup" stack. |
| **Roadmap Phase** | Phase 1C (AP Auto-File) + Phase 4 (Invoice Matching) |
| **Priority** | **High** |

---

### QC-001: John's QC Tracking (suspected — unconfirmed)

| Field | Value |
|---|---|
| **Name** | QC inspection tracker(s) — specifics unknown until John interview |
| **Owner** | John |
| **Department** | QC |
| **Purpose** | Suspected: tracks inspection hold points, MTR status, NDE results, customer inspection schedules, weld records. Answers: "Is this job ready for inspection? Are we compliant?" |
| **Core Entities** | Job, Inspection, Weld_Record, Weld_Procedure, Employee (welders), Document (MTRs, test reports) |
| **Source Systems** | JobBOSS (operation hold points), physical inspection, possibly ShopFloor |
| **Capture Method** | Unknown — suspected manual Excel. ShopFloor usage status unknown. |
| **Update Frequency** | Unknown |
| **Consumers** | John, April (checks MTR status for him), ASME Authorized Inspector |
| **Pain Points** | Unknown depth. April said she checks MTR status for John — suggests he may not have real-time visibility. PM meeting agenda requires QC documentation ready for customer review — how is that assembled? |
| **Target Solution** | If ShopFloor is active → expand usage. If not → evaluate ShopFloor activation vs. OTTO QC module. Inspection hold points auto-notify John when job reaches that operation (requires traveler scanning). |
| **Roadmap Phase** | Phase 1A (Traveler Scanning for notifications) + TBD based on John interview |
| **Priority** | **High** (ASME compliance implications) |

---

## 4. Link to Roadmap — Top Candidates for Early Replacement

### Top 5 Early Replacement/Automation Candidates

| Rank | Artifact | Why | Roadmap Deliverable |
|---|---|---|---|
| **1** | SS-012: Handwritten Timesheets | Highest single-person time cost (Scott 500 hrs/yr). Foundation for everything else — real-time data enables dashboards, report automation, and scheduling. Already licensed in JobBOSS. | Phase 1A: Traveler Scanning |
| **2** | SS-005: Monday Meeting Reports | Dustin spends hours every Monday printing, calculating, and preparing. Pure report automation — the data already exists in JobBOSS. SQL queries replace 16 pages of printed reports. | Phase 1B: Monday Report Automation |
| **3** | SS-006: Build Plan Template | Double data entry (Dustin fills Excel, Sherri re-types into JobBOSS). Errors in routing corrupt all downstream efficiency data. Affects every single job. | Phase 2A: Build Plan Automation |
| **4** | PF-001: Physical Invoice Stacks | Sherri's daily AP workflow is entirely paper-based matching. Power Automate is a near-zero-cost quick win for auto-filing. Bigger gains from invoice-to-PO matching come later. | Phase 1C: AP Auto-File |
| **5** | SS-010: Indeed Candidate Tracker | Sherri's self-reported #1 pain point. $75/day per posting wasted on unqualified traffic. Three department heads independently asked for resume help. Job posting optimizer is a quick build on existing OTTO patterns. | Phase 2D: Indeed Optimizer |

### Full Artifact-to-Roadmap Mapping

| Artifact ID | Artifact Name | Roadmap Phase(s) |
|---|---|---|
| SS-001 | PM Tracker | 1A, 2B |
| SS-002 | Master Schedule | 1A, 2B |
| SS-003 | Released Jobs Tracker | 1A (eliminated) |
| SS-004 | Priority List | 1A, 1B |
| SS-005 | Monday Meeting Reports | 1B |
| SS-006 | Build Plan Template | 2A, 4B |
| SS-007 | Bill of Materials | 3C, 4A |
| SS-008 | Vendor Shortlist | 4A |
| SS-009 | Payroll Prep Spreadsheet | N/A (self-resolving) |
| SS-010 | Indeed Candidate Tracker | 2D |
| SS-011 | Access Employee DB | 2 (onboarding) |
| SS-012 | Handwritten Timesheets | 1A |
| SS-013 | Efficiency Tracker | 1B, 4C |
| SS-014 | Per-Project Schedules | 2B |
| PF-001 | Physical Invoice Stacks | 1C, 4 |
| QC-001 | QC Tracking (unconfirmed) | 1A, TBD |

---

## 5. Clarifying Questions

### To confirm what we think we know

1. **April:** I've identified your PM Tracker, Master Schedule, Released Jobs tracker, and per-project schedules. Are there any other spreadsheets or trackers you maintain that I haven't seen?

2. **Dustin:** Beyond the Priority List, Efficiency Tracker, and the 3 Monday reports — do you maintain any other spreadsheets? Any scheduling tools? Anything on paper besides the timesheets?

3. **Nick:** You showed me the BOM and vendor list. Do you track vendor quote history anywhere? When you compare quotes, do you save that comparison, or is it one-time use?

4. **Sherri:** How many different spreadsheets or lists do you maintain right now? I've seen the candidate tracker, payroll prep sheet, and the Access database. Is there anything else — receiving logs, AP aging, check registers?

### To resolve unknowns

5. **John:** What does your daily tracking look like? Walk me through what you open, what you check, and what you update. (This fills QC-001 completely.)

6. **John:** Does ShopFloor generate your shop travelers, or are travelers created separately?

7. **April:** The RTR checklist in your PM Tracker — is that your only record of whether a job is ready for release, or does Dustin have his own?

8. **Dustin:** You said you schedule at 85% of quoted hours. Is that written down anywhere, or is it just what you do? Is it the same 85% for every work center?

9. **Chris:** When you create a job in JobBOSS, do you reference a checklist or template, or do you just know what to enter?

10. **Nick:** When you do the stock check for the preliminary BOM, do you record what you found in stock, or do you just adjust the BOM? Is there any inventory tracking in JobBOSS that reflects what's on the shop floor?

### To determine system ownership long-term

11. **General:** For each tracker that overlaps between departments (April's PM Tracker vs. Dustin's Priority List vs. Released Jobs), who is the authoritative source when they disagree?

12. **David:** When you want a status update on a job, who do you ask and what do you look at? (Reveals which tracker David trusts as the source of truth.)

13. **Roy (IT):** Are there any automated reports or scheduled jobs currently running against the JobBOSS database? Any Crystal Reports on a schedule? Any SQL Agent jobs?
