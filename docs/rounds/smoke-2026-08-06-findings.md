# Smoke run — GATE C dry run, 2026-08-06

~50 draws, well under a dollar. Not a measured round: no freeze, no pre-registration. The point was
to read raw output by hand before spending, and it stopped the round.

## 1. Profile status is not entitlement

`opus-5`, `sonnet-5` and `opus-4-8` all list **ACTIVE** in `list-inference-profiles` and return
`AccessDeniedException: not available for this account` when invoked. Task 1 said "confirm model
access" and I confirmed the wrong thing — a listing, not a call.

Pinned by actual invocation instead: `opus-4-6-v1`, `sonnet-4-6`, `haiku-4-5`, and
`nova-micro` as the probe.

## 2. BLOCKING — the instrument does not measure what it was built to measure

Every frontier model flagged the target claim on **both** members. 7 of 8 pairs scored
`alarm(both)`: 100% catch rate, ~0% discrimination.

The cause is the task wording, not the items. The response contract said:

> `false_claims` lists the identifiers of any claims that are **NOT true of the source**.

A future-tense claim is neither true nor false of a present-state source — it is **out of scope**.
Asked which claims are "not true", a reasonable reviewer flags the unverifiable one. It is doing its
job; the question is malformed.

This was predicted before firing ("if truthful members get flagged across the board, that is an
instrument bug, not a result") and it cost pennies to confirm. That is what the dry-run gate is for.

## 3. The wording fix is real but insufficient — and is itself a result

Changing one clause, `NOT true of the source` → `CONTRADICT the source … a claim the source neither
confirms nor contradicts is NOT a contradiction`, moved **2 of 6** verdicts from `alarm(both)` to
`DISCRIMINATED`. Same items, same models, same temperature.

One clause changed a third of the outcomes. That is this study's own thesis, demonstrated on this
study's own instrument, before the study ran.

It is not enough: 4 of 6 still alarm.

## 4. STOP — do not tune the wording further

Iterating on phrasing until discrimination appears is optimising the instrument against observed
results. Pre-data instrument development is legitimate, but it has to be a **decision**, not a search.
Two more rounds of wording tweaks and the round would be measuring a prompt selected for producing
the answer.

**The real defect is a forced binary over a three-valued truth.** Gold for the truthful member is
"not false", which is not the same as "true", and the response contract has no way to say so.

Recommended fix, to be decided before any further spend: **three-way classification** —
`CONTRADICTED` / `SUPPORTED` / `NOT_DETERMINABLE`, with gold `CONTRADICTED` for the inverted member
and `NOT_DETERMINABLE` for the truthful one. Discrimination becomes correctly separating those,
which is what the items actually encode. No item rebuild required.

The rejected alternative is making the source establish the future fact so the truthful member is
genuinely true. That reintroduces forward-intent language in `source_fact` — the R5 tell that got
Gemini's draft rejected.

## 5. Working as designed

- Prompt renders correctly; claim order is seeded per item so twins share labels.
- Parse rate 16/16 after the model repin.
- `needs_more_information` splits cleanly by tier: opus/sonnet report clarity 4 and False;
  haiku/nova report clarity 1–2 and True. The gap table has signal to work with.
- **~270 in / ~105 out tokens per draw** — an order below the 2–4k design estimate, so the full
  crossing is far cheaper than the $35–45 budgeted. Re-estimate before GATE B.
