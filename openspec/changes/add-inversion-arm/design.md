# add-inversion-arm — design

## The instrument in one paragraph

A pair is two artifacts identical except one token, each shown with the same change under review and
the same source. A reviewer whose verdict **tracks the token** flags the false member and clears the
true one. A reviewer that reads tone, alarms constantly, or scans only the diff cannot separate them.
Discrimination is therefore the whole measurement, and any answer-key leak is neutralized by
construction because it leaks identically into both members.

## Item schema

```json
{
  "pair_id": "tense/01",
  "family": "tense",
  "placement": "out-of-diff",
  "polarity": "inverted",
  "artifact": "the document excerpt, claims labelled [C1]..[Cn]",
  "target_claim": "C3",
  "change_under_review": "the diff the reviewer is asked to review",
  "source": "the code the claims are about",
  "gold": { "false_claims": ["C3"] },
  "exoneration": "derivable from source: gate.py:41 reads verdict_emitted at request time",
  "token_delta": { "from": "no longer depends", "to": "will no longer depend" },
  "formal_reading": {
    "inverted":  "enforced(now) == True",
    "truthful":  "enforced(now) == False AND enforced(future) == True",
    "source_fact": "enforced(now) == False"
  }
}
```

**`formal_reading` is the column that makes an item checkable by inspection.** The wording and the
gold label are both recorded above, but without the logical form in between there is nothing to
verify the label *against* — you are trusting whoever wrote it. Writing the reading down forces the
question "does this token actually change the truth value, or only the emphasis?", which is the
failure mode that produces a non-discriminating pair. Report per reading-shape as well as per family;
a token that flips a quantifier and a token that flips a tense may not be the same difficulty.

This is also the honest form of "three faithful readings of one sentence": if a single wording admits
more than one formal reading, the item is ambiguous rather than inverted, and belongs in a separate
class or gets cut.

The truthful twin is the same object with `polarity: "truthful"`, the token restored, and
`gold.false_claims: []`.

**`family` is narrowed to `tense` for round 1, with `polarity` as a calibration family.** The five
kinds in `docs/single-token-inversion.md` §2 spread twelve pairs into 2–3 each — enough for a
direction, not a ranking. Tense is the right one to concentrate on: it is the originating case
(`no longer depends` → `will no longer depend`), the least covered in the existing literature
(negation, quantifiers and connectives are well studied; tense in a *claim about system state* is a
different object from tense in narrative), and the most common real defect, because specification
documents routinely describe intended state in the present tense.

**Why a calibration family is not optional.** If tense shows no effect, that reading is ambiguous
between *models handle this fine* and *the instrument is dull*. A small set of `polarity` pairs —
the family where the literature says there should be an effect — separates those two. It is the
discrimination guard applied to families instead of tiers, and without it a null result cannot be
interpreted at all.

**`exoneration` is a build-time constraint, not metadata.** Why a claim is true or false must be
derivable from the material the model is shown, never from a stipulation that overrides its plain
reading. An item whose correct answer requires deferring to an injected convention measures
convention-deference, not reading — and inverts the capability being selected for.

## Factors and cell count

| Factor | Levels |
|---|---|
| Placement | in-diff, out-of-diff |
| Instruction regime | R0 bare, R1 flag-anything-untrue, R2 derive-from-source, R3 disclosed |
| Model tier | 3 frontier + 1 probe |
| Polarity | inverted, truthful (both always fire) |

16 pairs (12 tense + 4 polarity calibration) × 2 polarities × 2 placements × 4 regimes × 4 models ×
5 draws = **5,120 draws**, roughly $35–45. That is the full crossing and it is above the original
estimate; the pre-registration may cut placement or a regime to fit budget, and must say which and
why rather than quietly sampling.

## The instruction regimes — the arm's real question

- **R0 bare.** "Review this change." No mention of claims, documents, or correctness.
- **R1 directed.** "Review this change. Flag any statement in the provided material that is not true
  of the source."
- **R2 derivation.** "Work out from the source what actually holds, then check every labelled claim
  against what you derived."
- **R3 disclosed.** The system prompt states plainly that this is a study of whether single-token
  changes to a claim are noticed, and asks for the model's honest reading.

R2 is the cheapest possible version of a source-derivation discipline. If R2 closes the out-of-diff
gap and R0 does not, an instruction bought it. If R2 does not close it, the gap is not an instruction
problem — the more useful result of the two.

