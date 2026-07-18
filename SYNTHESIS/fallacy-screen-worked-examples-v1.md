---
title: Fallacy-Screen Worked Examples
type: synthesis
status: active — full run, all twelve claims, all twenty-four checks (source argument + our own write-up per claim)
vault: TRC
date: 2026-07-17
tags: [resilience]
---

# Fallacy-Screen, Run for Real — All Twelve Claims

## Why this file exists

[[fallacy-screen-layer-v1]] proposed a check for broken arguments, but never ran it. [[next-steps-v1]] named that gap as Priority 1: run the check on one real claim per case first, and write down a real result for each — not a hoped-for one. This file did that first, against [[eggs-003]], [[covid-003]], and [[blackhole-002]] — the three highest-stakes claims per case, per [[crux-analysis-v1]]'s own ranking. **Update, 2026-07-17, later same day:** extended to the remaining nine claims, closing the gap [[fallacy-screen-layer-v1]] itself named ("running this check against the remaining six claims... remains the next real step. We haven't taken it yet") — now twelve of twelve, not six of nine, since [[covid-005]] and [[covid-006]] joined the project the same day.

We check two things per claim, per [[fallacy-screen-layer-v1]]'s own rule: the source's own argument, and our own write-up about that source. Both checks appear below for each claim.

---

## eggs-003 (PREDIMED, diabetic subgroup)

**Checking the source's own argument:** the original phrase, "no evidence of interaction by diabetic status," reads as a terse result statement, not a full argument. No fallacy found here — the source doesn't argue anything at length enough to break.

**Checking our own write-up:** here we found something real. Our own Analysis section states, flatly: "no evidence of interaction" actually means "underpowered to detect an interaction," not "detected absence of interaction." That statement reads as settled. But [[crux-analysis-v1]] treats this exact question as open, and names what would actually settle it: a real power calculation, using PREDIMED's actual diabetic-subgroup sample size — a calculation we haven't run.

**Fallacy Identification:** a rushed conclusion. We treated wide, overlapping confidence intervals as proof of "underpowered," without running the specific calculation that would actually establish that.

**Direction of Error:** toward over-confidence in our own claim — we made "underpowered" sound more certain than our own evidence supports.

**Group Tag:** causal and statistical.

**Why this matters:** this stands as the single clearest result from running Fallacy-Screen for real. It caught our own project overclaiming, in a file we wrote weeks ago and never re-checked until now. This validates the whole point of running a fallacy check on our own output, not only on outside sources.

---

## covid-003 (furin cleavage site, knowability argument)

**Checking the source's own argument:** Peter's argument runs: this genetic feature looked unlike anything used before, and virologists expected it to work poorly — so it argues against, not for, artificial origin. One might expect an appeal-to-ignorance shape here (no published pre-2019 study used this sequence, therefore no engineer could have known it would work). Checked carefully: this doesn't hold up as a hidden fallacy, because the claim file's own Adversarial Interpretation section already names the counter-argument directly — engineers might have deliberately chosen an unusual feature specifically to imitate nature. The gap gets named openly as an unresolved crux, not smuggled as a settled conclusion.

**Fallacy Identification:** none found, in the source's argument.

**Checking our own write-up:** our own Analysis section states plainly that a careless paraphrase of this claim flips which side of the debate it actually supports — and our write-up correctly catches that inversion rather than committing it. No fallacy found in our own prose either.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Why this matters:** a clean null result, stated explicitly rather than skipped — exactly what [[fallacy-screen-layer-v1]]'s own rules require. This claim already does real, honest work naming its own open questions, and the Fallacy-Screen check confirms that rather than finding something new.

---

## blackhole-002 (CERN safety argument, evaporation)

**Checking the source's own argument:** CERN's FAQ presents two claims as if they independently support each other — black holes stay unlikely to form, and even if they formed, they'd evaporate too fast to cause harm. Our own claim file's Analysis already catches the core problem: both predictions come from the exact same underlying physics theory, not from two separate facts. Checked against our 25 named categories directly: nothing on our list names this specific move cleanly. The closest fits (false equivalence, non sequitur) don't quite capture it. This argument doesn't equate two different things, and it doesn't reach an invalid conclusion from its stated premises — it counts two conclusions from one shared premise as if they came from two separate premises.

