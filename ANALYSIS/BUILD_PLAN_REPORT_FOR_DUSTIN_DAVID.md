# Build Plan Analysis Report
### Savannah Tank & Equipment Corp.
### Prepared for Dustin & David | April 2026

---

## What This Report Is

We analyzed **96 completed jobs** that have all three data sources: certified drawings, MASTER BUILD PLANs, and actual hours from JobBOSS. We also cross-referenced the PM Tracker (PO dates, drop-dead dates, ship dates) against actual shop floor operation dates from JobBOSS.

The goal: understand where the current build plan process works well, where it doesn't, and what OTTO can do about it.

---

## The Big Picture: How Are We Doing?

### On-Time Delivery: 64.5%

Of 62 jobs with both a ship date and a drop-dead date tracked in the PM Tracker:
- **40 shipped on time** (before or on drop-dead date)
- **22 shipped late** (after drop-dead date)
- Average job ships **13 days early**, but that average hides some painful outliers — a few jobs were 100+ days late

### Timeline Breakdown (Averages)

| Phase | Average Days |
|-------|-------------|
| PO received to first shop operation | **134 days** |
| Fabrication span (first op to last op) | **83 days** |
| Total lead time (PO to ship) | **216 days** |

The 134-day pre-fabrication period covers engineering, drawing approval cycles, procurement, and release to shop. That's where delays accumulate before the shop even touches material.

### Hour Estimation Accuracy

Across 96 completed jobs with actual hours:

| Category | Count | % |
|----------|-------|---|
| On target (within +/- 10%) | 32 | 33% |
| Overestimated (actual < 90% of estimate) | 38 | 40% |
| Underestimated (actual > 110% of estimate) | 26 | 27% |

**The estimates tend to run high.** Average ratio is 0.94 (actuals come in ~6% under estimate). That's not terrible for the overall job, but the accuracy varies wildly at the individual operation level.

---

## Where the Build Plan Gets It Right

### The Template System Works

The 159-operation master template with structured op numbering (.100s = nozzles, .300s = shells, .600s = fit, etc.) is well-organized. Engineers activate 30-65 operations per job depending on complexity, and the selection logic is sound.

### The Work Center Split is Consistent

Across all jobs analyzed, the hour distribution holds a predictable pattern:

| Work Center | % of Total Hours | Notes |
|-------------|-----------------|-------|
| PRE FAB | ~50% | Always the largest share |
| FIT | ~38% | Grows slightly for larger tanks |
| FINISHING | ~10% | Does NOT scale linearly with size |
| MOVE/SHIP | ~2% | Small but consistently underestimated |

If a build plan's PRE FAB share is significantly below 45% or above 60%, that's a flag worth checking.

### QC Checkpoints Are Consistently Placed

Every plan includes 8-15 INSPECTION operations at zero hours. These serve as process gates (UT heads, QC pre-subcontractor, QC internal, QC fab, QC test, QC clean, QC sandblast, QC paint, QC final). They're correctly at 0 estimated hours since they're quality gates, not labor ops.

---

## Where the Build Plan Misses

### The 5 Operations That Account for Most of the Error

These five operations alone were responsible for **+787 hours of underestimation** across 2024 jobs:

| Operation | Jobs | Avg Est | Avg Actual | Avg Ratio | Total Overrun |
|-----------|------|---------|------------|-----------|---------------|
| Cut Parts on Burn Table | 47 | 18.4h | 23.5h | **1.35x** | +240h |
| Clean Tank Complete | 27 | varies | varies | **1.19x** | +184h |
| Fit Top to Shell | 33 | varies | varies | **1.64x** | +147h |
| Tack Shell Courses | 34 | varies | varies | **1.33x** | +118h |
| BI, SQ, T&C Shells | 37 | varies | varies | varies | +98h |

Meanwhile, **Clean & Prep Parts** is consistently over-estimated (avg ratio 0.78 — budgeting 16.5h but taking 11.5h).

### The "Identical Estimate" Problem

