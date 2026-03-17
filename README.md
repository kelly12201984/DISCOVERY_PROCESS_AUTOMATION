# Savannah Tank — Operations Discovery

## What This Repo Is

This is the working repository for a **3-week operations discovery engagement** at **Savannah Tank & Equipment Corporation**, conducted by **Kelly Arseneau / Savannah Intelligence Systems LLC** (March 16 – April 3, 2026).

Everything in this repo exists to answer one question: **Where can automation eliminate manual work, reduce errors, and give people their time back?**

Any Claude Code session working in this repo should evaluate every document, dataset, and system with that lens. The goal is not documentation for documentation's sake — it's finding what to automate, what to buy off the shelf, and what to build custom.

---

## The Company

**Savannah Tank & Equipment Corporation** is a custom pressure vessel and tank manufacturer in Savannah, GA. ASME code shop. Every job is make-to-order — nothing is standard. They're growing fast and their staff has more work than they have time. The president (David Onachilla) has seen what automation did for the sales/estimation process and wants that relief extended to every department.

### How a Job Flows (Simplified)

```
Customer RFQ → Estimation/Quote (Chris, OTTO) → Customer PO → Job Created in JobBOSS
→ Engineering (Nick, Rutang + India team: calcs, drawings, BOMs)
→ Procurement (Nick: vendor RFQs, material purchasing)
→ Production Scheduling (Dustin: Excel-based schedule)
→ Shop Floor Fabrication (Sammy, Scott, Kevin + crew: cutting, rolling, welding, assembly)
→ QC Inspection (John: weld maps, hydro tests, MTRs, code compliance docs)
→ Shipping → Invoicing (Sherri)
```

Every handoff in that chain is where data gets re-entered, information gets lost, and people waste time chasing status updates.

---

## The Automation Vision

**OTTO is the brain. JobBOSS is the system of record. Staff approves — machines execute.**

Today, the same data gets typed into emails, Excel, JobBOSS, proposals, POs, and the P drive in various formats by various people. The vision is:

1. **OTTO captures and generates data** (estimates, BOMs, vendor RFQs, job specs)
2. **Humans review and approve** (Nick approves the BOM, selects the vendor, etc.)
3. **OTTO pushes to JobBOSS with one click** (job creation, BOM entry, PO generation — no re-keying)
4. **Dashboards pull from JobBOSS/OTTO** so everyone sees real-time status without asking anyone

The end state: nobody types the same information twice, nobody walks across the shop to ask "where is this job," and nobody spends hours assembling reports that should be automatic.

---

## Key People

| Person | Role | What They Do | Key Pain Points to Investigate |
|--------|------|-------------|-------------------------------|
| **David Onachilla** | President | Decision-maker. In India (soft retirement). Responds to visuals. Fixed price only — never show hourly rates. | Wants "Siri for Savannah Tank." Wants tools in staff's hands ASAP. |
| **Chris Fletcher** | Sales Manager | Primary customer contact. Runs full sales cycle. Primary OTTO user. Kelly's husband. | Wears too many hats. Bottleneck for quoting. Can't see job status without chasing people. |
| **April Lewis** | Project Manager | Tracks every job lifecycle. Runs Monday PM meetings. Manages customer communication. | Entire tracking system is a massive Excel workbook (PM_Tracker). Manually updates 30+ columns per job by asking people. |
| **Nick Patel** | Engineering / Procurement | Oversees US + India engineering team. Manages vendor RFQs and material purchasing. | Dual role is massive scope. Vendor RFQ tracking is manual (Excel/email/memory). |
| **John Corwin** | Quality Control | Inspections, compliance documentation, ASME/API code compliance. | Documentation is time-consuming. Currently doing ASME audit prep (happens once every 3 years). |
| **Sherri Jones** | Office Manager / Accounting | PO entry into JobBOSS, vendor payments, AP/AR, HR, general admin. | Manual PO entry. Portal access to ECI (JobBOSS support). Data re-entry between systems. |
| **Dustin Bolgrihn** | Production Manager | Shop floor scheduling and production management. | Excel-based schedule works but disconnected from everything else. Gets blindsided by changes. |
| **Rutang** | Lead Engineer (India) | Design calculations, drawings, engineering reviews. Remote via Splashtop. | Dependent on specs from Nick. Handoff to shop floor has version control issues. |

---

## Systems & Technology

### Current Stack

| System | What It Does | Integration Status |
|--------|-------------|-------------------|
| **JobBOSS 18.2** (Classic) | ERP — job tracking, PO entry, scheduling, inventory, labor. System of record. | **SDK available** — COM-based, XML requests, .NET wrapper. SDK Developer's Guide and Data Dictionary are in this repo. |
| **OTTO** | Custom automation platform built by Kelly. Python/FastAPI/SQLite3/HTML+JS. | Handles estimation, quotes, proposals, pricing. RFQ intake module in development. Cloud migration planned. |
| **HubSpot + ZoomInfo** | CRM / Sales prospecting | Unknown integration potential with OTTO/JobBOSS. |
| **AMETank** | API tank design software | XML export capability (has had issues with v18.11.27). |
| **COMPRESS** | ASME vessel calculations | Licensed via Sentinel LDK. |
| **AutoCAD / Inventor** | Engineering drawings | Standard CAD tools. |
| **Microsoft 365** | Available to all staff | Power Automate, SharePoint, Teams, Forms — largely unused for automation. Evaluate during discovery. |
| **Excel** | Everything else | Scheduling, PM tracking, pricing, vendor tracking. Excel is the duct tape holding the company together. |
| **P Drive** | Shared network file storage | Messy, unstructured, version control issues. Current home for all job folders and documents. |
| **Splashtop** | Remote access for India team | |

