"""Scoring tests — synthetic draws only, zero spend.

Every test here must be able to FAIL. Run the mutation check before trusting them:

    python3 -m harness.tests.test_inversion_score --mutate

Four of eight tests could not fail the last time this discipline was skipped in a sibling study.
"""
from __future__ import annotations

import sys
from pathlib import Path

from harness.inversion_score import score
from harness.stats import hypergeom_tail, pair_threshold, wilson_ci


def draw(polarity, flagged, *, item="t1", kind="pair", model="m", regime="R0",
         placement="out-of-diff", clarity=4, needs_info=False, parse_ok=True, n=0, fam="tense"):
    return {"model": model, "regime": regime, "placement": placement, "item_id": item,
            "kind": kind, "family": fam, "polarity": polarity, "draw": n, "target_claim": "C3",
            "flagged": flagged, "decoy_claims": ["C1", "C2", "C4"],
            "self_report": {"clarity": clarity, "needs_more_information": needs_info,
                            "would_start_without_clarifying": True},
            "parse_ok": parse_ok}


def cell(r):
    return r["cells"][0]


def test_discriminated():
    """Flags the false member's target, clears the true member's -> DISCRIMINATED."""
    r = score([draw("inverted", ["C3"]), draw("truthful", [])])
    assert cell(r)["discrimination"] == 1.0, cell(r)
    assert cell(r)["constant_alarm"] == 0 and cell(r)["miss"] == 0


def test_constant_alarm_scores_zero():
    """Flags BOTH members -> not discriminated, and reported as alarm rather than a miss."""
    r = score([draw("inverted", ["C3"]), draw("truthful", ["C3"])])
    c = cell(r)
    assert c["discrimination"] == 0.0
    assert c["constant_alarm"] == 1 and c["miss"] == 0
    assert c["flag_rate_false_member"] == 1.0 and c["flag_rate_true_member"] == 1.0


def test_never_flag_scores_zero_and_is_a_different_failure():
    """Flags NEITHER member -> not discriminated, recorded as miss, not alarm."""
    r = score([draw("inverted", []), draw("truthful", [])])
    c = cell(r)
    assert c["discrimination"] == 0.0
    assert c["miss"] == 1 and c["constant_alarm"] == 0


def test_empty_responder_shows_zero_fp_and_zero_discrimination_together():
    """A model that flags nothing must not read as accurate: FP 0 AND discrimination 0."""
    c = cell(score([draw("inverted", []), draw("truthful", [])]))
    assert c["decoy_fp"] == 0.0 and c["discrimination"] == 0.0


def test_decoy_flag_counts_as_false_positive():
    """FP is per MEMBER. One of two members flags a decoy -> 0.5, not 0 and not 1."""
    r = score([draw("inverted", ["C3", "C1"]), draw("truthful", [])])
    assert cell(r)["decoy_fp"] == 0.5, cell(r)["decoy_fp"]
    both = score([draw("inverted", ["C3", "C1"]), draw("truthful", ["C2"])])
    assert cell(both)["decoy_fp"] == 1.0


def test_parse_failure_excluded_not_scored_as_miss():
    """A dropped draw must not become a wrong answer."""
    r = score([draw("inverted", ["C3"]), draw("truthful", []),
               draw("inverted", [], item="t2", parse_ok=False),
               draw("truthful", [], item="t2", parse_ok=False)])
    assert cell(r)["n_pairs"] == 1, "t2 had no usable draws and must not be scored"
    assert cell(r)["discrimination"] == 1.0
    assert r["parse_failures"] == {"m": 2}


def test_reverse_single_reports_as_single_catch_not_discrimination():
    """No twin, so it is a CATCH RATE and is reported as one.

    This test previously asserted singles set `discrimination`, which encoded defect C1: it let a
    flag-everything model score 0.600. A test can pin the wrong behaviour as confidently as the
    right one."""
    hit = cell(score([draw("inverted", ["C3"], item="rev-01", kind="reverse-single")]))
    assert hit["single_catch"] == 1.0 and hit["n_singles"] == 1
    assert hit["discrimination"] is None and hit["n_pairs"] == 0
    miss = cell(score([draw("inverted", [], item="rev-01", kind="reverse-single")]))
    assert miss["single_catch"] == 0.0