Jobs 24-027 through 24-036 (a batch of 10 similar tanks) all received identical estimates of 94h or 117h. Actual hours ranged from 50h to 74h — a 30-50% overestimate on every single one. The template wasn't adjusted to reflect that these were simpler builds.

The flip side also happens: Job 24-011 was estimated at 264h and took 388h (47% over). Job 24-013 was estimated at 264h and took 371h (41% over). Same estimate, same miss — the template didn't account for the additional complexity.

**This is the core problem OTTO can solve: matching the estimate to the specific tank, not to a generic template.**

### Accessories Are the Wild Card

Ladders, handrails, and platforms only appear on ~32% of jobs (typically large vessels 300+ hours). When they do appear, the estimates are among the least reliable:

- Build Ladder-Weld: Job 24-003 estimated 40h, took 59h
- Build Platform-Weld: Job 24-003 estimated 35h, took 48.5h
- Burn Platform Grating: Job 24-003 estimated 10h, took 22.5h

Accessories aren't templated as well because they vary so much — a simple caged ladder vs. a full platform with swing gate and rest platforms are completely different scopes.

### Move/Ship Operations Are Systematically Low

Every MOVE TANK and SHIPPING operation is estimated at 2-8 hours, but actuals regularly run 1.5-2x that. "Prepare Tank for Shipment" has an average ratio of **2.15x** — estimates are roughly half of what it actually takes.

---

## What the Inline Notes Tell Us

The MASTER BUILD PLAN's most valuable feature is the inline fabrication notes — the text added by the engineer after reading the drawing. Examples:

- "BUILD TOP IN (2) SECTIONS" — tells the shop the head is too large for single-piece fabrication
- "ROLL (8) SHELL SECTIONS" — quantifies the work for the shell roller
- "DO NOT CUT COLLAR CONNECTIONS" — prevents a costly mistake
- "WELD OUTSIDE SEAM W/COBOT" — specifies the welding method
- "INCL HOLE WATCH" — safety requirement for confined space internal welding
- "***MAKE SURE LADDER DOES NOT COVER NOZZLES***" — fit-up warning

### Which Operations Always Get Notes (100% of the time):
- Fabricate miscellaneous parts — always needs specifics
- Install dip pipe supports — usually "INCL HOLE WATCH"
- Install internals — specific internals to install
- Miscellaneous Fabrication — always custom scope

### Which Operations Never Get Notes:
- All QC Inspection checkpoints (standardized gates)
- Burn and clean parts (consistent process)
- Install name tag, Clean tank complete, Load on truck

### What This Means:
The notes are where the engineer translates the drawing into shop instructions. About half the operations sometimes need notes, and the content falls into clear categories:
1. **Quantity/scope**: "INCL (4) LIFT LUGS", "ROLL (2) DOUBLE SHELLS"
2. **Method**: "WELD OUTSIDE SEAM W/COBOT", "MAKE FULL PEN WELD FROM OUTSIDE"
3. **Caution**: "CHECK BEFORE BURNING", "CHECK WITH QC FOR TEST PRESSURE"
4. **Part references**: "BUILD N9", "FOR MANWAY", "CABLE SUPPORT; CLIP FOR N2"

---

## How Work Actually Flows Through the Shop

The build plan sequence numbers suggest operations run in order. **They don't.** The actual data shows massive parallel execution:

### Job 24-003 (571 est hrs, 81 ops, 93 calendar days)

| Phase | Start Date | End Date | Calendar Span |
|-------|-----------|----------|---------------|
| PRE FAB | 06/17 | 09/03 | 78 days |
| FIT | 07/22 | 08/26 | 35 days |
| FINISHING | 08/22 | 09/18 | 27 days |

**PRE FAB and FIT overlapped by 35 days** — the entire FIT phase ran inside PRE FAB's span. On 15 separate days, multiple operations started simultaneously. The shop starts fitting the tank body while still fabricating accessories (ladders, platforms, handrails).

This pattern is consistent across all job sizes:
- Small jobs (~65 calendar days): phases overlap by ~8 days
- Medium jobs (~93-108 days): phases overlap by ~31-35 days
- Large jobs (~147 days): phases overlap by ~39 days

