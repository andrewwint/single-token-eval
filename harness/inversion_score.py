"""Score a measured round: paired discrimination, decoy FP, and the self-report gap.

The headline is DISCRIMINATION, never a bare catch rate. A pair counts only when the false member's
target claim is flagged AND the true member's is not. Flagging both is constant alarm; flagging
neither is a miss; both score zero, and the component rates are always reported alongside so the two
are distinguishable.

Draw row shape (produced by inversion_run.py):

    {"model", "regime", "placement", "item_id", "kind", "polarity", "draw",
     "target_claim": "C3", "flagged": ["C3", "C1"], "decoy_claims": ["C1","C2","C4"],
     "self_report": {"clarity": int, "needs_more_information": bool,
                     "would_start_without_clarifying": bool},
     "parse_ok": bool}

`parse_ok: false` rows are excluded and counted separately. A parse failure is not a miss — scoring
it as one would let a flaky output format masquerade as a reading failure.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from harness.stats import discrimination_guard, wilson_ci

CLEAR_LEVELS = {3, 4, 5}  # pre-declared: what counts as "reported clear" for the gap table


def _majority(vals: list[bool]) -> bool | None:
    """True iff a strict majority are True. None when there is nothing to decide."""
    if not vals:
        return None
    return sum(1 for v in vals if v) * 2 > len(vals)


def _cell(r: dict) -> tuple:
    return (r["model"], r["regime"], r["placement"])


def score(draws: list[dict]) -> dict:
    usable = [d for d in draws if d.get("parse_ok", True)]
    parse_fail = defaultdict(int)
    for d in draws:
        if not d.get("parse_ok", True):
            parse_fail[d["model"]] += 1

    # member-level majority: was the target claim flagged?
    member: dict[tuple, list[bool]] = defaultdict(list)
    fp: dict[tuple, list[bool]] = defaultdict(list)
    gap = defaultdict(lambda: {"clear_correct": 0, "clear_wrong": 0,
                               "unclear_correct": 0, "unclear_wrong": 0})

    for d in usable:
        key = _cell(d) + (d["item_id"], d["polarity"])
        hit = d["target_claim"] in d.get("flagged", [])
        member[key].append(hit)

        # A false positive is any flagged claim that is a decoy. Keyed per MEMBER, not per item:
        # pooling both members averages one member's over-firing away against the other's silence,
        # which is the same conflation the discrimination metric exists to avoid.
        fp[key].append(
            any(c in d.get("decoy_claims", []) for c in d.get("flagged", [])))

        # the gap table: correctness depends on which member this is
        correct = hit if d["polarity"] == "inverted" else not hit
        sr = d.get("self_report") or {}
        clear = (sr.get("clarity") in CLEAR_LEVELS
                 and not sr.get("needs_more_information", False))
        bucket = ("clear_" if clear else "unclear_") + ("correct" if correct else "wrong")
        gap[_cell(d)][bucket] += 1

    # pair-level discrimination
    items = {(k[3], k[4]): None for k in member}
    by_cell = defaultdict(lambda: {"disc": 0, "n": 0, "alarm": 0, "miss": 0,
                                   "flag_false": 0, "flag_true": 0, "n_false": 0, "n_true": 0})
    kinds = {d["item_id"]: d.get("kind", "pair") for d in usable}

    for cell in {_cell(d) for d in usable}:
        ids = {k[3] for k in member if k[:3] == cell}
        for iid in ids:
            inv = _majority(member.get(cell + (iid, "inverted"), []))
            tru = _majority(member.get(cell + (iid, "truthful"), []))
            s = by_cell[cell]
            if inv is not None:
                s["n_false"] += 1
                s["flag_false"] += int(inv)
            if tru is not None:
                s["n_true"] += 1
                s["flag_true"] += int(tru)

            if kinds.get(iid) == "reverse-single":
                s["n"] += 1
                s["disc"] += int(bool(inv))
                continue
            if inv is None or tru is None:
                continue
            s["n"] += 1
            if inv and not tru:
                s["disc"] += 1
            elif inv and tru:
                s["alarm"] += 1
            elif not inv:
                s["miss"] += 1

    out = {"cells": [], "parse_failures": dict(parse_fail)}
    for cell, s in sorted(by_cell.items()):
        rate = s["disc"] / s["n"] if s["n"] else 0.0
        lo, hi = wilson_ci(s["disc"], s["n"])
        fp_keys = [k for k in fp if k[:3] == cell]
        fp_hits = sum(1 for k in fp_keys if _majority(fp[k]))
        out["cells"].append({
            "model": cell[0], "regime": cell[1], "placement": cell[2],
            "discrimination": round(rate, 3), "ci95": [round(lo, 3), round(hi, 3)],
            "n_pairs": s["n"], "constant_alarm": s["alarm"], "miss": s["miss"],
            "flag_rate_false_member": round(s["flag_false"] / s["n_false"], 3) if s["n_false"] else None,
            "flag_rate_true_member": round(s["flag_true"] / s["n_true"], 3) if s["n_true"] else None,
            "decoy_fp": round(fp_hits / len(fp_keys), 3) if fp_keys else None,
            "gap": dict(gap[cell]),
        })

    # tier guard, computed per regime+placement so a single aggregate cannot hide a spread
    guards = {}
    for reg, pl in {(c["regime"], c["placement"]) for c in out["cells"]}:
        tiers = {c["model"]: c["discrimination"] for c in out["cells"]
                 if c["regime"] == reg and c["placement"] == pl}
        guards[f"{reg}/{pl}"] = discrimination_guard(tiers)
    out["discrimination_guard"] = guards
    return out


def render(r: dict) -> str:
    lines = [f"{'model':22s} {'regime':4s} {'placement':12s} {'disc':>6s} {'95% CI':>15s} "
             f"{'alarm':>6s} {'miss':>5s} {'FP':>6s}  gap(clear&wrong)"]
    lines.append("-" * 108)
    for c in r["cells"]:
        g = c["gap"]
        tot = sum(g.values()) or 1
        lines.append(
            f"{c['model']:22s} {c['regime']:4s} {c['placement']:12s} {c['discrimination']:6.3f} "
            f"[{c['ci95'][0]:.2f},{c['ci95'][1]:.2f}]{'':>4s} {c['constant_alarm']:6d} {c['miss']:5d} "
            f"{(c['decoy_fp'] if c['decoy_fp'] is not None else 0):6.3f}  "
            f"{g['clear_wrong']}/{tot} ({g['clear_wrong']/tot:.0%})")
    lines.append("")
    lines.append("gap(clear&wrong) = reported clear, did not ask for more information, and got the "
                 "target claim wrong.")
    lines.append("The component flag rates are in the JSON: a model flagging both members scores 0 "
                 "discrimination, and so does one flagging neither. They are not the same failure.")
    for k, g in r["discrimination_guard"].items():
        if not g["discriminating"]:
            lines.append(f"  !! {k}: {g['verdict']}")
    if r["parse_failures"]:
        lines.append(f"  parse failures (excluded, NOT scored as misses): {r['parse_failures']}")
    return "\n".join(lines)


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "results/draws.jsonl")
    draws = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    r = score(draws)
    print(render(r))
    Path("results/scores.json").write_text(json.dumps(r, indent=2) + "\n")


if __name__ == "__main__":
    main()
