---
title: Fallacy-Screen Layer
type: synthesis
status: active — wired into ingest.py as screen_claim(), run for real against all twelve claims (see fallacy-screen-worked-examples-v1.md)
vault: TRC
date: 2026-07-17
tags: [resilience]
---

# Fallacy-Screen — A Proposed New Step for Catching Bad Arguments

## Why this file exists

[[two-layer-architecture-v1]] already catches one kind of problem well: a sentence that hides an assumption behind a word like "is." It doesn't catch a second kind of problem: a sentence that hides a broken argument behind smooth, correct-sounding writing. An AI system can write a bad argument — a rushed conclusion, a fake cause, an argument that just repeats itself — with the exact same confident tone it uses for a good one. Nothing in our current process checks for this.

This matters most when an AI system writes or picks the source material we feed into our process, or when an AI system writes our own rewrite and check steps. A person can make a bad argument too, and our [[adversarial-robustness-criterion-6]] file already covers three ways a person might try to game our method. This file names a different problem: an AI writing a bad argument, on either side of our process.

## Where this step goes, and why

This step goes fourth in line, after three steps that already exist:

**Cut filler words (while writing)** → **Rewrite in E-Prime (the check-hidden-assumptions step)** → **Fallacy-Screen (this step)** → **Check for gaps and misuse (the last step)**

This order follows a clear reason. Cutting filler words happens while the AI writes — it changes how the AI reasons in the moment. Rewriting in E-Prime happens after the AI finishes writing — it works on the finished sentence, forcing out anything hidden. Two different moments: one happens during thinking, one happens after.

Fallacy-Screen comes right after the E-Prime rewrite, for two reasons. First, it needs the rewritten sentence, not the raw one — a bad argument shows up more clearly once a sentence already says what it rests on. Second, cutting filler words and rewriting in E-Prime both leave one question untouched: does the argument actually hold up? Fallacy-Screen asks that question, using the cleanest version of the text available.

The last step — checking for gaps and misuse — comes after Fallacy-Screen, because that step assumes the argument already holds up logically. Flagging a gap in an argument that fails on its own terms wastes the flag.

## Two places this step needs to run

**On the way in.** Before any AI-written or AI-picked source material enters our process — a model-written summary, an AI-filtered search result, an AI-written FAQ — we check it for bad arguments. This step names the fallacy in the source's actual argument, not in its wording (that job belongs to a different, earlier step). Skip this check, and a bad argument in the source sails straight through our rewrite step untouched. The rewrite exposes hidden assumptions. It doesn't fix a broken argument.

**On the way out.** We also run this check on our own rewrite and our own check-step writing, once we produce it. An AI can accidentally write a bad argument while explaining a claim — for example, treating "the rewrite exposed assumption X" as proof that the underlying science holds up, which jumps from one small observation about wording straight to a big scientific conclusion it doesn't support. Skip this check, and our own writing could carry the exact problem this whole project argues against.

## The list of bad-argument types we check for

A working list, split into four groups by the kind of gap each one hides.

### Broken structure

- **Circular argument** — the conclusion just restates the starting assumption in different words
- **False choice** — presenting two options as the only options, when more exist
- **Part-to-whole mixup** — assuming something true of the parts must hold true for the whole, or the other way around
- **Word-shift** — a key word quietly changes meaning partway through the argument
- **Non sequitur** — the conclusion doesn't actually follow from the stated reasons, even if each reason sounds true on its own

### Bad use of data

- **False cause** — treating "these two things happened together" as "one caused the other"
- **Rushed conclusion** — treating one small or unusual case as proof of a general rule
- **Survivorship bias** — looking only at the successes and ignoring the failures that never made it into view
- **Ignoring the base rate** — letting one vivid example override what usually actually happens
- **Texas sharpshooter** — spotting a pattern after the fact, then acting like someone predicted it in advance
- **Gambler's fallacy** — believing a string of past, unrelated outcomes changes the odds of the next one
- **Double-counting** — treating two conclusions that share one common premise as if they independently confirm each other. This one differs from the other twenty-five: it already exists as a recognized idea in probability and evidence reasoning (sometimes called "non-independent evidence," or "don't double-count your evidence"). It just sat outside the classical, Latin-named fallacy tradition the other twenty-five categories draw from. We hadn't included it until [[fallacy-screen-worked-examples-v1]] found the gap in real material.

### Persuasion instead of evidence

- **Appeal to authority** — using someone's status or title in place of actual evidence (see the important caveat below)
- **Personal attack** — attacking the source's character instead of answering their argument
- **Origin attack** — dismissing a claim because of where it came from, instead of checking whether it holds up now
- **Straw man** — restating someone's position as weaker than it really is, then knocking down that weaker version
- **Red herring** — bringing up something irrelevant to pull attention away from the real question
- **Bandwagon** — treating a claim's popularity as proof of its truth
- **Tu quoque** ("you too") — pointing out someone's own inconsistency instead of answering their point

### Shifting the boundaries

