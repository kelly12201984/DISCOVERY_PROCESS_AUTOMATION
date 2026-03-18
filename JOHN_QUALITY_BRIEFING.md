# John Corwin — Quality Briefing (Pre-Discovery)
**Role:** Quality Manager, Savannah Tank & Equipment
**Date:** March 18, 2026 | **Source:** Discovery documents from `JOHN/`, cross-references from Strategy Deployment & other stakeholder docs
**Note:** Pre-discovery — documents only, no interview yet.

---

## What John Owns

| Document | What It Is | Format | Scope |
|----------|-----------|--------|-------|
| **QC Requirements Tracker 3-12-26.xlsx** | Master QC status for all active jobs | Excel | 40 jobs, 7 quality gates each |
| **Released Jobs QC Requirements Tracker.xlsx** | Detailed QC tracking for released jobs (subcontractor info, dates) | Excel | 37 released jobs |
| **2026 RT Pass - Failure Rate Sheet.xlsx** | Individual RT shot results with welder/joint/defect detail | Excel | 46 RT shots in 2026 |
| **2025 Defect % Tracker.xlsx** | Monthly weld defect rates by joint type and welder | Excel | Full 2025, 4,250 joints |
| **NATIONAL BOILER LOG.xlsx** | National Board registration tracking for ASME vessels | Excel | 67 jobs, 38 registered / 29 pending |
| **Missing POs For Certified Jobs List.xlsx** | Certified jobs missing QC-related purchase orders | Excel | 10 jobs with missing NDE/PWHT POs |
| **ITP-098-25 Rev. 2.xlsx / .pdf** | Sample Inspection & Test Plan (Coastal Tech) | Excel + PDF | 13-step ITP template |
| **26-3-6 Cal Log.docx** | Calibration log for all measuring/test equipment | Word | 17 instruments, all current |
| **NCR 003-26.pdf** | Sample Non-Conformance Report (3rd of 2026) | PDF | Formal NCR process |
| **2025 Quality Improvement Action Plan.rtf** | Quality improvement plan (could not extract) | RTF | ~16KB file |
| **Welding Inspector Job Description Rev.3.docx** | Job description for unfilled QC Inspector role | Word | AWS CWI required |
| **WELD PROCEDURE LOG.mdb** | Weld procedure specifications & qualifications | Access DB | 1.2MB (not extractable) |
| **PT Info/ (7 files)** | PT procedures, personnel qualifications, test forms, equipment certs | Various | Complete PT program documentation |

---

## QC Requirements Tracker — The Big Picture (as of 3/12/2026)

John tracks 7 quality gates per job across ~40 active jobs:

### Completion Status by Gate

| Quality Gate | Required | Complete | In Progress | Not Started | % Done |
|-------------|----------|----------|-------------|-------------|--------|
| **ITP Created** | 39 | **39** | 0 | 0 | **100%** |
| **RT (Radiographic Testing)** | 39 | ~15 | 2 | ~22 | **38%** |
| **MT/PT (Magnetic/Penetrant)** | 39 | ~12 | 0 | ~27 | **31%** |
| **PWHT (Post-Weld Heat Treat)** | 14 | ~3 | 0 | ~11 | **21%** |
| **Hydro Test** | 39 | **~6** | 0 | ~33 | **15%** |
| **NB Registration** | 39 | ~20 | 0 | ~19 | **51%** |
| **Documentation** | 39 | ~5 | ~3 | ~31 | **13%** |

**Key takeaway:** Only 6 of 39 required hydro tests are complete. The entire Epic (14 vessels), SNF (8 vessels), and most late-stage pipeline jobs haven't started QC work yet. Massive backlog ahead.

### Jobs Fully Through QC (All Gates Complete)

| Job # | Customer | Description |
|-------|----------|-------------|
| 010-25 | KC | Claflin Chest |
| 011-25 | KC | Claflin Chest |
| 013-25 | KC | Claflin Chest |
| 017-25 | KC | Dilution Chest |
| 040-25 | Nak Kiln | Rotary Kiln |
| 046-24 | Symrise | Blending Tank |

