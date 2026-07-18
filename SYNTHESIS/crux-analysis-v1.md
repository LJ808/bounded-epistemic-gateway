---
synthesis_type: crux_analysis
claims_analyzed: 12
cases_covered: [eggs-health, covid-origins, black-holes]
tags: [resilience]
---
# The Key Open Questions — All Twelve Claims

We actually ran this check across our real project. This document doesn't just describe what the check would find someday. It shows what we found.

## The Questions Ranked by How Much They'd Change, If Answered

### Question 1 (matters most): [[eggs-003]]

**The question:** One study (called PREDIMED) found no real difference in egg-related heart risk between people with diabetes and people without. Does that mean diabetes truly doesn't change the risk? Or does it mean the study just didn't include enough diabetic people to detect a real difference, even though the raw numbers hinted at one?

**Why this question matters most:** The answer directly changes how we read a different claim in this project ([[eggs-001]]), which found nearly double the heart-attack risk for diabetics who eat eggs. If PREDIMED's "no difference" result reflects a true absence of any difference, then that other claim's finding might just reflect random noise from a small group, pointing the wrong way. If PREDIMED's result instead reflects "too few people to tell," then the other claim's finding stands unchallenged. The numbers in each study read clearly enough on their own. The real dispute sits entirely in how to interpret them.

**What would settle it:** A statistician could calculate this directly. Given how many diabetic people PREDIMED actually studied, how big would a real difference have needed to be for the study to reliably catch it? If that minimum size turns out bigger than the actual difference PREDIMED saw, then PREDIMED's "no difference" finding tells us nothing useful — it doesn't disprove the other study at all.

### Question 2: [[covid-003]]

**The question:** COVID's virus carries an unusual genetic feature (scientists call it a furin cleavage site) that looks different from what nature typically produces, and that only became easy to build in a lab using methods invented after COVID already existed. Does that unusual feature count as evidence the virus came from a lab? Or as evidence it came from nature?

**Why this ranks second:** Both sides of the actual COVID-origins debate treat this single genetic detail as central to their argument. Our earlier check (in the claim file itself) already found that a careless reader could walk away believing the exact opposite of what the evidence actually supports. High stakes, and a real risk of getting flipped around by mistake.

**What would settle it:** Someone would need to check whether genetic engineers, back in 2019, had access to any method — published or not — that could have predicted this genetic feature would actually work, before COVID ever appeared. Nothing in our source material answers that question.

### Question 3: [[blackhole-002]] — UPDATED, partially answered same session

**The question:** Does CERN's safety argument rest on one single idea (the same physics theory that predicts a black hole could form also predicts it would instantly evaporate)? Or does it also rest on a second, separate kind of evidence (real astronomical objects like neutron stars and white dwarfs, which prove similar processes already happen safely in nature)?

**Why this ranks third:** This carries the least urgency of our three questions — everyone involved already treats the actual risk as extremely small, even though getting it wrong would carry enormous stakes.

**What we originally guessed, and what turned out true:** We'd guessed, without reading CERN's full report, that the two arguments would probably collapse into one reason stated twice. Reading the actual report ([[blackhole-003]]) shows that guess was wrong. LSAG's own report treats the two arguments as additive and independent ("in addition to"), not one restated — a real, checked finding, not a repeat of our earlier speculation. What the full report doesn't do: rank one argument as carrying more of the actual safety weight than the other. That narrower question stays open even now.

**What would still settle it:** The report LSAG's own Section 4 cites for further detail (Giddings & Mangano, arXiv:0806.3381) might address this weighting question directly — not read in this project yet.

## What Evidence or Viewpoints We're Missing

**Eggs case:** All three of our sources come from large, observational studies or from combined analyses of several such studies. None of our sources come from a randomized controlled trial — the gold-standard kind of study where researchers randomly assign half the people to eat eggs and half not to. As it happens, that kind of trial doesn't really exist for long-term heart-disease outcomes anywhere in the wider scientific literature, only for short-term markers like cholesterol. This counts as a real gap in the actual science, not just a gap in what we happened to read.

**COVID case:** Both debate participants and both judges originally appeared in our project secondhand, through one journalist's (Scott Alexander's) written summary of the debate. **Update:** both judges' full written decisions now sit in the vault directly. Eric Stansifer's ([[covid-004]]) came first; Will van Treuren's ([[covid-005]], [[covid-006]]) followed later the same day once Jay provided the PDF and linked Bayesian-model spreadsheet directly, closing the Google-Drive-viewer blocker that had kept it secondhand. All of our claims about "what the judges concluded" now rest on each judge's own words, not a summary of either.

**Black holes case:** CERN's full 2008 technical safety report — the actual document CERN's short public FAQ summarizes — originally never entered this project; every claim rested on the FAQ's short version alone. **Update, same session:** now ingested directly ([[blackhole-003]]), and it answers part of what the FAQ left unclear — LSAG's own report treats the same-theory argument and the astrophysical check as two additive, independent lines of defense, not one restated. It does not answer which of the two carries more actual safety weight; that specific question, raised in [[blackhole-002]], stays open even in the full primary source. A second named gap (the collision-geometry question in [[blackhole-001]]) also survives the full report intact — LSAG acknowledges the gap exists but defers its resolution to a separate, still-uningested paper (Giddings & Mangano, arXiv:0806.3381).

**The pattern across all three cases, updated:** Originally, every case worked from a summary, a write-up, or an FAQ — never from raw data, a full transcript, or a full report. That's no longer true everywhere: four real primary-source claims entered this project the same day ([[covid-004]] and [[blackhole-003]] first, then [[covid-005]] and [[covid-006]]), each closing part of a gap this file already named. The eggs case still rests entirely on published studies (its own kind of primary source, just not a transcript or a judge's verdict) with no equivalent gap to close. This still counts as an honest limit of what we actually built — most of this project still rests on summaries — but it no longer counts as a limit of the method itself in every case. Where we had time to go get the primary source, the method handled it the same way it handled everything else: forced rewrite, checked assessment, honest gaps named.

## Where Confident-Sounding Words Outrun the Actual Evidence

The clearest example in this whole project: our third eggs claim uses the phrase "no evidence of interaction," which sounds like a settled, closed question. The actual numbers behind that phrase point to something much weaker: an underpowered test that couldn't have caught a real difference even if one existed. This gap between how a claim sounds and what its numbers actually show counts as the single biggest one we found across all twelve claims — bigger than anything in the COVID or black-holes claims. In those two other cases, the confident-sounding language (CERN's "would have no time," the debater's "epidemiologically impossible") at least pointed in the right direction. It just overstated how certain that direction really was.

## What This Check Actually Shows

- Running this check on twelve real claims, not a made-up example set, produces a real ranking with real reasoning behind it — not just a list of topics.
- The "what are we missing" check found one real, shared problem across all three completely different cases: relying on secondhand summaries instead of original sources. That pattern only became visible once we ran the check across the whole project at once. Looking at any single case alone would have missed it.
- A person reviewed and wrote this file by hand. We didn't automate it. Our own plan for this project calls for exactly that at this stage: a first pass that a person checks and writes up directly, not a fully automatic verdict with nobody reviewing it.
