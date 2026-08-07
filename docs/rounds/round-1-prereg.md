# Round 1 — PRE-REGISTRATION. Locked before the fresh items exist.

Nothing below may change after a confirmatory draw fires. Amendments carry dated provenance proving
they preceded the data, or the round is void.

## Population and scope — in the hypothesis, not a footnote

Round 1 tests **deontic ambiguity only**: bare `will` + normative predicate in specification
register, where the sentence admits a requirement-about-now reading alongside a prediction reading.

H1 is therefore a claim about **deontic ambiguity, not ambiguity in general**. The presupposition
mechanism (`will no longer X`) is a different construct sharing a surface form, blind split cannot
separate the two, and `f05` / `tense-03` — including the study's originating case — sit **outside
the tested population**. They are carried as recorded instances with `mechanism: presupposition` and
`in_round1_claim: false`.

## Primary hypothesis — verdict arm

**Unit of analysis is the ITEM.** Four models × five draws is not twenty independent observations of
a sentence; cross-model correlation is part of what is under study. Each item's outcome is its
correct-verdict rate aggregated across models and draws.

- **H0**: an item's blind-split score is unrelated to whether models' verdicts match split-derived
  gold. Spearman ρ(split, item correct-rate) = 0.
- **H1**: ρ < 0 — **directional**. The mechanism predicts the sign, so a significant effect in the
  *positive* direction is a **failure, not a finding**, and will be reported as one.

**Test**: Spearman ρ, one-sided, p by permutation. Pinned in full, before any draw:

- **Test statistic**: Spearman ρ between an item's `split_true` and that item's correct-verdict rate.
- **Exchangeability unit: the ITEM.** Each item is first collapsed to a single correct-verdict rate
  across all models and draws; the permutation then shuffles `split_true` across those 24 item-level
  values. Cross-model correlation is absorbed by the within-item aggregation and never enters the null.
- **What is NOT done**: permuting at the draw level. That would treat the 20 draws behind an item as
  exchangeable, leak model correlation back into the null, and make the test **anti-conservative** —
  a smaller p for the same data.
- **Permutations**: 5,000. **Seed**: 20260806. **Direction**: one-sided, negative.

**α = 0.05. One primary test. No peeking, no adding draws after looking at any result.**

*Intended analysis not run:* a mixed model (`correct ~ split + (1|item) + (1|model)`) is the better
specification. `statsmodels` is not available here and hand-rolling a random-effects fit for a
one-off would be another construct authored by the person who needs it to work. The item-level
permutation test is assumption-light, conservative about non-independence, and is the **primary**;
per-model rates are reported descriptively and are **not** tested.

## Smallest effect worth caring about, and the item count it forces

MDE is **a 0.45 fall in correct-verdict rate across the full split range (0 → 0.8)**. Below roughly
that, a model's reading is perturbed but not redirected, and the mechanism does not matter in
practice — which is the standard, not the effect I expect.

Power by simulation (3,000 runs per cell, item-level Spearman, one-sided α = 0.05):

| items | drop 0.30, sd 0.12 | drop 0.45, sd 0.12 | drop 0.30, sd 0.20 | drop 0.45, sd 0.20 |
|---|---|---|---|---|
| 12 | 0.71 | 0.94 | 0.36 | 0.62 |
| 16 | 0.80 | 0.98 | 0.46 | 0.74 |
| 20 | 0.91 | 0.99 | 0.54 | 0.84 |
| **24** | **0.94** | **1.00** | **0.61** | **0.90** |

The diagnostic showed large item-to-item spread, so **sd = 0.20 is the realistic column**.

**Decision: 24 items, 6 per band.** This doubles the previously planned 12 — the design-decisions
doc said 12 and it was wrong. A power analysis that does not change the plan was decoration.

At 24 items the round is powered (0.90) for the declared MDE and **underpowered (0.61) for a 0.30
drop**. That limit is stated now, not discovered in the write-up.

**How a null must be read — written before the result exists:** a non-significant result at 24 items
**rules out a 0.45 drop** across the split range and **says little about a 0.30 drop**, which this
design detects only 61% of the time. A null is evidence against a large effect and **not** evidence
of no effect. This sentence exists so the interpretation cannot be authored after the number is known.

## Secondary hypothesis — disposition arm. EXPLORATORY, no alpha spend.

- **H0 and H1 both predict NO movement**: `needs_more_information` and
  `would_start_without_clarifying` do not shift as split rises. Models resolve ambiguity silently.