Only **6 jobs are fully through QC** out of 40 tracked.

---

## RT (Radiographic Testing) — 2026 Results

### Overall Pass/Fail Rates

| Metric | Value |
|--------|-------|
| Total RT shots (2026) | 46 |
| First-pass pass rate | **82.6%** (38 of 46) |
| First-pass fail rate | **17.4%** (8 of 46) |
| Repaired & passed on re-RT | **100%** (all 8 failures) |

### Failure by Joint Type — Nozzles Are the Problem

| Joint Type | Shots | Failures | Fail Rate |
|-----------|-------|----------|-----------|
| **Nozzle** | 18 | **7** | **38.9%** |
| Circumferential seam | 20 | 1 | 5.0% |
| Long seam | 8 | 0 | 0% |

**Nearly 4 in 10 nozzle welds fail RT on the first shot.**

### Failure by Defect Type

| Defect | Count | % of Failures |
|--------|-------|---------------|
| Porosity | 4 | 50% |
| Slag inclusion | 2 | 25% |
| Incomplete fusion | 1 | 12.5% |
| Crack | 1 | 12.5% |

### Problem Welders

| Welder | Failures | Total Shots | Fail Rate | Notes |
|--------|----------|------------|-----------|-------|
| **W-05** | 3 | 5 | **60%** | All nozzle welds — worst performer |
| **W-09** | 2 | 2 | **100%** | Every shot failed (small sample) |
| W-03 | 1 | 3 | 33% | Nozzle porosity |
| W-06 | 1 | 6 | 17% | Crack — root cause: preheat issue |

---

## 2025 Defect Tracking — Full Year

| Metric | Value |
|--------|-------|
| Shop-wide YTD defect rate | **2.1%** |
| Total joints inspected | 4,250 |
| Total defects | 89 |
| Best month | May (1.5%) |
| Worst month | February (3.1%) |
| Trend | Generally improving through the year |

### By Joint Type (2025)

| Joint Type | Total Joints | Defect Rate |
|-----------|-------------|-------------|
| Long seam | 850 | **0%** |
| Patch | 500 | **0%** |
| Circumferential seam | 1,700 | 2.8% |
| Nozzle | 1,200 | **3.5%** (worst) |

**Consistent with 2026 data: nozzle welds are the persistent quality problem.**

---

## Missing POs — 10 Jobs Blocked

| Job # | Customer | Missing PO Items |
|-------|----------|-----------------|
| 010-25 | KC | NDE subcontractor PO |
| 011-25 | KC | NDE subcontractor PO |
| 013-25 | KC | NDE subcontractor PO, PWHT PO |
| 016-25 | KC | NDE subcontractor PO |
| 040-25 | Nak Kiln | Third-party inspection PO |
| 062-25 | Reco | NDE subcontractor PO |
| 083-25 | Synthomer | RT film/processing PO |
| 089-25 | Valmet | NDE subcontractor PO, third-party inspection PO |
| 098-25 | Coastal Tech | NDE subcontractor PO |
| 101-25 | Harper Love | PWHT PO |

These jobs are certified and released but **cannot proceed past inspection hold points** until POs are placed with subcontractors.

---

## National Board Registration Log

| Status | Count |
|--------|-------|
| Registered | ~38 |
| Pending | ~29 |
| **Total** | **~67** |

- All vessels are ASME Section VIII, Div. 1
- Authorized Inspector: **Hartford Steam Boiler (HSB)** for all jobs
- Jurisdictions: GA (most), SC (KC jobs), PA (Valmet), TX (Atlas)
- Every ASME-stamped vessel must be registered before the stamp can be applied

---

## QC Subcontractors

| Service | Subcontractor | Notes |
|---------|--------------|-------|
| RT / NDE | **Acuren** | All NDE work outsourced |
| PWHT | **Team Industrial Services** | All PWHT outsourced |
| AI (Authorized Inspector) | **Hartford Steam Boiler** | Required for ASME stamp |

