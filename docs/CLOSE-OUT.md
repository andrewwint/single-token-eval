# Close-out — the study is frozen

**Frozen 2026-08-12.** Round 1's verdict arm never fired. Round 2 (the register study) is cancelled,
not parked. No further measurement will be taken on this item set.

## What ran

| | |
|---|---|
| Blind split measurement | **1,920 judgements** — 48 pairs × both members × 4 models × 5 draws |
| Deontic diagnostic | 96 draws, exploratory |
| Paraphrase validation | 240 draws, exploratory |
| Smoke runs | ~50 draws, two contracts, one superseded |
| **Verdict arm** | **never fired** |

Total spend: under $5.

## What was found

Four models, the same sentences, no context, one question — *does this assert something about how
the system behaves now?*

**Opus 0.73 · Haiku 0.68 · Nova 0.50 · Sonnet 0.24** on `will`-form claims, against a `claim_false`
control at **1.00 / 0.99 / 0.87 / 1.00**. The control is what rules out a misread question; the two
models furthest apart both sit at 1.00 on it, so the headline comparison carries no comprehension
confound.

Underneath the panel offset there is real sentence-level signal — item explains **61%** of the
model-centred variance and all six pairwise correlations are positive. The models disagree about
their *baseline* for `will` and agree about *which sentences are slippery*.

## Why it stopped where it did

Three things were open and none was resolved:

1. **An independent cold read** of the item set, which gated band assignment. The first reviewer
   recused after receiving the diagnostic before the sentences — correctly, since it could no longer
   certify its own blindness.
2. **The split-measure decision.** The pre-registered factor turned out to be ~70% between-model
   offset. A model-centred fix exists and works, and adopting it would have been the *third*
   correction to one measure. A sequence of individually justified corrections converging on the
   version that finally works is hard to distinguish from fitting the instrument to its own data.
3. **A human baseline.** Every reader on both sides of the measurement is a language model. Nothing
   internal to the design can detect a convention the four share and people do not.

Stopping at three corrections was the discipline working, not the study failing. The panel-offset
result is complete on its own and needed no verdict arm.

## The durable finding is about the instrument, not the sentences

Nine declared controls turned out not to fire, and every one was found by something structural
rather than by care:

- `--budget` was parsed and never enforced; `--budget 0.00` fired all 5,600 draws
- the freeze gate fell open on a `FROZEN.md` with no digest line — 5,584 calls, exit 0
- "REFUSING TO SHIP" wrote its 48 payload files *before* refusing, and overwrote a good key
- `hit` was unpinned from the target claim, so flagging only decoys scored as a catch
- reverse-singles pooled a bare catch rate into discrimination — flag-everything scored 0.600
- the mutation sweep silently truncated at 7 of 10 mutants
- three "surviving" mutants were degenerate fixtures that could not fail
- the GATE-A cue test was one-sided, passing a perfect anti-correlated tell
- **`p01` broke the one-token invariant despite my own hand-verification of that exact property**

The last one is the argument in miniature: the ad hoc check and the item came from the same
understanding, so the hole in one was the hole in the other.

## Why `items/` is published

It was withheld while measurement was live, because publishing an item set makes it training data
and burns any future measurement on it. With the study frozen there is no future measurement to
protect, and the balance inverts: published items let a reader check whether `claim_false` is
genuinely unambiguous, whether the pairs are fair, and whether the finding survives their own
reading. Auditability is now worth more than contamination resistance.

**If this ever unfreezes, the items are spent.** Any new round needs new sentences.
