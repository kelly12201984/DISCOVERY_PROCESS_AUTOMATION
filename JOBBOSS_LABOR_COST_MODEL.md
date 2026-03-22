# How JobBOSS Calculates Labor Costs at ST&E

**Source:** PRODUCTION database on DC2 | **Date:** 2026-03-22

---

## The Two-Rate System

JobBOSS uses **different rates for estimates vs. actuals**:

```
 ESTIMATES                          ACTUALS
 ┌─────────────────────┐            ┌──────────────────────────┐
 │ Flat $20.00/hr       │            │ Employee's actual rate    │
 │ (from Work Center)   │            │ ($19–$45/hr)              │
 │                      │            │                           │
 │ Same rate regardless  │            │ Rate depends on WHO       │
 │ of who does the work │            │ clocks the hours          │
 └─────────────────────┘            └──────────────────────────┘
```

| | Estimated | Actual |
|---|---|---|
| **Labor Rate** | $20.00/hr (Work Center flat rate) | Employee's hourly rate ($19–$45) |
| **Burden Rate** | $230.00/hr (Work Center burden) | Employee rate × 2.30 |
| **Total Loaded Rate** | $250.00/hr | Employee rate × 3.30 |

---

## Where the Rates Come From

### Estimated Rate → Work Center Table

Every direct Work Center has the same rates:

| Work Center | Setup Rate | Run Rate | Labor Burden | Machine Burden | GA Burden |
|-------------|-----------|---------|-------------|---------------|----------|
| PRE FAB | $20.00 | $20.00 | $230.00 | $0.00 | $0.00 |
| FIT | $20.00 | $20.00 | $230.00 | $0.00 | $0.00 |
| FINISHING | $20.00 | $20.00 | $230.00 | $0.00 | $0.00 |
| WELD | $20.00 | $20.00 | $230.00 | $0.00 | $0.00 |
| SHIPPING | $20.00 | $20.00 | $230.00 | $0.00 | $0.00 |
| *(all others)* | $20.00 | $20.00 | $230.00 | $0.00 | $0.00 |

**Formula:** `Est Labor = $20 × Est Hours` and `Est Burden = $230 × Est Hours`

### Actual Rate → Employee Table

When someone logs time, JobBOSS uses **their personal hourly rate**:

| Rate Range | Employees | Who |
|-----------|-----------|-----|
| $45.00 | 2 | Scott Shuman, Sammy Chavis (supervisors) |
| $41.00 | 1 | Randall Shuman |
| $37.00–$39.00 | 4 | Steven Lewis, Kevin McMyoore, Raymond Sellars, Cody Moose |
| $30.00–$34.00 | 7 | Shelbi Foltyn, Jason Batchelor, Wes Benoit, Kevin Free, etc. |
| $25.00–$28.00 | 9 | Alberto Acosta, Joseph Fahey, Brittany Mock, Carl Wolfe, etc. |
| $19.00–$23.00 | 5 | Keith Wheeler, Jerry Hodge, John Swanger, Robert Moore, etc. |

```
  Employee Rate Distribution (32 shop employees)

  $19-20  ████                    4 employees
  $21-25  ██████                  6 employees
  $26-28  █████                   5 employees
  $29-31  ██████                  6 employees
  $32-34  ███                     3 employees
  $35-39  ████                    4 employees
  $40-45  ███                     3 employees
          ─────────────────────
          Avg: $29.83/hr
          Weighted Avg (by hrs worked): $31.00/hr
          Estimate Rate: $20.00/hr  ← 35% below actual
```

**Formula:** `Act Labor = Emp Rate × Act Hours` and `Act Burden = Emp Rate × 2.30 × Act Hours`

---

## The 2.30x Burden Multiplier

Every employee gets the **same 2.30x multiplier** applied to their rate for burden:

| Employee | Hourly Rate | × 2.30 | = Burden/Hr |
|----------|------------|--------|------------|
| Scott Shuman | $45.00 | × 2.30 | = $103.50 |
| Kevin McMyoore | $39.00 | × 2.30 | = $89.70 |
| Carl Wolfe | $28.00 | × 2.30 | = $64.40 |
| Keith Wheeler | $19.00 | × 2.30 | = $43.70 |

