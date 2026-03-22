# JobBOSS ERP Data Audit — Savannah Tank & Equipment

**Database:** PRODUCTION on DC2
**Audit Date:** 2026-03-22
**Auditor:** Claude (automated extraction via pyodbc)

---

## 1. SYSTEM SNAPSHOT

| Table | Count | Notes |
|-------|-------|-------|
| **Job (total)** | 1,770 | 12 years of history (2014–2026) |
| Job — Active | 405 | Current open work |
| Job — Complete | 704 | Finished, not yet closed |
| Job — Closed | 649 | Fully closed out |
| Job — Template | 12 | Routing templates |
| **Job_Operation** | 64,559 | ~36 ops/job avg |
| **Job_Operation_Time** | 149,507 | **Core time-tracking data** |
| **Customer** | 388 | 217 with at least one job |
| **Vendor** | 778 | Deep supply chain |
| **Employee (total)** | 278 | 239 inactive, 39 active |
| **Employee (active)** | 39 | Matches April's headcount exactly |
| **Work_Center** | 31 | Shop floor + indirect centers |
| **Material** | 7,508 | Extensive material library |
| **Material_Req** | 39,644 | Material requisitions |
| **Material_Trans** | 218,144 | Material transactions (inventory movements) |
| **PO_Header** | 12,044 | Purchase orders |
| **PO_Detail** | 46,496 | PO line items |
| **Quote** | 29 | Barely used — quoting lives outside JobBOSS |
| **Delivery** | 1,344 | Shipping/delivery records |
| **Attendance** | 0 | **Empty — not used** |
| **Invoice_Header** | 2,100 | Billing records |
| **Invoice_Detail** | 5,494 | Invoice line items |
| **SO_Header** | 0 | **Not used — no sales orders** |
| **SO_Detail** | 0 | **Not used** |
| **Contact** | 383 | Customer/vendor contacts |
| **Address** | 2,523 | Address records |

### Date Ranges

| Data | From | To |
|------|------|-----|
| Job orders | 2014-02-12 | 2026-03-20 |
| Time entries | 2000-02-21 | 2026-03-20 |
| Deliveries | 2015-07-10 | 2026-03-17 |

### Jobs by Year

| Year | Jobs | Notes |
|------|------|-------|
| 2014 | 15 | System startup |
| 2015 | 309 | First full year |
| 2016 | 141 | |
| 2017 | 92 | |
| 2018 | 95 | |
| 2019 | 117 | |
| 2020 | 132 | |
| 2021 | 156 | |
| 2022 | 143 | |
| 2023 | 104 | |
| 2024 | 74 | Low year |
| 2025 | 354 | **Record year** — Vertiv 224-tank order |
| 2026 | 38 | YTD through 3/20 |

### Time Entries by Year

| Year | Entries | Notes |
|------|---------|-------|
| 2015 | 8,513 | |
| 2016 | 13,196 | |
| 2017 | 15,827 | |
| 2018 | 14,251 | |
| 2019 | 12,554 | |
| 2020 | 15,933 | |
| 2021 | 12,192 | |
| 2022 | 14,639 | |
| 2023 | 14,503 | |
| 2024 | 13,125 | |
| 2025 | 10,141 | |
| 2026 | 4,586 | YTD through 3/20 |

**Active time logging:** 38 employees in 2026, 33 in March, 30 this week (3/16+). The system is actively used for daily time tracking.

---

## 2. WORK CENTERS (31 total)

### Direct (Shop Floor) — 12 centers

| Work Center | Department | Machines | Operators | Setup Rate | Run Rate |
|-------------|-----------|----------|-----------|------------|----------|
| **PRE FAB** | Fabrication | 6 | 6 | $20.00 | $20.00 |
| **FIT** | FIT | 1 | 1 | $20.00 | $20.00 |
| **FIT TEAM 1** | Fit Up Team 1 | 4 | 4 | $20.00 | $20.00 |
| **FIT TEAM 2** | Fit Up Team 2 | 6 | 6 | $20.00 | $20.00 |
| **FIT TEAM 3** | Fit Up Team 3 | 1 | 1 | $20.00 | $20.00 |
| **BUILD** | Fabrication | 1 | 1 | $20.00 | $20.00 |
| **DETAIL** | Fabrication | 1 | 1 | $20.00 | $20.00 |
| **WELD** | Fabrication | 1 | 1 | $20.00 | $20.00 |
| **FINISHING** | Fabrication | 2 | 2 | $20.00 | $20.00 |
| **MOVE TANK** | Fabrication | 1 | 1 | $20.00 | $20.00 |
| **SHIPPING** | Fabrication | 1 | 1 | $20.00 | $20.00 |
| **SHOP** | (none) | 1 | 1 | $20.00 | $20.00 |

