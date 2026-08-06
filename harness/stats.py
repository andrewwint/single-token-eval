"""Pure statistics for the study. No dependency beyond the standard library.

`wilson_ci` and `discrimination_guard` are VENDORED from the sibling study
`review-discipline-eval` (`harness/stats.py`, `harness/ablation.py`), copied 2026-08-06. They are
frozen helpers with no live upstream, so a copy carries no drift risk — unlike mirroring a predicate
that changes, which that study had to manage with generated conformance vectors.

`hypergeom_tail` and `pair_threshold` are new here: this study's classes are unbalanced, so a
binomial null would be wrong.

Docstring examples double as sanity checks (run: python3 -m doctest harness/stats.py -v).
"""
from __future__ import annotations

import math


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score 95% CI for a binomial proportion k/n. Correct at the boundaries where the
    Wald interval degenerates.

    >>> lo, hi = wilson_ci(0, 20); round(lo, 3), round(hi, 3)
    (0.0, 0.161)
    >>> lo, hi = wilson_ci(20, 20); round(lo, 3), round(hi, 3)
    (0.839, 1.0)
    >>> lo, hi = wilson_ci(5, 20); round(lo, 3), round(hi, 3)
    (0.112, 0.469)
    """
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def hypergeom_tail(n: int, k_success: int, draws: int, t: int) -> float:
    """P(X >= t) drawing `draws` from `n` containing `k_success` successes, without replacement.

    The right null for a judge that flags a set of sentences with no information about which are
    false. A binomial null would assume it answers each independently at a fixed rate, which
    over-rewards a judge that simply flags a lot.

    >>> round(hypergeom_tail(48, 12, 12, 7), 4)
    0.0047
    >>> round(hypergeom_tail(48, 12, 12, 3), 3)   # the expected count is 3
    0.638
    """
    lo = max(0, draws - (n - k_success))
    hi = min(draws, k_success)
    return sum(
        math.comb(k_success, i) * math.comb(n - k_success, draws - i) / math.comb(n, draws)
        for i in range(max(t, lo), hi + 1)
    )


def pair_threshold(n: int, k_false: int, alpha: float = 0.01) -> tuple[int, float]:
    """Smallest hit-count clearing `alpha` when a judge flags exactly `k_false` of `n` sentences.

    >>> pair_threshold(48, 12)[0]
    7
    """
    for t in range(k_false + 1):
        p = hypergeom_tail(n, k_false, k_false, t)
        if p <= alpha:
            return t, p
    return k_false, hypergeom_tail(n, k_false, k_false, k_false)


def discrimination_guard(tier_scores: dict[str, float]) -> dict:
    """Can this item set separate tiers at all? `tier_scores`: {tier: discrimination_rate}, ideally
    including a PROBE tier expected to score lower. If every tier — probe included — scores
    identically, the set cannot discriminate, so an equivalence claim is unsupported: report
    "insufficient discrimination" rather than concluding the tiers are equal.

    VENDORED from review-discipline-eval `harness/ablation.py`.

    >>> discrimination_guard({"opus": 0.8, "probe": 0.8})["discriminating"]
    False
    >>> discrimination_guard({"opus": 0.8, "probe": 0.3})["spread"]
    0.5
    """
    vals = list(tier_scores.values())
    spread = (max(vals) - min(vals)) if vals else 0.0
    discriminating = spread > 0.0
    return {
        "discriminating": discriminating,
        "spread": spread,
        "tiers": dict(tier_scores),
        "verdict": ("discriminating" if discriminating
                    else "insufficient discrimination — cannot conclude equivalence"),
    }