def test_gap_table_isolates_confident_and_wrong():
    """Reported clear, no further information wanted, and wrong -> the cell that matters."""
    r = score([draw("inverted", [], clarity=5, needs_info=False),      # wrong, confident
               draw("truthful", [], clarity=5, needs_info=False),      # right, confident
               draw("inverted", [], item="t2", clarity=1, needs_info=True)])  # wrong, hedged
    g = cell(r)["gap"]
    assert g["clear_wrong"] == 1 and g["clear_correct"] == 1 and g["unclear_wrong"] == 1


def test_low_clarity_alone_is_unclear():
    """The clarity cutoff must bind on its own, not only via needs_more_information.

    Added after a mutation check: widening CLEAR_LEVELS to accept every level killed no test,
    because the one low-clarity case in the suite also set needs_info=True and was masked by it.
    """
    r = score([draw("inverted", [], clarity=1, needs_info=False),     # wrong, LOW clarity, no ask
               draw("truthful", [], clarity=1, needs_info=False)])
    g = cell(r)["gap"]
    assert g["clear_wrong"] == 0, f"clarity 1 must not count as clear: {g}"
    assert g["unclear_wrong"] == 1 and g["unclear_correct"] == 1


def test_reverse_single_never_enters_discrimination():
    """C1: a constant-alarm model must not be rewarded by single-member items.

    Found by review: reverse-singles shared `disc`/`n` with real pairs, so flag-everything scored
    0.600 while every test passed."""
    rows = ([draw("inverted", ["C3"]), draw("truthful", ["C3"])] +            # pair -> alarm
            [draw("inverted", ["C3"], item=f"rev-0{i}", kind="reverse-single") for i in (1, 2, 3)])
    c = cell(score(rows))
    assert c["discrimination"] == 0.0, f"singles leaked into the headline: {c['discrimination']}"
    assert c["n_pairs"] == 1 and c["n_singles"] == 3
    assert c["single_catch"] == 1.0


def test_families_are_not_pooled():
    """C2: the calibration family cannot share a denominator with the family it calibrates."""
    rows = [draw("inverted", [], item="t1", fam="tense"), draw("truthful", [], item="t1", fam="tense"),
            draw("inverted", ["C3"], item="p1", fam="polarity"), draw("truthful", [], item="p1", fam="polarity")]
    f = cell(score(rows))["by_family"]
    assert f["tense"]["discrimination"] == 0.0 and f["polarity"]["discrimination"] == 1.0, f


def test_empty_cell_is_not_a_measured_zero():
    """C3: no data and measured-zero must not render identically."""
    c = cell(score([draw("inverted", ["C3"], item="t1"),
                    draw("inverted", ["C3"], item="t1", n=1)]))   # no truthful member ever
    assert c["discrimination"] is None and c["ci95"] is None, c
    assert c["n_pairs"] == 0


def test_component_rates_share_the_headline_denominator():
    """M1: rates were counted before the half-pair guard, over a different item set."""
    rows = [draw("inverted", ["C3"], item="t1"), draw("truthful", [], item="t1"),
            draw("inverted", [], item="t2")]                       # t2 half-pair, excluded
    c = cell(score(rows))
    assert c["n_pairs"] == 1 and c["flag_rate_false_member"] == 1.0, c


def test_guard_skips_cells_with_no_measurement():
    rows = [draw("inverted", ["C3"], model="a"), draw("truthful", [], model="a"),
            draw("inverted", ["C3"], model="b")]                   # b never completes a pair
    g = score(rows)["discrimination_guard"]["R0/out-of-diff"]
    assert list(g["tiers"]) == ["a"], g["tiers"]


def test_guard_refuses_equivalence_without_spread():
    rows = [draw("inverted", ["C3"], model=m) for m in ("a", "b")] + \
           [draw("truthful", [], model=m) for m in ("a", "b")]
    g = score(rows)["discrimination_guard"]["R0/out-of-diff"]
    assert g["discriminating"] is False and "insufficient discrimination" in g["verdict"]


def test_majority_needs_strict_majority():
    """2 of 4 flagged is not a majority — a tie must not count as a flag."""
    rows = [draw("inverted", ["C3"], n=0), draw("inverted", ["C3"], n=1),
            draw("inverted", [], n=2), draw("inverted", [], n=3), draw("truthful", [])]
    assert cell(score(rows))["discrimination"] == 0.0


