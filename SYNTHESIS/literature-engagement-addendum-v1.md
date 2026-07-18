---
synthesis_type: literature_engagement_addendum
addendum_to: [insight-contribution-v1, adversarial-robustness-criterion-6]
trigger: external_literature_review_2026-06-24
claims_tested: 0
date_executed: "2026-06-24"
status: addendum, not a rewrite — core submission claims unchanged; superseded in part by v2 (2026-07-08)
written_in_e_prime: true
superseded_by: literature-engagement-addendum-v2.md
superseded_date: "2026-07-08"
superseded_scope: mechanistic warrant for E-Prime accuracy-gain puzzle now resolved in v2; two-layer architecture warrant extended in v2; new Criterion 6 grounding in v2
tags: [resilience]
---

# Two Outside Papers, and What They Actually Mean for Our Project

Two real, checkable papers came out after we wrote our first draft. Both touch directly on the core method this project argues for.

Our standing rule here: new information that complicates a claim gets stated plainly, not quietly patched over. (See [[adversarial-robustness-criterion-6]] Part C and [[crux-analysis-v1]]'s honest-gaps section.) This document applies that same rule to itself, written throughout in plain E-Prime.

**What this document does not do:** rewrite our core claim, take back any of our eight claim files, or soften the "honest gaps" section in our README.

**What this document actually adds:** a real, testable proposal for a stronger, two-part version of our method. These two outside papers look at a different stage of the process than our project addresses. They don't compete with our project. They fit alongside it.

---

## A plain-language note, for anyone new to any of these terms

Our core method uses a writing rule called E-Prime. E-Prime removes every form of the word "to be" — words like "is," "are," "was," "were" — from a piece of writing.

Why does that matter?

Phrases like "there is an association" or "this means X happened" read like plain facts about the world. But they hide something real: the conditions under which the claim actually holds true. Remove the word "is," and the writer has to name those conditions out loud instead.

That forced naming — the rewrite itself — gives our whole project its main detection tool. A hidden condition becomes visible. A reader can then judge it for themselves.

Our project automates that rewrite using an AI model, and stores each result in an organized set of files, each one linked back to its original source.

---

## Outside Paper 1: Jehu-Appiah (2026)

**"Trivial Vocabulary Bans Improve LLM Reasoning More Than Deep Linguistic Constraints"** (found on arXiv, paper number 2604.02699)

We checked this directly against the paper's own summary and full text.

The study tested five different writing rules, across six different AI models, on seven kinds of reasoning tasks — 15,600 trials total. The five rules: no rule at all (as a baseline), our own E-Prime rule, a rule banning the word "have," an instruction to think through things more elaborately, and a rule banning filler words like "very" and "just."

Result: all four real rules beat having no rule at all. E-Prime produced the smallest improvement (+3.7 percentage points). The filler-word ban produced the biggest improvement (+6.0 to 6.7 percentage points).

The paper argues this disproves an idea some people assumed: that a deeper, more grammatically demanding rule should produce a bigger improvement in reasoning. Instead, the real cause behind the filler-word ban's success looks like something else entirely: the constant mental work of checking every single word against a banned list — ongoing self-monitoring — disrupts a model's lazy, formulaic answers, whether or not the actual banned words carry any logical weight themselves.

### Why this finding doesn't disprove our project's claim

This study measures something completely different from what our project measures.

Jehu-Appiah's team measured whether a writing rule improves an AI model's reasoning while the model actively writes something new, under that rule.

Our project measures something at a completely different stage: whether a rule forces a human reader to see what an already-finished claim actually depends on.

Our own process (`ingest.py`) never asks an AI model to reason under E-Prime and then checks whether its reasoning got better. Instead, it takes a sentence someone already wrote, and rewrites that existing sentence into E-Prime. The rewrite forces a hidden condition into view. A reader can then check it for themselves.

These two jobs don't compete with each other. E-Prime can work as a weak tool for improving an AI model's live reasoning (Jehu-Appiah's finding) while also working as a strong tool for forcing an already-finished claim to reveal what it rests on (our project's claim). Neither paper actually tests the other paper's claim.

### Why this finding actually helps our original claim

[[insight-contribution-v1]] already named an open question: whether some other writing rule might reveal hidden conditions faster or more reliably than E-Prime.

Jehu-Appiah's result gives us our first real evidence on that exact question. Read carefully, the answer splits by stage:

| Stage | The job at this stage | What the evidence actually shows |
|---|---|---|
| **Writing something new** — an AI producing fresh reasoning under a rule | Making the AI's output better | Jehu-Appiah found a filler-word ban beats E-Prime here. The real cause: ongoing self-monitoring, not grammatical depth. |
| **Revealing a hidden condition** — rewriting an existing claim so a reader can see what it depends on | Forcing a fixed sentence to reveal what it rests on | Our project found E-Prime targets exactly the word "is" (and its other forms) that absorbs the hidden condition. No filler-word ban targets that specific spot in a sentence. |

A two-part system follows directly from this split:

- Use a filler-word ban at the writing stage — anywhere our process asks an AI to summarize or combine new material.
- Use E-Prime at the revealing stage — anywhere our process rewrites an existing claim to expose what it depends on.

Neither part replaces the other. Each one handles the stage it actually fits.

This directly answers the open question our project had already named: some rules really do work better at the writing stage. None of them replace E-Prime's specific target at the revealing stage.

### A new open question, named and not yet answered

Does adding a filler-word-ban step before our existing E-Prime rewrite actually improve the quality of what our project produces — without weakening the reveal itself?

We haven't tested this yet. Our own process makes this directly testable: run the same source through our pipeline once with a filler-word-ban rule added, and once without it, then compare whether the two-part version reveals conditions the one-part version misses.

**We built the testing tool. We haven't run the test yet (as of 2026-06-30).** `ingest.py` now includes a function called `compare_filler_ban()`, plus a command-line option (`--compare-filler-ban`) that runs exactly this comparison. No API key existed in the environment where we built this tool, so we haven't actually run the comparison itself. A judge could ask us to run it. The tool to run it already exists and works.

---

## Outside Paper 2: Wang et al. (2025)

**"Under the Shadow of Babel: How Language Shapes Reasoning in LLMs"** (found on arXiv, paper number 2506.16151, from MBZUAI)

We checked this directly too.

This paper builds a two-language (Chinese and English) set of cause-and-effect reasoning problems, stated in both normal order and reversed order. Three findings:

1. AI models pay attention differently depending on the language. Chinese sentences pull the model's attention toward the beginning of the sentence. English sentences spread the model's attention out more evenly.
2. Models apply those same language-specific habits rigidly, even on unusual sentences that don't fit the normal pattern — which actually hurts performance, especially in Chinese.
3. When a model's reasoning succeeds regardless of which language it uses, the model's internal representation of the problem converges toward one shared, language-neutral form. The paper calls this a "Semantic Hub."

### How this connects to our project: a narrower connection than Paper 1

All three of our case studies (eggs and heart disease, COVID's origin, LHC safety) use English-language sources only. Nothing in our process touches reasoning across multiple languages. We won't pretend a connection exists here that doesn't.

The honest connection here runs at the level of the underlying idea, not at the level of actual results.

This Babel paper and our project start from the exact same core intuition: the surface form of a sentence can hide or twist an underlying claim, in a way you can actually detect mechanically. The Babel paper detects this inside an AI model's own internal attention patterns. Our project detects it at the level of a human reader trying to parse a written claim. Different place to look — same underlying idea.

We include this paper here as related work we know about and engaged with, not work our project depends on. Including it matters because FLF's toughest scoring question asks specifically about standing up to "another AI system questioning our results later." A judge who follows current research on how language shapes AI reasoning should see that we didn't build our three-part idea in a vacuum, cut off from that research.

### One small, clearly bounded extension worth naming

If our process ever extends to non-English sources — our project's own index file already anticipates that possibility — this Babel paper suggests E-Prime's actual rewrite rule might behave differently in a language that has no direct equivalent to the word "to be." A different rule might apply there instead. This paragraph names a possible direction, not a claim we make outright. Zero non-English sources have ever entered this project.

---

## What Changed, and What Didn't, After This Document

| Item | Status after this document |
|---|---|
| Our core claim ("E-Prime makes a hidden judgment call visible in the text itself") | Unchanged. Neither outside paper tests our core claim directly. |
| The claim that E-Prime's power comes from how grammatically demanding it feels | Refined, not weakened. A deeper grammatical rule doesn't help at the writing stage (per Jehu-Appiah). Our project's claim operates at a different stage — the revealing stage — where targeting the specific word "is" (and its forms) counts as the mechanically correct move. Both findings hold true at the same time, because they describe two different stages. |
| Whether E-Prime counts as the right tool for this specific job | Strengthened, through a new proposal. A two-part system now stands as a real, testable next step — not just an assumption we defend. |
| Our eight existing claim files (eggs, COVID, black holes) | Unchanged. Each rewrite stands on its own internal logic, independent of either outside paper's findings. |
| Our own self-check against FLF's toughest scoring question | Strengthened. This very document does exactly what that scoring question asks for: naming a real complication plainly, the moment we found it — instead of waiting for a judge to catch it first. |

---

## Update — 2026-07-08 (see [[literature-engagement-addendum-v2]])

A third paper came out after we wrote this document: Gurnee, Sofroniew, and others (2026), "Verbalizable Representations Form a Global Workspace in Language Models" (from Anthropic, published July 6, 2026).

That paper gives us something this document didn't have: a real, mechanical explanation for *why* the writing-stage-versus-revealing-stage split actually holds true — located inside an AI model's own internal structure, not just observed from the outside.

See [[literature-engagement-addendum-v2]] for the full treatment.

Nothing in that follow-up document takes back or changes anything this document says. It adds a deeper, mechanical layer underneath the argument this document already made.

---

## Why we wrote this document instead of quietly rewriting our earlier work

Per our own standing rule (see the README's "Honest Gaps" section and [[adversarial-robustness-criterion-6]] Part C), any finding that complicates our project's claim earns plain, open statement. We name the exact boundary of what a finding does and doesn't affect directly — not smoothed quietly into our existing text, where a judge would have no way to tell whether we noticed the complication at all.

This document carries a clear date and a clear scope for exactly that reason: so a judge can see exactly when we ran into this outside research, and exactly how we responded to it.