**Fallacy Identification:** a gap in our own list, not a clean match to any of the 25 named categories. We flagged this as a proposed 26th category, **double-counting** — treating two conclusions that share one common premise as if they independently confirm each other. Worth stating plainly: this isn't a fallacy nobody has ever named before. It's a recognized idea in probability and evidence reasoning (often called "non-independent evidence"), just one our original list hadn't included, since that list drew from the classical, Latin-named fallacy tradition rather than from evidence-reasoning terminology.

**Direction of Error:** toward over-confidence in the claim — CERN's safety argument reads as doubly-supported when it actually rests on one single argument, stated twice.

**Group Tag:** closest to causal and statistical, as a near-relative of treating correlated evidence as independent.

**Checking our own write-up:** our own Analysis section already states this tentatively and honestly ("on reflection, the safety-relevant weight likely sits with...") rather than asserting it as settled. No fallacy found in our own prose.

**Why this matters:** this result does exactly what [[fallacy-screen-layer-v1]]'s own honest-gap section predicted before we ever ran a real test: an uncatalogued fallacy form can slip past a fixed list of 25 categories. Running the check for real found precisely that limitation, on the very first attempt, in real material — not a hypothetical worry, but a demonstrated one.

---

## eggs-001 (Li 2013, pooled meta-analysis)

**Checking the source's own argument:** "there is a dose-response positive association between egg consumption and the risk of CVD and diabetes." This states a pooled correlational finding, not an extended argument chain — little structure for a fallacy to hide in. The "dose-response" framing carries a mild risk of sounding more causal than the underlying data supports (dose-response patterns are one of several classical criteria epidemiologists use to argue for causation), but the claim file's own Adversarial Interpretation section already names this directly: "the 'dose-response' framing in the conclusion oversells what a single highest-vs-lowest comparison actually shows." Already surfaced, not smuggled.

**Fallacy Identification:** none found, in the source's argument.

**Checking our own write-up:** the Analysis section states what the claim entails and what would falsify it (a properly adjusted cohort producing a null or reversed estimate), then correctly notes [[eggs-002]] reports exactly that — stated as a description of what eggs-002 reports, not as a claim that eggs-002 has already falsified eggs-001. No fallacy found.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Why this matters:** a clean result on both sides, consistent with covid-003's pattern — the claim file already did honest work naming its own overselling risk before this check ever ran.

---

## eggs-002 (Zhong/Drouin-Chartier 2020, adjusted cohort)

**Checking the source's own argument:** "consumption of at least one egg per day was not associated with incident cardiovascular disease risk after adjustment for updated lifestyle and dietary factors." A conditional null result, correctly scoped to "after adjustment" rather than stated as an unconditional fact. No fallacy found in the source's own sentence.

**Checking our own write-up:** the Analysis section raises a real methodological risk directly — that BMI and statin use might function as mediators rather than confounders, which "would make this null result an artifact of over-adjustment, not evidence of safety." Stated as a conditional ("if... would make"), not asserted as fact. This names a real statistical risk (over-adjustment / conditioning on a mediator) that doesn't map cleanly onto any of the 26 named categories — similar in kind to how [[blackhole-002]]'s "double-counting" sat outside the original 25 before this check surfaced it. Worth naming honestly: over-adjustment bias is a real, recognized methodological concept in causal inference, distinct from double-counting, and this project's list still doesn't include it as a named category. Not added here as a 27th category on the strength of one instance — [[fallacy-screen-layer-v1]]'s own rule requires a real finding before adding a category, and this claim file already states the risk as an open, unresolved conditional rather than asserting the error occurred, so no fallacy actually got committed here to anchor a new category to.

**Fallacy Identification:** none found — the risk is real but already honestly hedged as conditional, not committed.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Why this matters:** a second clean result, and a second reminder (after blackhole-002) that this project's 26-category list may still have gaps — this time one that didn't need adding, because the claim file never asserted the error as fact in the first place.

---

