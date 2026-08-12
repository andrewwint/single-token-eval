# single-token-eval

**Does a reviewer's verdict track a single token?**

A claim is an assertion, and its truth flips on one token exactly the way a conditional flips on one
operator: `<` / `>`, `must` / `must not`, `all` / `any`, an inserted `not`, `is` / `will be`. This
repo measures whether a model reviewing a claim notices when that token moves.

The originating case was prose, not code. A line of documentation said a safety gate **no longer
depends** on the model producing the correct verdict. At that commit it still did — the honest
version was **will no longer depend**. One word, and the sentence goes from a claim about what the
system enforces today to a statement about where it is headed. A careful independent reviewer read
it and did not notice the two are different claims.

## The instrument: twin pairs

The hard part of measuring a one-token defect is that anything written around it gives the answer
away — a comment, a variable name, a test's name, the tone of the surrounding paragraph. You can
audit a fixture for hints and still miss one. You can never prove you removed the last one.

So every item is built **twice**, byte-identical except the inverted token. One member's claim is
true of the source; the other's is false. A pair scores only when the false member is flagged **and**
the true member is not.

> Any hint you failed to remove sits in **both** members, so it cannot move the score. A tell that
> gives away the answer gives away the same answer twice.

The measurement stops depending on your ability to write a clean fixture — unverifiable — and starts
depending on the two members being identical, which a build script asserts.

Three degenerate strategies fail for free: flag everything (flags both), flag nothing (flags
neither), and match on tone (the tone is identical).

## Why Bedrock, single-shot

Draws are one `Converse` call at temperature 0 with the artifact, the change under review, and the
source in the prompt. No tools, no file access, no agent loop.

Two reasons, and the second is the stronger one:

1. **No agentic confound.** An agent with file access confounds *did the model catch it* with *did
   the agent go looking* — the exact axis under test.
2. **Hermeticity.** A local coding agent reads `~/.claude` — global agents, skills, settings, memory,
   MCP servers — none of which is pinned or recorded. A sibling study had to disclose this as an open
   bound because relocating the config broke keychain auth on the measurement host. A `Converse` call
   has no such surface: **the prompt is the entire input.**

## Layout

```
docs/single-token-inversion.md   the design doc — the family, the traps, the discipline
docs/rounds/                     round-N-prereg.md (locked before spend) -> round-N-findings.md
items/                           frozen twin pairs + FROZEN.md (sha256)
harness/                         runner, scorer, vendored stats helpers
results/                         append-only draws.jsonl
openspec/                        spec-driven change proposals
```

## Status — FROZEN

**Frozen 2026-08-12.** The verdict arm never fired and round 2 is cancelled. See
[`docs/CLOSE-OUT.md`](docs/CLOSE-OUT.md) for what ran, what was found, and why it stopped where it did.

## About `items/`

`items/` holds the sentence pairs and their gold labels. They were withheld while measurement was
live — publishing an item set makes it training data and burns any future measurement on it.

With the study frozen that trade inverts. There is no future measurement to protect, and published
items let a reader check whether `claim_false` is genuinely unambiguous, whether the pairs are fair,
and whether the finding survives their own reading. **If this ever unfreezes, the items are spent and
a new round needs new sentences.**
