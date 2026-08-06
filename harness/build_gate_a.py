"""Emit the GATE A pass-1 payload deterministically from the item set.

The payload is DATA, not judgement — never ask a model to assemble it. Doing so has already
produced, in one attempt: the wrong dataset, an unshuffled list whose twins sat a fixed distance
apart, and a preamble that stated the answer key outright.

Writes two files:
  build/gate-a-pass1.md   -> goes to the cold reader. No polarity hint, no ids, shuffled.
  build/gate-a-key.json   -> NEVER goes to the cold reader. Scoring only.

Usage:  python3 -m harness.build_gate_a [items/draft-tense.json ...]
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEED = 20260806  # fixed: the shuffle is reproducible and recorded, not incidental

PREAMBLE = """\
Below are sentences taken from software design documents. Each one is either an accurate
description of what a system does, or an inaccurate one — but you are **not** being shown the
systems, so you cannot check any of them.

For each sentence:

1. Guess **ACCURATE** or **INACCURATE**.
2. Rate confidence **1** (pure guess) to **3** (high confidence).
3. Say what you used to guess.

You should be at chance. If you find yourself above chance, the thing that let you do it is what
I need to know — length, specificity, register, subject matter, how alarming it sounds, which
subsystems appear, sentence shape, anything at all.
"""
# Deliberately absent from PREAMBLE: how many are accurate, that they come in pairs, that any
# grammatical feature distinguishes them. Each of those is the answer key.


def load(paths: list[str]) -> list[dict]:
    items: list[dict] = []
    for p in paths:
        items.extend(json.loads((REPO / p).read_text()))
    return items


def build(items: list[dict]) -> tuple[str, list[dict]]:
    rows = []
    for it in items:
        # Reverse-polarity singles carry no twin; pairs contribute both members.
        if it.get("kind") == "reverse-single":
            rows.append({"text": it["claim_false"], "gold": "INACCURATE", "src": it["id"]})
            continue
        rows.append({"text": it["claim_false"], "gold": "INACCURATE", "src": it["id"]})
        rows.append({"text": it["claim_true"], "gold": "ACCURATE", "src": it["id"]})

    random.Random(SEED).shuffle(rows)
    for n, r in enumerate(rows, 1):
        r["n"] = n

    body = "\n".join(f"{r['n']}. {r['text']}" for r in rows)
    return f"{PREAMBLE}\n{body}\n", rows


def main() -> None:
    paths = sys.argv[1:] or ["items/draft-tense.json"]
    items = load(paths)
    payload, rows = build(items)

    out = REPO / "build"
    out.mkdir(exist_ok=True)
    (out / "gate-a-pass1.md").write_text(payload)
    (out / "gate-a-key.json").write_text(json.dumps(rows, indent=2) + "\n")

    n_inacc = sum(1 for r in rows if r["gold"] == "INACCURATE")
    print(f"{len(rows)} sentences from {len(items)} items -> build/gate-a-pass1.md")
    print(f"  INACCURATE {n_inacc} / ACCURATE {len(rows) - n_inacc}   (seed {SEED})")

    # An evaluator scoring above this is reading something. With a single-polarity set that is
    # guaranteed, and the "tell" it finds will be tense itself — the variable under test, not a
    # leak. Refuse to emit a payload that cannot be interpreted.
    polarities = {(it.get("kind") or "pair") for it in items}
    if "reverse-single" not in polarities:
        print("\n  REFUSING TO SHIP: item set is single-polarity — every false claim is present "
              "tense.\n  Pass 1 is guaranteed above chance and its result is uninterpretable.\n"
              "  Add the reverse-polarity singles first (see docs/questions/REVIEW.md).")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
