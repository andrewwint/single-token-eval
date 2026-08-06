# inversion-arm Specification (delta)

## ADDED Requirements

### Requirement: Items ship as twin pairs differing by exactly one token
Every item SHALL be a pair of artifacts byte-identical except for the inverted token, where one
member's target claim is TRUE of the accompanying source and the other's is FALSE. The pair SHALL be
the unit of construction; a member SHALL NOT be built or fired alone.

#### Scenario: members differ somewhere other than the token
- **WHEN** the builder diffs the two members and finds any difference beyond the declared token
- **THEN** the build fails loud and the pair is not admitted to the frozen set

#### Scenario: context telegraphs the answer
- **WHEN** surrounding prose, a claim label, or formatting hints at the correct token direction
- **THEN** the hint is present identically in both members and cannot produce a differential score —
  the pairing, not a cold read, is the load-bearing defense

### Requirement: A pair scores only on differential discrimination
The arm SHALL score a pair as DISCRIMINATED only when the false member's target claim is flagged AND
the true member's target claim is not. It SHALL NOT report a bare catch rate as the headline metric,
and it SHALL report both component rates alongside every discrimination figure.

#### Scenario: a model flags both members
- **WHEN** the majority verdict flags the target claim on both members of a pair
- **THEN** the pair scores NOT DISCRIMINATED and the behavior is reported as constant alarm, never
  as a catch

#### Scenario: a model flags neither member
- **WHEN** the majority verdict flags the target claim on neither member
- **THEN** the pair scores NOT DISCRIMINATED as a miss

### Requirement: The response contract is three-valued
Each artifact SHALL carry visibly-labelled claims, and the model SHALL return one verdict per claim
from `CONTRADICTED` / `SUPPORTED` / `NOT_DETERMINABLE`. The arm SHALL NOT ask a binary
true/false question of a claim the source cannot settle.

#### Scenario: a claim the source neither establishes nor refutes
- **WHEN** a future-tense claim is judged against a source describing only present state
- **THEN** `NOT_DETERMINABLE` is available and is the gold verdict — a binary contract forces the
  model to call an out-of-scope claim false, which collapses discrimination and measures the
  question's malformation rather than the model's reading

#### Scenario: gold differs by family
- **WHEN** the truthful member's target claim is scored
- **THEN** gold is `NOT_DETERMINABLE` for `tense` (the future claim asserts nothing about now) and
  `SUPPORTED` for `polarity` (the source establishes the correct polarity)

### Requirement: Grading is deterministic comparison, never an LLM judge
Grading SHALL compare the returned verdicts against the item's gold by exact value. No model SHALL
be used to score another model's output.

#### Scenario: a response cannot be parsed
- **WHEN** a draw's response yields no parseable verdict map
- **THEN** the draw is recorded `parse_ok: false`, excluded from scored draws, and counted in a
  per-model parse-failure total — it is never silently scored as a miss

### Requirement: Every draw retains its raw response
The runner SHALL store the model's response text verbatim on the draw row, alongside the parsed
result.

#### Scenario: the parser or the scoring rule changes
- **WHEN** a scoring rule is revised after a round has fired
- **THEN** the stored round is re-scorable from the retained text without re-spending, and a
  re-score SHALL NOT modify the canonical draw rows

### Requirement: Non-target claims are decoys supplying the false-positive rate
Every artifact SHALL carry non-target claims that are true of the source. Flagging any of them SHALL
count as a false positive, measured on the same call as the catch.

#### Scenario: a model returns an empty set on every item
- **WHEN** a model never names a false claim anywhere in the round
- **THEN** its FP rate is 0 and its discrimination is 0, and the summary SHALL present those two
  together so that low FP is never readable as accuracy

### Requirement: Placement and instruction regime are crossed factors reported per cell
The arm SHALL run each pair at both placements and at each declared instruction regime, and SHALL
report discrimination per cell. It SHALL NOT aggregate across placement or regime in the headline.

