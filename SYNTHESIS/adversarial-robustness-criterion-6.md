---
synthesis_type: adversarial_robustness_test
framework: e_prime_defense_against_motivated_misreading_and_source_gaming
claims_tested: 8
attack_vectors: reader_side_10_per_claim_plus_source_side_per_case
date_executed: "2026-06-17"
tags: [resilience]
---
# Our Toughest Test — FLF's Criterion 6
## Can Someone Trick Our Method, Either as a Reader or as the Original Source?

FLF's exact wording for this test: "How well do the artefacts and methodology hold up when participants and consumers have differing views and priorities? Outputs withstand motivated reading and downstream-model interrogation. The methodology resists being gamed by sources optimizing to mislead. Failure modes and uncertainties are named and bounded, not hidden."

In plain words: can a reader twist our claims to mean what they want them to mean? And separately, can whoever wrote the original source material trick our method from the very start, before any reader even sees it?

This file tests **two separate kinds of trickery**, because the actual criterion asks about both:

1. **A reader tricking themselves.** Someone reads one of our claims and picks only the parts that support what they already wanted to believe.
2. **A source tricking everyone from the start.** The person or group who wrote the original study, debate, or official statement built it, on purpose, to mislead — before we ever touched it.

A method that only stops the first kind of trickery leaves half the test unanswered. Most of our earlier work covered only the first kind. This file adds the second.

---

## Part A: Can a Reader Trick Themselves?

[Full detail on all eight claims lives in a separate file, linked below. The short version follows here.]

### What we found

**Five ways E-Prime stops a reader cold — the reader has to add new words to twist the meaning:**

1. **Turning "happened together" into "caused it."** We replace "is associated with" with "correlates with." This blocks someone from quietly upgrading a correlation into a cause.
2. **Cherry-picking the number, dropping the uncertainty.** We put the main number and its uncertainty range in the same sentence. Dropping one now takes a visible, deliberate edit.
3. **Hiding a judgment call inside a small word.** Words like "is," "seems," and "means" let a writer skip past a judgment call. We replace them with wording that forces the judgment call into view.
4. **Citing a result without saying how researchers got it.** We tie every claim to the actual study design behind it — how many people, what kind of study. This blocks quoting a result with no context.
5. **Mixing up which assumption actually does the work.** Some claims quietly rest on one specific assumption out of several possible ones. We name that assumption directly instead of letting it hide.

**Five things E-Prime makes visible but can't fully fix — it flags the gap instead of closing it:**

6. **Not knowing who actually took part in the study.** We can't invent missing details about who took part in a study. But we do flag the open question: who actually took part?
7. **Too few people to trust the result.** We can't shrink a wide uncertainty range. But we do put the actual numbers in the sentence, so a wide range stays visible instead of getting summarized away.
8. **Studies nobody ever ran.** We can't produce research nobody ran. But we refuse to write around that gap as if it doesn't exist.
9. **A claim resting on an unsettled theory.** We can't judge whether a theory holds up. But we do expose that the claim depends on it.
10. **Leaving out where information came from.** We treat that omission as a choice worth naming, not an innocent shortcut.

Full detail on all eight claims (three eggs, three covid, two black-hole) lives in [`per-claim-attack-vector-breakdown.md`](per-claim-attack-vector-breakdown.md). This pattern holds across all three, very different kinds of case.

---

## Part B: Can the Original Source Trick Everyone From the Start?

Part A never tested this. The real question: when the person who wrote the original study, debate argument, or official statement builds it on purpose to mislead, does our method catch that — or does it just copy the trick into cleaner-sounding sentences?

### Test 1: Picking a Study Group to Get the Answer You Want (Eggs Case)

**The trick:** Someone funds a study on a small group of people chosen in advance to produce the answer they want — say, people who already have egg allergies or inflammation. They then publish "Our group showed more inflammation on an egg-heavy diet," without saying how they picked that group.

**Does our method catch this?**

No, not on its own, and we should say that plainly instead of softening it. Our method forces the sentence to become "Our group of X people showed a Y increase in this inflammation marker" — more specific than the original, but it still can't reveal how the group got picked if the source itself never says. Our rewrite can only force visibility of what someone actually wrote down. It can't produce information nobody wrote down in the first place.

**What our method does instead:** It makes the missing question impossible to ignore. Once a sentence has to name a specific group size and a specific outcome, a reader immediately sees the gap: "X people — but who actually made up that group?" Our method turns that gap into a clearly named open question, instead of letting "our group" pass as good enough on its own.

**Bottom line:** Our method turns this kind of trickery from invisible into flagged-but-unsolved. That counts as real progress, and also as a real, honest limit — not a full solution. One of our own actual claims proves this happens in practice, not just in theory: our second eggs claim already names this exact gap in its own write-up — "a source that wants eggs to look safe could pick an adjustment method that quietly removes the real signal. Nothing in this source rules that out." Our method caught its own blind spot on a real claim, unprompted.

