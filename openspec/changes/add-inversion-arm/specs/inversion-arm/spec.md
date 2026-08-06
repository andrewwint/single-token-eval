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

### Requirement: Grading is deterministic set comparison, never an LLM judge
Each artifact SHALL carry visibly-labelled claims, and the model SHALL return the identifiers of the
claims it believes false. Grading SHALL be exact set comparison against the item's gold.

#### Scenario: a response cannot be parsed
- **WHEN** a draw's response yields no parseable claim-identifier set
- **THEN** the draw is recorded `parse_ok: false`, excluded from scored draws, and counted in a
  per-model parse-failure total — it is never silently scored as a miss

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