John must coordinate scheduling with all three external companies — each is a potential delay point.

---

## Inspection & Test Plan (ITP) — Template

John's ITP for Job 098-25 shows a 13-step inspection framework:

| Step | Activity | QC Role | Hold Point? |
|------|----------|---------|-------------|
| 1 | Material Verification (MTRs) | Review/Witness | No |
| 2 | Dimensional Check — Heads | Review/Witness | No |
| 3 | Dimensional Check — Shell | Review/Witness | No |
| 4 | Fit-Up Inspection | Review/**Hold** | **Yes** |
| 5 | In-Process Weld Visual | Review/Witness | No |
| 6 | NDE — RT | Review/**Hold** | **Yes** (customer witness) |
| 7 | NDE — MT/PT | Review/**Hold** | **Yes** |
| 8 | PWHT (if required) | Review/Witness | No |
| 9 | Hydrostatic Test | Review/**Hold** | **Yes** (customer witness) |
| 10 | Final Dimensional | Review/Witness | No |
| 11 | Nameplate/Stamping | Review/**Hold** | **Yes** |
| 12 | Final Visual/Cleaning | Review/Witness | No |
| 13 | Documentation Package (MDR) | Review/**Hold** | **Yes** |

**6 hold points** per vessel means 6 times production stops and waits for John's sign-off. With 39 active ASME jobs, that's ~234 hold point inspections.

---

## Calibration Status (as of 3/6/2026)

| Equipment | Count | Status |
|-----------|-------|--------|
| Tape measures | 3 | Current |
| Scales/levels | 2 | Current |
| UT thickness gauges | 2 | Current (external lab) |
| Pressure gauges (0-300, 0-600, 0-1000 PSI) | 3 | Current (external lab) |
| Thermometer/pyrometer | 1 | Current (external lab) |
| Weld gauge sets | 2 | Current |
| Calipers (6" and 12") | 2 | Current (external lab) |
| Micrometer (0-1") | 1 | Current (external lab) |
| Square (24") | 1 | Current |
| **Total** | **17** | **All current — ASME audit-ready** |

---

## Qualified Inspection Personnel — Critical Bottleneck

| Person | VT Level | PT Level | Can Work Independently? |
|--------|----------|----------|------------------------|
| **John Corwin** | **Level II** | **Level II** | **Yes** — only independent inspector |
| Julian Adkins | Level I | Level I | **No** — requires Level II oversight |

**John is the only person who can independently perform and sign off on VT and PT inspections.** If John is unavailable (sick, vacation, pulled into meetings), inspections stop. Julian can assist but cannot sign off.

The **Welding Inspector Job Description Rev. 3** (dated Jan 2026) describes the unfilled position that would fix this:
- AWS CWI (Certified Welding Inspector) required
- ASME Section V/VIII/IX knowledge
- 5+ years welding inspection experience
- PT Level II certification
- This hire would create a second independent inspector

---

## NCR Process

NCR 003-26 (the third NCR of 2026, ~mid-March) confirms John has a formal Non-Conformance Report process with:
- Root cause analysis
- Corrective action documentation
- Disposition (accept/repair/reject)
- Verification of corrective action
- Close-out sign-off

**Rate:** ~3 NCRs in ~2.5 months = roughly **1–1.5 NCRs per month** in 2026.

---

## 2026 Quality Targets (from Strategy Deployment)

| Metric | Target | Current Status |
|--------|--------|---------------|
| Customer quality escapes (U.S.) | **Zero** | No escapes documented (on target) |
| ASME Section VIII Div. 1 certification | **Retain** | Joint Review **May 2026** — ~6 weeks away |
| Visual Quality Standards Guide | Complete by 12/31/2026 | Unknown |
| India fabrication review process | Established by 4/1/2026 | **~2 weeks away** — status unknown |
| U.S. Rework hours | <1.25% of direct labor | John tracks; Dustin reports |
| U.S. Cost of Quality | <$1.75 per direct labor hr | Unknown |

---

## ASME Joint Review Readiness (May 2026)

Items the ASME auditor will check, and John's status:

| Audit Item | Status | Evidence |
|-----------|--------|---------|
| Calibration records | **Ready** | Cal log current, 17 instruments |
| Written procedures (PT, etc.) | **Ready** | PT-100 procedure documented, updated |
| Personnel qualifications | **Ready** | VT/PT qualification records, vision exams on file |
| NCR process | **Ready** | Formal NCR system active (NCR 003-26) |
| National Board registrations | **Partial** | 38 registered, 29 pending |
| Weld procedures (WPS/PQR) | **Unknown** | In Access DB — not extractable |
| Quality manual/QMS | **Unknown** | Strategy deployment says "implement QMS across all locations" |
| Job documentation (ITPs, MDRs) | **Partial** | ITPs created for all jobs; MDRs in progress |

---

## Coordination Points

| Who | What John Shares | Direction |
|-----|-----------------|-----------|
| **Dustin Bolgrihn** | Rework data, QC hold/release decisions, inspection scheduling | John -> Dustin |
| **April Lewis** | Inspection status at hold points, documentation packages, ship readiness | John -> April |
| **Nick Patel** | India quality standards, fabrication inspection criteria | Bi-directional |
| **Acuren** (NDE sub) | RT/NDE scheduling, results, reports | Bi-directional |
| **Team Industrial** (PWHT sub) | PWHT scheduling, charts, records | Bi-directional |
| **Hartford Steam Boiler** (AI) | ASME inspections, stamp authorization, NB registration | External -> John |

---

## Key Risk Flags

| Risk | Detail |
|------|--------|
| **John is the only independent inspector** | Level II VT/PT — if he's unavailable, inspections stop |
| **QC Inspector position unfilled** | Job description written (Jan 2026) but hire not made |
| **Massive QC backlog** | Only 6 of 39 hydro tests complete; entire Epic/SNF pipeline untouched |
| **~234 hold point inspections ahead** | 39 ASME jobs x 6 hold points each |
| **10 jobs missing QC subcontractor POs** | Can't pass hold points until NDE/PWHT POs are placed |
| **Nozzle weld failure rate at 39%** | Nearly 4 in 10 nozzle RT shots fail — rework driver |
| **W-05 at 60% failure rate, W-09 at 100%** | Individual welder quality issues |
| **ASME Joint Review in ~6 weeks** | May 2026 — calibration/procedures ready, but NB registrations and QMS gaps |
| **India inspection process due 4/1/2026** | ~2 weeks — status unknown |
| **NDE/PWHT fully outsourced** | Scheduling dependency on Acuren and Team Industrial |

---

## What We Don't Know Yet (Discovery Interview Questions)

### Workload & Capacity
- What does John's typical day look like?
- How many inspections per day/week is John currently performing?
- Is John the bottleneck in production flow? How often does production wait for him?
- What's the status of the QC Inspector hire?

### ASME Audit
- How confident is John about the May 2026 Joint Review?
- What's in the Weld Procedure Log (Access DB) — how many WPS/PQRs?
- What gaps remain in ASME documentation?
- Is the quality manual/QMS documented?

### Nozzle Weld Problem
- Is the 39% nozzle failure rate being addressed? How?
- Has W-05 been retrained or reassigned? W-09?
- Are nozzle weld procedures adequate, or is this a procedure/process issue?

### India Quality
- What's the status of the India fabrication review process (due 4/1/2026)?
- How will India inspections work logistically?

### Process & Tools
- What's in the Quality Improvement Action Plan RTF?
- How does John create/manage ITPs — one per job or templated?
- Are NCRs tracked over time — is there a log beyond individual reports?
- How does John communicate hold point status to Dustin/April?
- What role does JobBOSS play in John's workflow?

### Cost of Quality
- How is CoQ calculated? What's included?
- Is the $1.75/direct labor hour target realistic?
- What's the current CoQ?
