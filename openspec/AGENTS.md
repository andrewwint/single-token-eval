# OpenSpec conventions

> Hand-authored scaffold (the `openspec` CLI is not installed). Running `openspec update` later will
> regenerate this file in the canonical form.

This project uses spec-driven change proposals. Three stages:

1. **Propose** — create `openspec/changes/<id>/` with a `proposal.md`, `tasks.md`, an optional
   `design.md`, and spec deltas under `specs/<capability>/spec.md`. Do not write implementation code
   yet.
2. **Approve** — the human reviews the proposal. Nothing is built until it is approved.
3. **Implement & archive** — build against the tasks; when shipped, fold the deltas into
   `openspec/specs/<capability>/spec.md` (the source of truth) and move the change to
   `openspec/changes/archive/`.

## Layout

```
openspec/
  project.md                    # project context (source of truth for "why")
  AGENTS.md                     # this file
  specs/<capability>/spec.md    # current, shipped truth
  changes/<id>/
    proposal.md                 # Why / What Changes / Impact
    tasks.md                    # implementation checklist
    design.md                   # technical decisions (optional)
    specs/<capability>/spec.md  # delta only
```

## Spec delta format

```
## ADDED Requirements
### Requirement: <short name>
The system SHALL <behavior>.

#### Scenario: <short name>
- **WHEN** <trigger>
- **THEN** <observable outcome>
```

Use `## MODIFIED Requirements` / `## REMOVED Requirements` for changes to shipped specs. Every
requirement needs at least one scenario. Keep requirements testable and observable.

## A note specific to this repo

Spec deltas here describe **measurement apparatus**, so "testable and observable" is strict: a
requirement whose scenario cannot be checked without firing a paid round belongs in a round
pre-registration (`docs/rounds/`), not in a spec. Specs govern the instrument; pre-registrations
govern a run of it.

## Active changes

- `add-inversion-arm` — the study's first arm. **Proposed, not approved.**