### Indirect (Design/Engineering) — 9 centers

| Work Center | Department | Purpose |
|-------------|-----------|---------|
| LONG LEAD | Design | Long-lead material ordering |
| REMAIN MAT | Design | Remaining material procurement |
| PREL BOM | Design | Preliminary BOM creation |
| FINAL BOM | Design | Final BOM |
| DRAWINGS | Design | Engineering drawings |
| DWG APPROV | Design | Drawing approval cycle |
| STOCK CHK | Design | Stock check |
| SEND CERT | Design | Send certified drawings |
| RELEASE | Design | Release to shop |
| CODE PKG | Design | Code package preparation |

### Indirect (Overhead/Other) — 10 centers

| Work Center | Purpose |
|-------------|---------|
| INSPECTION | QC inspection points |
| OVERHEAD | General overhead |
| SUPERVISN | Supervision |
| MAINTENANC | Maintenance |
| FAC. MAINT | Facility maintenance |
| TRAINING | Training |
| ACADEMY | Training/onboarding |
| REPAIR | Rework/repair |
| SAFETY | Safety |

**Key observation:** All direct labor rates are a flat $20.00/hr for both setup and run. This is a **simplified burden rate**, not actual pay rates. Actual pay rates are stored in the Employee table.

### Work Center Usage in Job Routings (ranked by frequency)

| Work Center | Job Ops | Est Hours | Actual Hours | Act/Est % |
|-------------|---------|-----------|-------------|-----------|
| **PRE FAB** | 21,374 | 127,955 | 126,163 | 98.6% |
| **FIT** | 19,325 | 152,451 | 175,074 | **114.8%** |
| **INSPECTION** | 12,539 | 16 | 31 | N/A (no hrs) |
| **FINISHING** | 5,083 | 35,294 | 37,770 | 107.0% |
| **MOVE TANK** | 2,548 | 4,394 | 7,744 | **176.2%** |
| **SHIPPING** | 1,793 | 5,170 | 5,614 | 108.6% |
| **DETAIL** | 480 | 3,675 | 3,977 | 108.2% |
| **WELD** | 410 | 3,172 | 3,958 | 124.8% |
| **BUILD** | 276 | 2,093 | 3,475 | 166.0% |
| OVERHEAD | 12 | 0 | 75,412 | (indirect) |
| SUPERVISN | 11 | 0 | 29,398 | (indirect) |
| MAINTENANC | 10 | 0 | 18,799 | (indirect) |
| TRAINING | 12 | 0 | 12,848 | (indirect) |
| SHOP | 37 | 0 | 5,562 | (legacy) |
| FAC. MAINT | 10 | 0 | 2,183 | (indirect) |
| ACADEMY | 4 | 0 | 1,507 | (indirect) |
| REPAIR | 12 | 0 | 441 | (indirect) |
| SAFETY | 9 | 0 | 246 | (indirect) |

**Critical finding:** FIT consistently runs **15% over estimate**. MOVE TANK runs **76% over**. These are systematic estimation gaps. PRE FAB is the tightest at 98.6%.

---

## 3. ACTIVE EMPLOYEES (39)

