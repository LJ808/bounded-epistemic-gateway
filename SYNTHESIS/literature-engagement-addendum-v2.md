---
synthesis_type: literature_engagement_addendum
addendum_to: [insight-contribution-v1, adversarial-robustness-criterion-6, literature-engagement-addendum-v1]
trigger: anthropic-global-workspace-paper-2026-07-06
claims_tested: 0
date_executed: "2026-07-08"
status: addendum — core submission claims unchanged; v1 claims unchanged; new theoretical warrant added
written_in_e_prime: true
tags: [resilience]
---

# A Third Outside Paper — What Anthropic's New AI Research Means for Our Project

A third real paper now speaks directly to the theoretical foundation our whole project rests on.

Gurnee, Sofroniew, and others (2026), "Verbalizable Representations Form a Global Workspace in Language Models," published July 6, 2026, introduces a new way to look inside an AI model while it works — the researchers call their tool the J-lens. The J-lens lets researchers watch an AI model's actual reasoning process while the model runs, in real time. It finds one specific, important part of the model's internal state, which the paper calls the J-space.

Our standing rule here: new evidence that speaks to our project's claims gets stated plainly — not quietly folded in, and not selectively quoted to only show the parts that make us look good. This document states exactly what the J-space paper shows, exactly where its findings make our project stronger, where it gives us a real mechanical explanation we didn't have before, and where it opens new tough questions a judge might now reasonably ask.

---

## A plain-language note before we go further

AI models generate text by passing information through many internal processing steps, one after another — think of them like stages in an assembly line. Early stages handle basic pattern recognition. Middle stages handle actual reasoning and inference. Late stages pick the specific words the model finally writes down.

The J-lens, built by Anthropic's researchers, makes that middle stage's reasoning readable, for the first time, at real scale. It reveals one specific area — the J-space — where the ideas relevant to a task show up and actually shape what the model eventually writes.

This matters for our project because our whole project's core claim concerns exactly this: what hides in the middle of a chain of reasoning — inside a written sentence, in our case, not inside a model's internal machinery. This new paper shows the exact same hide-and-detect pattern happening at the level of the model itself. Both find the same underlying structure, just in two completely different places.

---

## Outside Paper 3: Gurnee, Sofroniew, Pearce, and others (2026), Anthropic

**"Verbalizable Representations Form a Global Workspace in Language Models"**
Published July 6, 2026. https://transformer-circuits.pub/2026/workspace/index.html

The J-lens works by measuring, for each processing stage inside the model, how much influence that stage's internal state actually has on the words the model picks — both right away and later on — averaged across a large number of examples. That averaging step separates real, purposeful reasoning from random, incidental noise.

The resulting J-space carries several properties worth naming plainly:

- The model can describe what sits in its J-space, if you simply ask it. ("What are you thinking about right now?")
- Outside instructions can actually change what sits in the J-space. ("Ignore that piece of information.")
- What sits in the J-space actually causes the model's final conclusions. Take away that content, and the conclusion itself changes.
- The J-space only activates for tasks that require real thought — simple pattern-matching skips it entirely.

Blocking a model's access to its own J-space left basic fluency and simple classification tasks working fine. Multi-step reasoning, flexible combination of ideas, and the model's ability to describe its own thinking all broke down badly. The J-space carries the actual reasoning. The surface-level output can survive without it — and still read as smooth, coherent writing.

---

## Finding 1: This new paper backs up our core claim — and now gives us a real mechanical reason why

Our whole project's core argument, laid out in [[insight-contribution-v1]], works like this.

A written sentence can absorb a hidden condition — a research-method choice, a chain of evidence, a boundary on where a claim actually applies — in a way that reads like plain fact. "There is an association between eggs and heart disease" reads like a fact about eggs themselves. It actually only holds true given one specific statistical setup, with one specific set of adjustment choices.

Rewriting in E-Prime forces that hidden condition into view. The sentence has to name what it rests on, because the phrase "is an association" can't survive the rewrite without exactly doing that.

This new J-space paper gives us, for the first time, a real mechanical reason why that hide-and-reveal pattern actually works at a deeper level.

