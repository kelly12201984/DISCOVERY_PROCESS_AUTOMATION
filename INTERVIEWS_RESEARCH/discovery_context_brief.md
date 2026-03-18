# DISCOVERY ENGAGEMENT CONTEXT BRIEF
## Paste this into any new AI chat to get it up to speed

---

## WHO I AM
Kelly Arseneau, owner of Savannah Intelligence Systems LLC. Solo automation consultancy. MS in Applied Data Science. I built OTTO — a custom business automation platform — for Savannah Tank and Equipment Corp. I'm direct, I use profanity, don't sugarcoat things for me.

## WHAT I'M DOING RIGHT NOW
Three-week discovery engagement at Savannah Tank (March 16 – April 3, 2026). Fixed price $8,400, paid in three weekly installments of $2,800.

## THE GOAL
Identify automation opportunities across all departments. Evaluate existing tools, off-the-shelf options, M365 capabilities, and JobBOSS integration options. Deliver a prioritized automation roadmap organized by: fastest to implement + most relief for users. David (president) wants tools in his staff's hands ASAP — the company is growing fast and needs automation wherever possible. If off-the-shelf solves it, we go off-the-shelf. If it needs to be built, we build it.

## DELIVERABLES
1. Department-by-department findings — what each person does, bottlenecks, automation opportunities
2. Systems and tools evaluation — JobBOSS integration, off-the-shelf tools, build-vs-buy recommendations
3. Prioritized automation roadmap — ordered by speed of implementation × user relief
4. Executive presentation to David and Chris

## THE COMPANY: SAVANNAH TANK AND EQUIPMENT CORP
Custom pressure vessel and tank manufacturer in Savannah, GA. ASME code shop. Make-to-order — every job is custom. Growing fast. Uses JobBOSS for shop management (need to confirm if classic or JobBOSS²). Has Microsoft 365. Files currently live on a shared P drive (messy, unstructured). India engineering team (led by Rutang) handles calculations and drawings remotely.

## KEY PEOPLE

**David Onachilla** — President. Decision-maker. Currently in India. Stepping back toward soft retirement. Responds to visuals and his own conclusions. Negotiates on price. Thinks in weekly payment blocks. Never show him hourly rates. He did NOT communicate this discovery engagement to his staff yet — Chris is handling that at standup Tuesday 3/18.

**Chris Fletcher** — Sales Manager. My husband. Primary OTTO user. Becoming "David Jr." as David steps back. Sees the full sales-to-production lifecycle. Taking on leadership responsibilities. Will introduce the discovery engagement to staff.

**April** — Project Manager. The connective tissue between departments. Sees every job lifecycle, every handoff, every delay.

**Nick** — Engineering / Procurement. Handles technical engineering AND material purchasing. Coordinates with India engineering team. Bridge between what was quoted and what gets built.

**John** — Quality Control. IMPORTANT: John is preparing for an ASME audit THIS WEEK and Mon-Tue next week. ASME audits happen once every 3 years. Do NOT schedule his interview until Wed-Thu of Week 2 (3/25-3/26) when audit is done and pain points are fresh.

**Sherri** — Office Management / Accounting. Back office — invoicing, AP/AR, general admin. Interacts with JobBOSS for financial processes.

**Dustin** — Production / Shop Floor. Runs the shop floor. Last interview — by then I'll have heard every other department's perspective on production.

**Rutang** — Leads the India engineering team. Remote. Handles calculations and drawings.

## EXISTING SYSTEMS & TECH
- **OTTO** — My custom platform. Python, pywebview, SQLite3, FastAPI, HTML/JS frontend. Currently handles estimation, quotes management, proposal generation, pricing admin. Cloud migration planned (SQLite → PostgreSQL, pywebview → FastAPI web app, Entra ID auth).
- **JobBOSS** — Shop management / ERP. Quoting, scheduling, job tracking, inventory. Need to evaluate SDK integration options. Classic JobBOSS SDK is COM-based (.NET wrapper, XML requests, requires session ID and user seat). JobBOSS² reportedly has NO API per GetApp.
- **Microsoft 365** — Available to all staff. Power Automate, SharePoint, Teams all potentially usable. Power Automate has process mining capability (90-day free trial available).
- **P Drive** — Shared network drive. Current file storage. Messy, unstructured, version control issues.
- **AMETank** — Engineering software for tank design. XML export issues were a prior pain point (version 18.11.27 regression).
- **COMPRESS** — Engineering calculations software. Licensed via Sentinel LDK.

## INTERVIEW SCHEDULE (REVISED)
- Mon 3/17: Chris informal download (done or in progress)
- Tue 3/18: Standup intro. Begin scheduling.
- Wed 3/19: April interview (PM)
- Thu 3/20: Nick interview (Engineering/Procurement)
- Fri 3/21: Sherri interview (Office/Accounting)
- Mon 3/23: Dustin interview (Production)
- Wed 3/25: John interview (QC — post ASME audit)

## WHAT I'M LISTENING FOR ACROSS ALL INTERVIEWS
1. **Information flow failures** — where data gets stuck, re-entered, or lost between departments
2. **Manual processes** — Excel workarounds, copy-paste workflows, hand-assembled reports
3. **JobBOSS pain points** — what they use vs. what it can do, where data is stale/incomplete
4. **Communication gaps** — how departments find out about problems, meetings that exist only because info doesn't flow
5. **Quick wins** — "I spend X hours doing Y," "I wish I could see Z," any quantifiable time sinks
6. **P drive chaos** — wrong versions, can't find files, no structure

## HOW TO HELP ME
When I paste an interview transcript:
1. Extract every pain point and bottleneck mentioned
2. List current tools and workarounds described
3. Identify information the person needs but doesn't have easy access to
4. Flag automation opportunities (categorize as: quick win / medium effort / major build)
5. Note dependencies on other departments
6. Flag contradictions with previous interviews (I'll tell you what prior interviews revealed)
7. Suggest follow-up questions for remaining interviewees based on what this person revealed

## BACKGROUND CONTEXT
- Three prior vendors failed to deliver a working estimation system before I built OTTO
- Phase I (Estimator MVP, $17K) accepted Jan 2026
- Phase II (Quotes, Proposals, Pricing Admin, $10K after negotiation) completed early 2026
- Phase III was proposed as cloud migration + jobs module but David opted for discovery-only engagement first
- The strategic question: "The Toolbox" (standalone apps, P drive stays central) vs "The System" (connected platform with structured database enabling future AI)
- David's pattern: negotiates vendor pricing down, thinks in weekly payments, fixed price only
- RFQ intake module in development: polls Gmail, Claude API extracts fields from customer emails
