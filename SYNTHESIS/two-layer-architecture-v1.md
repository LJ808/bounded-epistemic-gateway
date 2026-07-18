---
title: Two-Layer Architecture
type: synthesis
status: active
vault: TRC
date: 2026-06-30
tags: [resilience]
---

# The Rewrite Step and the Check Step — How They Work, and the Rules Each One Follows

## Why this file exists

FLF reviewer Oly Sourbut looked at our first eight claim files and found a real problem: each one mixed the mechanical E-Prime rewrite together with the deeper checking work, all in one continuous block of writing. He called this "rhetoric linting" — no clear split, no separate checking step. This file fixes that. It names two clear steps and states exactly what rules each step must follow, so the split becomes real structure, not just a new label on the same old thing.

## The two steps

**Step one: the Rewrite.** Takes the source's exact original wording and produces an E-Prime rewrite. Purely mechanical — no claim about what the rewrite means, no flagged confusion, no argument about how someone might misuse it. We can check this step against exactly one rule: does the rewrite remove every form of the word "to be," while keeping the source's actual meaning intact?

**Step two: the Check.** Takes the rewrite from step one as its only input, and runs three separate checks against it. Every claim file now states these three checks explicitly, so anyone — not just the person who wrote it — can verify the check against the rewrite without redoing the work from scratch.

## The three rules for step two, the Check

**Name what got hidden.** This part must name the exact word or phrase the E-Prime rule forced out of the original sentence, then say plainly what that word hid — a missing number, a missing mechanism, a missing direction of cause and effect. A real answer here names the specific thing that got hidden. It doesn't just wave at "more nuance" in general.

**Name what stays unclear.** This part must state what neither the original source nor the rewrite actually settles — not something the rewrite itself left vague, but a real gap that survives even after the rewrite. If the rewrite itself already answers something, it doesn't belong in this section.

**Show both sides of misuse.** This part must give two readings, not one: how a reader who wants to reject the claim could misuse the rewrite, and how a reader who wants to accept the claim could misuse the rewrite. Giving only one side fails this rule.

## What this actually gives us

Splitting these two steps turns one impossible-to-answer question — "did the rhetoric-linting work happen correctly?" (the old, mixed-together version asked a reader to judge one big, undifferentiated paragraph) — into three separate questions anyone can actually check: does the first part name a specific hidden item? Does each unclear-gap flag actually survive the rewrite? Does the misuse section cover both directions? Checking the quality of one claim now comes down to four clear yes-or-no answers (the three Check-step rules, plus the rewrite-quality check) — not one big, subjective judgment call. Across all eight claims, that means thirty-two total yes-or-no answers to check, not eight enormous subjective calls.

This also confirms exactly what Oly suggested. The real contribution this project makes sits in the Check step, not equally across the whole submission. FLF's own competition names three separate layers — ingestion, structure, and assessment — and under that framework, our Rewrite step (their "ingestion") counts as ordinary, expected groundwork. Any careful E-Prime rewrite would do the same job. Our Check step — the checkable, rule-bound work of naming what got hidden, what stays unclear, and how someone could misuse the claim — carries the actual, real contribution this submission makes.

## Real code, not just a heading in a document

`ingest.py` now runs these two steps as two separate functions, and you can call each one on its own. `ingest_claim()` returns only the rewrite. `assess_claim()` takes that rewrite as its required input, and refuses to run at all without it. The command line even lets you run `--ingest-only`, to show the rewrite step running completely by itself. This makes the split a real property of the actual code — not just a writing convention we layered on top of one messy process.

## Where we've applied this

All eight claim files (three eggs claims, three COVID claims, two black-hole claims), as of June 30, 2026. Each claim file also carries a "Related Claims" section. That section sits outside both steps entirely — it holds cross-reference links between claims, not rewrite work or check work.