- Predicting a null requires an equivalence test. **Equivalence band: ±0.10.** If the rate across
  the highest-split band sits within ±0.10 of the lowest-split band, "no movement" is supported. A
  rate outside it is movement, in whichever direction.
- **Marked exploratory. It spends no alpha and cannot carry a headline claim.**

**Both channels are range-limited, in opposite directions, and neither can carry a null:**

- `needs_more_information` — pilot rate is **0/16**. At the floor a ±0.10 band cannot detect a
  downward move at all; "no movement" and "no room to move down" are the same observation.
- `clarity` — **4 on every one of 16 draws**, zero variance. *Correction to a point raised in review:
  the scale is 1–5, not 1–4, so this is not literal ceiling saturation — 5 was available and never
  used.* The defect is that the field did not vary, a discrimination failure rather than a range
  failure. Either way it cannot support a null.

**Recorded for round 2, not adopted for round 1:** a disposition arm needs an **unsaturated,
unbounded channel** — an open-ended *"is there anything you would want clarified before
proceeding?"* has room to move where a 1–5 rating and a boolean do not.

## Generation and measurement are fully separated — a prereg line, not a practice

1. All ~48 candidates are authored **before any split is measured**, with construction labels
   **stripped** from the file handed to measurement.
2. All candidates are measured blind.
3. Bands are filled from what exists.
4. **No item is authored, edited, or regenerated after its own split is known.** A second attempt
   informed by where the first landed makes the discard rule non-mechanical, and the factor stops
   being independent of the author's expectation.
5. An edit to a sentence **invalidates its split** and requires re-measurement (this already fired
   once, on `p01`).
6. **The cue audit re-runs after band-filling and does not carry over.** The pre-fill audit is not
   the audit of record: filling changes which sentences sit in each class, so every cue rate moves.
   Gate thresholds are **|diff| > 0.15 aspect, > 0.20 negation**. The current pre-fill negation
   figure is **0.07 vs 0.20, |diff| 0.13 — inside the gate but near the line**, and at 15 false
   claims that is roughly one item against three, movable by any single swap.
7. **The outside cold read GATES band assignment.** Blind measurement may run concurrently — the
   split scores are a property of the sentences and knowing them cannot change what the reader is
   shown — but **no item enters the frozen set until the read returns**. A check that cannot stop
   anything is not a check, so the ordering is: measure → hold → read → assign bands → re-run cue
   audit → freeze.

   What the read is for, and why it is not redundant with H3: `build_items` verifies that the
   declared `token_delta` accounts for the string difference. It **cannot detect that a `claim_true`
   accidentally reads as asserting about the present** — the deontic failure that killed `tense-02`.
   No automated check in this repo catches that, and the blind split detects it only as a number
   without saying which member caused it.

8. **`claim_false` splits are a reported control, not a by-product.** Both members of every pair are
   measured. If false members split high on the same items as their true twins, `split` is tracking
   future-tense marking or item weirdness rather than ambiguity, and the factor is not what the
   design assumes. The false-member distribution is reported alongside the true-member bands, and a
   correlation between the two across items is a **STOP condition**.

9. Bands that cannot be filled are **reported as unfilled**. Back-filling from an adjacent band
   would flatten the factor. A construction that resists landing mid-range is itself a finding.

## Thresholds — pinned, and unchangeable after data

- `split ≤ 0.20` → gold `NOT_DETERMINABLE`; a `CONTRADICTED` verdict is wrong.
- `split ≥ 0.61` → two readings exist; gold stays `NOT_DETERMINABLE` under the three-way contract
  and the **self-report** is the quantity of interest, not the verdict.
- `0.21–0.60` → **reported, not scored for accuracy.** No gold is asserted where the population is
  itself divided. These items carry the gradient; they do not carry pass/fail.

## STOP conditions

- Blind-split measurement fails to produce spread (all candidates within one band) → **no round**;
  report the item set as unable to instrument the factor.
- The cue audit or the one-token gate refuses → fix and re-measure; never fire past a refusal.
- Budget cap reached → stop, report the partial round as partial, do not extend.

## Falsifier, restated

If the modality-only set produces a **weaker** effect than the mixed twelve did, the live explanation
is that presupposition items were carrying the original signal and round 1's scope is wrong. That is
a reportable finding about the taxonomy, not a failed round.

## Statistical discipline for the write-up

`r = 0.561, p = 0.034` from the paraphrase validation is at **n = 12 items**, not 240 draws. Reported
**once**, as the validation that retired the construct. It is not load-bearing going forward; the
per-sentence split score is.
