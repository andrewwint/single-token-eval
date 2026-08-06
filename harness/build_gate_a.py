"""Emit the GATE A pass-1 payload deterministically, one sentence per file.

The payload is DATA, not judgement — never ask a model to assemble it. Doing so produced, across two
attempts: the wrong dataset, an unshuffled list whose twins sat a fixed distance apart, and a
preamble that stated the answer key outright.

DESIGN (revised — see docs/questions/REVIEW.md):
The pool is `claim_false` members (gold FALSE) against `decoys` (gold TRUE). Twins are excluded.
Testing a member against its twin is uninterpretable: every claim_true is future-tense and a future
sentence asserts nothing about now, so it cannot be the inaccurate one. The judge would score 100%
by noticing tense — the one thing the design guarantees is visible — and a ceiling score would be
misread as catastrophic leakage.

Against decoys, tense is held constant: everything in the pool is present-tense and describes a
system. The only remaining cues are the ones actually worth detecting — length, specificity, alarm,
register, subject matter.

Writes:
  build/pass1/NNN.md    -> one sentence per file. Send as SEPARATE calls, never one context.
  build/gate-a-key.json -> NEVER goes to the judge. Scoring only.

Usage:  python3 -m harness.build_gate_a [items/draft-tense.json ...]
"""
from __future__ import annotations

import json
import random
import re
import statistics as st
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEED = 20260806  # fixed: the shuffle is reproducible and recorded, not incidental

# Deliberately absent: the expected result, how many are false, that items come in pairs, that any
# grammatical feature distinguishes them. "You should be at chance" is itself an answer key — it
# tells the judge the expected outcome and invites it to perform the expectation by randomizing.
PROMPT = """\
Below is one sentence from a software design document. It either describes what the system does, or
describes something the system does not do.

You are not being shown the system.

Answer with exactly one word, ACCURATE or INACCURATE, then a confidence from 1 to 3.
"""

PERFECT = re.compile(r"\b(has|have|had)\s+(been\s+)?\w+(ed|en|wn|ne|t)\b", re.I)


def load(paths: list[str]) -> list[dict]:
    out: list[dict] = []
    for p in paths:
        out.extend(json.loads((REPO / p).read_text()))
    return out


def pool(items: list[dict]) -> list[dict]:
    rows = [{"text": it["claim_false"], "gold": "INACCURATE", "src": it["id"]} for it in items]
    rows += [{"text": d, "gold": "ACCURATE", "src": it["id"]}
             for it in items for d in it["decoys"]]
    random.Random(SEED).shuffle(rows)
    for n, r in enumerate(rows, 1):
        r["n"] = n
    return rows


def audit(rows: list[dict]) -> list[str]:
    """Asymmetries between the two classes that a judge could key on instead of meaning."""
    bad, good = [r for r in rows if r["gold"] == "INACCURATE"], [r for r in rows if r["gold"] == "ACCURATE"]
    problems = []

    b_perf = sum(1 for r in bad if PERFECT.search(r["text"]))
    g_perf = sum(1 for r in good if PERFECT.search(r["text"]))
    b_rate, g_rate = b_perf / len(bad), g_perf / len(good)
    if abs(b_rate - g_rate) > 0.15:
        problems.append(
            f"ASPECT ASYMMETRY: present-perfect in {b_perf}/{len(bad)} false vs {g_perf}/{len(good)} "
            f"true. 'has/have + participle' predicts the label. Add present-perfect decoys, or "
            f"convert those claims to simple present.")

    bl = [len(r["text"].split()) for r in bad]
    gl = [len(r["text"].split()) for r in good]
    if abs(st.mean(bl) - st.mean(gl)) > 2.0:
        problems.append(f"LENGTH ASYMMETRY: false mean {st.mean(bl):.1f} vs true mean {st.mean(gl):.1f} words.")

    return problems


def main() -> None:
    items = load(sys.argv[1:] or ["items/draft-tense.json"])
    rows = pool(items)
    base = sum(1 for r in rows if r["gold"] == "INACCURATE") / len(rows)

    out = REPO / "build"
    (out / "pass1").mkdir(parents=True, exist_ok=True)
    for r in rows:
        (out / "pass1" / f"{r['n']:03d}.md").write_text(f"{PROMPT}\n{r['text']}\n")
    (out / "gate-a-key.json").write_text(json.dumps(rows, indent=2) + "\n")

    print(f"{len(rows)} sentences ({len(items)} false, {len(rows)-len(items)} true) "
          f"-> build/pass1/*.md   seed {SEED}")
    print(f"  base rate FALSE = {base:.3f} — 'chance' is NOT 50%. A judge flagging k at random")
    print(f"  gets {base:.2f}k true positives. Pre-register the threshold against that, not 0.5.")
    print("  SEND AS SEPARATE CALLS. In one context the judge compares sentences to each other,")
    print("  which converts blind classification into relative ranking and measures something else.")

    problems = audit(rows)
    if problems:
        print("\n  REFUSING TO SHIP:")
        for p in problems:
            print(f"   - {p}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
