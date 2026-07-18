---
title: Index
type: index
status: active
vault: TRC
date: 2026-06-28
tags: [resilience]
---

# FLF Submission — Claim Vault Index

This project holds twelve claims — eight from the original build, plus [[covid-004]] and [[blackhole-003]] added the same session, then [[covid-005]] and [[covid-006]] added later the same day, all four from real primary sources that close parts of previously-named gaps. We rewrote each one using the E-Prime rule and checked what the rewrite revealed. We built this in a real note-taking app (Obsidian), across all three case studies FLF gave us. Nothing below counts as a placeholder. Every claim file links to a real source and shows a real before-and-after rewrite.

## Navigation

### By case
- **Eggs, heart disease, and diabetes:** [[eggs-001]] · [[eggs-002]] · [[eggs-003]]
- **COVID's origin:** [[covid-001]] · [[covid-002]] · [[covid-003]] · [[covid-004]] · [[covid-005]] · [[covid-006]]
- **Black holes and the LHC:** [[blackhole-001]] · [[blackhole-002]] · [[blackhole-003]]

### Other project files
- [[insight-contribution-v1]] — names the three kinds of hidden assumption we found (which study, which chain of reasoning, which limited scope), states one prediction we could test, and reports what actually happened when we tested it
- [[crux-analysis-v1]] — ranks the single questions that matter most per case, names what evidence or viewpoints this project still lacks, and separates persuasive wording from real evidence, across all twelve claims
- [[adversarial-robustness-criterion-6]] — our toughest test. Ten different ways a reader could misread a claim, and three ways a source could try to game the method, checked against all eight claims
- [[literature-engagement-addendum-v1]] — our response to two real outside papers we found after finishing our first draft. Proposes splitting the method into two steps: rewrite, then check
- [[two-layer-architecture-v1]] — the exact rules for that two-step split, applied to all eight claims and wired into `ingest.py` as real, runnable code. Written after FLF reviewer Oly Sourbut's feedback
- [[structure-layer-mapping-v1]] — FLF asked for a third step, showing how claims connect to each other. This file names where we already do that work, and what a real, dedicated version of that step would still need
- [[structure-layer-worked-example-v1]] — the real version that file said didn't exist yet: a fixed four-tag format (a fourth tag, combines_with, added later the same day), applied to every within-case pair across all three cases, as a structured edge list and a table
- [[fallacy-screen-layer-v1]] — a fourth step, wired into `ingest.py` as `screen_claim()`. Instead of catching hidden assumptions, it catches broken logic — twenty-six named types of bad argument (one added after a real test found a gap), checked in both the source material and our own writing
- [[fallacy-screen-worked-examples-v1]] — that check, run for real against all twelve claims: caught our own project overclaiming a result, a source's own "rushed conclusion" twice, a source's own "false equivalence" once, and found the gap that became the twenty-sixth category
- [[near-duplicate-check-v1]] — checked every pair among all eight existing claims for a restated conclusion. Found none — but found this project had been stating "nine claims" when only eight exist, corrected here
- [[next-steps-v1]] — what we'd build next, in what order, and why. All seven priorities done or wired the same day

### Sources (the real documents we worked from)
- [[li-2013-meta-analysis]]
- [[zhong-drouin-chartier-2020-bmj]]
- [[diez-espino-2017-predimed]]
- [[rootclaim-debate-session1]]
- [[rootclaim-debate-session2]]
- [[cern-official-faq]]
- [[stansifer-2024-covid-decision]] — one of the debate's two independent judges, ingested directly from his own written decision, not from a summary
- [[van-treuren-2024-covid-decision]] — the debate's other independent judge, ingested directly from his own written decision and linked Bayesian-model spreadsheet, not from a summary
- [[lsag-2008-full-report]] — CERN's actual full technical safety report, ingested directly rather than through the public FAQ that summarizes it

## What this project has, and what it doesn't

**Has:** Twelve real claims. Eight from the original build, rewritten by hand using E-Prime from real published sources, across three very different kinds of case (a pooled statistical study, a live debate, an official FAQ page). Four more — [[covid-004]] and [[blackhole-003]] added the same session, [[covid-005]] and [[covid-006]] added later the same day — directly from real primary sources: both of the COVID debate's independent judges' own written verdicts, and CERN's full technical safety report, each closing part of a gap this project had already named about relying on secondhand summaries. We linked related claims to each other based on what we actually found while working through them — not links we planned out in advance.

**Doesn't have:** A complete picture of any of the three cases. Each case has many more sources out in the world that we haven't worked through yet. Each SOURCES file names what we skipped, and so does the "missing perspectives" part of [[crux-analysis-v1]]. We built a sample sized to fit a judge's reading time, not a finished, complete system.

## How someone else could add to this project

1. Pick a source we haven't worked through yet (see [[crux-analysis-v1]]'s "missing perspectives" section for what's still uningested — the Giddings & Mangano paper LSAG cites for further detail, and the genetic-evidence and Method 1 portions of [[van-treuren-2024-covid-decision]] not yet ingested into a claim, are the clearest examples now).
2. Follow the same steps: pull the exact original wording, force the E-Prime rewrite, write down what the rewrite reveals that the original hid, and save the new claim using the same file format every other claim in this project uses.
3. Link the new claim to existing ones where it supports them, disagrees with them, or names a key open question shared between them.
4. Once a case has three or more new claims, redo the ranking in [[crux-analysis-v1]] and check whether it changes. Re-run [[near-duplicate-check-v1]] too — a thirteenth claim is exactly the kind of addition that check exists to catch.

Extending this project doesn't require learning E-Prime. Reading, linking, and building on an existing claim only takes ordinary reading. Writing a brand-new claim from scratch does require learning E-Prime first. This split matters: it means someone new can pick this project up and add to it right away, without a steep learning curve first.
