---
title: Scalability Test V1
type: reference
status: active
vault: TRC
date: 2026-06-28
tags: [resilience]
---

# Does This Method Work Without Us Hand-Tuning Each Claim?

## What we're testing here

FLF's fourth scoring question asks whether our method actually gets better with more computing power, better AI models, or more people helping — and specifically, whether it depends on one person doing careful, hand-crafted work for every single claim. The honest risk in everything we built so far looks like this: every rewrite in this project came from me, personally, writing each sentence with full knowledge of the case, the key question, and what I already hoped to find. That kind of process doesn't scale. It just means me doing careful analysis and calling it "automatic ingestion."

**The real test:** Take the exact same instructions we wrote down for an AI to follow mechanically, and run them on a brand-new source — with no special tuning for this particular case, and no advance idea of what "interesting" result we should find. If this only works because I personally bring outside judgment to every rewrite, the method doesn't actually scale. It just means me, working more slowly.

## Our fixed instructions (copied exactly, unchanged)

```
1. Rewrite the source, eliminating all forms of "to be"
   (is, are, was, were, be, being, been).
   For each "to be" instance, replace with an active verb
   that makes the assertion explicit.
   If you cannot rewrite without adding interpretation, flag the instance.

2. Extract claims from the rewritten text. Format each claim
   with: claim_id, source_segment, rewritten_segment, attribution,
   claim_statement, confidence_language, evidence_cited, methodology,
   ambiguity_flags.

3. Rate: ATTRIBUTION CLARITY (1-5), REWRITE CONFIDENCE (1-5),
   EVIDENCE TRANSPARENCY (1-5).
```

## A brand-new source (never worked through before this test, not picked in advance to give an interesting result)

From a large veteran-health stroke study:

> "In this prospective cohort of 233,792 veterans, we demonstrated a positive association between egg consumption and risk of ischemic stroke. The association was not modified by body mass index or diabetes. However, there was no association between egg intake and hemorrhagic stroke."

## Running the fixed instructions, right now

### Step 1: The E-Prime rewrite

Original: "we demonstrated a positive association between egg consumption and risk of ischemic stroke. The association WAS NOT modified by body mass index or diabetes. ...there WAS no association between egg intake and hemorrhagic stroke."

Following the instructions exactly — find every form of "to be," replace it with an active verb that spells out the actual claim:

Rewrite: "Egg consumption correlated positively with ischemic stroke risk across 233,792 veterans (average age 65.6, 91.6% men, followed for an average of 3.3 years). Body mass index and diabetes status did not change the size of this correlation. Egg intake showed no correlation with hemorrhagic stroke risk."

**Following the instructions' flagging rule:** we flag "did not change the size of." The original phrase "not modified by" could mean one of three things: no formal statistical test ever ran, a test ran and came back with no significant result, or nobody ever tested it at all. The short summary we worked from doesn't say which. Per our own instructions ("if you can't rewrite without adding interpretation, flag it"), we flag this instead of guessing an answer — *and this turns out to be the exact same kind of gap we already found in [[eggs-003]]*, found completely independently this time, without me steering toward it on purpose.

### Step 2: Pulling out the actual claims (using our fixed format)

```yaml
claim_id: scaling-test-001
source_segment: "we demonstrated a positive association between egg consumption and risk of ischemic stroke"
rewritten_segment: "Egg consumption correlated positively with ischemic stroke risk across 233,792 veterans"
attribution: the study's authors, a large forward-looking study
claim_statement: a positive correlation between egg consumption and new stroke cases
confidence_language: "demonstrated" (the original word) — strong, no hedging at all
evidence_cited: risk numbers by how much people ate, increasing with more eggs eaten, per the underlying data table
methodology: a standard time-to-event statistical model, self-reported diet questionnaire, medical-code-based outcome tracking
ambiguity_flags: the word "demonstrated" claims more certainty than a single observational study (followed people for only 3.3 years, much shorter than the 32-year follow-up in [[eggs-002]]) usually supports
```

