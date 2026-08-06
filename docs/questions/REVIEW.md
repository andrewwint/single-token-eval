# Draft review — three vendor sets

Checked mechanically (word-level diff, declared-vs-observed `token_delta`, forward-intent language in
`source_fact`, decoy-vs-source similarity) rather than by eye. Verdict: **claude-online is the base
set; gemini's decoys are the thing worth taking from it; chatgpt is not usable as-is.**

| | multi-edit | delta wrong | intent-tells in source | restated decoys |
|---|---|---|---|---|
| chatgpt | 2/12 | 0/12 | 0/12 | **28/36** |
| claude-online | 1/12 | 1/12 | 0/12 (see below) | 15/36 |
| gemini | 2/12 (really ~12) | **~12/12** | **8/12** | **0/36** |

## Ruling: R1 is unsatisfiable as written, and the founding case is what breaks it

English future tense is periphrastic — it is built with an auxiliary — so "exactly one token" cannot
survive contact with most of the family. The diff shows precisely where it breaks:

- `are` → `will be`, `has` → `will have`, `checks` → `will check` — **one contiguous edit.** Fine.
- `no longer depends` → `will no longer depend` — **two discontiguous edits** (insert `will`, inflect
  `depends`→`depend`), because the matching `no longer` sits between them.

The second is the originating example. A strict R1 would exclude the case that motivated the study,
which is a sign the rule is wrong rather than the item.

**Amended rule: one minimal grammatical edit — a single tense/aspect change, however many surface
tokens it takes.** The construct is preserved exactly: maximum semantic leverage, minimum visual
footprint. Record `edit_ops` per item so the footprint is a reported property rather than a
pass/fail gate.

This is a definitional fix made **before any data exists**, not a threshold moved after seeing
scores. Dated here for the pre-registration.

## Per-vendor

**chatgpt — unusable as the base.** Constructions are clean and its `token_delta` fields are honest,
but **28 of 36 decoys are restatements of `source_fact`** (e.g. source says "The authorization layer
checks role memberships only", decoy says "The authorization layer checks role memberships"). A
decoy that repeats the source exerts no false-positive pressure, so the FP channel is dead: every
model would score FP = 0 for a reason having nothing to do with its judgement. Its `source_fact`
entries are also thin and abstract — they assert what the system does without naming anything a
reviewer could check against, which weakens R4.

**gemini — best decoys, worst everything else.** Its decoys are the only genuinely paraphrased set in
the three (0/36 restatements) and they are worth harvesting. Against that:
- **`token_delta` is systematically truncated** — `"populates" → "will"`, `"are" → "will"`,
  `"has" → "will"`, `"no" → "will"`. The checker only caught two because it matched leniently on
  substrings; by eye it is wrong in essentially every item.
- **8/12 `source_fact` entries announce the answer** — "scheduled for implementation next sprint",
  "remains unmerged in code review", "under development in a separate feature branch", "slated for
  version 2.4". Both members share it so the pairing still holds, but it primes a reader that the
  present-tense claim is false, which inflates the catch rate for a reason unrelated to reading tense.
- **tense-05 and tense-12 use `shall`, which is a modal, not a tense.** "Tenant telemetry data shall
  be isolated" is a requirement statement. Wrong family — those belong to a modal round.

**claude-online — the base set.** Concrete, code-anchored `source_fact` entries that name checkable
artifacts (`crypto.py`, `backoff.py`, the `dlq` table, the `TOKEN_BUCKET` flag), which is what makes
R4 real rather than nominal. Eight distinct constructions, twelve distinct domains. It also
self-flagged its own two weakest items, which is the behavior the prompt asked for and the other two
did not produce.

Two corrections applied:
- **tense-07** used a bare future perfect ("will have moved") with no by-clause, which reads stilted
  and risks cueing on register rather than tense — it self-flagged this. Rewritten to
  `has moved` → `will move`.
- **The one R5 flag on tense-07 is a checker false positive.** "behind the `TOKEN_BUCKET` flag, which
  is disabled in every environment" states present configuration, not future intent. My regex was
  too broad; Claude's set has **no genuine intent-tells**.

## Residual risk worth recording

Seven of twelve items sit on security-adjacent surfaces (HMAC, authz, credential logging, encryption,
session cookies). Models are heavily tuned to flag security problems, so both rates may run high. The
twin pair controls for it — both members are equally security-framed, so discrimination is unaffected
— but it is a reason not to read the component rates as general.

## Blocking defect: the item set is single-polarity

**In all 12 items `claim_false` is the present-tense member and `claim_true` is the future-tense
member.** That is how the generation prompt asked for them, and it is a hole. A model can score 100%
discrimination with a rule that never reads `source_fact`: *flag the present-tense claim.* The rule is
even defensible — a present-tense claim about an unbuilt feature is the classic documentation bug — so
it would look exactly like source-derivation while being pattern-matching, which is the one
distinction this study exists to make.

The fix is already established practice here. From the judge spot-read pre-registration:

> a **single-polarity** gate is passable by a degenerate constant … that reasons about nothing. So the
> set also carries **3 reverse-polarity singles**.

**Add 3 reverse-polarity singles in which the FUTURE-tense claim is the false one** — `source_fact`
establishes that the planned change was cancelled and its implementation removed, so the future claim
asserts something that will not happen. Build them as **singles, not pairs**: once the plan is dead
both tenses are false, so there is no clean twin to pair against. A "flag the present tense" strategy
scores 0/3 on them by construction.

These must exist before GATE A, or the cold read has to be paid for twice.

## Remaining work

- 3 reverse-polarity singles (above) — blocking.
- The 4 `polarity` calibration pairs are not drafted. They need the same treatment and should come
  from a **separate generation run**, so a defect in how the tense items were authored cannot
  silently affect the family whose job is to detect it.