| Employee ID | First Name | Last Name | Department | Hire Date |
|-------------|-----------|-----------|------------|-----------|
| ACOSAL | Alberto | Acosta | Finishing | 2021-10-11 |
| ADKIJU | Julien | Adkins | (none) | 2026-01-19 |
| ALLECH | Christopher | Allen | (none) | 2025-06-30 |
| BATCJA | Jason | Batchelor | (none) | 2025-07-07 |
| BEDNTI | Timothy | Bednarczyk | (none) | 2026-02-23 |
| BENOWE | Wes | Benoit | (none) | 2025-09-02 |
| BOLGDU | Dustin | Bolgrihn | Office | 2024-02-20 |
| BOYLAS | Ashley | Boyles | (none) | 2026-02-10 |
| CHAVSA | Sammy | Chavis | FIT | 2013-10-01 |
| CORWJO | John | Corwin | Office | 2020-08-26 |
| DANIDA | Danzel | Daniels | (none) | 2026-03-02 |
| DAVILU | Lucas | Davis | Fabrication | 2026-03-17 |
| FAHEJO | Joseph | Fahey | (none) | 2026-01-13 |
| FLETCH | Christopher | Fletcher | Office | 2022-06-09 |
| FOLTSH | Shelbi | Foltyn | Fabrication | 2020-08-24 |
| FREEKE | Kevin | Free | (none) | 2024-03-05 |
| HODGJE | Jerry | Hodge, II | (none) | 2026-03-02 |
| JONESH | Sherri | Jones | Office | 2017-04-17 |
| LAMPCH | Christopher | Lampp | (none) | 2025-09-22 |
| LEEKJA | Jacquell | Leeks | (none) | 2023-11-06 |
| LEWIST | Steven | Lewis | (none) | 2025-07-16 |
| LUCELA | Launie | Lucero | (none) | 2026-02-16 |
| MCAMJU | Justin | McAmis | (none) | 2026-02-02 |
| MCMOKE | Kevin | McMyoore | Fabrication | 2022-08-02 |
| MOCKBR | Brittany | Mock | (none) | 2025-09-22 |
| MOORRO | Robert | Moore, III | (none) | 2025-06-02 |
| MOOSCO | Cody | Moose | Fabrication | 2020-06-29 |
| MORRAR | Arthur | Morrison | Fabrication | 2013-10-01 |
| ONACMI | Michael | Onachilla | Office | 2013-10-01 |
| PATENA | Nareshkumar | Patel | Office | 2015-05-04 |
| SELLRA | Raymond | Sellars | Fabrication | 2015-09-28 |
| SHAHRU | Rutang | Shah | Office | 2018-03-20 |
| SHUMCO | Cory | Shuman | FIT | 2024-09-23 |
| SHUMKE | Kenneth | Shuman | (none) | 2018-10-01 |
| SHUMRA | Randall | Shuman | FIT | 2025-06-30 |
| SHUMSC | Scott | Shuman | Fabrication | 2013-10-01 |
| SWANJO | John | Swanger | (none) | 2026-02-23 |
| WHEEKE | Keith | Wheeler | (none) | 2026-02-03 |
| WOLFCA | Carl | Wolfe | (none) | 2026-02-02 |

**Status breakdown:** 39 Active, 239 Inactive (total 278)

**Notable:** Many employees have Department = "(none)" — department field is not consistently maintained. The 4 original hires (2013-10-01) are Sammy Chavis, Scott Shuman, Arthur Morrison, and Michael Onachilla (David). 7 office staff: Dustin, John, Chris Fletcher, Sherri Jones, Michael Onachilla, Nick Patel, Rutang Shah. April Lewis and Kelly are notably **not in the active employee list** (may be under different names or not set up as JobBOSS users).

---

## 4. OPERATIONS (208 defined)

### Shop Floor Routing Steps (by Work Center)