**FIT always begins roughly 1/3 to 1/2 of the way through PRE FAB.** The trigger is "core shell and head pre-fab complete" — not "all pre-fab complete."

---

## Certified Drawing Extraction: What's on Sheet 1

We examined certified drawings across 5 different tank types (120 gal portable to 41,800 gal process vessel). Every drawing uses the same Savannah Tank template with four structured data tables in consistent positions:

| Table | Location | Reliability |
|-------|----------|-------------|
| Nozzle Schedule | Top-right | HIGH — same columns every drawing |
| Materials of Construction | Center-right | HIGH — standard rows + extras |
| Design Data | Right of Materials | HIGH — same fields every drawing |
| Capacity & Weights | Bottom-right | HIGH — always present |

The vessel specs that drive the build plan are all on Sheet 1:
- **Shell diameter** determines rolling and welding hours
- **Shell courses** directly set how many courses to roll, bevel, and tack
- **Nozzle count and sizes** drive the entire nozzle fabrication block
- **Head type** (F&D, flat, cone) determines which head operations to include
- **Design code** (ASME vs API) determines whether ASME hold points and stamp requirements are needed
- **Accessories** (ladder, handrail, platform) add 20+ operations when present
- **Material** (carbon steel vs stainless vs duplex) affects welding methods and hours

---

## The Invisible Schedule Killer: End-of-Job Wait Time

**This is the single most important finding in this report.**

The build plan tracks labor hours. But the finishing phase is dominated by *wait time* — waiting for inspections, waiting for paint/sandblast queues, waiting for shipping coordination. That wait time is completely invisible in the current system.

### The Numbers

**End-of-job phases (FINISHING + INSPECTION + MOVE + SHIPPING) consume 57% of total calendar time but only 15% of labor hours.**

That's a 3.8x disproportion. The average job spends 42 calendar days in finishing — roughly half the total fabrication span — doing work that only accounts for 15% of the labor budget. The other 85% of the calendar time in that phase is *waiting.*

### Where the Calendar Time Goes

| Gap | Avg Calendar Days | Max | What's Happening |
|-----|------------------|-----|-----------------|
| Move to Paint Area → Prepare for Shipment | **20.8 days** | 69 days | Paint queue, application, cure time, sandblast |
| Prepare for Shipment → Load on Truck | **14.3 days** | 70 days | Shipping coordination, customer pickup scheduling |
| QC Inspection - Paint | **17.8 days** | 69 days | Waiting for inspector + rework if needed |
| QC Inspection - Sandblast | **17.5 days** | 69 days | Same pattern |
| QC Inspection - Test | **9.2 days** | 42 days | Hydro/pneumatic test + inspector |
| QC Inspection - Fab | **7.2 days** | 42 days | Structural inspection before moving on |

### The Worst Examples

| Job | Total Calendar Days | End-Phase Calendar Days | % in End-Phase | Labor % in End-Phase |
|-----|-------------------|----------------------|----------------|---------------------|
| 24-069 | ~100+ | 88% | 88% | 10% |
| 24-011 | ~100+ | 83% | 83% | 13% |
| 24-045 | ~80+ | 84% | 84% | 19% |

These tanks were essentially built and waiting. The fabrication was done, but they sat through weeks of finishing, testing, inspection, and shipping delays.

### QC Inspections Are Completely Untracked

**Zero of the 447 inspection operations across all 2024 jobs have an Actual_Start date in JobBOSS.** Nobody is logging when inspections happen. This means:
- You can't tell if a QC gate blocked progress for 1 day or 3 weeks
- You can't identify which inspectors or inspection types are bottlenecks
- You can't predict how long the finishing phase will take
- When a tank ships late, you can't trace *which* inspection or finishing step caused the delay

### What This Means for the Build Plan

The build plan needs **two types of estimates** for every operation:

