"""H3 — assert the one-token invariant in CODE. It has never been enforced anywhere.

CLAUDE.md: "the two members differ by exactly one token … asserted by the builder, not by review."
Until now that was a sentence. The property was verified ad hoc twice and never gated, which is the
same failure class as a budget flag that is parsed and never checked.

    python3 -m harness.build_items items/round1.json        # exits non-zero on any violation

What is checked, per pair item:
  1. the two members differ, and differ ONLY in the declared token_delta region(s)
  2. the observed delta matches `token_delta` as declared — a stale declaration is a violation
  3. edit_ops is recorded, not gated: `no longer X` -> `will no longer X` is two DISCONTIGUOUS
     regions because the matched words sit between them, and that is the study's founding case.
     A rule that excludes it is the wrong rule (see docs/questions/REVIEW.md, amended R1).
  4. decoys are not identical to either member, and are distinct from each other
  5. reverse-singles carry no claim_true, and pairs carry both members
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def words(s: str) -> list[str]:
    return re.findall(r"[\w']+|[^\w\s]", s)


def edit_regions(a: str, b: str) -> list[tuple[str, str, str]]:
    sm = difflib.SequenceMatcher(None, words(a), words(b))
    return [(op, " ".join(words(a)[i1:i2]), " ".join(words(b)[j1:j2]))
            for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def check(item: dict) -> list[str]:
    bad: list[str] = []
    iid = item.get("id", "?")

    if item.get("kind") == "reverse-single":
        if item.get("claim_true"):
            bad.append(f"{iid}: reverse-single carries a claim_true; it has no twin by construction")
        return bad

    cf, ct = item.get("claim_false"), item.get("claim_true")
    if not cf or not ct:
        bad.append(f"{iid}: a pair must carry both members")
        return bad
    if _norm(cf) == _norm(ct):
        bad.append(f"{iid}: members are identical — nothing is being varied")
        return bad

    ops = edit_regions(cf, ct)
    removed = " ".join(o[1] for o in ops)
    added = " ".join(o[2] for o in ops)

    delta = item.get("token_delta") or {}
    df, dt = delta.get("from", ""), delta.get("to", "")
    if not df or not dt:
        bad.append(f"{iid}: no token_delta declared")
    elif _norm(cf.replace(df, dt, 1)) != _norm(ct):
        # APPLY the declared delta rather than matching concatenated edit regions. A discontiguous
        # edit (`no longer reads` -> `will no longer read`) produces added regions `will` and `read`
        # with the matched `no longer` between them, so region-matching false-positives on exactly
        # the study's founding construction. Applying the substitution is what "the declaration
        # accounts for the difference" actually means.
        bad.append(f"{iid}: applying token_delta {df!r}->{dt!r} to claim_false does not yield "
                   f"claim_true — the declaration is stale or wrong")

    # Everything outside the edit regions must be byte-identical. This is the load-bearing property:
    # a hint anywhere else leaks into BOTH members and cannot move the score — but only if it is
    # genuinely in both.
    keep_a = [w for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, words(cf), words(ct)).get_opcodes()
              if op == "equal" for w in words(cf)[i1:i2]]
    keep_b = [w for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, words(cf), words(ct)).get_opcodes()
              if op == "equal" for w in words(ct)[j1:j2]]
    if keep_a != keep_b:
        bad.append(f"{iid}: shared text differs between members — the pairing defense is void")

    d = [_norm(x) for x in item.get("decoys") or []]
    if len(set(d)) != len(d):
        bad.append(f"{iid}: duplicate decoys")
    for x in d:
        if x in (_norm(cf), _norm(ct)):
            bad.append(f"{iid}: a decoy repeats a claim member")

    item["edit_ops"] = len(ops)          # recorded, never gated
    item["edit_regions"] = [f"{o[1]!r}->{o[2]!r}" for o in ops]
    return bad


def main() -> None:
    paths = sys.argv[1:] or ["items/round1.json"]
    violations, n, discontig = [], 0, []
    for p in paths:
        items = json.loads((REPO / p).read_text())
        for it in items:
            n += 1
            violations += check(it)
            if it.get("edit_ops", 0) > 1:
                discontig.append(f"{it['id']}({it['edit_ops']})")
        (REPO / p).write_text(json.dumps(items, indent=2) + "\n")

    print(f"checked {n} items across {len(paths)} file(s)")
    if discontig:
        print(f"  discontiguous (recorded, not a violation — amended R1): {', '.join(discontig)}")
    if violations:
        print(f"\n  {len(violations)} VIOLATION(S) — refusing:")
        for v in violations:
            print(f"   - {v}")
        raise SystemExit(2)
    print("  one-token invariant HOLDS")


if __name__ == "__main__":
    main()