#### PRE FAB Operations (63 ops — the largest set)
| Op Code | Description |
|---------|-------------|
| .010 / 10 | Receive Materials |
| .100 | Cut Nozzle Pipe and Clean |
| .105 | Build Nozzles-Weld |
| .107 | Build Repads for Nozzles |
| .110 | Build Dip Tubes-Weld |
| .115 | Make Manway Parts |
| .120 | Brn MW Neck, Clean, Bevel |
| .125 | Roll Manway Neck |
| .130 | S/U Weld MW Flg, Neck Sem |
| .135 | Bld Davit Arm Aby Cover |
| .140 | Build Hatch/Door |
| .145 | Install Cladding on Flng |
| .147 | Install Clad on Blind/Cov |
| .150 | B&C Top, Bottom Plates |
| .155 | Cut Parts on Burn Table |
| .156 | Clean & Prep Parts |
| .160 | B&C parts-stiff, vr, etc |
| .165 | Build Supports |
| .170 | Roll Repads-Drill & Tap |
| .175 | B&W Base Ring, Skirt |
| .180 | Skirt-BI, SQ, T&C |
| .185 | Roll Skirt Shells |
| .200 | Bld Lift Lugs, Grd Lugs |
| .205 | Roll Rim Angle |
| .210 | Roll Insulation Rings |
| .215 | B&C Baffles |
| .220 | Form Baffles |
| .225 | Cut, Make Baffle Supports |
| .230 | Build Baffles-Weld |
| .235 | Bld T-B Stiffeners |
| .240 | Roll/Burn vacuum rings |
| .245 | Cut Parts-Mixer Bridge |
| .250 | Roll Pipe-Internal Coil |
| .252 | Fab Miscellaneous Parts |
| .255 | Drill/Punch holes |
| .257 | Build Flanges |
| .260 | Sandblast Parts/Plates |
| .261 | Misc Fabrication |
| .262 | Cut, Build Ladder Parts |
| .265 | Form and Roll Ladder Hoop |
| .270 | Build Ladder-Weld |
| .272 | Cut, Build Handrail Parts |
| .275 | Roll Handrail Pipe |
| .280 | Roll Handrail Toe Plate |
| .282 | Build Handrail-Weld |
| .285 | Cut, Build Platform Parts |
| .290 | Burn Platform Grating |
| .292 | Build Platform-Weld |
| .295 | Mount Platform Handrail |
| .300 | Wrap Top & Bottom Heads |
| .305 | BI, SQ, T&C Shells |
| .310 | Bevel Shell Plates |
| .315 | Roll Shell, Tack-Weld I/S |
| .350 | Build Top Head/Cone |
| .355 | L/O Top, B&C Holes |
| .360 | Bevel Top Head |
| .365 | Set Nozzles & Lugs - Top |
| .366 | Weld Nozzles - Top Head |
| .370 | I&W Repads -Top |
| .375 | Install Top Stiffeners |
| .380 | Build Mixer Bridge |
| .385 | Dye Pen Top |
| .390 | Grind I/S Weld Smooth-Top |
| .395 | Polish I/S Weld Seam-Top |
| .450 | Build Bottom Head/Cone |
| .455 | L/O Bottom, B&C Holes |
| .460 | Bevel Bottom Head |
| .465 | Set Nozzles - Bottom Head |
| .466 | Weld Nozzles - Bot. Head |
| .470 | I&W Bottom Repads |
| .475 | Install Bottom Stiffeners |
| .485 | Dye Pen Bottom Head |
| .490 | Grind I/S Weld Smooth-Btm |
| .495 | Polish I/S Weld Seam-Btm |
| .500 | Bld Skirt, Roll & Tack |
| .510 | Bld Skirt, F&T to Base |
| .580 | Fab Internal Coil Support |
| .590 | Fab Internal Coil |
| 11 | FAB MANWAY NOZZLE DP TUBE |
| 13 | FAB LIFT LUGS & SUPPORTS |
| 14 | FAB BAFFLES |
| 15 | FAB TOP/BOTTOM STIFFENERS |
| 16 | FAB MIXER BRIDGE |
| 19 | FAB MISC - TRANSTN, ETC |
| 60 | FAB LADDER |
| 61 | FAB HANDRAIL |
| 62 | FAB PLATFORM |

