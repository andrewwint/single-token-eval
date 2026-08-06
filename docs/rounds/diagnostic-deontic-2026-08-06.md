# Diagnostic: does the future construction admit a deontic reading?

96 draws, under a dollar. **Not a measured round** — no freeze, no pre-registration, N=1 per cell,
and it used a diagnostic-only contract carrying a `rationale` field the scored contract does not
have. Recorded so it can never be mistaken for a result.

## The prediction, declared before running

An external review argued that the 5/8 smoke result was an **item effect, not a model effect**: all
four models handled `tense-01`, and three of four failed `tense-02` identically. Its explanation was
linguistic. Compare the two truthful claims:

- `tense-01` — *the webhook handler **will be switched** to HMAC comparison* — a change-event.
- `tense-02` — *the reports route **will restrict** access to admins* — bare `will` + active verb in
  documentation register, which in specification English is standardly **deontic**. *The system will
  validate all inputs* is a requirement about the system now, not a prediction about next quarter.

Under the deontic reading the claim asserts something present, the source contradicts it, and
`CONTRADICTED` is **correct**. Three frontier models resolved the modal the requirements way. That
is not a miss; it is the second meaning.

The 12 tense pairs were sorted into three groups **before any draw**:

- **safe** (change-event or perfect aspect): 01, 03, 07, 11
- **moderate** (passive, change-flavoured but deontic-capable): 04, 05, 10, 12
- **exposed** (bare `will` + stative/normative predicate): 02, 06, 08, 09

## Result — the gradient is monotonic and `exposed` is perfect

Truthful member correctly judged `NOT_DETERMINABLE`, 3 frontier models × 4 items per group:

| group | correct | rate |
|---|---|---|
| safe | 8/12 | **67%** |
| moderate | 3/12 | **25%** |
| exposed | 0/12 | **0%** |

The prediction was pre-declared and it held. `exposed` failing 12 out of 12 is not noise.

A rationale from `tense-08` (opus, truthful) confirms the mechanism directly — the model read *"will
not execute without an explicit operator command"* as a requirement:

> The source explicitly says migrations run automatically at container start and execution is not
> gated on operator input, contradicting the need for an operator command.

## The founding case is one of the broken ones

`tense-03` was classed **safe** and scored **0/3**. It is the originating example of the entire
study — `no longer depends` → `will no longer depend`.

The rationales show it is not deontic. All three models read the future claim as asserting the
dependency is **already** absent:

> The source explicitly states get_user() reads from the in-process LRU cache before querying
> Postgres, so it does depend on the cache.

So there are **two distinct failure modes**, not one:

1. **Deontic `will`** — a requirement about the present (`exposed` group).
2. **`no longer` presupposition** — *will no longer X* carries a presupposition about the current
   state, and the models resolve the whole sentence against it. The taxonomy did not predict this.

`tense-07` split 2/3, which is the boundary case: `sonnet` read the absence of any migration plan as
contradicting a claimed future move, while `opus` and `haiku` called it not determinable.

## Consequence: most of the item set is unusable as built

At best 4 of 12 tense pairs are sound (01, 11, and conditionally 04, 07). The rest fail R2 — the
token changes which reading is available rather than flipping a single truth value — and R2 was the
rule the whole instrument rests on.

This is not a scoring bug. The items were built to a rule that English does not honour for the
future tense in specification register.

## What must not happen next

Do not rebuild the items by searching for constructions that produce discrimination. That is
selecting the instrument for its answer, which the spec now forbids. The taxonomy above is a
*finding* about which constructions are truth-conditional and which are modal, and it should be
reported as one.

The honest options, to be decided before more spend:

1. **Narrow the claim.** Keep only change-event futures, report the study as measuring that
   construction, and state the bound.
2. **Make the ambiguity the subject.** The `exposed` items are not broken items — they are evidence
   that a single token puts a sentence into two readings, and that every frontier model silently
   picks one. That is closer to the question this study was started to answer.
3. **Add a fourth verdict** (`AMBIGUOUS`) and measure whether models can report the ambiguity rather
   than resolve it silently. Related to the self-report finding below.

Option 2 is the one that matches the originating incident, where a reviewer read past a tense flip
because the sentence supported two readings.

## The self-report field is dead, and that is the finding

All 16 rows of the smoke: `clarity: 4`, `needs_more_information: false`,
`would_start_without_clarifying: true`. Four models, both items, both polarities, **zero variance** —
including the three frontier draws that resolved a genuinely ambiguous modal and got the target wrong.

The instruction was not ignored. It was **resolved**, confidently, with no signal that a resolution
had occurred.

As an instrument the field has no discriminative power. As a finding it is the strongest evidence in
the repo, because the confusion is invisible from the inside. **An earlier summary reported a clean
tier split on this field; that was read off the superseded binary-contract rows and is withdrawn.**

## Confounds that block reading any of the above as a measurement

- **N=1 everywhere.** No variance estimate exists anywhere in this repo.
- **Target position is confounded with item** — `tense-01` targets C2, `tense-02` targets C3. With
  two items in the smoke these cannot be separated. Randomise target position within item before any
  measured round, or a position effect and the deontic effect stay indistinguishable.
- **`parse_ok` is true on 16/16** — the parser's failure branch has never executed. It is an alert
  that has never fired, and C4 was a bug in exactly that branch. Force a malformed response through
  it before GATE B.
- **Rationales exist only for the model whose labels are least reliable.** Only `nova-micro`
  volunteered prose under the scored contract; the frontier models complied with JSON-only. The
  diagnostic contract above adds `rationale` deliberately, and it is why the two failure modes were
  separable at all.
