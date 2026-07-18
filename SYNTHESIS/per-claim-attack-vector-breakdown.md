---
synthesis_type: reader_side_attack_vector_breakdown
framework: e_prime_defense_against_motivated_misreading
claims_covered: 8
companion_to: adversarial-robustness-criterion-6.md
date_executed: "2026-06-17"
tags: [resilience]
---
# Every Claim, Checked Against All Ten Ways a Reader Could Misread It
## The Detailed Version of Part A in Our Toughest Test

`adversarial-robustness-criterion-6.md` gives the short version of our ten-check pattern and promises this file as the detailed version. Here it is: for each of our eight claims, which of the ten checks actually apply, and how that claim's own rewrite already handles each one. We quote each claim file's own write-up directly, rather than making up new analysis here.

Not every check applies with equal force to every claim. Where a check doesn't really apply to a given claim, we say so plainly, instead of padding the list to look complete.

A quick note on abbreviations: RR means "risk ratio" (how much more or less likely something happens in one group versus another). HR means "hazard ratio" (a similar idea, used for risk over time). CI means "confidence interval" (the range the true number probably falls in — a wide range means less certainty).

The ten checks, using the same plain names from our toughest-test file:

1. Turning "happened together" into "caused it"
2. Cherry-picking the number, dropping the uncertainty
3. Hiding a judgment call inside a small word
4. Citing a result without saying how researchers got it
5. Mixing up which assumption actually does the work
6. Not knowing who actually took part in the study (flagged, not solved)
7. Too few people to trust the result (flagged, not solved)
8. Studies nobody ever ran (flagged, not solved)
9. A claim resting on an unsettled theory (flagged, not solved)
10. Leaving out where information came from (flagged, not solved)

---

## eggs-001 (the Li 2013 combined study)

**Checks this claim passes strongly:**
- **#2, cherry-picking the number.** Our rewrite forces both risk ratios into the same sentence: 1.19 (range 1.02–1.38) and 1.68 (range 1.41–2.00). Nobody can quote just the headline number and drop the range — the sentence itself won't allow it.
- **#3, hiding a judgment call.** The phrase "there is a dose-response positive association" collapses into one specific combined number. The rewrite forces the actual size of the effect into view, which the word "is" let a reader skip past.

**Checks this claim flags, but can't fully solve:**
- **#1, turning correlation into causation.** The claim file's own notes on unresolved questions say this directly: the word "association" leaves the direction of cause and effect unanswered. Our rewrite can't determine whether eating eggs causes heart risk, or whether some other factor causes both. It only stops the original wording from implying causation for free.
- **#10, leaving out where information came from.** The claim file's own notes on possible misuse point out that this combined study never adjusted for the same factors eggs-002 did, so comparing the two directly doesn't fully work. Our rewrite names this gap instead of letting the word "association" imply the two studies compare cleanly.

**Doesn't really apply here:** #5 (this claim involves no hidden technical assumption of that kind) and #9 (this claim doesn't rest on any unsettled theory).

---

## eggs-002 (the Zhong/Drouin-Chartier 2020 study)

**Checks this claim passes strongly:**
- **#3, hiding a judgment call.** "Was not associated" sounds like a stable, settled fact. Our rewrite forces the sentence to name the actual method (adjusting for lifestyle and diet) that produced that "no link found" result — the claim file's central move.
- **#4, citing a result without saying how researchers got it.** Our rewrite ties the "no link found" result directly to "adjustment for lifestyle and dietary factors." Nobody can quote "not associated" as if it held true regardless of which method the researchers used.

**Checks this claim flags, but can't fully solve:**
- **#6 and #10, not knowing who took part, and missing source detail.** The claim file's own notes on unresolved questions say plainly: the source never states whether it treated BMI and statin use as things that caused the confusion, or as things that sat in the causal chain itself. Our rewrite can't supply that missing methodological detail. It only makes the gap visible as an open question.
- **#1, a source-side version of turning correlation into causation.** The claim file's own notes on possible misuse state this directly: someone who wants eggs to look safe could pick an adjustment method that quietly removes a real signal by treating a real cause as a confusing factor instead. "Nothing in this source rules that out." This shows the claim file naming its own weak spot — not claiming a clean win.

**Doesn't really apply here:** #2 (nobody has reason to selectively quote this result's range — the result itself came up null) and #5, #9.