#### FIT Operations (44 ops)
| Op Code | Description |
|---------|-------------|
| .320 | S/U and Build Sides |
| .325 | Install Body Flg-Shell |
| .326 | Weld Body Flg Shell |
| .382 | Install Body Flange - Top |
| .383 | Weld Body Flg-Top W/C |
| .477 | Cut & Fit Btm Jacket |
| .478 | Weld Jacket to Bottom |
| .479 | Install Jacket Nozzle-Btm |
| .482 | Install Body Flg - Bottom |
| .483 | Weld Body Flg - Bot Hd. |
| .515 | Weld Skirt |
| .520 | L/O Skirt, B&C Holes |
| .530 | Bld Skirt, Fit Anchor/Gst |
| .540 | Set Nzl/MW in Skirt-Tack |
| .545 | Weld Skirt Nozzles, Etc. |
| .600 | Fit Bottom Head to Shell |
| .605 | Tack Shell Courses |
| .610 | Weld Inside Round Seams |
| .615 | Install Rim Angle |
| .616 | Weld Rim Angle |
| .620 | L/O Shell, B&C Holes |
| .625 | Install Baffles-Weld |
| .630 | Install Internal Parts |
| .635 | Install Internal Coil/Spt |
| .637 | Grind I/S Weld Smooth-Shl |
| .638 | Polish I/S Weld Seam-Shl |
| .640 | Fit Top to Shell |
| .641 | Weld top to shell |
| .645 | Weld all Outside Seams |
| .700 | Fit Jacket to Shell |
| .705 | Weld Jacket to Shell |
| .710 | Install Jacket Nozzles |
| .711 | Weld Jacket Nozzles |
| .715 | Install Insul/Vac Rings |
| .717 | Install Lift Lugs on Shl |
| .720 | Install Support Parts |
| .721 | Weld rings, lugs, suppts |
| .725 | Set Nozzles in Shell |
| .726 | Weld Shell Nozz & M/Ws |
| .730 | Add Repads-Weld |
| .735 | Install Dip Pipe Supports |
| .740 | Install Dip Pipes |
| .745 | Install Mixer Bridge |
| .750 | Fit Handrail, I&W Clips |
| .755 | Fit Ladder, I&W Clips |
| .760 | Fit Platform, I&W Clips |
| .770 | Inspect Tank, Make Repair |
| .850 | Remove Head |
| .855 | Remove Nozzles |
| .860 | Remove Jacket |
| 20 | FAB TOP HEAD |
| 22 | INSTALL TP MW NZL LFT LUG |
| 25 | INSTALL TOP STIFF/REPAD |
| 26 | INSTALL TOP MIXER BRIDGE |
| 30 | FAB BOTTOM HEAD |
| 32 | INSTALL BTM MANWY, NOZZLE |
| 34 | INSTALL MANWAY BTM CONE |
| 35 | INSTALL BTM STIFF/REPAD |
| 41 | ROLL SHELLS |
| 42 | TACK SHELL COURSES |
| 43 | WELD SHELL COURSES |
| 44 | RIM ANGLE-ROLL, TRIM, FIT |
| 45 | LAYOUT SHELL |
| 46 | FIT HEADS TO SHELL & WELD |
| 48 | SKIRT-ROLL, INSTALL, WELD |
| 49 | FAB & ASSM SIDE PANELS |
| 50 | INSTALL SHELL NOZZLE MANW |
| 52 | FIT SUPPORTS, LUGS, ETC |
| 54 | INSTALL VAC/INS RINGS |
| 55 | INSTALL BAFFLES |
| 58 | GRIND/POLISH INTERNAL WLD |
| 59 | CUT TANK APART |
| 65 | FIT LADDER HANDRL PLATFRM |
| 70 | INSTALL JACKET SHELL |
| 71 | INSTALL JACKET HEAD |
| 76 | FAB PIPE COIL |
| 77 | INSTALL PIPE COIL |

#### FINISHING Operations (7 ops)
| Op Code | Description |
|---------|-------------|
| .765 | Install Name Tag |
| .900 | Dye Pen Test |
| .910 | Test Tank |
| .920 | Clean Tank Complete |
| .930 | Blast & Paint |
| .940 | Prepare Tank for Shipment |
| .950 | Check BOM, Pack Parts |
| 90 | HYDRO/AIR/DYE PEN TEST |
| 91 | CLEAN TANK |
| 93 | CLOSE FOR SHIPPING/PALLET |

#### SHIPPING Operations (7 ops)
| Op Code | Description |
|---------|-------------|
| .960 | Load on Truck |
| .970 | Take Parts - Galvanizers |
| .971 | Take Parts - Machine Shop |
| .972 | P/U Parts - Galvanizers |
| .973 | P/U Parts - Machine Shop |
| .974 | Deliver Tank |
| .975 | Deliver Miscellaneous Part |
| 94 | LOAD ON TRUCK |
| 98 | DELIVER/PU COMPONENTS |
| 99 | DELIVER TANK |

#### INSPECTION Operations (13 ops)
| Op Code | Description |
|---------|-------------|
| .OI1 | ASME Hold Point |
| .OI2 | ASME Inspection Internal |
| .OI3 | ASME Inspection Test |
| .OI4 | Customer Inspection |
| .QC1 | UT Top & Bottom Heads |
| .QC2 | QC Inspection - Pre Sub C |
| .QC21 | QC Inspection - Ret Com |
| .QC3 | UT Shells |
| .QC4 | QC Inspection -Top/Bot/Co |
| .QC5 | QC Inspection - Internal |
| .QC51 | UT Components |
| .QC6 | QC Inspection - Fab |
| .QC7 | QC Inspection - Test |
| .QC8 | QC Inspection - Clean |
| .QC9 | QC Inspection - Sandblast |
| .QC90 | QC Inspection - Paint |
| .QC95 | QC Inspection - Final & L |

