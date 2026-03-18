# POST-INTERVIEW ANALYSIS PROMPT TEMPLATE
## Copy, fill in the blanks, paste with transcript

---

## PROMPT (paste this + transcript into Claude):

```
I'm doing a 3-week discovery engagement at Savannah Tank and Equipment Corp — a custom pressure vessel manufacturer in Savannah, GA. I'm interviewing department heads to identify automation opportunities and build a prioritized roadmap.

[PASTE CONTEXT BRIEF HERE IF THIS IS A NEW CHAT — otherwise skip]

This is my interview with **[NAME]** who handles **[ROLE]**.

**What I already know from prior interviews:**
[Fill this in — 3-5 bullet points of relevant findings from earlier interviews. Example:]
- April said job status tracking is completely manual and she spends 2+ hours/day chasing updates
- Nick mentioned drawings sometimes get to the floor with wrong revision numbers
- [Add whatever is relevant to this person's department]

**Here's the transcript:**

[PASTE TRANSCRIPT]

**Please analyze this and give me:**

1. PAIN POINTS & BOTTLENECKS — every friction point mentioned, with direct quotes where they said something revealing
2. CURRENT TOOLS & WORKAROUNDS — what they actually use and any "we do it this way because..." workarounds
3. INFORMATION GAPS — what info they need but can't easily get, and where that info actually lives
4. AUTOMATION OPPORTUNITIES — categorize each as:
   - 🟢 Quick Win (off-the-shelf or simple build, high relief, < 1 week)
   - 🟡 Medium Effort (needs some custom work, 1-4 weeks)
   - 🔴 Major Build (significant development, 1+ months)
5. CROSS-DEPARTMENT DEPENDENCIES — what this person needs from others and what others need from them
6. CONTRADICTIONS — anything that conflicts with what prior interviewees said
7. FOLLOW-UP QUESTIONS — what I should ask remaining interviewees based on what this person revealed
8. QUOTABLE MOMENTS — specific things they said that would land well in the executive presentation to David
```

---

## AFTER ALL INTERVIEWS — CROSS-REFERENCE PROMPT:

```
I've now completed all department interviews for my discovery engagement at Savannah Tank. Here are the individual analyses:

[Paste each interview analysis]

Please produce:

1. CONSOLIDATED PAIN POINT MAP — every pain point organized by department, with cross-department dependencies mapped
2. PROCESS FLOW GAPS — where the job lifecycle breaks down between departments (from RFQ → quote → engineering → procurement → production → QC → shipping → invoicing)
3. TOP 10 AUTOMATION OPPORTUNITIES — ranked by (speed of implementation) × (user relief), with estimated effort level and recommended approach (buy vs. build)
4. JOBOSS INTEGRATION PRIORITIES — which pain points could be solved by better JobBOSS integration vs. need external tools
5. M365 QUICK WINS — what can be done with Power Automate, SharePoint, or Teams that they're not doing today
6. THE "DAVID SLIDE" — the single most compelling finding that will make David say "yes, do that first" (remember: he responds to visuals and his own conclusions, not being told what to think)
7. CONTRADICTIONS & BLIND SPOTS — where departments disagree about how things work, and what leadership probably doesn't know is happening
```
