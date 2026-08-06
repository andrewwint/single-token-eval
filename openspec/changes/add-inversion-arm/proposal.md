# add-inversion-arm — the study's first arm

## Why

The repo exists to answer one question: does a reviewer's verdict track a single token in a claim?
Nothing is built yet. This change proposes the instrument, the factors, and the runner that produce
round 1.

The measurement problem comes first, because it dictates the design. A one-token defect is the
hardest thing to build a fair test for: everything written around it — a comment, a variable name, a
test's name, the tone of the paragraph — gives the answer away, and the smaller the defect, the more
any accidental hint dominates it. `docs/single-token-inversion.md` §3A names this as make-or-break
and calls for the strictest possible version of the no-answer-key invariant.

That invariant cannot be met by care alone. You can cold-read a fixture for tells and miss one; that
has happened, expensively, to readers looking for exactly that. **You can never prove you removed
the last hint.**

So the design has to make hints *harmless* rather than absent.

## What Changes

**1. The twin pair — items ship in matched halves.** Every item is built twice, byte-identical except
the inverted token. One member's target claim is TRUE of the accompanying source, the other's is
FALSE. Both always fire. Scoring is **paired discrimination**: a pair counts only when the false
member is flagged AND the true member is not.

This is the structural answer to §3A. Any hint that survived is present in **both** members, so it
cannot produce a differential score — a tell gives away the same answer twice. The instrument stops
depending on an unverifiable property (the fixture is clean) and starts depending on a checkable one
(the members are identical), asserted by the builder.

It also kills three degenerate strategies for free: flag-everything flags both, flag-nothing flags
neither, and tone-matching cannot separate members whose tone is identical.

**2. Enumerated claims, deterministic grading.** Each artifact carries visibly-labelled claims
(`[C1]`…`[Cn]`); the model returns `{"false_claims": ["C3"], ...}`. Grading is exact set comparison
against gold — no LLM judge anywhere in the pipeline. Non-target claims are **decoys**, true of the
source, and they supply the false-positive rate on the same call. Without them a model that
volunteers nothing scores as low-FP, which reads as accuracy and isn't.

**3. Three crossed factors, reported per cell.**
- **Placement** — the inverted token sits **in-diff** (measures directed-review thoroughness) or
  **out-of-diff** (measures source-derivation). §3B: placement selects the axis, so it is a factor,
  not an incidental property of an item.
- **Instruction regime** — bare review · flag-anything-untrue · derive-the-invariant-from-source.
  This is the arm's real question: whether an instruction closes whatever gap placement reveals.
- **Model tier** — three frontier tiers plus a probe expected to score lower, so a no-spread result
  reads as *the items are too easy to separate tiers* rather than *the tiers are equivalent*.

**4. Single-shot Bedrock `Converse`, temperature 0, no tools.** Two reasons. It removes the agentic
confound between *did the model catch it* and *did the agent go looking* — the exact axis under
test. And it is hermetic: no `~/.claude`, no global agents, skills, settings, memory or MCP servers
leaking into a draw. The prompt is the entire input, which is a stronger guarantee than the sibling
study could achieve on the same hardware.

**5. Runner and scorer.** `harness/inversion_run.py` and `harness/inversion_score.py`: frozen item
set verified by sha256 before spend, N draws × models, resumable via done-keys, budget cap with
graceful stop, append-only `results/draws.jsonl`. `wilson_ci` and `discrimination_guard` are vendored
from the sibling study rather than imported — frozen statistical helpers with no live upstream, so a
copy carries no drift risk.

## Revision log

**2026-08-06, after the GATE C dry run (~$1).** The binary response contract was replaced with a
three-way one. Under the binary form every frontier model flagged the target on both members — 7 of
8 pairs, ~0 discrimination — because a future-tense claim is neither true nor false of a
present-state source. The question was malformed, not the answers. Same items and models under the
three-way contract: **1/8 → 5/8 discriminated**. Four requirements were added as a direct result:
three-valued verdicts, verbatim transcript retention, access verified by invocation rather than by
listing, and declared controls having to be enforceable.

## Impact

- **New capability spec:** `inversion-arm`.
- **New code:** `harness/build_items.py`, `harness/inversion_run.py`, `harness/inversion_score.py`,
  `harness/stats.py` (vendored), `harness/tests/test_inversion_score.py`.
- **New items:** `items/items.jsonl` + `items/FROZEN.md`, built and frozen before firing.
- **New round docs:** `docs/rounds/round-1-prereg.md` committed **before any spend**, then
  `round-1-findings.md`.
- **Estimated spend:** ~$20–25 for the full crossing at N=5 draws. Single-shot calls are what make
  full crossing affordable rather than forcing a sampled design.
- **Publication boundary:** `items/` are answer keys. They are never published, and this repo is
  never sent to a cloud review tier. The publishable artifacts are the harness, the method, the
  pre-registration, and the results.
