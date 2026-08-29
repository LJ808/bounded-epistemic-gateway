---
synthesis_type: literature_engagement_addendum
addendum_to: [structure-layer-mapping-v1, two-layer-architecture-v1, insight-contribution-v1, neuro-symbolic-fallacy-screen-v1]
trigger: full-epistemic-stack-sourbut-goldhaber-lesswrong-20251219
claims_tested: 0
date_executed: "2026-08-28"
status: addendum — real, direct source of FLF's ingestion/structure/assessment rubric identified; the project already tracks that vocabulary (structure-layer-mapping-v1, dated 2026-07-17, names it as reviewer Oly Sourbut's own framework) without ever having read the document it came from, until now
written_in_e_prime: true
tags: [architecture, literature-review, reviewer-context]
---

# A Fifth Outside Paper — and the Direct Source of Our Own Reviewer's Framework

Sourbut and Goldhaber (2025), "A Full Epistemic Stack: Knowledge Commons for the 21st Century," posted to LessWrong 19th December 2025, a linkpost for oliversourbut.net. Both authors write in a personal capacity; their work at the Future of Life Foundation informs the piece directly.

This document names something plainer than any prior addendum in this series states: this paper's coauthor, Oliver Sourbut, functions as a real reviewer on this submission. `structure-layer-mapping-v1.md`, dated 2026-07-17, opens with a direct attribution: "FLF asked for three steps in this kind of project, not two. They call the three steps 'ingestion, structure, and assessment.'" `two-layer-architecture-v1.md`, dated 2026-06-30, names Sourbut by name as the reviewer who flagged an earlier structural problem in the project's first eight claim files.

Both of those documents predate this paper's public posting by roughly six months, yet both already carry its exact three-layer vocabulary — ingestion, structure, assessment — sourced secondhand through review feedback rather than through the paper itself. Real gap, worth stating plainly rather than smoothing over: FLF supplied this piece among the competition's own reference documents, and this project never opened it until this session, months after both the submission and the review conversations that already leaned on its framework. Nothing in this document changes the project's prior structural work; the mapping already held up independently, confirmed against the paper's own terms below. But a direct read earlier would have shown the project's own author the reviewer's underlying reasoning first-hand, not just its output in feedback form.

---

## What the paper actually proposes, stated plainly

The paper frames a "full epistemic stack": three layers a society's knowledge infrastructure would need to make shared reasoning easy, checkable, and hard to distort.

**Ingestion** — observations, data, and identity. Raw material enters the stack carrying real provenance: who produced it, under what guarantee (a staked reputation, a cryptographic signature, or nothing beyond "trust me"). The paper argues that cheap, LM-assisted metadata tagging can make this tractable at scale without requiring one centralised authority to store or process everything.

**Structure** — split into two distinct kinds. *Inference structure* traces a claim back through its supporting evidence and citations, a genealogy of how a conclusion got reached. *Discourse structure* tracks the live back-and-forth around a claim: counterarguments, refinements, competing positions, so a debate's real state stays legible rather than repeating itself endlessly. The paper singles out citation practice in science and journalism as a real, current failure of inference structure: a citation often points to an entire paper or book behind one narrow local claim, losing the exact scope of what that claim actually rests on.

**Assessment** — credence, endorsement, trust. The paper treats trust as a late-binding property: something resolved at the point of use, by whoever consumes the claim, not baked permanently into the structure itself. It names this deliberately, against designs that try to assign one fixed, universal probability or confidence score to a claim regardless of who's asking or why.

The paper's central architectural claim: these three layers benefit from staying loosely coupled rather than fused into one opinionated system. Structure metadata should stay minimally opinionated: interoperable, shareable, useful to many different downstream assessment approaches, rather than tied to one canonical judgment of what any given claim ultimately deserves as a trust score.

---

## Where the project's existing structure work already matches this, confirmed against the paper's own terms

`structure-layer-mapping-v1.md` already names four things a good structure step should do, attributed to the reviewer's own brief. Read against this paper directly, all four map cleanly onto the paper's *inference structure* definition specifically — the genealogy half of "structure," not the discourse half. Worth stating exactly, not left as a loose gesture: the project's existing structure-layer work covers half of what the paper's own "structure" layer names, the inference-genealogy half. The discourse half — competing positions, live refinement, tracking what a debate already covered so the same ground doesn't get re-litigated — has no direct counterpart in the project's current structure-layer work.