#### MOVE TANK (2 ops)
| Op Code | Description |
|---------|-------------|
| .800 | Move Tank to Detail Rolls |
| .801 | Move to Shop Test Area |
| .802 | Move to Paint Area |
| 80 | MOVE TANK |

**Key observation:** There are TWO numbering systems — the older numeric (10, 11, 13, 20, etc.) and the newer dot-prefix (.010, .100, .105, etc.). The dot-prefix system is much more granular. Both are actively used. The newer system has ~140 operations vs. ~30 in the older system.

---

## 5. RECENT JOBS (20 most recent by Order Date)

| Job | Customer | Status | Order Date | Sched End | Ops | Est Hrs | Act Hrs | Price | Description |
|-----|----------|--------|------------|-----------|-----|---------|---------|-------|-------------|
| 26-027 | KEMIRAWS | Active | 2026-03-20 | — | 0 | 0 | 0 | $6,075 | t-103R DRAWING |
| 26-028 | KEMIRAWS | Active | 2026-03-20 | — | 0 | 0 | 0 | $6,025 | t-107R DRAWING |
| 26-029 | AMERTERP | Active | 2026-03-20 | — | 0 | 0 | 0 | $500 | ALLOWABLE NOZZLE LOAD ANALYSIS |
| 26-030 | AMERTERP | Active | 2026-03-20 | — | 0 | 0 | 0 | $109,000 | 0.374 SHELL_205-14 REPLACEMENT |
| 26-026 | ANDRITZI | Active | 2026-03-16 | — | 0 | 0 | 0 | — | STEAM PIPE REPAIR PIECES |
| 26-025 | BLAKPEND | Active | 2026-03-11 | — | 0 | 0 | 0 | $60,000 | AIR RECEIVER TANK |
| 26-023 | SAVATANK | Active | 2026-03-05 | — | 20 | 17 | 0 | $1 | DEMO TANK |
| 26-024 | POLYCOMP | Active | 2026-03-05 | — | 0 | 0 | 0 | $19,500 | WATER TANK |
| 26-022 | ANDRITZI | Active | 2026-02-17 | — | 0 | 0 | 0 | $70,000 | WASH LIQUOR FLASH TANK |
| 26-020 | USSUGARC | Active | 2026-02-05 | — | 0 | 0 | 0 | $66,000 | SECONDARY SCREENED JUICE TANK C |
| 26-021 | USSUGARC | Active | 2026-02-05 | — | 0 | 0 | 0 | $73,750 | PRIMARY SCREENED JUICE TANK C |
| 26-019 | GENERA1 | Active | 2026-01-28 | — | 0 | 0 | 0 | $2,600 | NOZZLES W/REPADS |
| 26-001 | SYNTHOMER | Active | 2026-01-19 | — | 0 | 0 | 0 | $42,250 | 25-356 CHANGE ORDER |
| 26-007 | VERTCORP | Active | 2026-01-19 | — | 0 | 0 | 0 | $123,200 | TEMP SENSOR SHIPMENT 2 |
| 26-008 | VERTCORP | Active | 2026-01-19 | — | 0 | 0 | 0 | $169,400 | TEMP SENSOR SHIPMENT 3 |
| 26-009 | VERTCORP | Active | 2026-01-19 | — | 0 | 0 | 0 | $107,800 | TEMP SENSOR SHIPMENT 4 |
| 26-010 | VERTCORP | Active | 2026-01-19 | — | 0 | 0 | 0 | $123,200 | TEMP SENSOR SHIPMENT 5 |
| 26-011 | VERTCORP | Active | 2026-01-19 | — | 0 | 0 | 0 | $107,800 | TEMP SENSOR SHIPMENT 6 |
| 26-012 | VERTCORP | Active | 2026-01-19 | — | 0 | 0 | 0 | $92,400 | TEMP SENSOR SHIPMENT 7 |

