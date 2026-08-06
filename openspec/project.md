# project.md — why this repo exists

## The question

Does a reviewer's verdict track a **single token** in a claim?

Not "does it catch bugs" — that is measured everywhere. This measures the narrow, sharp case: one
token moves, the meaning inverts, and the diff is nearly invisible. `<` / `>`. `must` / `must not`.
`all` / `any`. An inserted `not`. `is` / `will be`.

## Where it came from

A line of documentation asserted that a safety gate **no longer depends** on a model producing the
correct verdict. At that commit it still did; the honest sentence was **will no longer depend**. One
word separates a present-tense enforcement claim from a statement of intent, and a careful
independent reviewer read past it.

The generalization is the reason this is a study and not an anecdote:

> An honesty claim is a semantic assertion, and its truth flips on a single token exactly the way a
> conditional flips on one operator. So prose claims deserve code-level review rigor — because they
> invert on single tokens the same way code does.

## Why this class specifically

It is simultaneously the **most dangerous** defect class and the **most discriminating** fixture
class, for the same reason: it survives a surface read and inverts the truth. That alignment is rare.
The fixture is hard for exactly the mechanism reason worth measuring — it tests **source-derivation,
not diff-scanning**.

## Why a separate repo

A sibling study (`review-discipline-eval`, under `PRODUCTS/discipline/`) pressure-tested an
orchestration skill and a review plugin by driving a local coding agent. It is a different subject
with a different contamination model, and its work is largely done.

Three things separate this one:

1. **Transport.** Draws here are single-shot Bedrock `Converse` calls, not agent runs. That removes
   the confound between *did the model catch it* and *did the agent go looking*.
2. **Hermeticity.** A local agent reads `~/.claude` — global agents, skills, settings, memory, MCP
   servers — none pinned, none recorded. The sibling study had to **disclose that as an open bound**,
   because relocating the config broke keychain auth on the measurement host. A `Converse` call has
   no such surface: the prompt is the entire input.
3. **Authoring context.** Items are authored inside this repo. A repo whose always-loaded context
   states the study's hypotheses is a poor place to build fixtures that must not telegraph their
   answer. This repo's `CLAUDE.md` carries conventions only.

What it deliberately does *not* claim: comparability with the sibling study's numbers. Those measured
a plugin, agentic, with tools, on code, non-hermetic. These measure a bare model, single-shot, no
tools, on prose, hermetic. They share vocabulary, not a baseline. Pin the baseline before comparing —
a cross-artifact difference reads like a finding and usually isn't.

## What "done" looks like

A pre-registered round, fired within its budget, with per-cell discrimination reported and a findings
doc written against the locked criteria — including the outcome *"the item set could not separate the
tiers,"* which is a result and not a failure.