## covid-001 (Peter, epidemiological-impossibility argument)

**Checking the source's own argument:** "it seems epidemiologically impossible for COVID to have been circulating much before... we would expect 256x as much COVID than we actually saw." The word "impossible" claims certainty a probabilistic growth-curve comparison doesn't actually establish — the argument rests on an unstated assumption (constant doubling rate, held backward in time) that the claim file's own Ambiguity Flags already names, but never formally tags as a fallacy type.

**Fallacy Identification:** rushed conclusion — treating a specific growth-rate model, built on an unstated constant-rate assumption, as proof of categorical "impossibility" rather than a probabilistic argument with real but bounded force.

**Direction of Error:** toward over-confidence in the claim — "impossible" oversells what the underlying math shows, in the direction that favors this claim's own zoonotic-timing conclusion.

**Group Tag:** bad use of data.

**Checking our own write-up:** the Analysis section already names both hidden assumptions (constant doubling rate; "observed" meaning detected, not true infections) without overclaiming either — properly hedged. No fallacy found in our own prose.

**Why this matters:** the first genuinely new fallacy tag from this batch, on a claim this project already treats as medium-confidence (`rewrite_confidence: medium`) — the check confirms that lower-confidence rating rather than surfacing a hidden problem never named before.

---

## covid-002 (Saar, Mr. Chen case)

**Checking the source's own argument:** "The only source saying that Mr. Chen got sick early was an anonymous interview... This means that whoever infected him was earlier than the index case." "This means" presents a deduction as automatic, when it depends entirely on one anonymous, unverified source's accuracy — the claim file's own Analysis already names this ("'This means' smuggles a deduction as automatic") but doesn't formally tag it.

**Fallacy Identification:** rushed conclusion — treating one anonymous-source anecdote as sufficient to establish a definitive timing/exposure fact, without the deduction's single point of failure (source reliability) getting acknowledged in the original argument.

**Direction of Error:** toward over-confidence in the claim — presented as settled ("this means") rather than as contingent on an unverified source, in the direction favoring lab-leak-side pre-market-circulation timing.

**Group Tag:** bad use of data.

**Checking our own write-up:** the Analysis section correctly exposes the single point of failure and cites Peter's direct, documented rebuttal (Chen's hospitalization records reportedly show a later onset date). The Ambiguity Flags section states "None remaining after the rewrite" — worth a precise read: this refers to ambiguity in the *argument's logical structure* (fully exposed by the rewrite), not to the underlying factual dispute (Chen's actual onset date), which stays genuinely unresolved in this vault. Not a fallacy, but a phrasing worth reading carefully rather than at face value.

**Why this matters:** a second rushed-conclusion instance, on the same general single-source-anecdote pattern as covid-001's constant-rate assumption — both push toward more certainty than a single data point should support, though in opposite directional favor (covid-001 toward zoonotic timing, covid-002 toward lab-leak timing).

---

## covid-004 (Stansifer, population-distance verdict)

**Checking the source's own argument:** an independent judge's Bayesian verdict, with named uncertainty ranges (Bayes factor 100–1000, narrowing to 10000 under one restricted framing he names himself) rather than a single unhedged number. The claim file's own Ambiguity Flags already surfaces the scope-sensitivity issue directly. Checked against the 26 categories: no clean match — professionally hedged reasoning with named sensitivity isn't the same shape as any of the persuasion-based or boundary-shifting categories, and the underlying calculation isn't presented as more certain than it is.

**Fallacy Identification:** none found, in the source's argument.

**Checking our own write-up:** the Analysis section treats covid-004 as independent corroboration of covid-001 (different mechanism, different source type). This pairing got specific scrutiny already in [[near-duplicate-check-v1]] for exactly the double-counting-adjacent risk this check would otherwise flag (two conclusions sharing a hidden common premise) — checked and confirmed as genuinely independent mechanisms (growth-curve math vs. population-distance modeling), not assumed. No fallacy found.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Why this matters:** a claim already subjected to unusually thorough cross-checking (near-duplicate check, structure layer) before this fallacy screen ever ran — consistent clean result.

---