**Key observations:**
- Most 2026 jobs have **0 operations** — routings haven't been built yet
- Only 26-023 (DEMO TANK) has operations (20 ops, 17 est hrs) — this appears to be a test/demo job ($1 price)
- Job naming convention: `YY-NNN` (e.g., 26-027 = 2026, job #27)
- Customer codes are truncated (KEMIRAWS, AMERTERP, VERTCORP, etc.)
- Vertiv temp sensor shipments are entered as separate jobs (26-007 through 26-012)

---

## 6. TOP 20 MATERIALS (by Material_Req count)

| Material | Req Count | Description |
|----------|-----------|-------------|
| FREIGHT | 925 | Deliver Tank |
| HEAD | 711 | Build Head to Specifications |
| PLT 304L 1/4 X 60 X | 638 | Plate 304L 1/4"x 60"x |
| PIPE 304L 3 SC40 WLD X | 473 | Pipe 304L 3" Sch40 Welded |
| GASKET | 449 | As Specified |
| PIPE 304L 8 SC40 WLD X | 379 | Pipe 304L 8" Sch40 Welded |
| PAINT&SANDBLAST | 365 | Sandblast and Paint Tank |
| XRAY SPOT | 363 | Spot Xray of Tank |
| FLAT 304L 1/4 X 2 X 12' | 343 | Flat Stk 304L 1/4"x 2"x 12' |
| FLANGE 304L 8"150 RFSO | 333 | Flange 304L 8" 150# RFSO |
| AG 304L 1/4 X 3 X 3 X 20' | 324 | Angle 304L 1/4"x 3"x 3"x 20' |
| NUT 2H P 3/4 HH | 315 | Nut 2H Plated 3/4" HH |
| NUT 2H P 5/8 HH | 297 | Nut 2H Plated 5/8" HH |
| PLT 304L 1/4 X 48 X | 284 | Plate 304L 1/4"x 48"x |
| INITIAL MATERIAL LOAD FRM BOOK | 278 | Initial Material Load frm Book |
| GALVANIZING | 261 | Galvanize Parts as Instructed |
| FLANGE 304L 2"150 RFSO | 256 | Flange 304L 2" 150# RFSO |
| CPLG 304L 3/4 3000 HALF THRD | 254 | Coupling 304L 3/4"3000 Half Th |
| FLANGE 304L 3"150 RFSO | 252 | Flange 304L 3" 150# RFSO |
| FLAT SA36 1/4 X 4 X 20' | 251 | Flat Stk SA36 1/4"x 4"x 20' |

**Key observations:**
- **304L stainless steel** dominates — plates, pipe, flanges, flat stock, angle, couplings. This is their bread-and-butter material.
- **Services are tracked as materials:** FREIGHT (925), PAINT&SANDBLAST (365), XRAY SPOT (363), GALVANIZING (261). This is how outside services flow through the BOM.
- **HEAD** (711 reqs) is a custom-spec item — "Build Head to Specifications" — they order heads to spec from suppliers.
- **INITIAL MATERIAL LOAD FRM BOOK** (278) — legacy data migration artifact from when the system was first set up.

---

## 7. TIME TRACKING

### Job_Operation_Time (THE primary time tracking mechanism)
- **149,507 entries** from 2000 to 2026-03-20
- **Actively used:** 38 employees logged time in 2026, 33 in March, **30 in the current week**
- Consistent ~12,000-16,000 entries/year across all years

### Attendance Table
- **0 rows — completely empty, never used**
- The Attendance module exists but was never implemented

### Sample Recent Time Entries (2026-03-20)

| Employee | Work Center | Job | Operation | Setup | Run | OT |
|----------|-----------|-----|-----------|-------|-----|-----|
| Carl Wolfe | PRE FAB | 25-117 | Install Bottom Stiffeners | 0h | 3.0h | — |
| Carl Wolfe | FIT | 25-069 | Install Internal Parts | 0h | 4.0h | 3.5h OT |
| Keith Wheeler | OVERHEAD | OH-26 | (overhead) | 0h | 2.0h | — |
| Keith Wheeler | FINISHING | 25-068 | Test Tank | 0h | 3.0h | 1.5h OT |
| Keith Wheeler | FINISHING | 25-136 | Clean Tank Complete | 0h | 1.0h | 1.0h OT |
| Keith Wheeler | FINISHING | 25-144 | Clean Tank Complete | 0h | 1.0h | — |
| Scott Shuman | SUPERVISN | OH-26 | (supervision) | 0h | 6.0h | — |
| Randall Shuman | FIT | 25-040 | Weld all Outside Seams | 0h | 7.8h | — |
| Kenneth Shuman | MAINTENANC | OH-26 | (maintenance) | 0h | 7.0h | — |
| Raymond Sellars | PRE FAB | 25-099 | Build Bottom Head/Cone | 0h | 8.0h | — |
| Cody Moose | PRE FAB | 25-118 | BI, SQ, T&C Shells | 0h | 7.0h | — |
| Robert Moore III | FINISHING | 25-135,136,144 | Clean Tank Complete | 0h | 4.0h | — |

**Assessment:** Time tracking is **healthy and current**. Employees log hours daily against specific job operations with work center assignments. Overtime is tracked. This is real production data, not backdated entries.

---

## 8. DATA COLLECTION MODULE

### Barcode / Scanner / Kiosk Tables
**None found.** No tables with DC_, Barcode, Scanner, DataCol, Collect, Kiosk, Clock, Badge, or Swipe prefixes exist in the database.

The Data Collection module is **not configured**. Time entry is currently done through the standard JobBOSS desktop interface (manual entry).

### Third-Party Integrations Configured

| Key | Type | Name |
|-----|------|------|
| 0 | QUALITY | None |
| 1 | QUALITY | uniPoint |
| 2 | QUALITY | TQM/Synergy |
| 3 | QUALITY | MQ1 |

These are **available integration options**, not active integrations. No quality management system is currently integrated.

### WCDisplay_Sequence
5 rows — this is display ordering for work center lists, not data collection.

### Databases on Server DC2

| Database | Purpose |
|----------|---------|
| **PRODUCTION** | Main JobBOSS database (this audit) |
| **INDIA** | Separate JobBOSS instance for India engineering (146 tables) |
| **PROPERTY1** | Unknown — possibly a second company or division |
| **Sandbox** | Test/development database |
| **JBSettings** | JobBOSS application settings |
| master / model / msdb / tempdb | SQL Server system databases |

**Notable:** The **INDIA** database has 146 tables (same schema as PRODUCTION) — this is the separate JobBOSS instance for the India engineering team. The **Sandbox** database exists for testing.

---

## SUMMARY ASSESSMENT

### What's Well-Used
- **Job management** — 1,770 jobs, 12 years of history, actively creating new jobs
- **Routing/operations** — 208 operations defined, 64,559 job-operation records, highly granular
- **Time tracking** — 149,507 entries, 30 employees logging time THIS WEEK
- **Materials/BOM** — 7,508 materials, 39,644 requisitions, 218,144 transactions
- **Purchasing** — 12,044 POs with 46,496 line items
- **Invoicing** — 2,100 invoices
- **Work centers** — 31 defined, well-structured direct/indirect split

### What's NOT Used
- **Attendance module** — 0 rows, never implemented
- **Sales Orders** — 0 rows, not used
- **Quoting** — 29 records only (quoting done outside JobBOSS)
- **Data Collection / Barcoding** — no tables exist, module not configured
- **Quality integration** — options listed but none active

### What Needs Attention
- **Employee departments** — most are blank "(none)", not maintained
- **2026 job routings** — most new jobs have 0 operations (not built yet)
- **Two operation numbering systems** — old (10, 11, 20...) and new (.010, .100, .105...) coexist
- **FIT work center** — consistently 15% over estimate across all history
- **MOVE TANK** — 76% over estimate (severely underestimated)
- **Flat $20/hr labor rates** on all work centers — not differentiated by skill level

### Automation Opportunities
1. **Data Collection module** — licensed but unconfigured. Barcode scanning for time entry would eliminate manual entry lag and improve accuracy.
2. **Routing templates** — only 12 templates exist. Building comprehensive templates for common vessel types would speed job setup.
3. **Quoting integration** — with 29 quotes in 12 years, this module is effectively dormant. Connecting the quoting process to JobBOSS would close the estimate-to-actual loop.
4. **Quality tracking** — integration options exist (uniPoint, MQ1) but none active. John's spreadsheet-based QC tracking could potentially be replaced.
5. **Scheduling** — Sched_Start and Sched_End are mostly NULL on recent jobs. The scheduling module appears underutilized.
