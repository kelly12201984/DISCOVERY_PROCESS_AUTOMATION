# Build Plan Automation: Key Findings from Data Analysis

## Finding 1: The Excel Build Plan IS the JobBOSS Routing

The MASTER BUILD PLAN.xlsx has 5 sheets:
- **Sheet2-PASTE HERE!** = A direct copy-paste from the JobBOSS job screen
- **Build Plan w Hours** = Same routing reorganized with section headers and inline notes
- **Build Plan - No Hours** = Same as above but without estimated hours (for shop floor posting)
- **Tasks with Hours** = Each operation as a separate work order card (for printing)
- **Tasks - No Hours** = Same cards without hours

The operations, op numbers, work centers, and estimated hours are **identical** between the Excel and JobBOSS. The Excel adds:
1. **Job-specific fabrication notes** inline (e.g., "BUILD TOP IN (2) SECTIONS", "DO NOT CUT COLLAR CONNECTIONS", "PREP (8) SHELL SECTIONS FOR ROLLING")
2. **Section headers** organizing operations into phases: Nozzles, Cut & Prep, Shells, Supports, Misc Parts, Ladders/Handrails/Platforms
3. **Completed By** columns for name, date, QC sign-off

**What this means for OTTO**: The Excel build plan is a printable shop document derived from the JobBOSS routing. OTTO doesn't need to create a separate Excel — it needs to populate the JobBOSS routing correctly, and the Excel generation is a formatting step.

## Finding 2: The Inline Notes Are the Real Value

The descriptions in JobBOSS are truncated to ~25 characters:
- JobBOSS: `Build Top Head/Cone`
- Excel: `Build top head/cone` + note: `BUILD TOP IN (2) SECTIONS`

- JobBOSS: `Roll Shell, Tack-Weld I/S`
- Excel: `Roll shells, tack and weld inside seams` + note: `ROLL (8) SHELL SECTIONS`

These notes contain **job-specific intelligence** that comes from the engineer reading the drawing. OTTO would need to derive these from the vessel specs (e.g., knowing an oversized top head requires 2-section fabrication).

## Finding 3: Estimation Accuracy is Bimodal

Across 48 real tank jobs in 2024:
- **40% on target** (within ±10% of estimate)
- **21% over** (actual exceeded estimate by >10%)
- **40% under** (actual was <90% of estimate)
- Average ratio: 0.94 (slightly over-estimating on average)

The under-estimates are suspicious — jobs 24-027 through 24-036 all have identical 94h or 117h estimates but actual hours of 50-74h. These look like a **batch of similar tanks where the template wasn't adjusted** to match the actual simpler builds.

The over-estimates include Job 24-003 (128%), 24-011 (147%), 24-013 (141%) — these are likely more complex tanks where the standard template underestimated.

**What this means for OTTO**: The current estimation process uses templates that work well for "average" tanks but systematically miss on simple repeats (over-estimates) and complex one-offs (under-estimates). OTTO can improve both by learning from actual hours.

## Finding 4: Vessel Specs Drive Everything

From the certified drawing for Job 24-003 (Aqueous Ammonia Tank), the specs that determine the build plan:

| Spec | Value | Routing Impact |
|------|-------|----------------|
| Shell ID | 120" | Determines PRE FAB hours for shells, rolling |
| Shell courses | 3 | Directly → 3 courses to roll, bevel, tack |
| Nozzles | 14 + 2 MW | Drives nozzle pipe cutting, welding, repad hours |
| Head type | F&D | Different ops than flat or cone heads |
| Design code | ASME | Adds ASME hold points, stamp requirements |
| FV design | Yes | Adds vacuum ring operations |
| Accessories | HR, Ladder, Platform | Adds 20+ ops for accessory fabrication |
| Weight | 22,500 lbs | Affects move/shipping operations |
| Material | SA516-70 | Standard; exotic materials would add hours |

The 28 operations in Job 24-003 that DON'T appear in Job 25-089 are almost entirely due to:
1. Accessories (ladders, handrails, platforms) — 24-003 has them, 25-089 doesn't
2. Head nozzle installation — 24-003 has nozzles in heads, 25-089 has them only in shell
3. Galvanizing — 24-003 sends parts to galvanizer, 25-089 goes to machine shop

## Finding 5: The Operation Numbering System is Structured

Op numbers follow a consistent scheme across all jobs:
- **.010** = Receive Material
- **.QC1** = UT Heads
- **.100-.147** = Nozzle & Manway fabrication
- **.155-.156** = Burn table / Clean parts
- **.165-.175** = Supports
- **.200-.261** = Misc parts (lugs, stiffeners, misc fab)
- **.262-.282** = Ladders, handrails
- **.285-.300** = Platforms
- **.305-.315** = Shell plate prep & rolling
- **.350-.375** = Top head
- **.450-.460** = Bottom head
- **.600-.750** = FIT operations (assembly)
- **.QC2-.QC5** = QC inspection checkpoints
- **.800+** = FINISHING (test, clean, paint, ship)

This numbering is the **template system** — operations are selected/skipped based on what the tank needs. OTTO can use this: if the drawing shows no ladder, skip .262-.270. If it shows cladding, include .145-.147.

## Next Steps

1. **Get more certified drawings into the repo** — we need to extract specs from 10-20 different tank types to build the mapping from specs → routing
2. **Compare the "Old Build Plan" vs "MASTER BUILD PLAN"** format — the older format (089-25 Build Plan.xlsx) has a simpler 2-column layout that may be the estimator's draft before Dustin formats it
3. **Build routing template classifier** — given vessel specs, predict which of the ~48% template matches apply
4. **Build hours estimation model** — given vessel specs + routing template, predict per-operation hours
5. **Parse the inline notes** — these are the highest-value data for OTTO's intelligence