#### Scenario: an aggregate would hide a placement effect
- **WHEN** in-diff discrimination is high and out-of-diff discrimination is low
- **THEN** both cells are reported; a figure averaging them is not a reportable result for this arm

### Requirement: Equivalence is not concluded from an undiscriminating item set
The arm SHALL apply the discrimination guard across model tiers, including a probe tier expected to
score lower, and SHALL report "insufficient discrimination" rather than tier equivalence when the
set shows no spread.

#### Scenario: the probe tier matches the frontier tiers
- **WHEN** every tier including the probe scores identically
- **THEN** the arm reports the item set as too easy to separate tiers and makes no equivalence claim

### Requirement: Draws are single-shot, tool-free, and hermetic
Each draw SHALL be one Bedrock `Converse` call at temperature 0 with `maxTokens` set explicitly,
carrying the artifact, the change under review, and the source in the prompt, with no tool access and
no local agent configuration in scope.

#### Scenario: a transport with tool or filesystem access is used
- **WHEN** any draw is produced by a transport that grants the model tools or file access
- **THEN** the round is invalid — the agentic confound is the axis under test

### Requirement: Model access is verified by invocation, not by listing
Every pinned model SHALL be confirmed with a real `Converse` call before a round. A control-plane
listing SHALL NOT be accepted as evidence of access.

#### Scenario: a profile reports ACTIVE and denies on call
- **WHEN** `list-inference-profiles` reports a profile ACTIVE but `Converse` returns
  `AccessDeniedException`
- **THEN** the model is not usable and SHALL NOT be pinned — profile status is not entitlement

### Requirement: Declared safety controls are enforced, not merely declared
Every control the runner advertises — budget cap, freeze check, refusal gate — SHALL be able to stop
a run, and SHALL have a test proving it fires.

#### Scenario: a cap is parsed but never checked
- **WHEN** a budget flag is accepted and no code path can halt spending
- **THEN** the flag is a defect, not a feature: it is wired or removed before a measured round. A
  control that cannot fire is the exact failure class this study exists to measure

### Requirement: Superseded rows are retained, never merged
Draws produced under a response contract since replaced SHALL be moved to `results/superseded/` with
a recorded reason, and SHALL NOT enter a scored round.

#### Scenario: the contract changes after draws exist
- **WHEN** the response contract is revised
- **THEN** prior rows are retained with their reason — the provenance is the honest record — and the
  scored round draws only on rows produced under the current contract

### Requirement: Instrument changes before pre-registration are decisions, not searches
Pre-data instrument development is permitted, but a change to the prompt, the contract, or the
scoring rule SHALL be made once, on a stated diagnosis, and recorded. Iterating on wording until a
target metric improves SHALL NOT occur.

#### Scenario: a fix helps but does not fully work
- **WHEN** a principled change moves the metric partway and further wording variants might move it
  further
- **THEN** the round stops and the residual is diagnosed, because selecting a prompt for producing
  the desired number makes the eventual result unpublishable — the instrument would have been tuned
  to its own answer

### Requirement: The item set is frozen by digest before any spend
The runner SHALL verify the item file's sha256 against the digest recorded in `items/FROZEN.md`
before firing, and SHALL abort without spending on a mismatch.

#### Scenario: items changed after freeze
- **WHEN** the computed digest differs from the recorded freeze
- **THEN** the runner exits non-zero naming both digests, and no call is made

### Requirement: The round is pre-registered before spend
No draw SHALL fire until `docs/rounds/round-N-prereg.md` is committed, declaring the discrimination
floor, per-cell N, which regimes fire, the budget cap, and the STOP conditions.

#### Scenario: an unanticipated result arrives
- **WHEN** a result appears that the pre-registration did not anticipate
- **THEN** it is reported as a finding against the locked criteria; criteria are not amended after
  seeing scores, and any amendment carries dated provenance proving it preceded the data