### JobBOSS SDK — Key Facts

- **Version:** JobBOSS 18.2 (Classic — NOT JobBOSS²)
- **SDK Type:** COM-based object (`JBInterface.exe`), XML request/response pattern
- **Authentication:** Requires `CreateSession()` with username/password, returns SessionID. Every query needs the SessionID embedded in XML.
- **Seat Limitation:** Each SDK session consumes a JobBOSS user seat. Cannot have parallel sessions on the same credentials without a semaphore.
- **SDK Developer's Guide and 18.2 Data Dictionary** are in this repo — READ THESE before evaluating any integration path.
- **The critical question:** What can we CREATE/WRITE via SDK (jobs, BOMs, POs, labor entries, status updates) vs. what can we only READ? This determines whether OTTO can push data to JobBOSS or only pull from it.
- **Alternative path:** Direct SQL Server database access for read-only reporting/dashboards if SDK write capabilities are limited.

---

## Discovery Engagement Details

### SOW Scope (What Kelly Is Contracted to Deliver)

1. **Department-by-department findings** — what each person does, where bottlenecks exist, where automation can help
2. **Systems and tools evaluation** — JobBOSS SDK integration options, off-the-shelf tools, M365 capabilities, build-vs-buy recommendations
3. **Prioritized automation roadmap** — recommended build order based on fastest to implement × most relief for users
4. **Executive presentation** to David and Chris summarizing findings and recommendations

### Interview Schedule

| Order | Person | Role | Status | Notes |
|-------|--------|------|--------|-------|
| 1 | Chris | Sales Manager | Informal download complete | Intelligence briefing — knows every department's pain |
| 2 | April | Project Manager | Scheduled 3/17 4pm | Full lifecycle view. Her PM_Tracker spreadsheet is the process map. |
| 3 | Nick | Engineering / Procurement | BLOCKED — surgery | Will schedule on return |
| 4 | Sherri | Office Mgmt / Accounting | Scheduled 3/18 | JobBOSS power user. Has ECI portal access. |
| 5 | Dustin | Production Manager | Pending | Shop floor. Interview last to validate what everyone else says. |
| 6 | John | Quality Control | BLOCKED — ASME audit | Schedule 3/25-26 post-audit when pain points are fresh. |

### Research Tracks (Non-Interview)

- **JobBOSS SDK evaluation** — Can we automate job creation, BOM push, PO creation, status updates, labor entry? What are the limits?
- **M365 evaluation** — Power Automate, SharePoint (replace P drive?), Teams, Forms
- **Off-the-shelf tools** — For each pain point, does a commercial solution already exist?
- **Meeting observation** — Sit in on PM meeting and/or production meetings if possible

---

## What's in This Repo

### Documents (from staff shared folders + ECI portal)

- `SDK Developer's Guide` — JobBOSS 18.2 SDK full reference
- `JobBOSS 18.2 Data Dictionary` — Every table and field in the database
- `PM_Tracker_-_Working.xlsx` — April's project tracking workbook (8 sheets: Drawing Submittal, Customer Drawing Return, RTR, Actual Dates, Date Calcs, Ship Date, Shipment Checklist, Change Orders, OGSM 2019, Drawing Efficiency)
- `MASTER_SCHEDULE.xlsx` — Production schedule
- `2026_Project_Management_Meeting_-_Working_Agenda.docx` — Weekly Monday 1:30pm PM meeting agenda (this IS the process map)
- Staff folder documents organized by person in `!KELLY_DISCOVERY/`

### Key Files for Claude Code

If you're a Claude Code session and you need to understand this engagement:

1. **Read this README first.**
2. **Read the SDK Developer's Guide** to understand what JobBOSS can and can't do programmatically.
3. **Read the Data Dictionary** to understand what data lives in JobBOSS.
4. **Read the PM Meeting Agenda** (`2026_Project_Management_Meeting_-_Working_Agenda.docx`) — this is the actual process flow for every job.
5. **Look at the PM Tracker** (`PM_Tracker_-_Working.xlsx`) — this is what April is doing manually that should be automated.

---

## How to Evaluate Anything in This Repo

When analyzing any document, spreadsheet, process, or system in this repo, always ask:

1. **What is being done manually that could be automated?**
2. **Where is data being re-entered that already exists somewhere?**
3. **What information are people chasing that should be visible in a dashboard?**
4. **Can the JobBOSS SDK handle this, or do we need an alternative path?**
5. **Is there an off-the-shelf tool that solves this, or does it need to be custom-built?**
6. **How fast could this be implemented and how much time would it save?**

The automation roadmap will be prioritized by: **(speed of implementation) × (user relief)**. Quick wins that save people hours per week go first. Major builds that require months of development go last — unless they unlock everything else.

---

## OTTO — Technical Context

- **Stack:** Python, FastAPI, SQLite3 (migrating to PostgreSQL), HTML/JS frontend, pywebview (migrating to web app)
- **Current Modules:** Estimator (Phase I), Quotes Management, Proposal Generator, Pricing Admin (Phase II)
- **In Development:** RFQ Intake (Gmail API polling → Claude API field extraction → routing)
- **Planned:** Cloud migration (PostgreSQL Flexible Server, Entra ID auth, RBAC), Jobs Module
- **Integration Goal:** OTTO ↔ JobBOSS bidirectional data flow. OTTO handles intelligence and UI, JobBOSS is system of record.