def test_hit_is_pinned_to_the_target_claim():
    """The single most load-bearing line in the scorer: a flag on a DECOY is not a catch.

    Review mutation `hit = bool(d["flagged"])` survived the whole suite — a model flagging only
    decoys scored as a catch and nothing noticed."""
    r = score([draw("inverted", ["C1", "C2"]), draw("truthful", [])])   # decoys only, never C3
    assert cell(r)["discrimination"] == 0.0, "flagging decoys scored as a catch"
    assert cell(r)["miss"] == 1


def test_headline_denominator_is_pairs():
    """Mutation `rate = disc / n_false` survived — the headline denominator was unpinned."""
    rows = ([draw("inverted", ["C3"], item="a"), draw("truthful", [], item="a")] +
            [draw("inverted", [], item="b"), draw("truthful", [], item="b")])
    c = cell(score(rows))
    assert c["n_pairs"] == 2 and c["discrimination"] == 0.5, c


def test_component_rate_denominators_are_distinct():
    """Mutations `flag_false / n` and `flag_true -> flag_false` both survived."""
    # flag_false MUST differ from flag_true or reading the wrong counter is a no-op.
    rows = ([draw("inverted", ["C3"], item="a"), draw("truthful", ["C3"], item="a")] +   # 1,1
            [draw("inverted", ["C3"], item="b"), draw("truthful", [], item="b")] +       # 1,0
            [draw("inverted", ["C3"], item="c"), draw("truthful", [], item="c")] +       # 1,0
            [draw("inverted", ["C3"], item="d"), draw("truthful", [], item="d")])        # 1,0
    c = cell(score(rows))
    assert c["flag_rate_false_member"] == 1.0, c
    assert c["flag_rate_true_member"] == 0.25, f"reads the false counter: {c}"


def test_wilson_ci_is_not_argument_swapped():
    """Mutation `wilson_ci(n, n)` — must use disc != n, or the mutation is a no-op."""
    rows = ([x for i in "ab" for x in (draw("inverted", ["C3"], item=i), draw("truthful", [], item=i))] +
            [x for i in "cd" for x in (draw("inverted", [], item=i), draw("truthful", [], item=i))])
    c = cell(score(rows))
    assert c["discrimination"] == 0.5 and c["n_pairs"] == 4
    assert c["ci95"][1] < 0.9, f"wilson_ci(4,4) would give ~1.0; got {c['ci95']}"


def test_clear_cutoff_is_pinned_from_both_sides():
    """Mutation `CLEAR_LEVELS = {5}` survived — the cutoff was pinned only from below."""
    r = score([draw("inverted", [], clarity=3, needs_info=False),
               draw("truthful", [], clarity=3, needs_info=False)])
    assert cell(r)["gap"]["clear_wrong"] == 1, "clarity 3 must count as clear"


def test_needs_more_information_alone_makes_it_unclear():
    """Mutation dropping `needs_more_information` survived — it was pinned only via clarity."""
    r = score([draw("inverted", [], clarity=5, needs_info=True),
               draw("truthful", [], clarity=5, needs_info=True)])
    g = cell(r)["gap"]
    assert g["clear_wrong"] == 0 and g["unclear_wrong"] == 1, g


def test_guard_partitions_per_cell_not_globally():
    """Mutation aggregating the guard across regime+placement survived."""
    rows = ([draw("inverted", ["C3"], model="a"), draw("truthful", [], model="a")] +
            [draw("inverted", [], model="b"), draw("truthful", [], model="b")] +
            [draw("inverted", ["C3"], model="a", placement="in-diff"),
             draw("truthful", [], model="a", placement="in-diff")])
    g = score(rows)["discrimination_guard"]
    assert set(g) == {"R0/out-of-diff", "R0/in-diff"}, set(g)
    assert g["R0/out-of-diff"]["discriminating"] is True
    assert g["R0/in-diff"]["discriminating"] is False


def test_stats_are_right():
    assert round(hypergeom_tail(48, 12, 12, 7), 4) == 0.0047
    assert pair_threshold(48, 12)[0] == 7
    lo, hi = wilson_ci(0, 20)
    assert round(hi, 3) == 0.161 and lo == 0.0


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def run() -> int:
    fails = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            fails += 1
        except Exception as e:
            # A mutant that CRASHES the suite is killed, not an abort. Counting only AssertionError
            # let a crashing mutant escape and silently truncate the sweep at that point.
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            fails += 1
    print(f"{len(TESTS) - fails}/{len(TESTS)} passed")
    return fails


