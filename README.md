---
title: Readme
type: reference
status: active
vault: TRC
date: 2026-06-28
tags: [resilience]
---

# FLF Epistemic Case Study Submission
## Using a Writing Rule to Catch Hidden Assumptions

"Epistemic" means about how we know things. Not what we believe. How we check it.

**Case studies:** Eggs and heart disease. COVID's origin. Whether the world's largest particle collider could make a black hole.

**The main idea:** We use a strict writing rule called E-Prime. E-Prime bans every form of the word "to be" — no "is," no "are," no "was," no "were." That one rule forces a sentence to say what it actually rests on, instead of hiding behind a confident-sounding word like "is."

**How the pipeline works, updated June 30:** Every claim passes through two steps.

Step one: rewrite the sentence in E-Prime. No interpretation yet. Just the mechanical rewrite.

Step two: check what the rewrite reveals. What did the original sentence hide? What stays unclear even after the rewrite? How could someone misuse it?

FLF reviewer Oly Sourbut suggested this two-step split. See [`two-layer-architecture-v1.md`](flf-vault/SYNTHESIS/two-layer-architecture-v1.md) for the exact rules each step follows. See [`ingest.py`](flf-vault/ingest.py), where the two steps run as two separate, checkable pieces of code.

---

## Try it yourself (takes under a minute)

```
cd flf-vault
pip install -r requirements.txt
python3 ingest.py --demo
```

