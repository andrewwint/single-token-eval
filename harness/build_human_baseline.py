"""Build the human-baseline packet: 15 sentences, one yes/no question, ~10 minutes.

WHY THIS EXISTS: every reader in this study is a language model, on both sides. Ambiguity is defined
by disagreement among four models, and the verdict arm would score those same models against that
definition. If the four share a reading convention for `will` that people do not, "ambiguity" is a
property of this panel rather than of English — and nothing internal to the design can detect it.

The question is IDENTICAL to the one the models answered. That identity is what makes the two
comparable; changing the wording to sound more natural would destroy the comparison.

    python3 -m harness.build_human_baseline    # -> build/human-baseline-packet.md  (send this)
                                               #    build/human-baseline-key.json   (do NOT send)

Design:
  * 12 `claim_true` sentences, 3 sampled from each measured split band, so a human/model correlation
    can be computed across the range rather than at one end of it.
  * 3 `claim_false` sentences as ATTENTION CHECKS. These are plain present-tense assertions; all four
    models answered YES on them at 0.87-1.00. A respondent who answers NO to these was not reading,
    and their row is excluded before any comparison.
  * Order is shuffled on a pinned seed; band membership is never visible.
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAND = REPO / "items" / "candidates-round1.json"
OUT = REPO / "build" / "human-baseline-packet.md"
KEY = REPO / "build" / "human-baseline-key.json"
SEED = 20260806
VALID_MAX = 0.20
BANDS = [(0.0, 0.20), (0.21, 0.40), (0.41, 0.60), (0.61, 1.01)]
PER_BAND = 3
N_CHECKS = 3

QUESTION = """Below are 15 sentences, each taken from a software design document.

For each one, answer a single question:

    Does it assert something about how the system behaves NOW?

Answer YES or NO. There is no trick and no right answer I am looking for — several of
these are genuinely arguable, and "it depends how you read it" is useful information.
If you feel that way about one, answer with your first instinct and add a note.

Please do not discuss them with anyone else before answering, and please answer in
order rather than reading all 15 first.
"""

ID = re.compile(r"^\d{1,2}\.$")
SENT = re.compile(r"^\s{4}\S.*$")


def build():
    items = [c for c in json.loads(CAND.read_text()) if c["split_false"] <= VALID_MAX]
    rng = random.Random(SEED)

    picked = []
    for lo, hi in BANDS:
        pool = sorted([c for c in items if lo <= c["split_true"] <= hi], key=lambda c: c["id"])
        take = rng.sample(pool, min(PER_BAND, len(pool)))
        picked += [(c, "true") for c in take]

    check_pool = sorted([c for c in items if c not in [p[0] for p in picked]], key=lambda c: c["id"])
    picked += [(c, "false") for c in rng.sample(check_pool, N_CHECKS)]

    rng.shuffle(picked)
    rows, lines = [], [QUESTION, ""]
    for n, (c, member) in enumerate(picked, 1):
        text = c["claim_true"] if member == "true" else c["claim_false"]
        rows.append({"n": n, "item": c["id"], "member": member, "text": text,
                     "model_split": c["split_true"] if member == "true" else c["split_false"],
                     "attention_check": member == "false"})
        lines += [f"{n}.", f"    {text}", ""]
    return "\n".join(lines), rows


def main() -> None:
    packet, rows = build()

    # Whitelist of permitted line shapes — the same defence as the cold-read builder. A blacklist of
    # forbidden words cannot tell metadata from English and false-positives on sentence content.
    allowed = set(QUESTION.splitlines())
    leaks = [l for l in packet.splitlines()
             if l.strip() and l not in allowed and not ID.match(l) and not SENT.match(l)]
    if leaks:
        raise SystemExit(f"REFUSING — {len(leaks)} line(s) outside permitted shapes: {leaks[:3]}")
    if any(str(r["model_split"]) in packet for r in rows if r["model_split"] not in (0.0, 1.0)):
        raise SystemExit("REFUSING — a split value appears in the packet text")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(packet)
    KEY.write_text(json.dumps(rows, indent=2) + "\n")
    n_check = sum(1 for r in rows if r["attention_check"])
    print(f"wrote {OUT}")
    print(f"  {len(rows)} sentences: {len(rows)-n_check} measured + {n_check} attention checks")
    print(f"  bands sampled: {PER_BAND} per band across {len(BANDS)}, seed {SEED}")
    print(f"  leakage self-check: clean\n")
    print(f"wrote {KEY}  — SCORING ONLY. Do not send this to a respondent.")
    print("\n  SEND THE PACKET VERBATIM. ~10 minutes per person; aim for 5 or more people.")
    print("  Exclude any respondent who answers NO to an attention check before comparing.")


if __name__ == "__main__":
    main()
