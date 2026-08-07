"""Tests for the three modules that had none: inversion_run, build_gate_a, score_gate_a.

An independent review found these entirely untested while inversion_score had 12 tests. The gap
mattered: every fail-open control lived in this half of the codebase.

    python3 -m harness.tests.test_run_and_gates
"""
from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

from harness.build_gate_a import audit, pool
from harness.build_items import check as item_check
from harness.inversion_run import _norm_label, _norm_verdict, one, render
from harness.score_gate_a import score as gate_score

REPO = Path(__file__).resolve().parent.parent.parent
ITEMS = json.loads((REPO / "items" / "round1.json").read_text())


class StubClient:
    """Stands in for bedrock-runtime so the parser's failure branch can be exercised with no spend.

    `parse_ok` was true on 16/16 real draws, so that branch had never executed — an alert that has
    never fired. C4 was a bug living in exactly there."""

    def __init__(self, text, stop="end_turn", raise_exc=None):
        self.text, self.stop, self.raise_exc = text, stop, raise_exc

    def converse(self, **kw):
        if self.raise_exc:
            raise self.raise_exc
        return {"output": {"message": {"content": [{"text": self.text}]}},
                "usage": {"inputTokens": 100, "outputTokens": 20}, "stopReason": self.stop}


def _draw(text, **kw):
    it = dict(ITEMS[0])
    return one(StubClient(text, **kw), "opus-4.6", it, "inverted", "out-of-diff", "R0", 0)


# --- the parser branch that had never executed ------------------------------------------------

def test_target_without_a_verdict_is_not_parse_ok():
    """Silence on the target is not 'did not flag'. On the truthful twin that scored as CORRECT."""
    r = _draw('{"verdicts": {"C1": "SUPPORTED"}}')            # target is C2..C4, never C1 alone
    tgt = r["target_claim"]
    if tgt != "C1":
        assert r["parse_ok"] is False, r
        assert "no verdict for target" in r["error"]


def test_label_and_verdict_shapes_are_normalised_not_dropped():
    tgt = render(dict(ITEMS[0]), "inverted", "out-of-diff", draw=0)[1]
    r = _draw(json.dumps({"verdicts": {f"[{tgt}]": "CONTRADICTED."}}))
    assert r["parse_ok"] is True and r["flagged"] == [tgt], r
    assert r["verdicts"][tgt] == "CONTRADICTED"


def test_unrecognisable_verdict_is_recorded_not_silently_ignored():
    tgt = render(dict(ITEMS[0]), "inverted", "out-of-diff", draw=0)[1]
    r = _draw(json.dumps({"verdicts": {tgt: "PROBABLY FALSE"}}))
    assert r["parse_ok"] is False
    assert any("PROBABLY FALSE" in u for u in r["unparsed_verdicts"]), r["unparsed_verdicts"]


def test_transport_error_is_not_a_parse_failure():
    """Parse-failure rate is a statistic about model behaviour; API errors would poison it."""
    r = one(StubClient("", raise_exc=RuntimeError("ThrottlingException")),
            "opus-4.6", dict(ITEMS[0]), "inverted", "out-of-diff", "R0", 0)
    assert r["parse_ok"] is False and r.get("transport_error") is True


def test_stop_reason_is_recorded():
    tgt = render(dict(ITEMS[0]), "inverted", "out-of-diff", draw=0)[1]
    r = _draw(json.dumps({"verdicts": {tgt: "CONTRADICTED"}}), stop="max_tokens")
    assert r["stop_reason"] == "max_tokens", "a truncated reply must be visible, not invisible"


def test_raw_is_retained_verbatim():
    tgt = render(dict(ITEMS[0]), "inverted", "out-of-diff", draw=0)[1]
    txt = "prose before\n" + json.dumps({"verdicts": {tgt: "SUPPORTED"}}) + "\ntrailing"
    assert _draw(txt)["raw"] == txt


# --- render: the pairing defense and the position confound -------------------------------------

def test_twins_share_claim_labels_at_every_draw():
    for it in ITEMS:
        for d in range(5):
            _, ti, di = render(it, "inverted", "out-of-diff", draw=d)
            _, tt, dt = render(it, "truthful", "out-of-diff", draw=d)
            assert ti == tt and di == dt, f"{it['id']} draw {d}: label differs across twins"


def test_target_position_varies_across_draws():
    """Seeding by item id alone pinned each target to one position forever, confounding position
    with item. tense-01 was always C2 and tense-02 always C3."""
    moved = sum(1 for it in ITEMS
                if len({render(it, "inverted", "out-of-diff", draw=d)[1] for d in range(5)}) > 1)
    assert moved >= len(ITEMS) - 1, f"only {moved}/{len(ITEMS)} items move their target across draws"