### Test 2: Choosing Words That Sound More Certain Than They Should (COVID Case)

**The trick:** Someone in a debate picks a phrase — like "epidemiologically impossible" — built to sound more rigorous than the actual math behind it. They know confident-sounding language convinces people, whether or not the evidence backs it up.

**Does our method catch this?**

Mostly yes, and more successfully than Test 1. The original claim — "it seems epidemiologically impossible" — sounds exactly like the kind of confident phrase a debater picks on purpose. Our rewrite ("assuming a case count that doubles every 3.5 days, a November 11 start implies 256 times more cases than we actually saw") loses that same confident tone, because now it has to state its assumption out loud. Once the assumption has to sit right next to the conclusion, a debater loses the option of hiding it.

**Bottom line:** This gives the strongest result in this whole project for catching a source trying to mislead. The trick specifically depended on hiding an assumption inside confident wording. Our method structurally blocks exactly that move. Our own first COVID claim's write-up already found this same detection-rate assumption on its own, before we ran this test.

### Test 3: An Institution Reassuring the Public While Hiding Real Gaps (Black Holes Case)

**The trick:** An institution facing public worry — CERN, in this case — has a reason to sound reassuring even where its actual argument has real gaps. Public panic costs the institution more than an imperfect safety argument does. A short FAQ format, answering questions briefly and confidently, naturally serves reassurance more than full honesty.

**Does our method catch this?**

This gives the single most useful test in this whole project, because it shows our method working exactly as intended, and it shows exactly where the method's limit sits. Our rewrite of the relevant claim exposes something the original FAQ hides: two reassurances that sound independent ("black holes stay unlikely to form" and "even if they form, they stay safe") actually rest on the exact same underlying physics theory. A reader who trusted "two separate safety arguments" gets corrected into seeing "one argument, said twice."

**What this doesn't catch:** Whether CERN's own reassurance goal shaped which arguments made it into the short public FAQ, versus the full 2008 technical safety report. We already flagged, elsewhere in this project, that we never actually worked through that fuller report. That means the strongest possible test here — comparing the public-facing reassurance against the full technical case — remains untried. Not because our method failed, but because we never fed it the comparison document.

**Bottom line:** Our method correctly catches a source hiding something *within one document* (the false-independence trick above). It cannot yet catch a source leaving something out *across two different documents*, if we never worked through the second one. That counts as a real, named limit — not a failure of the method, but a limit on what we've actually built so far, and we're saying so directly instead of staying quiet about it.

---

## Part C: What This Actually Proves, No Exaggeration

FLF's Criterion 6 asks two separate questions. Our evidence supports different confidence levels for each one.

**"Can a reader twist our claims, or can another AI system poke holes in them later?"** — **Strongly supported.** Part A's ten-check analysis, across eight claims and three very different kinds of case, shows a real, repeated pattern: our method blocks five kinds of reader trickery outright, and flags five more kinds as open gaps instead of hiding them.

**"Can the original source trick our method from the start?"** — **Partly supported, with one clear, named limit.** Test 2 (COVID) shows clear, real resistance. Test 3 (CERN) shows resistance within one document, but a real, unaddressed gap across two different documents. Test 1 (eggs) shows our method turning an invisible trick into a flagged, unsolved question — real value, but short of full resistance.

**The honest summary:** Our method catches hidden problems and forces them into view. It doesn't stop lying outright, and it can't recover information a source chose never to write down. What it reliably does: it makes the exact spot where a hidden trick would have to hide clearly visible, so a missing piece of information becomes its own, obvious red flag instead of smooth, confident-sounding prose. This matches what Part A already found for readers. Now we've confirmed the same holds for sources trying to trick us from the start — with one clear exception: catching a trick that spans two documents we never both fed into our method.

---

## How to Test a New Source

To check whether a new source could trick our method:

1. Ask what the source's likely motive looks like — money, reputation, winning a debate, telling a good story.
2. Ask: what would that motive make the source want to leave out, frame in its own favor, or bury inside confident-sounding language?
3. Run the E-Prime rewrite. Then check: does the missing information now show up as a visible, obvious gap (like Test 1)? Does the confident wording become impossible to keep without naming the assumption it was hiding (like Test 2)? Or does catching the trick require comparing this document against a second document we never worked through (like Test 3)?
4. Write down which pattern applies. Pattern 2 (Test 2's kind) gives the strongest result. Pattern 1 (Test 1's kind) stays real, but only partial. Pattern 3 (Test 3's kind) means our own project's limited scope sets the boundary, not the method itself — and that deserves plain statement as something worth extending, not something to hide.
