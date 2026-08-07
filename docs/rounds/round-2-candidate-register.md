# Round 2 candidate — does specification register change how `will` is read?

**PARKED. Not started, not approved, no measurement taken.** Recorded so it is not rediscovered, and
deliberately not folded into round 1.

## The question

Round 1 measures bare `will` in prose. But requirements are not usually written that way. They are
written in registers that **pin** modal meaning by convention:

- **RFC 2119** — `MUST` / `SHALL` / `SHOULD` / `MAY`, with `SHALL` defined as an absolute requirement.
- **Gherkin / BDD** — `GIVEN` / `WHEN` / `THEN`, where the `THEN` clause states an observable outcome.

If those conventions do what they claim, they should suppress the disagreement round 1 measured.

## Why this is a second factor, not a better instrument

Testing in BDD register does not measure the same thing more cleanly — it changes the thing being
measured. That is the point.

The round-1 finding is **descriptive**: four models disagree about `will`. A reader cannot act on it.
Adding register makes it **prescriptive**: if bare `will` splits 0.50 and `SHALL` splits 0.05, the
result is *write requirements in RFC 2119 register and most of the ambiguity goes away* — advice,
testable, and usable by anyone who writes specs.

## Prediction, with its falsifier — written before any measurement

**Predicted:** `SHALL` reduces ambiguity about *whether the sentence is a requirement* and does
**nothing for — possibly worsens —** ambiguity about *whether the behaviour is implemented*.

RFC 2119 pins `SHALL` = absolute requirement. It says nothing about implementation status. So
*"The endpoint SHALL reject unsupported Content-Type"* is unambiguously normative and unambiguously
**silent** about today's code. Under the blind question — *does this assert something about how the
system behaves NOW?* — that should push readers toward a confident **NO**, collapsing the split for
a reason that is not clarity about the system.

**Falsifier:** if `SHALL` items split at or above bare `will`, the convention does not pin the
reading and the prescriptive claim dies. If `SHALL` items split near zero **with high YES** — read as
describing the built system — the prediction is inverted and the register is actively worse, which
would be the more useful finding.

**Gherkin is predicted to behave differently again**, not merely less: *"THEN the request is
rejected"* is structurally a statement about observed behaviour, so it should read as present-tense
description. If it does, BDD register would be the one that *removes* the escape hatch bare `will`
provides.

## A design problem this candidate has to solve first

**The twin-pair instrument may not transfer.** Gherkin's `THEN` clause is conventionally present
tense, so there is no natural one-token future variant of it — *"THEN the request will be rejected"*
is not idiomatic Gherkin. If the pairing device does not apply, round 2 measures the **split of a
single requirement-shaped sentence per register**, not paired discrimination.

That is a weaker instrument and the weakness must be declared up front, not discovered. It also
means round 2 is not a drop-in reuse of round 1's harness: the blind-split measurement and the cue
audit transfer; `build_items`' one-token assertion does not.

## Method sketch

Same 48 source facts. Each claim rewritten into three registers, authored before any measurement,
construction labels stripped:

| register | example |
|---|---|
| bare `will` | The endpoint will reject requests with an unsupported Content-Type. |
| RFC 2119 | The endpoint SHALL reject requests with an unsupported Content-Type. |
| Gherkin | WHEN a request arrives with an unsupported Content-Type / THEN the request is rejected. |

Blind measure as in round 1 — *does this assert something about how the system behaves NOW?* — 4
models × 5 draws. Register is a within-item factor, so each sentence is its own control and the
panel offsets (opus 0.73, sonnet 0.24) cancel within item.

Cost is small: the blind probe returns one word, so this is roughly the size of the round-1
measurement.

## Why it is parked rather than started

Round 1 is blocked on **decisions**, not on ideas. Starting a new factor now would make *"the round
did not resolve, so we ran a different round"* the shape of the project — the drift pattern this
repo has already corrected twice. Round 1's outcome, including the possibility that its factor is
abandoned, gets settled on its own terms first.

## The loop worth naming

This repo's own `openspec/` specs are written in exactly this register — `SHALL`, `#### Scenario:`,
`WHEN`, `THEN`. Round 2 would measure the language the project writes its own requirements in, and
the result would apply to those specs first.

Related: `docs/rounds/round-1-prereg.md`, `docs/rounds/round1-split-measure-diagnostic.md`.