def test_render_differs_only_by_the_token_out_of_diff():
    import difflib, re
    for it in ITEMS:
        a, _, _ = render(it, "inverted", "out-of-diff", draw=0)
        b, _, _ = render(it, "truthful", "out-of-diff", draw=0)
        w = lambda s: re.findall(r"[\w']+|[^\w\s]", s)
        ops = [o for o in difflib.SequenceMatcher(None, w(a), w(b)).get_opcodes() if o[0] != "equal"]
        assert ops, f"{it['id']}: twins are identical"
        assert len(ops) <= 2, f"{it['id']}: {len(ops)} edit regions in the rendered prompt"


# --- build_items: the one-token gate -----------------------------------------------------------

def test_item_gate_rejects_a_change_beyond_the_token():
    it = json.loads(json.dumps(ITEMS[0]))
    it["claim_true"] = it["claim_true"].replace(".", " immediately.")
    assert item_check(it), "a change beyond the declared token must be a violation"


def test_item_gate_accepts_the_discontiguous_founding_construction():
    it = {"id": "x", "kind": "pair",
          "claim_false": "The middleware no longer reads the legacy cookie.",
          "claim_true": "The middleware will no longer read the legacy cookie.",
          "token_delta": {"from": "no longer reads", "to": "will no longer read"}, "decoys": []}
    assert item_check(it) == [], "the study's founding construction must not be a violation"


# --- build_gate_a: the cue audit ---------------------------------------------------------------

def test_cue_audit_catches_a_tense_leak():
    it = json.loads(json.dumps(ITEMS))
    it[0]["claim_false"] = "The worker will be moved onto the queue."      # future in the FALSE class
    assert any("TENSE LEAK" in p for p in audit(pool(it))), "a future-tense false claim must be caught"


def test_cue_audit_catches_an_aspect_asymmetry():
    it = json.loads(json.dumps(ITEMS))
    for x in it:
        x["claim_false"] = "The system has been switched to the new path."
        x["decoys"] = ["The path exists.", "A caller reaches it.", "Config selects it."]
    assert any("ASPECT ASYMMETRY" in p for p in audit(pool(it)))


def test_clean_set_passes_the_audit():
    assert audit(pool(json.loads(json.dumps(ITEMS)))) == []


# --- score_gate_a: two-sided, and degenerate responses --------------------------------------

def _key(n=64, k=16):
    return [{"n": i + 1, "gold": "INACCURATE" if i < k else "ACCURATE"} for i in range(n)]


def _ans(flag, n=64):
    return [{"n": i + 1, "verdict": "INACCURATE" if (i + 1) in flag else "ACCURATE"} for i in range(n)]


def test_anti_correlated_cue_fails():
    """H5: flagging exactly the TRUE sentences is a perfect inverted tell; one-sided reported PASS."""
    r = gate_score(_ans(set(range(17, 33))), _key())
    assert r["hits"] == 0 and r["p_value"] <= 0.01, r
    assert "FAIL" in r["verdict"] and r["tail"] == "under", r["verdict"]


def test_correlated_cue_fails():
    r = gate_score(_ans(set(range(1, 17))), _key())
    assert "FAIL" in r["verdict"] and r["tail"] == "over"


def test_chance_passes():
    r = gate_score(_ans(set(range(1, 5)) | set(range(20, 32))), _key())
    assert r["verdict"].startswith("PASS"), r


def test_degenerate_responses_are_invalid_not_passes():
    for flag, word in ((set(range(1, 65)), "everything"), (set(), "nothing")):
        r = gate_score(_ans(flag), _key())
        assert r["degenerate"] and "INVALID" in r["verdict"], r["verdict"]
        assert word in r["verdict"]


def test_unknown_and_unparsed_answers_are_counted_separately():
    a = _ans(set(range(1, 5))) + [{"n": 999, "verdict": "INACCURATE"}, {"n": 5, "verdict": "maybe"}]
    r = gate_score(a, _key())
    assert r["unknown_ids"] == 1 and r["unparsed"] == 1, r


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    f = 0
    for t in TESTS:
        try:
            t()
        except Exception as e:
            print(f"FAIL {t.__name__}: {type(e).__name__}: {e}")
            f += 1
    print(f"{len(TESTS) - f}/{len(TESTS)} passed")
    sys.exit(f)
