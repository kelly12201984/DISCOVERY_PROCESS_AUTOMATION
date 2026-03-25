# Chris Fletcher — Sales Manager Briefing
## Based on: CHRIS/ folder contents, JobBOSS data, system design docs, interviews

**Date:** 2026-03-24
**Status:** Discovery Draft

---

## Role Summary

Chris Fletcher is the Sales Manager and is becoming "David Jr." as David Onachilla steps toward retirement. He is the primary OTTO user, runs the full sales-to-production lifecycle (RFQ → estimate → proposal → PO → job creation), and is the main customer-facing contact. He introduced the discovery engagement to staff.

---

## What's in Chris's Folder

### 1. JOBHISTORY.xls — The Master Sales Ledger

**This is a massive artifact.** 39 sheets spanning 1998 to 2026, plus 8 billing schedule sheets (2009-2016) and a Data Collection sheet. This is essentially the entire sales history of Savannah Tank going back 28 years.

**Structure per year-tab:** RECORD, JOB #, PO DATE, APP. DWG DUE DATE, CUSTOMER, DESCRIPTION, CONTACT, PHONE, SELLER, PURCHASE ORDER #, M/H (man hours), VA$ (value-added dollars), VPH (VA$ per hour), Code, Contract Amount, Amt. Billed, Quoted Lead Time After Drawings, Billing status, MONTH, WEEK

**2025 Summary:**
- **361 jobs** logged
- **$16.86M** total contract value
- **$10.03M** billed (59% collection rate — $6.8M unbilled)
- **60,618 man hours** quoted
- **$9.71M VA$** (value-added — contract minus materials)
- Almost entirely Chris: 348 jobs sold by "CF", only 10 by "SB"
- Code mix: 270 ASME Stamped, 52 API, 21 unspecified, 3 ASME no-stamp

**2025 Top Customers by Contract Value:**

| Customer | Contract Value | Jobs |
|---|---|---|
| Vertiv Corporation | $4,961,600 | 232 |
| Kimberly Clark | $1,892,350 | 20 |
| Reco Commercial Systems | $1,636,000 | 16 |
| Nak Kiln Services | $1,128,000 | 1 |
| Andritz | $900,450 | 5 |
| Irving Tissue | $894,350 | 14 |
| Valmet | $835,000 | 1 |
| Epic Systems Group | $773,700 | 17 |

Vertiv dominates — 64% of all jobs and 29% of contract revenue. That's massive concentration risk.

**2026 Summary (YTD through ~March 20):**
- **29 jobs** so far
- **$2.53M** contract value
- **$420K** billed (17% collection rate — early in lifecycle)
- **5,600 man hours** quoted
- SNF ($1.29M, 8 jobs) and Vertiv ($862K, 8 jobs) lead again

**Billing Schedule Sheets (2009-2016):** These track milestone billing per job — Approved Drawings %, Material Receipt %, Final %, Retention %, Freight, Extras. This is the billing lifecycle that April's PM Tracker now partially covers. These sheets stopped in 2016, suggesting the billing tracking process moved elsewhere (likely April's domain).

**Data Collection Sheet:** A weekly intake summary feeding the dashboards — week-of date, contract $, hours, VA$, plus monthly rollups. This is the raw data entry point for the Sales Tracker dashboards.

---

### 2. Sales Tracker 2026.xlsx — The Active Sales Dashboard

Three sheets: Dashboard P1, Dashboard P2, and the weekly data table.

**Dashboard P1 — YTD Order Intake vs. Plan:**
- **YTD Actual: $2,450,001**
- **YTD Target: $3,250,000**
- **Gap: -$799,999 (-24.6%)**
- Also shows Factory Backlog by Week (hours)

**Dashboard P2 — Sales Funnel + Metrics:**

Active 30-day funnel (13 deals):

| Quote # | Company | Amount | Man Hours | Prob% | Prob$ |
|---|---|---|---|---|---|
| 9378 | Fortera | $3,620,000 | 7,400 | 50% | $1,810,000 |
| 9087 | Franklin Engineering | $1,034,000 | 2,298 | 50% | $517,000 |
| 9338 | Valmet | $1,041,000 | 1 | 20% | $208,200 |
| 9166 | Syensqo | $910,000 | 823 | 50% | $455,000 |
| 9399 | SNF | $452,250 | 1,308 | 90% | $407,025 |
| 9417 | Kiewit | $424,000 | 1,169 | 50% | $212,000 |
| 9042 | Perdue Chicken | $297,000 | 1,350 | 50% | $148,500 |
| 9192 | IMI Industrial | $264,500 | 958 | 20% | $52,900 |
| 9344 | EPIC Systems | $103,750 | 521 | 40% | $41,500 |
| 9228 | National Gypsum | $95,000 | 382 | 75% | $71,250 |
| 9039 | Wellons | $69,500 | 314 | 50% | $34,750 |
| 9238 | VEi Global | $46,500 | 227 | 90% | $41,850 |
| 9366 | Andritz | $32,250 | 104 | 30% | $9,675 |

**Total pipeline: $8.39M raw / $4.01M probability-weighted**

Funnel metrics:
- **YTD Quotes: 49 actual vs. 64 target (-23.4%)**
- **YTD Quoted Value: $11.75M actual vs. $22M target (-46.6%)**
- Gauges track monthly order intake (red/amber/green) and VA$/Hour ($205.68 actual)