---

## eggs-003 (the Díez-Espino/PREDIMED 2017 study)

**Checks this claim passes strongly:**
- **#3, hiding a judgment call.** This gives our single clearest example in this whole project. "No evidence of interaction" forces open into two real numbers: a hazard ratio of 1.33 (range 0.72–2.46) versus 0.96 (range 0.33–2.76) — a 38 percentage-point gap sitting underneath two wide, overlapping ranges. The claim file itself rates this rewrite as high-confidence, for exactly this reason.
- **#7, too few people to trust the result.** Named directly. The claim file's own analysis states that "no evidence of interaction" actually means "not enough people in this group to detect an interaction," not "we detected a true absence of one." We flag this. We can't manufacture statistical power the original study never had.

**Checks this claim flags, but can't fully solve:**
- **#8, studies nobody ever ran.** The claim file notes that the real uncertainty lives entirely in the source's own plain-language conclusion. Only a bigger, properly sized follow-up study would actually settle this question. Our rewrite makes the gap visible. It doesn't close it.

**Doesn't really apply here:** #1 (this claim asks about one subgroup's response, not about cause and effect in general), #2 (the range already sits inside the rewrite, not selectively dropped), #4, #5, #9, #10.

---

## covid-001 (Peter's argument about timing)

**Checks this claim passes strongly:**
- **#3, hiding a judgment call.** "Seems epidemiologically impossible" forces open into "implies 256 times more cases than we actually saw." The claim file notes this new version "can't carry the same confident tone" once the assumption underneath it has to show up in the same sentence.
- **#4, citing a result without saying how researchers got it.** Our rewrite ties the whole argument to one specific, named assumption: a case count that doubles every 3.5 days — an assumption the original buried inside the word "seems."

**Checks this claim flags, but can't fully solve:**
- **#6, a version involving unclear detection rates.** The claim file's own analysis traces a real tension: elsewhere in the same debate, the transcript implies the actual detection rate changed over time (after wet-market testing began on December 30), which this argument's math never accounts for. Our rewrite surfaces this as an open question. Per the claim file's own notes on possible misuse: "neither side, in the actual transcript, runs this calculation explicitly" — the gap stays open, not closed.
- **#10, missing source detail.** The claim file states this plainly: "the argument's whole force depends on a constant detection rate — an assumption Peter never states and never defends."

**Doesn't really apply here:** #2, #5, #9.

---

## covid-002 (Saar's argument about Mr. Chen)

**Checks this claim passes strongly:**
- **#3, hiding a judgment call.** "This means" forces open into an explicit "if this holds, then that follows" chain, per the claim file's own analysis. This gives the cleanest single example of this particular check anywhere in the COVID case — rated high-confidence in the claim file itself.
- **#10, missing source detail.** Our rewrite names, directly, "the accuracy of one newspaper interview as the only source for this person's symptom-onset date" — exactly the single point where the whole argument could fail, which the claim file says the rewrite exists specifically to expose.

**A genuine reversal worth naming directly:** the claim file's own notes on possible misuse state that this rewrite actually makes the claim more exposed to scrutiny, not less — useful for someone evaluating the claim, a real problem for someone trying to defend it in a debate. Worth naming here because it gives a real example of E-Prime working against the claim-holder's own interest — stronger proof of fairness than a method that only ever makes claims look stronger.

**Doesn't really apply here:** #1, #2, #4, #5, #6, #7, #8, #9 — this claim comes down to one single question of source reliability, not many different checks, and the claim file's own notes on unresolved questions say plainly: "none remaining after the rewrite."

---

## covid-003 (Peter's argument about a specific genetic feature)

**Checks this claim passes strongly:**
- **#3, hiding a judgment call, with an extra twist.** "Is a mess" and "expected to work poorly" force open into a question about what scientists could have known and when. The claim file's own analysis finds something beyond the usual pattern here: a careless, shortened version of this claim ("shows signs of artificial insertion") doesn't just compress the original — it flips which side of the debate the evidence actually supports. This gives our strongest single example of a summary doing more than losing nuance — it catches a summary getting the direction of the evidence backwards.
- **#9, a claim resting on an unsettled question.** Our rewrite ties the claim to "computational modeling that happened after COVID already existed," explicitly dating the evidence relative to the event itself. The claim file's own notes on possible misuse use this dating to frame the real open question: does a method existing after the fact tell us anything about what scientists could have done before it existed?

