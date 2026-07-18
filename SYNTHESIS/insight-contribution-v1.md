---
title: Insight Contribution V1
type: reference
status: active
vault: TRC
date: 2026-06-28
tags: [resilience]
---

# Our Real Insight — Three Kinds of Hidden Assumption

## What this document does

Our first two worked examples (eggs and heart disease, the COVID debate) didn't just prove that rewriting in E-Prime works. Read side by side, they revealed something neither one shows on its own: the kind of hidden problem E-Prime catches changes in a predictable way, depending on what kind of source we're working from. And that change itself tells us what kind of digging a case actually needs.

This document states that finding directly. It tests whether the finding holds up beyond the first two examples. It also names exactly what would prove the finding wrong.

---

## The finding, in plain words

Standard, confident-sounding summaries fail in one specific, repeated way. They squeeze a claim's real dependency — the thing the claim actually rests on — into a small word like "is," which then reads like a fact about the world, instead of a fact about the argument.

"There is an association" reads like a fact about eggs. It actually means: *given this one specific way of adjusting the numbers.*

"This means X happened" reads like solid logic. It actually means: *given that this one source got it right, with nothing else backing it up.*

Rewriting in E-Prime forces every claim like this to name its real dependency, because words like "is an association" and "this means" can't survive the rewrite without naming what stands behind them. That much held true across both of our first two examples. What changed between the two examples: **the kind of dependency each rewrite exposed.**

| Kind of source | What the word "is" was hiding | What the rewrite exposed |
|---|---|---|
| A combined study across many people (the eggs case) | A choice researchers made about which factors to adjust for, and whether those factors actually cause the outcome or just happen alongside it | **A study-design dependency:** the claim holds true *for this specific study's math*, not true *of eggs themselves* |
| A back-and-forth debate (the COVID case) | One single link in a chain of reasoning — one source, one date, one assumption held fixed | **A reasoning-chain dependency:** the claim holds true *only if this one link in the chain actually holds*, and the real fight in the debate happens over that one link |

These don't count as two versions of the same problem. They count as two genuinely different problems that happen to look the same on the surface — both hide behind a word like "is." This counts as the real discovery here: **the surface sign stays the same, even though the actual underlying problem changes completely.** E-Prime works as a detector across very different kinds of sources for exactly this reason — it doesn't care what kind of hidden dependency it finds. It only checks whether a sentence can survive with every form of "is/was/are" removed. But what someone should do *after* finding the hidden dependency looks completely different depending on which kind it turns out to be. In the eggs case, the next move asks a statistics question: did the researchers adjust for the right things? In the COVID case, the next move asks an evidence question: find and attack that one weak link in the chain.

## Why this matters more than just "E-Prime helps writing sound clearer"

Saying "E-Prime forces precision" states something true, but not very surprising — writers have known that clear rules force clearer writing for a very long time. What we actually found, by comparing our two cases side by side, goes further: **the exact same simple mechanical rule works across two completely different kinds of problem without any changes, and what it reveals each time tells you which kind of problem you're actually looking at.**

That matters for a very practical reason. A method that needs a redesign for every new kind of case can't scale, and can't build on itself over time. A method whose actual checking rule stays fixed, while what it reveals adapts automatically to whatever kind of case you feed it, can scale — because adding a third, fourth, or fiftieth kind of case doesn't require rebuilding the rewrite step. It only requires building a growing list of which kind of hidden dependency tends to show up in which kind of case.

## A third prediction, made and written down before we tested it

If this finding holds true, then our third case — black holes and CERN, a topic where almost everyone already agrees on the answer — should reveal a *third* kind of hidden dependency, different from the first two. The prediction follows, written down before we ever ran the actual rewrite:

**Our prediction: a scope dependency.** A settled, agreed-upon claim like "CERN won't create a dangerous black hole" usually hides neither a study-design choice nor a single weak link in a chain. It hides a *boundary* — the claim only holds true within certain limits (how much energy the collision produces, what timescale a certain physics process needs), and the plain-language version drops that boundary silently. "Black holes will disappear before they can cause harm" sounds like a settled fact. Once forced through E-Prime, it needs to say *which* specific physics process makes them disappear, and *under which untested conditions* that claim actually holds — revealing whether the settled consensus rests on stretching known physics past where anyone's actually tested it, rather than on direct proof.

**We wrote this prediction down so it could get proven wrong.** If running the actual rewrite on CERN's material instead produced a study-design dependency or a reasoning-chain dependency, our three-part idea would need a rework — either a fourth category, or proof that our three kinds of case actually collapse into fewer categories than we thought. Either result would teach us something real. This doesn't work as a safe, unfalsifiable guess. We stated exactly what result would prove us wrong, before running the test.

**What actually happened, after we ran it (see [[blackhole-001]] and [[blackhole-002]]):** our prediction held up, with one twist we didn't expect. Both CERN claims did reveal a scope dependency on the first rewrite, exactly as predicted. But digging one level deeper into each scope dependency, we found it actually resolves into a reasoning-chain dependency underneath. [[blackhole-002]]'s safety argument, traced far enough, comes down to whether a separate kind of evidence — real astronomical objects behaving the same way — actually carries the weight, rather than the "same theory predicts both formation and disappearance" argument. This means our three categories might not stay cleanly separate. Look closely enough at a scope dependency, and it can turn into a reasoning-chain dependency, one step below the surface. This raises a real, honestly open question: would a fourth kind of case — a disagreement over values, say, or a pure math dispute — reveal a genuinely new, fourth kind of dependency? Or does everything eventually boil down to the same question: which single link, if it broke, would change the whole conclusion?

## What this idea gives us, going forward

If this idea holds up across all three of FLF's case studies, and ideally beyond them too, this three-part idea itself becomes the real, reusable thing this project produces — more useful than the note-taking structure we built it in. A future investigator, before doing any actual work on a brand-new case, could ask one simple question first: does this dispute look like a combined-study case, a back-and-forth-debate case, or a settled-consensus case? That question alone would help predict where the hidden assumptions probably sit, before reading a single source. That counts as a real, testable claim about how to size up an unfamiliar dispute quickly — closer to what FLF's own "insight contribution" question asks for than anything in our very first draft.

## What we don't claim

- We don't claim these three kinds of hidden dependency cover every possible case. A fourth kind of case — a pure math dispute, say, or a values disagreement dressed up as a factual one — might reveal a completely different, fourth kind.
- We don't claim this idea came from pure theory. It came from two real, executed examples and one prediction we stated and then tested. The prediction held, but with a twist neither original example predicted — a more complicated result than a simple "yes, correct," and worth stating honestly as such instead of smoothing it over.
- We don't claim E-Prime stands as the only possible way to find this pattern. We claim E-Prime works as a cheap, purely mechanical way to trigger this kind of discovery — not necessarily the only one. Whether some other simple rule (banning words like "might" or "could," for instance, or banning certain grammatical structures) would reveal the same three-part pattern faster or more reliably stays untested, and counts as a fair, tough question for a judge to raise.