## covid-005 (Van Treuren, HSM traffic-share model)

**Checking the source's own argument:** Van Treuren applies a 2x spreading advantage then a 5x downward adjustment he names "(arbitrary)" in the same sentence he applies it. Naming a judgment call as arbitrary, in the same breath, counts as honest epistemic labeling, not a hidden fallacy — the opposite of what a fallacy conceals. The claim file's own Ambiguity Flags and Adversarial Interpretation sections already interrogate this specific step (what removing it would do to the headline number, and the asymmetry of applying two named downward adjustments to one side without a matching named adjustment to the other).

**Fallacy Identification:** none found beyond what this claim's own Ambiguity Flags and Adversarial Interpretation already name — the scrutiny-asymmetry concern is surfaced explicitly, not smuggled.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Checking our own write-up:** the Analysis section states the corroboration with covid-001 and covid-004 in properly hedged terms, citing the near-duplicate check rather than asserting independence unchecked. No fallacy found.

**Why this matters:** built with this check's categories already in mind (this claim entered the vault after [[fallacy-screen-layer-v1]] existed), which likely explains the clean result — the asymmetry risk got named at claim-creation time rather than needing a separate pass to surface it.

---

## covid-006 (Van Treuren, prior-odds/WIV-capability calculation)

**Checking the source's own argument:** Van Treuren moves his backbone-probability estimate from 1-in-1000 to 1-in-100 "because I do find the (later) non-sharing of the database odd" — a numeric factor justified by a stated intuition rather than a fully argued evidentiary chain. This claim's own Ambiguity Flags already names it directly: the adjustment "rests on a single named factor... that Van Treuren himself calls 'somewhat suspicious' rather than resolved." Checked against the 26 categories: closest candidates are non sequitur (the specific 10x figure doesn't follow from a stated mechanism) or appeal to ignorance (absence of an innocent explanation for the outage treated as raising suspicion) — neither fits cleanly, and Van Treuren doesn't present the adjustment as more certain than it is; he flags it as a judgment call in his own text.

**Fallacy Identification:** none found beyond what this claim's own Ambiguity Flags already name.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Checking our own write-up:** the Analysis and Adversarial Interpretation sections both hedge appropriately, naming which inputs come from Van Treuren's own judgment versus debate evidence. No fallacy found.

**Why this matters:** same pattern as covid-005 — a claim built with this check's own categories already in view, producing a clean result on both sides.

---

## blackhole-001 (CERN FAQ, energy-equivalence argument)

**Checking the source's own argument:** "The LHC can only reproduce phenomena that already happen naturally... it would contradict what we see: stars, galaxies and the Earth still exist." This treats cosmic-ray collisions against a stationary target (the atmosphere, the Moon, other stars) as equivalent to the LHC's two-fast-particle, head-on, center-of-momentum collisions, on the strength of one shared trait (comparable energy), while a trait that matters (collision geometry) goes unaddressed. The claim file's own Analysis already names this gap in plain language ("the energy-equivalence argument doesn't automatically establish geometry-equivalence") but doesn't formally tag it.

**Fallacy Identification:** false equivalence — treating energy-matched but geometrically different collision types as interchangeable for safety purposes, without addressing the geometry difference the source itself doesn't close.

**Direction of Error:** toward over-confidence in the claim — makes the LHC-is-safe conclusion look more settled than the stated evidence, on its own, actually establishes.

**Group Tag:** shifting the boundaries.

**Checking our own write-up:** the Analysis section names the geometry gap directly and doesn't overclaim a resolution, correctly flagging it as CERN's fuller safety case's job to address (which [[blackhole-003]] later partially does). No fallacy found in our own prose.

**Why this matters:** the second genuinely new fallacy tag from this batch — like covid-001's "rushed conclusion," a real finding that sharpens a gap this claim file already knew about into a named, checkable category rather than leaving it as untagged prose.

---

## blackhole-003 (LSAG full 2008 report)

**Checking the source's own argument:** the white-dwarf/neutron-star survivorship argument (cosmic-ray-produced black holes would have destroyed these dense stars over their observed lifetimes; they haven't been destroyed; therefore such black holes don't form dangerously) uses specific, individually observed astronomical objects and their known accretion timescales — not a bare "we still exist" appeal, which would risk an observer-selection framing. Checked against the 26 categories: this is a properly constructed astrophysical argument from absence of a specific predicted signature (destroyed white dwarfs/neutron stars), not a rushed conclusion or a survivorship-bias error, because the "survivors" here are external objects we can observe destroyed or intact from a distance, not a set of observers who could only exist if undestroyed.

**Fallacy Identification:** none found, in the source's argument.

**Checking our own write-up:** the Analysis section discusses LSAG's "in addition to" framing (two additive, independent arguments) without asserting a ranking between them that the source itself doesn't provide, and correctly notes what this claim doesn't resolve (which argument carries more weight). No fallacy found.

**Direction of Error:** not applicable.

**Group Tag:** not applicable.

**Why this matters:** the most rigorously constructed source document in this project (a full technical safety report, not a debate transcript or a short FAQ), and it shows — the one case in this batch where the source's own argument construction leaves the least room for a hidden fallacy to hide in.

---

## What running this for real actually shows

Twelve claims checked, twenty-four sub-checks (source argument + our own write-up, per claim), five real findings worth naming and one genuine null pattern that dominates:

**From the first three-claim run:**
- **eggs-003:** the check caught a real overclaim in our own prior work — the strongest possible result for a self-check, since it means the tool works against us too, not only against outside sources.
- **covid-003:** a clean null result, and a claim file that already did the honest work on its own, confirmed rather than improved by the check.
- **blackhole-002:** a genuine gap in our original 25-category list, caught in real material on the first real run, leading to the 26th category (double-counting).

**From the second, nine-claim run:**
- **eggs-001, blackhole-003:** clean on both sides — no fallacy in the source, none in our write-up.
- **eggs-002:** clean, but surfaced a second possible taxonomy gap (over-adjustment / conditioning on a mediator) that didn't get added as a 27th category, because the claim file only names it as an open risk, never asserts it as a committed error — the same discipline that kept blackhole-002's finding honest rather than speculative.
- **covid-001, covid-002:** two real "rushed conclusion" findings, both in the *source's* own argument (not our write-up), both already partially named in prose by the claim files themselves but never formally tagged until this run. Interesting pattern: both push toward more certainty than a single data point or a probabilistic model should support, but in opposite directional favor (covid-001 toward zoonotic timing, covid-002 toward lab-leak timing) — evidence this project's own claim set doesn't lean toward flattering one side of the debate over the other.
- **blackhole-001:** one real "false equivalence" finding, in the source's own argument — the energy-equivalence-without-geometry-equivalence gap this claim file already knew about, now formally tagged.
- **covid-004, covid-005, covid-006:** clean on both sides. Worth noting: covid-005 and covid-006 (built the same day as this extended run, with [[fallacy-screen-layer-v1]]'s categories already available) show the cleanest results of the batch — consistent with the idea that a category list, once it exists, can get applied at claim-creation time rather than needing a separate later pass to catch what it would have caught anyway.

**Overall pattern:** every real finding in this project so far (eggs-003's overclaim, blackhole-002's double-counting gap, covid-001's and covid-002's rushed conclusions, blackhole-001's false equivalence) showed up in material written *before* this check existed or ran against it. No fallacy found anywhere in this project's most recently written claims (covid-004 through covid-006) or in any of this project's own write-ups (the Analysis sections), across all twelve claims. This suggests two things worth stating honestly rather than claiming credit for: the check works (it found five real, previously-untagged issues in older material), and writing with the check's categories in mind from the start produces cleaner results than running the check after the fact — though twelve claims and one project's writing style isn't enough evidence to call that second pattern proven, only observed.

This updated [[fallacy-screen-layer-v1]]'s taxonomy from 25 to 26 named categories after the first run (double-counting). This second run didn't add a 27th, despite surfacing one real candidate (over-adjustment bias in eggs-002) — that candidate stayed a named, honest risk in the claim file rather than a committed error, and this project's own rule requires a real committed instance, not a plausible risk, before adding a category.