No account or key needed for `--demo`. If you have an Anthropic API key (a personal password for using Anthropic's AI model), run `python3 ingest.py "your claim here"` to test it on your own sentence.

---

## Where to start

### If you have 15 minutes
1. Read [`INDEX.md`](flf-vault/INDEX.md) first. It maps out all twelve claims and every file in this project.
2. Pick one case. Read one or two of its claim files. Each one shows the sentence before and after the rewrite.
3. Skim Part C of [`adversarial-robustness-criterion-6.md`](flf-vault/SYNTHESIS/adversarial-robustness-criterion-6.md). It gives the plain, unvarnished summary of where this method works and where it doesn't.
4. Skim [`literature-engagement-addendum-v1.md`](flf-vault/SYNTHESIS/literature-engagement-addendum-v1.md). It shows how we responded to two real outside papers we found after we finished our first draft.

### If you have 45 minutes
1. Read one claim from each case: `eggs-001.md`, `covid-001.md`, `blackhole-001.md`.
2. Open the files in Obsidian (the note-taking app this vault uses) and click the links between claims. You'll see how one claim actually connects to another.
3. Read [`crux-analysis-v1.md`](flf-vault/SYNTHESIS/crux-analysis-v1.md). It ranks the single questions that, if answered, would change the most about each case.

### If you want to run the code
1. `pip install -r requirements.txt && python3 ingest.py --demo`
2. With your own API key, run `ingest.py` on a claim from any topic you like.
3. Compare what you get against the worked examples in `adversarial-robustness-criterion-6.md`'s "Extension Protocol" section.

---

## What's in this project

```
flf-vault/
├── INDEX.md
├── ingest.py                                  ← the code, runnable in one command
├── requirements.txt
├── CLAIMS/
│   ├── eggs-cvd-diabetes/{eggs-001,002,003}.md
│   ├── covid-origins/{covid-001,002,003,004,005,006}.md
│   └── black-holes/{blackhole-001,002,003}.md
├── SOURCES/  (the nine documents we worked from)
└── SYNTHESIS/
    ├── crux-analysis-v1.md                      ← the key open questions per case
    ├── scalability-test-v1.md                   ← does this method still work on a bigger job?
    ├── per-claim-attack-vector-breakdown.md      ← every way someone could misread each claim
    ├── adversarial-robustness-criterion-6.md     ← the toughest test: can this get gamed?
    ├── literature-engagement-addendum-v1.md      ← our response to two outside papers, round one
    ├── literature-engagement-addendum-v2.md      ← our response to a third outside paper, round two
    ├── two-layer-architecture-v1.md              ← the two-step rewrite/check split, explained
    ├── structure-layer-mapping-v1.md             ← a third step FLF asked for, and how far we got on it
    ├── structure-layer-worked-example-v1.md      ← the real, structured version of that step, tested across all three cases
    ├── fallacy-screen-layer-v1.md                ← fourth step catching bad logic (26 categories), wired into ingest.py as screen_claim()
    ├── fallacy-screen-worked-examples-v1.md      ← that check, run for real against all twelve claims
    ├── near-duplicate-check-v1.md                 ← fifth step: checked every claim pair for a restated conclusion; found none, but found a wrong claim count instead
    └── next-steps-v1.md                          ← roadmap: all seven priorities done or wired this day
```

---

## Our main claim, stated plainly

**Rewriting a sentence in E-Prime makes a hidden assumption visible. It does not make lying or misreading impossible.**

Consider the problem this solves. A sentence like "eggs cause heart disease" sounds like a plain fact. It actually rests on a specific study, a specific group of people, and a specific way of adjusting the numbers. The word "cause" hides all of that. E-Prime forces the sentence to name what it rests on, because it can't use "cause" (or "is," or "means") to skip past that step.

Someone determined to mislead can still try. But now they have to add extra words to hide the gap, or leave a gap a careful reader can actually spot. Before E-Prime, they could hide the same gap inside one small, confident word.

We tested this claim two ways. First: ten different ways a reader could misread each of the original eight claims. Second: three ways a source could try to game the method — picking a friendly sample, using persuasive wording instead of evidence, or reassuring people right after raising a scary possibility. `adversarial-robustness-criterion-6.md` holds the full results, including where the method falls short.

---

## What we got wrong or left unfinished, stated honestly

- **We used two secondhand sources, now closed; one remains.** All three cases originally worked from a summary, a write-up of a debate, or an FAQ page — not the raw data, the full debate transcripts, or CERN's full 2008 safety report. **Update:** both COVID-debate judges' own written decisions now sit in the vault directly. [[covid-004]] comes from Eric Stansifer's decision; [[covid-005]] and [[covid-006]] come from Will van Treuren's, previously blocked by a hosting format this vault's tools couldn't render, provided directly by Jay this session. [[blackhole-003]] comes directly from CERN's full LSAG 2008 report, not the FAQ that summarizes it. One secondhand gap remains: the paper LSAG itself cites for further detail on collision geometry (Giddings & Mangano, arXiv:0806.3381).
- **We can catch this now, at least once.** Our method catches a source that treats two related facts as independent, when both facts sit in the same document (see `blackhole-002.md`). It originally couldn't catch a source leaving something out of one document that a different, uningested document would have caught. **Update:** we tested this directly. Reading CERN's full LSAG report (`blackhole-003.md`) after the FAQ (`blackhole-002.md`) did surface something the FAQ alone didn't show — confirmation that the two safety arguments run independently, not as one restated. It didn't, however, resolve the deeper question either document raises (which argument carries more real weight), so this capability still has real limits even where it worked.
- **Three questions named, one now partly answered.** Does one study's null result mean no effect exists, or just that the study didn't have enough people to detect one (see `eggs-003.md`)? Does the fact that a post-2019 method exists tell us anything about what a scientist could have done before 2019 (see `covid-003.md`)? These two stay fully open. The third — which part of CERN's safety argument actually holds the most weight (see `blackhole-002.md`) — got partly answered by reading the primary source directly (`blackhole-003.md`): the two arguments run independently, not as one restated, but which one matters more still isn't stated anywhere we've read. We name what's still open. We don't pretend to have closed more than we did.
- **One claim we caught and fixed.** We once wrote that this method gets better just by adding more computing power. We caught that we never actually tested it, and corrected the file to say so honestly.

---

## Contact

James Greathouse — james@senecacommons.com
Optional early check-in: June 21, 2026
Deadline: July 19, 2026
