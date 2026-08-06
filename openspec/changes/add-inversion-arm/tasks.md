# add-inversion-arm — tasks

Gates are ordered. Nothing below a **GATE** runs until the gate above it passes.

## 1. Pin the transport  (done)

- [x] IDs resolved and pinned. **Verified by invocation, not by listing** — `opus-5`, `sonnet-5`
      and `opus-4-8` list ACTIVE and deny on call.
- [x] Smoke draws fired; **~270 in / ~105 out per draw** measured, cost re-estimated in `design.md`.
- [x] Response contract revised binary → three-way after the dry run showed the binary form
      measured the wrong thing (`docs/rounds/smoke-2026-08-06-findings.md`).
- [x] Raw model output stored verbatim on every row, so a re-score never needs a re-spend.

## 2. Build the items

- [x] item build + audit (`harness/build_gate_a.py` cue audit) — emits **both** members of a pair from one source definition, so the
      twins cannot drift by hand.
- [x] **Builder assertion:** the two members differ by exactly the declared token and nothing else.
      Fail the build otherwise. This is the instrument's load-bearing property, so it is a hard
      assertion, not a review note.
- [x] 12 pairs minimum spread across the five families (`operator`, `modal`, `quantifier`,
      `polarity`, `tense`), each with ≥3 decoy claims true of the source.
- [ ] Every `exoneration` is derivable from the material shown. Cut any item whose correct answer
      needs a stipulation that overrides the source's plain reading.
- [ ] **Contamination cut:** cut any pair resolvable by token-matching the claim against the source
      without parsing the logic. The paired design makes this testable — if both members resolve by
      surface matching, the pair is not discriminating.

## 3b. Calibration + polarity balance  (done)

- [x] 4 `polarity` calibration pairs, negated member false in 2/4 so "flag the negation" scores 50%.
      **Authored in-repo, not from an independent generation run** — recorded in the items and in
      `REVIEW.md`; the cold read is the only independent check on them.
- [x] 3 reverse-polarity singles (future claim false), held out of the pass-1 pool.
- [x] `harness/score_gate_a.py` — pass 1 graded against the key, never self-reported.

## GATE A — independent cold read before freeze

- [ ] Independent local review of the item set, briefed **only** to answer: *does anything here
      reveal the correct token direction?* Not the hypothesis, not the expected result, not where to
      look.
- [ ] **Local only.** `items/` are answer keys — never send this repo to a cloud review tier.
- [ ] Findings resolved or items cut. A pair that cannot be built cold-read-clean is cut, not
      softened.

## 3. Freeze

- [ ] `items/items.jsonl` + `items/FROZEN.md` recording the sha256 and the freeze date.
- [ ] Runner verifies the digest before firing and exits non-zero without spending on mismatch.

## GATE B — pre-registration committed before any spend

- [ ] `docs/rounds/round-1-prereg.md` committed, declaring the discrimination floor, per-cell N,
      which regimes fire, the budget cap, the probe expectation for the discrimination guard, and
      the STOP conditions.
- [ ] Resolve the four open questions in `design.md`, including stating the `[C1]`-labelling ceiling
      explicitly and saying what per-family N does and does not support.

## 4. Runner and scorer

- [x] `harness/stats.py` — vendored `wilson_ci` + `discrimination_guard`, origin and copy date in the
      docstring.
- [x] `harness/inversion_run.py` — frozen-digest check, done-keys resume, bounded concurrency,
      append-only `results/draws.jsonl` with raw transcripts.
- [ ] **Budget cap is declared but not enforced** — the `--budget` flag is parsed and never checked
      against spend. Wire it, or remove the flag; a cap that cannot stop a run is worse than none.
- [ ] Independent harness review (baton `code-reviewer`) resolved before GATE B.
- [x] `harness/inversion_score.py` — per-member majority; DISCRIMINATED only when the false member is
      flagged and the true member is not; component rates and decoy FP reported alongside;
      `wilson_ci` intervals; discrimination guard across tiers.
- [x] Per-cell reporting (placement × regime × model × family). No aggregate headline across
      placement or regime.
- [x] `parse_ok: false` draws excluded and counted separately, never scored as misses.

## 5. Tests — before firing, not after

- [x] `harness/tests/test_inversion_score.py`, synthetic draws only, zero spend:
      - flagging both members → NOT DISCRIMINATED (constant alarm)
      - flagging neither → NOT DISCRIMINATED (miss)
      - flagging only the false member → DISCRIMINATED
      - an all-empty responder shows FP 0 **and** discrimination 0, surfaced together
      - a parse failure is excluded, not counted as a miss
      - a digest mismatch aborts without spending
      - the builder rejects a pair differing in more than the declared token
- [x] **Mutation-check the suite:** break each scoring branch on purpose and confirm the matching
      test fails. A test that cannot fail is not a check.

## GATE C — fire

- [ ] Dry run at N=1 on two pairs, all models, one regime. Read the raw responses by hand before the
      full round.
- [ ] Full round inside the pre-registered budget cap.
- [ ] `docs/rounds/round-1-findings.md` written against the locked criteria — including, if it
      applies, "the item set could not separate the tiers."