The paper shows that a model's actual intermediate reasoning steps show up in its J-space in the same order the underlying computation requires them — before the model's final answer ever appears in its output. Those steps actually cause the model's final word choices. Change the J-space's representation of one idea partway through, and the model's conclusion changes along with it.

This confirms our project's claim, but from inside the model itself. Our project shows that rewriting in E-Prime forces a written claim to expose its hidden condition, at the level of the actual prose. This new paper shows that AI models already hold an equivalent structure internally — an unspoken, working version of what their conclusion actually depends on — in a form the J-lens can read, and even change.

Both projects find the exact same underlying structure, just in two different places. The J-lens finds it inside the model itself. E-Prime forces it out into the text, where any human reader can find it too.

Before this paper came out, our project had no real mechanical explanation for *why* a phrase like "is an association" hides a statistical-method dependency from a reader with no statistics training. This new paper supplies exactly that explanation: smooth, grammatically correct writing can get produced through internal pathways that never surface the actual underlying reasoning to any part of the model a human could read. The paper documents this directly, in one of its own experiments: a model can correctly continue a passage written in Spanish, without the actual concept "Spanish" ever showing up as an active, causally important part of its J-space. The surface output came out fine. The underlying reasoning stayed completely hidden.

Rewriting in E-Prime works as an outside forcing mechanism that pushes a hidden condition into the readable layer of a sentence — the exact same move the J-lens performs from inside a model.

---

## Finding 2: A real mechanical explanation for a puzzling result from our first outside-paper document

Our first outside-paper document had to deal with an uncomfortable finding from Jehu-Appiah (2026): E-Prime produced the *smallest* improvement in accuracy, out of four rules tested, at the writing stage. A simple filler-word ban produced the biggest improvement.

Our first document explained this at a practical level: E-Prime does its job at the revealing stage. The filler-word ban does its job at the writing stage. Two different jobs, at two different points in the process.

This new J-space paper now gives us the actual mechanical reason underneath that practical explanation.

The J-space activates in a model's middle processing stages — roughly the middle third of the model's overall depth, sitting between early pattern-recognition and late word-selection. E-Prime operates entirely *after* those middle stages finish. It changes the surface text that the late, word-picking stages already produced. It never touches the middle-stage reasoning that actually generated the idea the text expresses.

A filler-word ban works completely differently. It applies an ongoing compliance burden throughout the entire writing process — constant self-editing pressure. That pressure operates much closer to the actual middle-stage reasoning itself. The paper shows that a direct instruction to "focus on" or "ignore" a concept can change what actually sits in the J-space. An ongoing vocabulary ban functions like a constant, implicit version of that same kind of instruction, and its effect very plausibly works through the same underlying mechanism.

This mechanical picture explains the whole result. E-Prime can't improve accuracy at the writing stage, because it only acts after the model's reasoning has already finished. The filler-word ban's bigger improvement follows because it acts while the reasoning happens. Neither result says anything bad about E-Prime's actual job at the revealing stage, where E-Prime acts on reasoning the model already finished, and forces its hidden condition into a form a human can read.

The two-part system our first outside-paper document proposed — a filler-word ban for writing, E-Prime for revealing — now carries a real mechanical justification. Each rule applies at exactly the stage where the evidence shows it actually works.

---

## Finding 3: What this means for our toughest self-check, Criterion 6