1. **Labor hours** (what it has now) — how many man-hours of work
2. **Calendar duration** (what it's missing) — how many days this step takes, including wait time

For PRE FAB and FIT operations, labor hours and calendar time are closely related — if you have the crew, the hours translate to days directly. But for FINISHING, INSPECTION, and MOVE operations, calendar time is 3-4x what labor hours suggest because of queuing, inspector availability, cure times, and coordination delays.

**If OTTO's build plan included estimated calendar days for the finishing phase — even rough ones — you could project realistic ship dates instead of discovering delays after they've already happened.**

---

## What OTTO Can Do With This

### Phase 1: Auto-populate the Build Plan Template
Given a certified drawing, OTTO can:
1. Read the vessel specs from Sheet 1 (structured tables = high extraction reliability)
2. Select the right operations from the 159-op template based on tank features
3. Estimate hours per operation using the 96-job historical dataset
4. Generate the inline notes for standard cases ("ROLL (X) SHELL SECTIONS" based on shell course count from drawing)

### Phase 2: Calibrate the Estimates
Using the 96 GOLD jobs (drawing + build plan + actual hours), OTTO can learn:
- Which operations are consistently over- or underestimated
- How hours scale with vessel dimensions (hours per nozzle, per shell course, per diameter inch)
- Which templates work for which tank types
- Apply correction factors to the 5 worst operations

### Phase 3: Realistic Timeline Projection
Using the PM Tracker dates + actual operation dates:
- Predict fab span based on job complexity
- Model the parallel execution pattern (FIT starts when core PRE FAB finishes)
- Flag jobs at risk of missing drop-dead dates earlier in the process

---

## Data Available for This Work

| Resource | Count | Coverage |
|----------|-------|----------|
| GOLD jobs (drawing + build plan + actual hours) | **96** | 2024-2025 |
| Certified drawings (Sheet 1 PDFs) | **122** | 2024-2026 |
| MASTER BUILD PLANs | **140** | 2024-2026 |
| PM Tracker jobs (PO dates, drop-dead dates) | **126** | 2024-2026 |
| JobBOSS operations with actual hours | **38,482** | All years |
| Unique operation descriptions in template | **159** | Master list |

---

## Questions for Dustin & David

1. **"Cut Parts on Burn Table" is the #1 source of estimation error (+240h total overrun across 2024). Is this one CNC setup or multiple? Should it be split into separate operations (shell parts, nozzle parts, accessory parts)?**

2. **Do nozzle fabrication hours scale linearly with count and size?** A 2" RFSO is quick; a 24" manway with davit arm is slow. Should "Build Nozzles-Weld" be split by nozzle size range?

3. **What triggers the start of FIT?** The data shows FIT starts ~1/3 through PRE FAB. Is there a specific "shell rolling complete" milestone, or is it a judgment call?

4. **Jobs 24-027 through 24-036 all got identical 94-117h estimates but took 50-74h. Were these a batch of similar tanks where the template wasn't adjusted?** Is this a common pattern for repeat work?

5. **How much of the inline notes are "always true for this tank type" vs. "one-off engineering judgment"?** For example, is "BUILD TOP IN (2) SECTIONS" always required above a certain diameter, or does it depend on shop floor conditions that day?

6. **Move/Ship operations are estimated at roughly half of actual every time.** Should these estimates be increased across the board, or is there something specific causing the overrun?

7. **The finishing phase averages 42 calendar days but only 15% of labor hours. What's eating the time?** Is it paint queue backlog? Inspector availability? Customer inspection scheduling? Shipping coordination? Where does a tank typically sit the longest after fabrication is done?

8. **Would it help to have estimated calendar days on the build plan alongside labor hours?** For example: "QC Inspection - Test: 0 labor hrs, 5 calendar days" or "Move to Paint Area: 4 labor hrs, 3 calendar days wait for paint bay." This would make the schedule visible in the build plan instead of being a separate mental model.

9. **Why aren't QC inspection dates being logged in JobBOSS?** Is it a process issue (inspectors don't have access), a training issue, or a deliberate choice? Even a simple "inspection completed" date stamp would let us identify bottlenecks.

---

*Data analysis performed by OTTO using JobBOSS export data, PM Tracker, MASTER BUILD PLANs, and certified engineering drawings from P:\JOBS\2024-2026.*