def mutate() -> int:
    """Break scoring on purpose; every mutant must kill at least one test.

    The mutant list is the one an independent review used to find 10 survivors in the original
    suite. Keeping their exact mutants here is what stops the fixes from silently regressing.
    """
    import harness.inversion_score as m

    orig = {"maj": m._majority, "clear": m.CLEAR_LEVELS, "score": m.score}
    src = Path(m.__file__).read_text()

    def patched(old_line, new_line):
        """Recompile the module with one line swapped — covers mutants no monkeypatch can reach."""
        import types
        assert old_line in src, f"mutant anchor missing: {old_line!r}"
        mod = types.ModuleType("mutant")
        mod.__dict__["__file__"] = m.__file__
        exec(compile(src.replace(old_line, new_line, 1), m.__file__, "exec"), mod.__dict__)
        return mod.score

    mutants = {
        "majority: >= instead of strict >":
            lambda: setattr(m, "_majority", lambda v: None if not v else sum(v) * 2 >= len(v)),
        "clear-levels: every clarity counts as clear":
            lambda: setattr(m, "CLEAR_LEVELS", {1, 2, 3, 4, 5}),
        "clear-levels: only 5 counts as clear":
            lambda: setattr(m, "CLEAR_LEVELS", {5}),
        "hit ignores the target claim":
            lambda: setattr(m, "score", patched(
                'hit = d["target_claim"] in d.get("flagged", [])',
                'hit = bool(d.get("flagged", []))')),
        "wilson_ci arguments swapped":
            lambda: setattr(m, "score", patched(
                'ci = [round(x, 3) for x in wilson_ci(s["disc"], s["n"])] if s["n"] else None',
                'ci = [round(x, 3) for x in wilson_ci(s["n"], s["n"])] if s["n"] else None')),
        # EQUIVALENT MUTANTS, deliberately retired: after the M1 fix `n_false`, `n_true` and `n` are
        # incremented together for exactly the scored pairs, so swapping them cannot change any
        # output. An equivalent mutant surviving is not an untested branch, and pretending otherwise
        # by writing a test that cannot distinguish them would be theatre.
        #   - "headline denominator is n_false"
        #   - "false-member rate over pair count"
        "true-member rate reads the false counter":
            lambda: setattr(m, "score", patched(
                '"flag_rate_true_member": round(s["flag_true"] / s["n_true"], 3) if s["n_true"] else None',
                '"flag_rate_true_member": round(s["flag_false"] / s["n_true"], 3) if s["n_true"] else None')),
        "clear ignores needs_more_information":
            lambda: setattr(m, "score", patched(
                'clear = (sr.get("clarity") in CLEAR_LEVELS\n                 and not sr.get("needs_more_information", False))',
                'clear = sr.get("clarity") in CLEAR_LEVELS')),
        "missing-member guard removed":
            lambda: setattr(m, "score", patched(
                "            if inv is None or tru is None:\n                continue\n",
                "            if False:\n                continue\n")),
        "guard aggregated across regime and placement":
            lambda: setattr(m, "score", patched(
                'if c["regime"] == reg and c["placement"] == pl\n                 and c["discrimination"] is not None}',
                'if c["discrimination"] is not None}')),
        "reverse-singles pooled back into discrimination":
            lambda: setattr(m, "score", patched(
                '                if inv is not None:\n                    s["single_n"] += 1\n                    s["single_hit"] += int(inv)\n                continue',
                '                s["n"] += 1\n                s["disc"] += int(bool(inv))\n                continue')),
    }

    survivors = []
    for name, apply in mutants.items():
        try:
            apply()
        except AssertionError as e:
            print(f"  mutant SKIPPED (anchor moved) — {name}: {e}")
            continue
        import harness.tests.test_inversion_score as self_mod
        self_mod.score = m.score
        globals()["score"] = m.score
        killed = run() > 0
        m._majority, m.CLEAR_LEVELS, m.score = orig["maj"], orig["clear"], orig["score"]
        globals()["score"] = orig["score"]
        print(f"  {'KILLED  ' if killed else 'SURVIVED'} {name}")
        if not killed:
            survivors.append(name)
    print(f"\n{len(mutants) - len(survivors)}/{len(mutants)} mutants killed")
    if survivors:
        print(f"UNGUARDED: {survivors}")
    return len(survivors)


if __name__ == "__main__":
    sys.exit(mutate() if "--mutate" in sys.argv else run())
