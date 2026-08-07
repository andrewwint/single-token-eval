# The pre-registered factor is contaminated. The signal underneath it is real.

1,920 blind judgements, 48 candidates, both members, 4 models × 5 draws. **No verdict draw has
fired.** This concerns the independent variable only; the outcome does not exist yet.

## The controls pass

- **STOP condition (prereg line 8)**: ρ(`split_true`, `split_false`) = **−0.091, p = 0.539**. No item
  splits high on both members. `claim_false` mean split 0.071 against `claim_true` 0.444. Split is
  not tracking future-tense marking or item weirdness.
- **The question is understood**: YES-rate on `claim_false` — a plain present-tense assertion — is
  1.00 / 1.00 / 0.99 / 0.87 across the four models. Disagreement is specific to `will`.

## The factor as pre-registered does not measure what it was meant to

**70% of the pooled split is between-model, not within-model** (mean within-model split 0.131 vs
pooled 0.444). The models hold radically different baselines for how `will X` reads:

| model | YES-rate on `claim_true` |
|---|---|
| opus-4.6 | 0.73 |
| haiku-4.5 | 0.68 |
| nova-micro | 0.50 |
| sonnet-4.6 | **0.24** |

Opus reads a bare-`will` claim as asserting about the present nearly three times as often as Sonnet
does, on the same 48 sentences. A pooled split score therefore encodes *how far apart these four
particular readers sit*, which is a property of the panel, not of the sentence.

## But the sentence-level signal is real, and it was hidden by the offsets

Removing each model's own baseline and re-testing:

- **Item explains 61%** of the model-centred variance.
- **All six pairwise correlations are positive and significant** (ρ = +0.285 to +0.663, every
  p ≤ 0.049). The models agree on *which* sentences read as present-asserting.

The raw per-item correlations looked near-zero only because the offset dominated. This is a
textbook rater-offset problem and centring is its textbook fix.

## Why I am not applying the fix unilaterally

Switching the factor from raw pooled split to a model-centred score would be a **change to a
pre-registered definition, made after seeing the independent variable's distribution**. The pinned
thresholds (`≤0.20`, `0.21–0.60`, `≥0.61`) are defined on the raw scale and do not map onto a
centred one, so adopting it forces new thresholds — and re-deriving thresholds after looking at data
is the exact move the pre-registration exists to prevent, even when the outcome is still unobserved.

It is also the **third** correction this measure has needed: assigned taxonomy → measured raw split →
now model-centred. Each correction was justified on its own, and a sequence of individually
justified corrections converging on the version that finally works is indistinguishable from fitting
the instrument to the data. Naming that is more useful than another self-approved fix.

**Decision required from the human and an independent reader. Options as I see them:**

1. **Amend the prereg** to a model-centred factor, with thresholds re-derived from quantiles of the
   centred distribution rather than round numbers, dated and recorded as post-IV / pre-DV.
2. **Fire as pre-registered** on the raw split, accepting that the factor is 70% panel-disagreement,
   and report the centred analysis as a secondary.
3. **Treat the offset itself as the finding** and stop trying to score verdicts against it. Four
   frontier models disagreeing this sharply about whether `will X` asserts something about now — with
   the present-tense control at 1.00 — is a result about specification language, not about any one
   sentence.

## Band fill under the pre-registered factor, HELD

Validity (`split_false ≤ 0.20`): **43/48 pass**; cut `m07 m24 m33 m46 m48`.

| band | range | n | status |
|---|---|---|---|
| b1 | 0.00–0.20 | 13 | OK |
| b2 | 0.21–0.40 | **4** | **UNDERFILLED** (target 6) |
| b3 | 0.41–0.60 | 12 | OK |
| b4 | 0.61+ | 14 | OK |

b2 is reported unfilled, not back-filled. No candidate may be authored or regenerated now that its
own split is known (prereg line 4).

## Not yet done

Bands remain **unassigned** pending the outside cold read, which gates assignment (prereg line 7).
The read's unique contribution is unaffected by any of the above: no automated check here can detect
a `claim_true` that accidentally reads deontically, and that is how `tense-02` died.

---

## Cold read contaminated — recorded as a failure, not written around

The reviewer holding the diagnostic received the 96 sentences afterwards and **recused**. That is
correct: it holds the validity cuts, the band counts, and the most-future-read list, and now holds
the sentences those ids attach to. It cannot partition its own reactions into the ones predating
the leak, and self-certifying that partition is the disposition-independence violation this study
exists to detect.

**Cause: the ordering was correct and enforced nowhere.** Send-order lived in message discipline.
Fourth instance this week of a prose obligation that did not self-enforce — after the budget flag,
the freeze gate, and the refusal that shipped its files before refusing.

**Fix, structural:** `harness/build_cold_read.py` emits the packet from **exactly one input**,
`items/_measure-blind.json`. It cannot open the diagnostic, the splits, or the candidate file
because it never names them. Blindness is a property of the script's imports rather than of anyone
remembering which message goes first.

Its self-check was wrong the first time and is worth recording. Version one scanned for forbidden
vocabulary and refused on `cut` — a legitimate word in *"Writes have been cut over to the new
column."* A blacklist cannot tell metadata from English: it either false-positives on content or
misses a field nobody told it about. Version two whitelists **line shapes** — the fixed prompt, a
blank, an id, or an `A:`/`B:` sentence — so anything else is a leak by construction. Negative-tested
against three injected leaks.

## Construction check: a categorical variable is hiding inside the continuous factor

The 48 contain two visibly distinct constructions, and they do not split alike:

| construction | n | mean split | median | range |
|---|---|---|---|---|
| bare `will` + verb | 33 | **0.500** | 0.50 | [0.00, 1.00] |
| `have been Xed` → `will be Xed` | 15 | **0.320** | 0.30 | [0.00, 0.90] |

Mann-Whitney U = 332, **p = 0.029** one-sided. And the band composition is lopsided at the top:

- low band (≤0.20), n=16 — 7 perfect→future, 9 bare will
- **high band (≥0.61), n=15 — 2 perfect→future, 13 bare will**

This is the old safe/exposed distinction surviving into the fresh set, as predicted. It is a
**finding, not a defect** — but it changes what the verdict arm tests. A continuous split factor
with a categorical variable inside it means an effect attributed to "ambiguity" could be an effect
of "bare `will` versus perfect aspect", and the two are not separable at n=48 with this imbalance.

Consequence for the pending decision: any option that fires a verdict arm must say whether
construction enters the model as a covariate, and the answer has to be fixed before bands are
assigned.
