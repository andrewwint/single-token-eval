# Item generation prompt — tense pairs

Paste the block below into a fresh chat with a frontier model. Output is a **draft**, never an item:
everything it returns has to survive the builder assertion, the `formal_reading` check, and GATE A's
cold read before it can be frozen.

Record which model produced each item in `items/FROZEN.md`. Drafting items with a model that is also
under test is a mild familiarity bias — not fatal, since the generator never answers the items, but
it is a fact the findings doc discloses rather than omits. Running the prompt twice against two
different vendors and keeping what both produce cleanly is the cheap mitigation.

---

You are helping build test items for a measurement study. I need 12 matched sentence pairs.
Precision matters far more than volume — a flawed pair is worse than a missing one.

## Background

I am testing whether a reviewer notices when a single word changes what a sentence claims about a
software system.

The originating example: a document said a safety gate "**no longer depends** on the model emitting
the correct verdict." At that commit, it still did. The honest sentence was "**will no longer
depend**." One word separates a claim about what is enforced today from a statement of intent. A
careful independent reviewer read straight past it.

## What I need

12 items. Each item has:

1. **source_fact** — one or two sentences stating plainly what the code actually does *now*. This is
   the ground truth every claim is checked against.
2. **claim_false** — a sentence asserting in the present (or present perfect) that the system
   already does something it does not yet do. FALSE of `source_fact`.
3. **claim_true** — the SAME sentence with exactly ONE token changed to a future tense or aspect.
   Because it asserts nothing about the present, it is NOT false of `source_fact`.
4. **formal_reading** — for each of the two, what is asserted, about what time.
5. **decoys** — 3 further claim sentences that ARE true of `source_fact`, in the same register.
   Distractors; not part of the pair.

## Hard rules

**R1 — Exactly one token differs** between `claim_false` and `claim_true`. Not one phrase, not a
rewording. Diff the two strings: everything else identical, including punctuation and word order.

**R2 — The token must flip the TRUTH VALUE, not the emphasis.** This is the rule most drafts break.

- GOOD: `validates` → `will validate` — one asserts present behavior, the other does not.
- BAD: `validates` → `is validating` — both assert present behavior; only aspect moved.
- BAD: `removes` → `removed` when `source_fact` leaves both readings defensible.

Ask of every pair: **is exactly one member false of `source_fact`, and the other not?** If both are
false, or neither is, cut the item.

**R3 — No tells.** Nothing may distinguish the members except the token itself. No hedge present in
one and absent in the other — no "currently", "already", "eventually", "soon", "planned". No
difference in confidence, length, or specificity. Someone shown a single member in isolation must
not be able to tell which one they are holding.

**R4 — Verifiable from `source_fact` alone.** That `claim_false` is false must follow from
`source_fact` as written — never from a convention, a norm, or an assumption I would have to supply.

**R5 — Neutral register.** Write claims the way real documentation writes them. No section headings,
no "Planned:" or "Current behavior:" framing. Tense must be the only temporal cue.

**R6 — Vary the construction.** Do not hand me 12 copies of `X` → `will X`. Use at least 5 distinct
tense/aspect constructions across the set — for example simple present → simple future; present
perfect → future; `no longer Xs` → `will no longer X`; `is Xed` → `will be Xed`; `has Xed` → `will
have Xed`. Label the construction each item uses.

**R7 — Vary the domain.** Not 12 sentences about authentication. Spread across subsystems:
authorization, caching, retries, input validation, logging, rate limiting, schema migrations,
encryption at rest, background jobs, deprecation.

## Output format

Return JSON, one object per item:

```json
{
  "id": "tense-01",
  "construction": "present perfect -> future",
  "domain": "webhook verification",
  "source_fact": "...",
  "claim_false": "...",
  "claim_true": "...",
  "token_delta": { "from": "...", "to": "..." },
  "formal_reading": {
    "claim_false": "asserts P holds at NOW",
    "claim_true": "asserts P holds at some time after NOW; asserts nothing about NOW",
    "source_fact": "P does not hold at NOW"
  },
  "decoys": ["...", "...", "..."]
}
```

## Before you answer

For each item, check R1 by diffing the two strings character by character, and check R2 by asking
whether exactly one member is false of `source_fact`. Drop anything that fails either.

If only 9 survive your own check, give me 9 and say which ones you cut and why. **Do not pad the set
to reach 12.**
