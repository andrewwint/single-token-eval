# CLAUDE.md

Guidance for working in this repo. Read `docs/single-token-inversion.md` and `openspec/project.md`
before making design decisions.

## What this is

A **controlled study**, not a shipping product. It measures whether a reviewer's verdict tracks a
single token in a claim — the operator/modal/quantifier/polarity/tense family where one token
inverts the meaning and the diff is nearly invisible.

**This file deliberately states no hypothesis and no expected result.** Items are authored in this
context, and a fixture built by something that knows what the study hopes to find is a leaked answer
key. Expectations live in a round's pre-registration, which is read only when opened.

## Core invariants (do not violate)

- **Twin members differ by exactly one token.** Asserted by the builder, not by review. This is the
  property the whole instrument rests on: if the two members differ anywhere else, a score difference
  no longer isolates the token.
- **Both members always fire.** A member is never built or run alone. The pair is the unit.
- **Score the pair, never a bare catch rate.** DISCRIMINATED means the false member was flagged and
  the true member was not. Report both component rates alongside it, so constant-alarm and
  never-flag behavior stay visible.
- **Grade deterministically.** Exact set comparison against the item's gold. No LLM judge.
- **Draws get no tools and no file access.** Single-shot `Converse`, temperature 0, `maxTokens` set
  explicitly. A draw with tool access invalidates the round — the agentic confound is the axis.
- **Freeze before firing.** The item file's sha256 is recorded in `items/FROZEN.md` and verified by
  the runner, which exits without spending on a mismatch.
- **Pre-register before spend.** `docs/rounds/round-N-prereg.md` is committed before any draw:
  pass criteria, per-cell N, budget cap, STOP conditions.
- **Pre-registered hypotheses are hypotheses, not targets.** Never tune an item after seeing results.
  If an item is found flawed, cut a new version with a changelog — never edit it in place. Any
  amendment to criteria carries dated provenance proving it preceded the data.
- **Exoneration must be derivable from the provided source.** Why a claim is true or false has to
  follow from the material the model is shown, never from an injected convention that contradicts
  its plain reading. An item that needs a stipulation measures convention-deference, not reading.
- **`items/` is answer keys.** Never publish them; never send this repo to a cloud review tier. Local
  review only.

## Conventions

- Go **spec-first via OpenSpec**: a `proposal.md` (Why / What Changes / Impact) approved before
  implementation code. Spec deltas use the `## ADDED Requirements` / `### Requirement:` /
  `#### Scenario:` format in `openspec/AGENTS.md`.
- **Prefer structure over prose for any always-fire obligation** — a builder assertion, a schema
  field, a test — over a note that hopes to be remembered.
- **Mutation-check the tests.** Break each scoring branch on purpose and confirm the matching test
  fails. A test that cannot fail is not a check.
- **Don't refactor mid-measurement.** If a round is live, leave the harness alone.

## Vendored helpers

`wilson_ci` and `discrimination_guard` are copied from the sibling `review-discipline-eval` study,
not imported. They are frozen statistical helpers with no live upstream, so a copy carries no drift
risk — unlike mirroring a predicate that changes. Record their origin in the module docstring.

## Commands

Nothing fires yet. The runner and scorer land after the proposal is approved; document their
invocations here when they do.