`two-layer-architecture-v1.md`'s rewrite/check split maps onto the paper's ingestion/assessment layers reasonably well: the rewrite step strips a claim down to its bare, checkable dependency (close to what the paper calls ingestion's demand for traceable provenance), and the check step reads that dependency and judges it (assessment). But naming it a *two*-layer architecture, against a reviewer whose own published framework names three, reads differently once the source document sits in view directly. `structure-layer-mapping-v1.md` already corrected this in July, adding the missing middle layer under the reviewer's own name for it. This paper confirms that correction held the right shape, structure genuinely sits as its own distinct layer, not a subset of either rewrite or check.

`insight-contribution-v1.md`'s finding — that stripping "is/was/are" forces a claim to name its real dependency, and that the *kind* of dependency exposed differs by source type (a study-design dependency for combined data, a reasoning-chain dependency for a live debate) — reads as a real, independently-derived instance of the paper's inference-structure concept, arrived at from direct work with actual claims rather than from reading this paper's abstract framing. Two separate lines of reasoning landing on the same structural need, same pattern this series already named once for the Artificial Hivemind paper (`literature-engagement-addendum-v3.md`, "Structural validation" section): one architectural, one empirical, converging without either informing the other, at least not until this session closes that gap directly.

---

## Where the paper reaches further than the Gateway currently does

The Gateway's own scoring work — `fallacy_bounds_screen()`, the four-state bounds design, the cross-family model comparisons in `literature-engagement-addendum-v3.md` — sits almost entirely inside the paper's *assessment* layer. Every one of those extensions asks the same underlying question the paper's assessment layer names: given a claim, how much credence does it deserve, and how does that credence get computed without collapsing genuine uncertainty into a false single verdict? The paper's late-binding-trust framing matches the Gateway's four-state design closely, already covered in the prior addendum's "Structural validation" section and not repeated here.

Two real gaps stand open, worth naming rather than glossing past:

**Discourse structure has no counterpart in this project yet.** The Gateway screens a claim against fixed fallacy categories; it doesn't track competing positions on that claim over time, or surface where a debate already settled a point versus where real disagreement persists. The paper names this as one of two distinct structure types, and the project currently builds only the other one.

**Provenance and ingestion sit almost entirely outside the Gateway's scope.** The claims fed into `fallacy_bounds_screen()` arrive already extracted and framed; the pipeline doesn't itself trace or verify where a claim's underlying data came from, or under what guarantee. The paper treats this as foundational, the layer everything else builds on. Worth naming as a real scope boundary, not a flaw: the project chose to build deep on assessment rather than wide across all three layers, a reasonable scope choice for a competition submission, but one the paper's framing makes explicit rather than implicit.

---

## The local-only constraint, read against the paper's own vision

The paper leans on distributed, LM-assisted clerical labor at real scale to reach its stated goal: a shared, interoperable structure layer many downstream tools draw from. `moe_router.py`'s own docstring states the project's standing rule plainly: local-only, no cloud API, in any framing, for any fallback tier. That constraint doesn't contradict the paper's vision, a bounded, auditable, single-operator instance of assessment-layer tooling still counts as a real, working example of the kind of tool the paper calls for, just built at a scale the paper doesn't itself require. But it does mean this project can't currently test the paper's core distribution claim: that a lightweight, shared metadata format lets many independent tools consume the same structure layer. That claim needs multiple real consumers to test, and this project, by its own standing design choice, stays a single local instance.

---

## What this document does not do

Claim the project's prior structure-layer work needs rebuilding — it doesn't; this paper confirms the July correction held the right shape rather than exposing a new problem with it. Claim independent verification of the paper's own empirical claims — the paper makes almost none; it argues a vision and a design case, not a set of testable findings, so no `CLAUDE_INDEPENDENT_RUNS` decomposition report accompanies this addendum the way one did for Artificial Hivemind. Claim the timeliness gap changed any decision already made — it didn't; every structural choice this paper's framework already touches got made and confirmed independently, before this document existed. What this document does: names the real source of a framework the project already uses under a reviewer's name only, and names two real, unclaimed extensions — discourse structure and ingestion/provenance — that the paper's full three-layer vision names and this project's current scope doesn't cover.