**Flagged, not solved:**
- **#8, studies nobody ever ran.** The real open question itself — whether a post-2019 computational result tells us anything about pre-2019 engineering knowledge — stays explicitly unresolved, per the claim file's own tag marking it as a key open question.

**Doesn't really apply here:** #1, #2, #4, #5, #6, #7, #10.

---

## blackhole-001 (CERN's FAQ, comparing to cosmic rays)

**Checks this claim passes strongly:**
- **#5, mixing up which assumption actually does the work.** This gives our defining example of this exact problem. The claim file's own analysis finds that "cosmic rays already hit Earth with similar energy" doesn't automatically mean "cosmic rays hit Earth in the same physical setup as the LHC's collisions." A fast particle hitting a stationary target doesn't automatically match two fast particles colliding head-on. The phrase "this already happens naturally" sounding completely safe combines two problems at once: a hidden judgment call (check #3) sitting on top of a hidden technical assumption (check #5). The claim file treats this as the first real, confirmed example of the "boundary" kind of hidden assumption our other big project file predicted in advance.

**Flagged, not solved:**
- **#8, studies nobody ever ran.** The claim file states plainly that CERN's fuller, full-length safety report likely addresses this exact collision-setup question, but "nothing in this FAQ text closes that gap" — and we never actually worked through that fuller report in this project.

**Doesn't really apply here:** #1, #2, #4, #6, #7, #9, #10.

---

## blackhole-002 (CERN's FAQ, the safety argument itself)

**Checks this claim passes strongly:**
- **#4, citing a result without saying how researchers got it.** This gives the claim file's central finding. The prediction that black holes could form, and the prediction that they'd instantly evaporate, both come from the exact same underlying physics theory — even though the original FAQ presents them as two separate, independent safety arguments. Our rewrite forces that shared root into a single sentence, which makes it impossible to describe the two arguments as independent without the sentence visibly contradicting itself.

**Flagged, not solved, with a real twist worth stating honestly:**
- **#8 and #9, studies nobody ran, and an unsettled theory.** The claim file's own notes on unresolved questions state that settling which argument actually carries the real safety weight — CERN's "same theory predicts both" point, or a separate check against real astronomical objects — would require reading CERN's full 2008 technical report directly, something we haven't done in this project. Notably, the claim file's own analysis goes further, and offers a tentative answer: the real safety weight probably sits with that separate astronomical check, not with the "same theory" argument — while explicitly flagging this as our predicted "boundary" kind of hidden assumption turning into a "single-link-in-a-chain" kind, on closer look. A real, testable claim we admit we haven't fully settled, not a finished result dressed up as one.

**Doesn't really apply here:** #1, #2, #6, #7, #10.

---

## The Pattern Across All Eight Claims

| Check | Shows up strongly in | Only flagged (not solved) in |
|---|---|---|
| #1 Turning correlation into causation | — | eggs-001, eggs-002 |
| #2 Cherry-picking the number | eggs-001 | — |
| #3 Hiding a judgment call | all eight claims, in some form | — |
| #4 Citing a result with no context | eggs-002, covid-001, blackhole-002 | — |
| #5 Mixing up the hidden assumption | blackhole-001 | — |
| #6 Not knowing who took part | — | eggs-002, covid-001 |
| #7 Too few people | eggs-003 | — |
| #8 Studies nobody ran | — | eggs-003, covid-003, blackhole-001, blackhole-002 |
| #9 Resting on an unsettled theory | covid-003 | blackhole-002 |
| #10 Missing source detail | covid-002 | eggs-001, eggs-002, covid-001 |

**An honest observation, stated plainly:** check #3 (hiding a judgment call) shows up in every single claim. That makes sense — it names the exact thing E-Prime targets by design. The other nine checks spread out unevenly across our eight claims. No single claim triggers all ten checks, and a few checks (#5 and #7 especially) only show up strongly in one claim each. This points to a real limit of an eight-claim, three-case project: covering more checks trades off against digging deep on any one claim. A bigger project would let each check get tested against more than one or two claims — which would matter most for checks #5 and #7, where our current evidence rests on a single example each.
