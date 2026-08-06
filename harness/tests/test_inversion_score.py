"""Scoring tests — synthetic draws only, zero spend.

Every test here must be able to FAIL. Run the mutation check before trusting them:

    python3 -m harness.tests.test_inversion_score --mutate

Four of eight tests could not fail the last time this discipline was skipped in a sibling study.
"""
from __future__ import annotations

import sys

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
    print(f"{len(TESTS) - fails}/{len(TESTS)} passed")
    return fails


def mutate() -> int:
    """Break scoring on purpose; every mutant must kill at least one test.

    A mutant that no test catches means that branch is unguarded — the test suite asserts nothing
    about it, and a regression there would ship silently.
    """
    import harness.inversion_score as m

    survivors = []
    mutants = {
        "majority: >= instead of strict >":
            lambda: setattr(m, "_majority", lambda v: None if not v else sum(v) * 2 >= len(v)),
        "clear-levels: treat every clarity as clear":
            lambda: setattr(m, "CLEAR_LEVELS", {1, 2, 3, 4, 5}),
    }
    orig_maj, orig_clear = m._majority, m.CLEAR_LEVELS
    for name, apply in mutants.items():
        apply()
        killed = run() > 0
        m._majority, m.CLEAR_LEVELS = orig_maj, orig_clear
        print(f"  mutant {'KILLED ' if killed else 'SURVIVED'} — {name}\n")
        if not killed:
            survivors.append(name)
    if survivors:
        print(f"UNGUARDED BRANCHES: {survivors}")
    return len(survivors)


if __name__ == "__main__":
    sys.exit(mutate() if "--mutate" in sys.argv else run())