**R3 is a condition, never the default.** Disclosure is not a hint the twin pair neutralizes; it is
an instruction that changes the task. Both members receive it, so the pairing still holds, but both
members are now told what to look for — which measures *can it find a tense flip when told to look
for tense flips*, an easier and different question. Held as its own cell, the R0→R3 contrast is
worth having: it separates capability from attention. If disclosure closes the gap, nobody had told
the reviewer to look. If it does not, prompting is not the lever.

Framing note: a model does not meaningfully consent, and reading R3's replies as introspection would
over-claim. R3 is an experimental condition, and *whether disclosure changes behavior* is a result to
report, not an assumption to build on.

## Two outputs per draw, and the gap between them

Every draw returns both a behavioral answer and a self-report, in one JSON object:

```json
{
  "false_claims": ["C3"],
  "self_report": {
    "clarity": 4,
    "needs_more_information": false,
    "would_start_without_clarifying": true,
    "understanding": "one sentence, in the model's own words, of what it was asked to do"
  }
}
```

`false_claims` is graded deterministically as specified. The `self_report` block is **never graded on
its own** — self-reported confidence is unverifiable in isolation, and a model saying it understood
tells you only what it says about itself.

The measurement is the **gap**: how often does a draw report high clarity and no need for more
information, and get the target claim wrong? That is deterministically checkable, because the
behavioral half is graded independently on the same call.

Report the four cells, not a correlation:

|  | correct | wrong |
|---|---|---|
| **reported clear, would proceed** | fine | **the finding** |
| **reported unclear, wanted more info** | cautious | appropriately stuck |

The bottom-right of that table is the benign case — a model that says it is confused and is wrong has
at least signalled. The top-right is the one that matters: confident, well-behaved, and wrong, with
nothing in its output to warn a reader. `understanding` is stored as free text for qualitative read;
it is not scored, and no LLM judge is introduced to score it.

## Transport

`bedrock-runtime` `Converse`, `temperature: 0`, `maxTokens` set explicitly. An unset value defaults
to the model's maximum and silently reserves far more quota than needed, which is a known cause of
unexpected throttling.

**Model IDs are resolved at build time, never written from memory.** Task 2 runs
`aws bedrock list-foundation-models`, confirms model access in the target region, and pins exact IDs
into the runner. The probe tier should be genuinely weaker or non-Anthropic so the discrimination
guard has something to fail against.

Response is requested as a JSON object; a small extractor tolerates fenced or prose-wrapped JSON. A
draw that fails to parse is recorded `parse_ok: false` and excluded, never counted as a miss.

## Cost

Roughly 2–4k input and a few hundred output tokens per draw. Full crossing lands near **$20–25**,
dominated by the top tier — under half of what an agentic round costs, which is what makes full
crossing affordable instead of a sampled design. The runner carries a budget cap and resumes from
done-keys, so a stop is never a loss.

## Vendored helpers

`wilson_ci` and `discrimination_guard` are copied from `review-discipline-eval`, not imported. They
are frozen statistical helpers with no live upstream, so a copy carries no drift risk — unlike
mirroring a predicate that changes, which is a coupling problem that study had to manage explicitly.
Record the origin and copy date in the module docstring.

## What this design does not claim

No comparability with the sibling study's numbers. Those measured a plugin, agentic, with tools, on
code, non-hermetic; these measure a bare model, single-shot, tool-free, on prose, hermetic. They
share the phrase "out-of-diff" and nothing else. A cross-artifact difference reads like a finding and
usually isn't — pin the baseline before comparing, or don't compare.

## Open questions for the pre-registration

1. **Pass criteria.** Discrimination is a rate; what floor counts as "tracks the token"? Locked
   before firing, whatever it is.
2. **Regime ordering.** All three regimes in one round, or R0 first as a baseline and R2 only if R0
   shows a gap? One round is cleaner, staged is cheaper.
3. **`[C1]` labelling is itself an intervention.** Labelled, numbered claims are far more reviewable
   than prose in the wild, so the measured discrimination is a **ceiling**, not an estimate. State
   the bound; do not generalize past it.
4. **Calibration-family N.** How many `polarity` pairs are enough to license the reading "tense showed
   no effect and the instrument was working"? Four is a guess; state the floor and what a null on the
   calibration family would mean (the round is uninterpretable, and says so).
5. **Budget vs. crossing.** The full crossing is now ~5,120 draws / $35–45. Decide before firing
   whether to cut placement or a regime, and say which — a quiet sample is worse than a declared cut.
6. **Self-report scale.** `clarity` as 1–5 invites false precision. Consider a three-level scale, and
   pre-declare which levels count as "reported clear" for the gap table, before seeing any responses.
