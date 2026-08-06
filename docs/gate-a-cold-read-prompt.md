# GATE A — cold-read brief

**Use a model that neither authored the items nor sits in the round's model set.** Claude authored
the base set and Claude tiers are under test, so it is disqualified on both counts. Gemini is the
default choice — and if a non-Anthropic model is later pinned as the round's probe tier, the cold
reader has to move again.

**Brief it blind.** Do not send `REVIEW.md`, the design doc, the vendor provenance, or the fact that
other drafts were rejected. Do not say what the study expects to find, which items are suspected
weak, or where to look. Send `items/draft-tense.json` with `gold`, `formal_reading`, `token_delta`,
and any `note` fields **stripped**, plus the prompt below.

Run it **twice as two separate passes**. A single combined brief lets the easier question crowd out
the harder one.

---

## Pass 1 — the tell check (no source shown)

> Below are sentences taken from software design documents. Each is either an accurate description of
> what a system does, or an inaccurate one — but you are **not** being shown the system, so you
> cannot check.
>
> For each sentence, guess whether it is the accurate or the inaccurate one, and rate your confidence
> 1–3. Then, separately, tell me what you used to guess.
>
> You should be at chance. If you find yourself above chance, the thing that let you do it is what I
> need to know: length, specificity, register, subject matter, how alarming it sounds, which
> subsystems appear, anything.

**What to do with the result.** This is measured, not opinionated. If it guesses meaningfully above
chance on shuffled members with no source, there is a tell — and *what it names* is the defect to
fix. At chance is the pass condition.

Present all members shuffled and individually, twins separated, ids stripped or randomized so a
`-true` / `-false` suffix cannot leak the answer.

## Pass 2 — the semantic check (source shown)

> For each item below you have a `source_fact` and two claim sentences that differ by one
> grammatical change, plus three additional claims.
>
> Answer three questions per item:
>
> 1. Is **exactly one** of the two claims false of `source_fact` — not both, not neither? If both or
>    neither, say so and explain which.
> 2. Does the falsity follow from `source_fact` **as written**, or does it require knowledge,
>    convention, or assumption you had to supply yourself? If you supplied anything, name it.
> 3. Are all three additional claims **true** of `source_fact`? Flag any that is false, unverifiable,
>    or merely a restatement of a `source_fact` sentence rather than something derived from it.
>
> Be blunt. A weak item I keep is more expensive than one you wrongly cut.

---

## Disposition

- Pass 1 above chance → fix what it named, re-run pass 1. Do not proceed on an explanation of why
  the tell is harmless.
- Pass 2 finds an item where both or neither claim is false → cut the item, do not repair it in
  place. Cut items are recorded with their reason in `REVIEW.md`.
- A pair that cannot be built cold-read-clean is **cut, not softened**. A gate that is not
  discriminating is not a gate.

Record the cold reader's model and date in `items/FROZEN.md` alongside the generator provenance.
