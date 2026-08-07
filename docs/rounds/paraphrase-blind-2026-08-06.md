# Blind paraphrase test — is ambiguity a property of the sentences?

240 draws, well under a dollar. **Exploratory, not confirmatory.** Run to answer one question before
the reframe could be accepted.

## Why this had to run first

The proposed reframe made gold taxonomy-dependent: `AMBIGUOUS` for exposed items,
`NOT_DETERMINABLE` for safe ones. But exposed-ness was assigned by one reviewer's linguistic
judgment about deontic `will`. That makes the scored quantity *does the model's ambiguity judgment
agree with the assigner's* — not a fact about language, and a disagreement is unadjudicable because
no ground truth exists outside the assignment. Same structure as a reviewer clearing its own
finding, one layer up in the instrument.

The fix is to establish ambiguity **independently of the hypothesis**, before it becomes gold.

## Method — blind

Each item's `claim_true` sentence alone. No source, no twin, no mention of tense, ambiguity, twins,
or the study:

> Below is one sentence from a software design document.
> Does it assert something about how the system behaves NOW?
> Answer with exactly one word: YES or NO.

4 models × 5 draws at temperature 1.0 = 20 judgments per sentence.
**Split score = 2·min(yes,no)/n** — 0 is unanimous, 1.0 is perfectly divided. An unambiguous sentence
produces agreement; a sentence carrying two readings produces a split. Ambiguity is thereby measured
as a property of the sentence, with no reference to anyone's taxonomy.

The taxonomy assignment was pinned in git at `ca3c05e`, **before these draws existed**.

## Result — the gradient holds, including the middle

| group | mean split | range | n |
|---|---|---|---|
| safe | **0.275** | [0.00, 0.80] | 4 items |
| moderate | **0.500** | [0.10, 0.80] | 4 items |
| exposed | **0.700** | [0.50, 1.00] | 4 items |

`r(assigned group rank, blind-measured split) = 0.561`, permutation **p = 0.034** (one-sided, 50,000
samples, seed 20260806).

The monotonic middle was named as the specific thing rationalisation cannot easily produce, and
`moderate` landed between the other two on an independent measurement. **Ambiguity is a property of
the sentences, not of the assigner's intuitions.** The reframe survives its dispositive test.

## But the taxonomy is a noisy proxy, and there is a better factor available

The group ranges **overlap heavily** — safe reaches 0.80 while exposed drops to 0.50. p = 0.034 at
n=4 per cell is thin, and two items are plainly misassigned:

- **`tense-03`, safe, split 0.80** — the originating example of the entire study. It is ambiguous,
  but by **presupposition**, not deontic modality: *will no longer X* carries a claim about the
  current state. The taxonomy misassigned it; the blind test caught it. That is the blind measure
  outperforming the construct it was validating.
- **`tense-10`, moderate, split 0.10** — near-unanimous *asserts about NOW*, so its `claim_true` does
  not read as a future claim at all. A different defect, also invisible to the taxonomy.

**So do not use the assigned group as the experimental factor. Use the measured split score.** That
removes the circularity completely rather than mitigating it: gold depends on an independently
measured property of each sentence, and no linguistic judgment of mine or anyone's enters the
scoring path. The taxonomy becomes what it should be — a hypothesis about *why* sentences split,
testable against the measurement, and already wrong on 2 of 12.

## The contract question

Offering an `AMBIGUOUS` verdict tells the model ambiguity is the subject. That is a demand
characteristic: it converts *does the model notice* into *can the model notice when told to look*.
The originating incident had no such button — a reviewer with a normal task resolved silently.

The disposition measurement already exists and matches the incident better: `clarity: 4`,
`needs_more_information: false`, `would_start_without_clarifying: true` on 16/16, including every
draw that resolved the modal wrongly. Those fields *were* the ambiguity channel under the three-way
contract, and they were dead.

**Three-way stays primary; four-way runs as a secondary capability arm.** If a model outputs
`AMBIGUOUS` when offered but reports `clarity: 4` when not, that gap is the finding, and it is
sharper than either arm alone.

## Still required before any confirmatory draw

- **Fresh items built to the ambiguity spec.** If the effect lives only in the 12 that broke, it is
  an artifact of this set.
- **Reverse polarity** — items where the *present-tense* member is the ambiguous one. If ambiguity is
  the mechanism the effect flips; if it does not, the finding is about `will` specifically, which is
  a different paper and the ambiguity framing would be wrong.
- **A prediction the old question does not make**, declared before firing.
- **Blind-split scores measured for every item and pinned to git** alongside the assignment, before a
  single confirmatory draw. If the factor can move after data arrives, none of this holds.
- n=4 per cell is thin. More items per group, not more draws per item — the draws are correlated.