- **Slippery slope** — claiming one small step guarantees a long chain of bad outcomes, without showing how each step actually leads to the next
- **No true Scotsman** — quietly narrowing a definition the moment someone brings up a counterexample
- **Motte-and-bailey** — making a bold claim, retreating to a safer, smaller claim when challenged, then quietly going back to the bold claim once the challenge passes
- **Appeal to nature** — treating "natural" as the same thing as "safe" or "good"
- **Sunk cost** — basing a decision on how much you've already invested, instead of what makes sense going forward
- **False equivalence** — treating two things as basically the same because they share one surface trait, while ignoring the ways that actually matter
- **Appeal to ignorance** — treating "nobody has disproven this" as the same as proof of truth (or the reverse)

This list stays open. We should add new types as we actually find them in practice, the same way the rest of this project grew its ideas from real examples, not from a list decided ahead of time.

### An important caveat: appeal to authority

Academic papers and official sources cite experts constantly. Doing so counts as normal, legitimate practice — a study citing earlier trial data, a debate judge's professional background, CERN citing its own physics consensus. None of that, on its own, counts as this fallacy. The fallacy only applies to one specific move: using someone's status in place of evidence, not alongside it. We only flag this fallacy where an argument leans on who said something instead of what they actually showed, or where a conclusion shows up with no supporting evidence anywhere nearby — not just summarized briefly, but genuinely missing. A cited expert view backed by real studies stays outside this category completely. The same view, asserted only by title or credential with nothing behind it, falls inside it. This distinction matters most for our own three case studies: the eggs study relies on cited research, the COVID debate relies on credentialed judges, and CERN's page relies on institutional physics consensus. This check exists to catch someone sneaking in false authority — not to flag normal, well-sourced citation as broken.

## What each check must include

**Name it and point to it.** Name the specific type of bad argument, and point to the exact sentence carrying it. "Something feels off" doesn't count as a finding.

**Say so when you find nothing.** If a check finds no bad argument, say that explicitly. Silence doesn't count as a clean result.

**Say which way it pushes.** State whether the bad argument makes the original claim look more convincing than it should, or makes a rebuttal of that claim look more convincing than it should. Those two directions matter differently, the same way our existing adversarial-robustness check already treats them differently for other kinds of problems.

**Say which group it belongs to.** Note which of the four groups above the bad argument falls under, so the whole list stays easy to sort as it grows past today's twenty-six entries.

## How this step fits with our other steps

This step differs from our last step (checking for gaps and misuse). That step asks what a rewrite leaves unclear, and how someone could misuse it. This step asks something earlier and more basic: does the argument even hold together, regardless of what stays unclear or how someone might misuse it? A claim can pass every gap-check and misuse-check we already run, and still rest on a circular argument or a false choice underneath.

This step also builds on [[adversarial-robustness-criterion-6]], instead of repeating it. That file already names three ways a person might try to game our method. This step names a fourth way, specific to AI writing: an AI system built to sound fluent and confident can produce a broken argument that reads as more convincing and more finished than the same broken argument written by a person — because sounding good and holding up logically come from two completely different things.

## What this step gives us

The same kind of gain our rewrite/check split already gave us, now applied to a list roughly three times bigger than where we started. Instead of one big, unanswerable question — "did this AI-written or AI-processed passage sneak in a broken argument?" — we get a fixed set of small, checkable yes-or-no questions: one per type of bad argument, across four groups, checked on both the source material and our own writing, each one naming exactly where it shows up, which way it pushes, and which group it belongs to.

This step also gets better as AI models get better, without us needing to change anything about the list or the rules. A stronger model catches subtler examples of each bad-argument type automatically — the same way a better model improves any rule-based check like this one, without the check itself needing to grow more complicated.

## Where this stands, honestly

This file laid out the shape, the placement, and the rules for this step first, before running it on anything. We have since run it for real against all twelve claims in this project — first against one claim per case ([[eggs-003]], [[covid-003]], [[blackhole-002]]), then against the remaining nine the same day — see [[fallacy-screen-worked-examples-v1]] for the actual results. `ingest.py` now runs this step as a third, separate, callable function (`screen_claim()`), the same way it already runs the rewrite step and the check step separately.

This idea also had one limit worth naming plainly before we ever tested it: a fixed list only catches the types of bad argument it names, and an AI system (or a source) could still write a broken argument some uncatalogued way nobody thought to list. That limit turned out real, not hypothetical: the very first real run of this check, against [[blackhole-002]], found exactly this — an argument pattern (double-counting, an already-recognized idea in probability reasoning that our original list simply hadn't included) that didn't cleanly match any of the twenty-five categories we started with. We added it as a twenty-sixth. This doesn't close the underlying limit, and it doesn't mean we discovered a brand-new fallacy nobody had named before — it means our list, built from the classical fallacy tradition, had a real gap that a different, adjacent tradition (evidence and probability reasoning) already covers. A twenty-seventh, genuinely uncatalogued form could still slip past today's list the same way this one slipped past yesterday's. We name that plainly here instead of treating one successful catch as proof the list now covers everything.