**Exception:** OVERHEAD, SUPERVISN, and MAINTENANC work centers get **$0 burden** — hours are tracked but not burdened.

---

## The Gap: Estimates vs. Actuals

Because the estimate rate ($20/hr) is below the actual average ($31/hr), **estimates systematically understate labor costs**:

| Job | Customer | Est Hrs | Act Hrs | Est Labor | Act Labor | Est Burden | Act Burden | Price |
|-----|----------|---------|---------|-----------|-----------|------------|------------|-------|
| 25-040 | Nak Kiln | 234 | 271 | $4,680 | $9,849 | $10,764 | $20,337 | $1,128,000 |
| 25-066 | Reco/Nudyne | 476 | 460 | $9,520 | $14,286 | $21,896 | $30,473 | $102,250 |
| 25-067 | Reco/Nudyne | 476 | 412 | $9,520 | $14,613 | $21,896 | $30,578 | $102,250 |
| 25-068 | Reco/Nudyne | 476 | 391 | $9,520 | $13,001 | $21,896 | $28,111 | $102,250 |
| 25-069 | Reco/Nudyne | 476 | 274 | $9,520 | $9,264 | $21,896 | $19,678 | $102,250 |
| 25-083 | Synthomer | 511 | 202 | $10,220 | $8,227 | $23,506 | $17,113 | $163,700 |
| 25-089 | Valmet | 1,700 | 1,999 | $34,000 | $72,810 | $78,200 | $150,093 | $835,000 |

### What's Happening

```
  Est Labor vs. Act Labor (sample jobs)

  25-040  Est ████████           $4,680
          Act ████████████████   $9,849     ← 2.1x over estimate

  25-066  Est ████████           $9,520
          Act ████████████       $14,286    ← 1.5x over estimate

  25-089  Est ████████████       $34,000
          Act ██████████████████████████████ $72,810  ← 2.1x over estimate

  25-083  Est ████████████       $10,220
          Act ████████           $8,227     ← under estimate (fewer hours)
```

**Two factors drive the gap:**
1. **Rate gap:** Estimates use $20/hr, actuals average $31/hr → **55% higher rate**
2. **Hours variance:** Some jobs run over on hours (25-089: 1,700 est → 1,999 actual)

When both stack: $20 rate × 1,700 hrs = $34K estimated vs. $31 avg × 1,999 hrs = $72K actual

---

## Summary

```
  ┌─────────────────────────────────────────────────────────┐
  │              ESTIMATE                ACTUAL              │
  │  ┌───────────────────┐    ┌───────────────────────┐     │
  │  │ Work Center Rate   │    │ Employee Hourly Rate   │     │
  │  │ $20.00/hr (flat)   │    │ $19-$45/hr (per person)│     │
  │  └────────┬──────────┘    └──────────┬────────────┘     │
  │           │                          │                   │
  │           ▼                          ▼                   │
  │  ┌───────────────────┐    ┌───────────────────────┐     │
  │  │ × Est Hours        │    │ × Actual Hours         │     │
  │  │ = Est Labor Cost   │    │ = Act Labor Cost       │     │
  │  └────────┬──────────┘    └──────────┬────────────┘     │
  │           │                          │                   │
  │           ▼                          ▼                   │
  │  ┌───────────────────┐    ┌───────────────────────┐     │
  │  │ WC Burden: $230/hr │    │ Emp Rate × 2.30        │     │
  │  │ × Est Hours        │    │ × Actual Hours         │     │
  │  │ = Est Burden       │    │ = Act Burden           │     │
  │  └───────────────────┘    └───────────────────────┘     │
  └─────────────────────────────────────────────────────────┘
```

| Metric | Value |
|--------|-------|
| Estimate labor rate | $20.00/hr (flat) |
| Actual weighted avg labor rate | $31.00/hr |
| Estimate understatement | ~35% on labor |
| Burden multiplier | 2.30x (uniform) |
| Estimate total loaded rate | $250.00/hr |
| Actual avg total loaded rate | ~$102/hr (rate + burden) |
