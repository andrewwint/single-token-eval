"""Score GATE A pass 1 against the key. The judge does not grade itself.

This exists because a cross-check returned "**PASS** — I expect to score essentially at chance"
without classifying a single sentence. That is a prediction about itself, not a result, and it is
the exact failure mode this study measures, appearing inside the study's own gate. An evaluator's
verdict on its own accuracy is inadmissible however confident it sounds.

Input: JSONL, one row per sentence — {"n": 1, "verdict": "ACCURATE"|"INACCURATE", "confidence": 1-3}
Any row whose `n` is absent from the key, or whose verdict is unparseable, is counted and reported
separately. It is never silently treated as a wrong answer.

    python3 -m harness.score_gate_a answers/gemini-pass1.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from harness.stats import hypergeom_tail, pair_threshold

REPO = Path(__file__).resolve().parent.parent
KEY = REPO / "build" / "gate-a-key.json"
ALPHA = 0.01


def score(answers: list[dict], key: list[dict]) -> dict:
    gold = {r["n"]: r["gold"] for r in key}
    n = len(gold)
    k_false = sum(1 for g in gold.values() if g == "INACCURATE")

    seen, unparsed, unknown = {}, 0, 0
    for a in answers:
        v = str(a.get("verdict", "")).strip().upper()
        if a.get("n") not in gold:
            unknown += 1
            continue
        if v not in ("ACCURATE", "INACCURATE"):
            unparsed += 1
            continue
        seen[a["n"]] = {"verdict": v, "confidence": a.get("confidence")}

    flagged = [i for i, r in seen.items() if r["verdict"] == "INACCURATE"]
    hits = [i for i in flagged if gold[i] == "INACCURATE"]
    draws = len(flagged)

    # p conditions on how many the judge actually flagged, so a judge flagging 40 of 48 is not
    # rewarded for volume: its expected hits rise with `draws` under the null too.
    #
    # H5 — TWO-SIDED. The one-sided version passed an ANTI-correlated cue: a judge flagging exactly
    # the 16 gold-ACCURATE sentences scored 0 hits where 4 were expected, p_upper = 1.0, and the
    # module reported "PASS — at chance". Systematically avoiding the false sentences requires
    # knowing which they are. A cue is a cue in either direction, and this gate exists to find cues.
    hi = hypergeom_tail(n, k_false, draws, len(hits)) if draws else None
    lo = (1.0 - hypergeom_tail(n, k_false, draws, len(hits) + 1)) if draws else None
    p = (min(1.0, 2 * min(hi, lo)) if draws else None)
    direction = None if not draws else ("over" if hi <= lo else "under")

    # A degenerate response carries no information and must not read as evidence of no cue.
    # `p = 1.0 if not draws` previously made "answered ACCURATE to all 64" a clean pass — the exact
    # false reassurance this module was written to stop.
    degenerate = (draws == 0 or draws == len(seen))
    t_ref, p_ref = pair_threshold(n, k_false, ALPHA)

    return {
        "n_pool": n, "n_false": k_false,
        "answered": len(seen), "unanswered": n - len(seen),
        "unparsed": unparsed, "unknown_ids": unknown,
        "flagged": draws, "hits": len(hits),
        "expected_hits_null": round(draws * k_false / n, 2) if n else 0.0,
        "p_value": None if p is None else round(p, 5),
        "tail": direction,
        "degenerate": degenerate,
        "verdict": ("INVALID — judge flagged " + ("nothing" if draws == 0 else "everything") +
                    "; no information, not evidence of no cue") if degenerate else
                   ("FAIL — tell detected (" + str(direction) + "-flagging)") if p <= ALPHA else
                   "PASS — at chance",
        "reference_threshold": {"if_flagged": t_ref and k_false, "needs_hits": t_ref, "p": round(p_ref, 5)},
        "confidence_on_hits": [seen[i]["confidence"] for i in hits],
        "hit_ids": sorted(hits),
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if not KEY.exists():
        raise SystemExit("no build/gate-a-key.json — run `python3 -m harness.build_gate_a` first")

    answers = [json.loads(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    r = score(answers, json.loads(KEY.read_text()))

    print(f"pool {r['n_pool']} ({r['n_false']} false) | answered {r['answered']}"
          f" | unparsed {r['unparsed']} | unknown ids {r['unknown_ids']}")
    if r["unanswered"]:
        print(f"  WARNING: {r['unanswered']} sentences unanswered — an incomplete run is not a pass")
    print(f"flagged {r['flagged']}, hits {r['hits']} (expected with no information: "
          f"{r['expected_hits_null']})")
    print(f"p = {r['p_value']} (two-sided, {r['tail']}-flagging)   ->   {r['verdict']}")
    print(f"\nreference: flagging {r['reference_threshold']['if_flagged']} needs "
          f">= {r['reference_threshold']['needs_hits']} hits to clear alpha={ALPHA}")

    if r["degenerate"] or (r["p_value"] is not None and r["p_value"] <= ALPHA):
        print("\n  A tell exists. NOW ask the judge what it used — and only now. Asking every run")
        print("  produces confabulation: a model asked what cue it used will always name one.")
        print(f"  Hit ids: {r['hit_ids']}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
