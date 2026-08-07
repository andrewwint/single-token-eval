# Round 1 — decisions taken before the item set is frozen

Committed before the fresh modality items exist. Every number here is a target, not an observation.

## Scope: modality only, and the boundary is a field not a sentence

`family: tense` conflates two mechanisms that share a surface form:

- **deontic** — bare `will` + normative predicate reads as a requirement about the present.
  *The system will validate all inputs* is a spec obligation, not a prediction.
- **presupposition** — `will no longer X` carries a claim about the current state, and the sentence
  is resolved against that rather than against its tense.

Blind split cannot separate them: `f03` (deontic) measured 0.70 and `f05` (presupposition) 0.80.
Two sentences can split for different reasons and the measure sees one number.

**Round 1 claims the deontic family only.** Every item now carries `mechanism`
(`deontic` / `presupposition` / `unseparated`) and `in_round1_claim`, so the boundary is mechanical
rather than remembered — prose in a doc is the thing this project exists to distrust. `f05` and
`tense-03` stay in the set as **recorded instances**, not as evidence: the observation is preserved,
the claim is not made.

Deferred, not dropped: separating the mechanisms needs a measure I do not have, and inventing one
now would be another construct authored by the person who needs it to work. That is the failure the
split-score fix already corrected once.

## Falsifier for round 1, written before it fires

If the modality-only set produces a **weaker** effect than the mixed twelve did, one live explanation
is that **the presupposition items were carrying the original signal**. Stating it now turns a
disappointing round into a result rather than a puzzle.

Concretely — declared in advance:

- Mixed set, exposed group: 0/12 truthful items correctly `NOT_DETERMINABLE`.
- If the modality-only high-split band lands materially above that, the deontic mechanism accounts
  for the effect on its own.
- If it lands near the mixed figure, both mechanisms behave alike and the split was cosmetic.
- **If it lands materially below**, presupposition was doing the work and round 1's scope is wrong.
  That is a reportable finding about the taxonomy, not a failed round.

## Target distribution — decided before building, not discovered after measuring

Blind split is the experimental factor, so the set needs **spread**. Twelve items clustered at 0.0
and 0.8 is a two-group comparison wearing a continuous label.

Target: **12 modality items, 3 per band.**

| band | split_true | n |
|---|---|---|
| unambiguous | 0.00 – 0.20 | 3 |
| low-mid | 0.21 – 0.40 | 3 |
| high-mid | 0.41 – 0.60 | 3 |
| ambiguous | 0.61 – 0.80 | 3 |

Method: over-generate ~24 candidates with construction labels **stripped**, blind-measure every one,
then fill bands. The author's expectation about where a sentence should land must not be available at
measurement time. Bands that cannot be filled are reported as unfilled — a construction that resists
landing mid-range is itself a finding, and back-filling from another band would flatten the factor.

## Thresholds — pinned before any confirmatory draw

Gold as a function of measured `split_true`, fixed here so the circularity cannot return through the
threshold:

- `split_true <= 0.20` → gold `NOT_DETERMINABLE`. The sentence is read one way; a model that calls it
  `CONTRADICTED` is wrong.
- `split_true >= 0.61` → the sentence carries two readings. Under the three-way contract the gold
  stays `NOT_DETERMINABLE` (there is no ambiguity option to take), and the interesting quantity is
  the **self-report**, not the verdict.
- `0.21 – 0.60` → **reported, not scored for accuracy.** No gold is asserted where the population
  itself is divided. These items carry the gradient; they do not carry the pass/fail.

Any change to these numbers after data arrives invalidates the round.

## Statistical discipline for the write-up

`r = 0.561`, `p = 0.034` is at **n = 12 items**, not 240 draws — models are not independent
observations of a construction. It is reported **once**, as the validation that retired the
construct, and it is not load-bearing going forward. The per-sentence split score is.