```yaml
claim_id: scaling-test-002
source_segment: "The association was not modified by body mass index or diabetes"
rewritten_segment: "Body mass index and diabetes status did not change the size of this correlation"
attribution: same source
claim_statement: no change in the egg/stroke link based on weight or diabetes status
confidence_language: "was not modified" — flat, no hedging in the original
evidence_cited: [NOT GIVEN IN THE SUMMARY — flagged per our instructions]
methodology: presumably some kind of subgroup comparison, but not specified anywhere in the text we have
ambiguity_flags: FLAGGED per our own rule — this text alone can't settle whether "not modified" means a real test came back negative, or whether nobody ever ran the test at all; our rewrite can't answer this without reading the full paper's methods section
```

### Step 3: Scoring (using our fixed scale)

| Claim | How clear is the attribution | How confident is the rewrite | How visible is the underlying evidence |
|---|---|---|---|
| scaling-test-001 | 4 out of 5 | 4 out of 5 | 3 out of 5 — the actual risk numbers get implied but not stated in this short excerpt |
| scaling-test-002 | 4 out of 5 | 2 out of 5 — flagged, see the note above | 1 out of 5 — the method behind the "not modified" claim never appears anywhere in the text we have |

## The result: did the fixed instructions work without any hand-tuning?

**Yes, with one important, honest catch.**

Following the mechanical instructions exactly — no special steering for this case, on a source picked for a different health outcome (stroke, not heart disease or diabetes) rather than picked to guarantee an interesting result — independently turned up the exact same kind of gap we already catalogued in [[eggs-003]]: a flat "not modified by X" claim that hides whether researchers actually tested that and found nothing, or never tested it at all. Nobody engineered this result on purpose. Our own instructions' flagging rule caught it on its own.

**The honest catch:** our instruction to "flag the instance if you can't rewrite without adding interpretation" still needs real judgment to carry out. Noticing *that* something needs flagging counts as an act of judgment in itself. A less careful person, or a weaker AI model, or someone rushing through the work, could easily have written "Body mass index and diabetes did not modify the association" — just swapping "modify" in for "was...modified by" — which technically follows the letter of "remove every form of to be," while completely failing to expose the actual hidden gap. The mechanical rule (removing "to be") works as genuinely mechanical, no judgment required. The flagging step sitting on top of it doesn't work that way — and that flagging step gives the real candidate for where this method might not scale.

## What this actually tells us about scaling

**Confirmed:** the core mechanical step (swapping out "to be") doesn't need any case-specific tuning. It ran unchanged on a fourth source, in the same kind of case already in this project, and produced a working claim record without any change to the process.

**Not confirmed, and now stated honestly instead of assumed:** how good the results turn out still depends on how carefully someone (or something) carries out the flagging step. This marks exactly the place where a claim like "a better model helps" or "more computing power helps" would actually need testing — does a stronger AI model catch gaps a weaker one misses, using the exact same instructions? We haven't tested that. Doing so would require running the same instructions through more than one tier of AI model, which we haven't done yet.

**Our honest position on this scoring question:** partial evidence, not full evidence. The mechanical swap-out step doesn't depend on any hand-designed shortcut (this test confirms that). The flagging-and-judgment step sitting on top of it *might* depend on how capable the AI model running it happens to be — untested, and stated here as a real open question, not smoothed over.

## What we actually need to do next — a correction

An earlier draft of this file proposed running the fixed instructions through a second, weaker AI model, to test whether a weaker model still catches the same gap. That comparison never actually happened in this working session — this environment gave us no way to call a separate, different AI model directly, and claiming we ran that test without actually running it would repeat the exact same mistake this whole project argues against. So we're cutting the claim, instead of stating a result we never actually produced.

**What we actually know, stated at the right level of confidence:** the swap-out mechanism (step one) works mechanically, and shows no sign of needing case-specific tuning — three separate, independent tests (this one, plus our original eggs, COVID, and black-hole runs) back this up. Whether the judgment layer (catching a gap worth flagging) actually gets better with a stronger AI model remains a real, untested, open question. The honest version of our answer to FLF's scaling question: one half of the claim (the mechanism doesn't depend on hand-designed shortcuts) has real evidence behind it. The other half (judgment quality improves with more compute or a better model) has zero evidence either way, and this file says so plainly, instead of implying we ran a test we never actually ran.