**Weekly Data (2026 tab):**
- Tracks Week #, Order Intake $, Hours, VA$, VA$/Hr
- Also tracks Backlog (Hours): actual vs. target (18,000) vs. red threshold (12,000)
- Week 1-2 were strong ($494K + $1.74M intake), then dropped off sharply
- Backlog started at 22,873 hours, declining to ~22,335 by Week 8 — still above target (18,000) and red (12,000)

---

### 3. Tank Datasheets for Customer — 4 Templates

These are blank customer-facing specification forms, one per tank type:

| Template | Key Differences |
|---|---|
| **ASME Vertical Tank** | Top Head Type, Bottom Head Type, Shell Height |
| **ASME Horizontal Tank** | Heads (single type), Shell Width, layout has attachments on right side |
| **API Tank** | Roof, Flat/Slope Bottom (no heads — atmospheric) |
| **API Tank with Legs** | Same as API but with leg support type |

**Common fields across all 4:** Purchaser/Client, Equipment No./Name, Location, Quantity, Design Code, Tank Diameter (OD/ID), Design Pressure, Design Temperature, Specific Gravity, Corrosion Allowance, Seismic Loading (Ss, S1), Wind Loading, Support Type, Attachments (Handrail, Ladder, Platform, Jacket, Internal Coil, Other), Material of Construction (Shell, Heads/Roof/Bottom), Nozzle Schedule (Mark, Service, Size, Type), Additional Requirements.

**Why this matters:** These datasheets are the structured input that should feed OTTO and eventually the iLogic automation. The fields here map directly to the TANK entity in the system design ERD. If these templates are consistently used, they're a clean data capture point for tank specs that currently live nowhere in JobBOSS.

---

## Key Observations

### Chris is the revenue bottleneck
- Seller "CF" handled 348 of 361 jobs in 2025 (96%). Only 10 went to "SB" and 1 to "RS" in 2026. Chris IS the sales department. If he's down, quoting stops.

### The JOBHISTORY file is irreplaceable institutional knowledge
- 28 years of every job Savannah Tank has ever done. Customer contacts, PO numbers, contract amounts, billing status, man hours, VA$ — all in one .xls file. This is not in JobBOSS (JobBOSS only goes back to ~2015 based on our data). If this file is lost, the pre-2015 history is gone.

### The Sales Tracker is well-designed but manually fed
- Chris enters the weekly data himself into the Data Collection sheet, which feeds the dashboards. The pipeline funnel with probability weighting is more sophisticated than most of the other spreadsheets in the shop. But it's still manual — every number typed by hand.

### 2026 is behind plan
- Quoting volume is 23% below target, quoted value is 47% below target, and order intake is 25% below target through Week 8. The backlog is healthy (above 18,000 hrs) but declining. The pipeline ($4M weighted) needs to close to catch up.

### Vertiv concentration risk
- 232 of 361 jobs in 2025 were Vertiv. If Vertiv pauses or moves to a competitor, it's a $5M hole in a $17M year.

### VA$/Hour is a critical metric Chris tracks
- This is essentially the value-added revenue per quoted labor hour — a proxy for job profitability before materials. The 2025 average was ~$160/hr; the current funnel shows $205/hr. Chris uses this to evaluate deal quality.

### The gap between JOBHISTORY and JobBOSS
- JOBHISTORY has 361 jobs for 2025. JobBOSS has only 1,758 total jobs across all years (2014-2026). The JOBHISTORY file captures jobs that may not yet be in JobBOSS (quotes not yet converted) and has richer sales context (contact names, phone numbers, seller codes, quoted lead times, billing milestones) that JobBOSS doesn't track.

### These tank datasheets should be the front door for automation
- They define the 4 tank types ST builds. Every field on these forms is a parameter that could feed: OTTO quoting, COMPRESS calc verification, iLogic drawing automation, Smart BOM generation, and the TANK dimension in the analytics model.

---

## Connections to Other Findings

| Chris's Data | Connects To |
|---|---|
| JOBHISTORY man hours (M/H) | Should reconcile with JobBOSS `Est_Total_Hrs` on jobs.csv — but JOBHISTORY has quoted hours while JobBOSS has build plan hours. These are different numbers (sales estimate vs. production estimate). |
| JOBHISTORY contract amounts | Should match JobBOSS `Total_Price` — worth validating |
| Sales Tracker backlog hours | Should align with active job estimated hours in JobBOSS — currently maintained independently |
| Tank datasheets | Map to COMPRESS XML parameters and OTTO's existing extraction — these are the human-readable version of what OTTO already parses from XML |
| VA$/Hour metric | Can be validated against FactTimeEntry actuals — are jobs that quote at $200/hr VA actually more profitable than $150/hr jobs? |
| The $20/hr labor rate issue | Chris's estimates use VA$ which excludes labor cost. But the build plan hours that flow from his estimates are costed at $20/hr in JobBOSS, which is wrong (actual avg is $30.78). This means JobBOSS shows inflated margins because labor is understated. |

---

## Automation Opportunities (from system design)

1. **Quote-to-Job Pipeline (Phase 2B):** OTTO quote won → auto-create job in JobBOSS + P drive folder. Eliminates Chris's manual job creation.
2. **Estimate Calibration (Phase 4B):** ML model trained on 149K historical time entries compares actual hours to Chris's quoted hours — feedback loop to improve future estimates.
3. **Sales Tracker Auto-Feed:** Data Collection sheet could pull from JobBOSS order data instead of Chris typing it. Pipeline could pull from OTTO quotes.
4. **Tank Datasheet → OTTO:** Structured datasheet intake as an alternative to XML upload for jobs where COMPRESS isn't run first.