Our first outside-paper document named our toughest self-check (adversarial robustness, FLF's Criterion 6) as the weakest section of our original project.

This new paper's section on catching AI models doing something wrong gives our project the strongest outside support we've received yet for our core claim about revealing hidden things.

The paper documents a striking finding. When a model processes a prompt that contains a hidden attempt to manipulate it — buried inside a search result, for instance — the model's J-space already holds the concepts "injection attempt" and "fake" before the model ever produces a single word of output. The model caught the manipulation attempt internally. That internal catch never showed up anywhere in its actual response.

This matches, almost exactly, the claim our project makes in [[adversarial-robustness-criterion-6]]: a real, relevant judgment can happen entirely inside a system, without ever surfacing anywhere a human could read it. The J-lens makes that internal catch visible. Rewriting in E-Prime makes the equivalent hidden problem visible, at the level of written prose.

The paper documents a second finding in that same section. After safety training, a model asked to do a roleplay task holds the concepts "fictional" and "disclaimer" in its J-space while it writes its response — before it writes a single word. The model flagged, internally, that it had switched away from its normal default mode. That flag also never showed up anywhere in the actual output.

Our project's claim in [[adversarial-robustness-criterion-6]] Part C — that a claim record with clearly labeled source and dependency information works as an outside, visible parallel to a model's own internal safety self-checking — now carries a real mechanical justification from this new paper. Both approaches push a hidden judgment from an internal, invisible layer out to a visible, checkable one. The J-lens surfaces it from inside the model. Our project's own claim format surfaces it inside the written claim itself.

---

## One new tough question this paper raises

A judge familiar with this new paper might now reasonably raise the following challenge:

*If an AI model's own internal reasoning space already holds the exact hidden step that E-Prime rewriting would reveal, why does the outside rewriting step add anything at all? A judge equipped with J-lens tools could just check hidden conditions directly inside the model — making E-Prime pointless.*

This challenge deserves a direct answer, not a dodge. Two real answers, stated plainly.

**First: the J-lens needs direct access to a model's own internal processing states.** That kind of access doesn't extend to human readers, to other AI models without special interpretability tools, or to anyone working from text alone. Our project's whole method operates on the actual output text — in a form any reader can check, with no special tools required at all. This new paper itself confirms that smooth, fluent output can completely hide its own internal reasoning and still read as coherent, convincing writing. Rewriting in E-Prime forces that hidden reasoning into the text itself, where anyone working from text alone can actually find it.

**Second: the J-lens, right now, only handles single-word ideas.** The paper states this limit directly, itself. The hidden conditions our project's whole typing system targets — "which specific statistical adjustment the researchers chose," "whether a specific physics process actually applies at the relevant energy level" — span many words, and represent whole structured commitments, not single ideas. E-Prime works at the level of sentence structure, which can reveal multi-word hidden conditions just fine. The J-lens can't reach that level yet.

This challenge, in the end, names a real limit of text-based revealing, in a world where advanced AI-interpretability tools now exist — not a real disproof of our method. A future system combining J-lens checking with E-Prime's text-level revealing would outperform either one alone.

---

## What this document does not claim

We haven't run any new claims through our actual process in response to this new paper. Our eight existing claim files stay exactly as they were. No claim in our project depends on this new paper's findings. This document adds theoretical backing to claims our project already made based on independent evidence — not new factual claims that come from this paper itself.

This new paper also doesn't prove our specific three-part typing system (study-design dependency, reasoning-chain dependency, boundary dependency) correct on its own. That three-part system comes from three real, executed case studies and one stated, tested prediction, laid out in [[insight-contribution-v1]]. This new paper backs up the underlying mechanism our project relies on. It doesn't independently test the specific three-part system we built by applying that mechanism.

---

## What This New Document Adds to Our Project's Overall Claim

| Item | Status after this document |
|---|---|
| Our core claim ("E-Prime makes a hidden judgment call visible in the text itself") | Strengthened — now carries a real mechanical justification from how AI models actually work internally, not just a practical argument. |
| Our earlier resolution of the E-Prime accuracy-gain puzzle (writing stage versus revealing stage) | Deepened — that practical distinction now maps onto a real mechanical one: E-Prime acts after a model's reasoning stages finish; writing-stage rules act while those stages run. |
| Our two-part system (filler-word ban for writing, E-Prime for revealing) | Now carries real mechanical justification: each rule maps to the exact stage where the evidence shows it actually works. |
| Our toughest self-check (Criterion 6, adversarial robustness) | Strongest outside support we've received yet: this new paper's findings on catching AI models internally give a direct mechanical parallel to our own claim-record approach. |
| The new tough question this paper raises | Named and directly answered: J-lens tools could, in principle, check hidden conditions without E-Prime, but that access doesn't extend to text-only readers, and currently only handles single-word ideas. |
| Our eight existing claim files | Unchanged. |
