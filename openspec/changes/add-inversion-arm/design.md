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
  "token_delta": { "from": "no longer depends", "to": "will no longer depend" }
}
```

The truthful twin is the same object with `polarity: "truthful"`, the token restored, and
`gold.false_claims: []`.

**`family`** covers the five kinds in `docs/single-token-inversion.md` §2 — `operator`, `modal`,
`quantifier`, `polarity`, `tense`. Report per family; an aggregate across families washes out real
differences the same way a catch rate washes across defect classes.

**`exoneration` is a build-time constraint, not metadata.** Why a claim is true or false must be
derivable from the material the model is shown, never from a stipulation that overrides its plain
reading. An item whose correct answer requires deferring to an injected convention measures
convention-deference, not reading — and inverts the capability being selected for.

## Factors and cell count

| Factor | Levels |
|---|---|
| Placement | in-diff, out-of-diff |
| Instruction regime | R0 bare, R1 flag-anything-untrue, R2 derive-from-source |
| Model tier | 3 frontier + 1 probe |
| Polarity | inverted, truthful (both always fire) |

12 pairs × 2 polarities × 2 placements × 3 regimes × 4 models × 5 draws = **2,880 draws**. That is
the full crossing. The pre-registration may cut regimes or draws to fit budget and must say so
explicitly rather than quietly sampling.

## The instruction regimes — the arm's real question

- **R0 bare.** "Review this change." No mention of claims, documents, or correctness.
- **R1 directed.** "Review this change. Flag any statement in the provided material that is not true
  of the source."
- **R2 derivation.** "Work out from the source what actually holds, then check every labelled claim
  against what you derived."

R2 is the cheapest possible version of a source-derivation discipline. If R2 closes the out-of-diff
gap and R0 does not, an instruction bought it. If R2 does not close it, the gap is not an instruction
problem — the more useful result of the two.

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
4. **Per-family N.** Twelve pairs across five families is 2–3 pairs each — enough to report a
   direction, not enough to rank families. Say which of those the round is claiming.
