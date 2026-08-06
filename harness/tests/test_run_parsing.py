"""C4 regression: a model's silence on the target must never score as a clear.

Every shape below previously produced parse_ok=True with an empty `flagged`, which on the truthful
member is scored CORRECT — inflating discrimination.
"""
from __future__ import annotations

import sys

from harness.inversion_run import _norm_label, _norm_verdict


def test_label_shapes_normalise():
    for raw in ("[C2]", "C2", "c2", "Claim 2", " C 2 ", "claim C2"):
        assert _norm_label(raw) == "C2", raw
    assert _norm_label("the second one") is None


def test_verdict_shapes_normalise():
    assert _norm_verdict("CONTRADICTED.") == "CONTRADICTED"
    assert _norm_verdict(" contradicted ") == "CONTRADICTED"
    assert _norm_verdict({"verdict": "SUPPORTED"}) == "SUPPORTED"
    assert _norm_verdict("NOT_DETERMINABLE") == "NOT_DETERMINABLE"
    assert _norm_verdict("probably false") is None
    assert _norm_verdict("") is None


def test_unrecognised_shapes_are_not_silently_dropped():
    assert _norm_label("Q7") is None and _norm_verdict("MAYBE") is None


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    f = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}"); f += 1
    print(f"{len(TESTS)-f}/{len(TESTS)} passed")
    sys.exit(f)
