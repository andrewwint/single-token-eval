"""Fire a round: one Bedrock Converse call per draw. Append-only, resumable, budget-capped.

Model IDs are RESOLVED, not remembered — every id below was read from
`aws bedrock list-inference-profiles` on 2026-08-06 and confirmed ACTIVE. Anthropic models on this
account are INFERENCE_PROFILE only, so the bare `modelId` from list-foundation-models will not
invoke; the profile id is required.

    python3 -m harness.inversion_run --smoke              # 2 items x 4 models x 1 regime, N=1
    python3 -m harness.inversion_run --budget 40          # full round, capped
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DRAWS = REPO / "results" / "draws.jsonl"
ITEMS = ["items/draft-tense.json", "items/draft-polarity.json"]
REGION = "us-east-1"
MAX_TOKENS = 500          # explicit: an unset value reserves the model maximum and causes throttling
TEMPERATURE = 0.0

# Verified 2026-08-06 by an actual Converse call, not by list-inference-profiles. A profile can be
# ACTIVE and still be denied: opus-5, sonnet-5 and opus-4-8 all list ACTIVE on this account and
# return "not available for this account" when invoked. Profile status is not entitlement.
MODELS = {
    "opus-4.6":   "us.anthropic.claude-opus-4-6-v1",
    "sonnet-4.6": "us.anthropic.claude-sonnet-4-6",
    "haiku-4.5":  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "nova-micro": "us.amazon.nova-micro-v1:0",   # PROBE — expected to score lower
}

# USD per 1M tokens, (input, output). A cap that cannot price a draw cannot stop a run, so an
# unpriced model is refused rather than run uncapped. Refresh from current Bedrock pricing and
# record the date whenever these change.
PRICES_2026_08_06 = {
    "opus-4.6":   (15.00, 75.00),
    "sonnet-4.6": (3.00, 15.00),
    "haiku-4.5":  (1.00, 5.00),
    "nova-micro": (0.035, 0.14),
}

REGIMES = {
    "R0": "Review the change below.",
    "R1": ("Review the change below. Flag any statement in the provided material that is not true "
           "of the source."),
    "R2": ("Work out from the source what actually holds, then check every labelled claim against "
           "what you derived."),
    "R3": ("This is a study of whether single-token changes to a claim are noticed. Read the "
           "material and give your honest reading of it."),
}

# THREE-WAY, not binary. The binary contract asked which claims were "not true of the source",
# which conflates CONTRADICTED with NOT_DETERMINABLE. A future-tense claim is neither true nor false
# of a present-state source, so every model flagged it and discrimination collapsed to ~0 (see
# docs/rounds/smoke-2026-08-06-findings.md). The truth here is three-valued; the contract now says so.
CONTRACT_VERSION = "three-way-v1"
RESPONSE_CONTRACT = """
Judge each labelled claim against the SOURCE, and reply with JSON only:

{"verdicts": {"C1": "CONTRADICTED" | "SUPPORTED" | "NOT_DETERMINABLE", ...},
 "self_report": {"clarity": 1-5, "needs_more_information": true|false,
                 "would_start_without_clarifying": true|false,
                 "understanding": "one sentence on what you were asked to do"}}

  CONTRADICTED     - the source shows the claim is false.
  SUPPORTED        - the source shows the claim is true.
  NOT_DETERMINABLE - the source neither establishes nor refutes it.

Give a verdict for every claim.
"""


def load_items() -> list[dict]:
    out = []
    for p in ITEMS:
        out.extend(json.loads((REPO / p).read_text()))
    return out


def digest() -> str:
    h = hashlib.sha256()
    for p in ITEMS:
        h.update((REPO / p).read_bytes())
    return h.hexdigest()


def render(item: dict, polarity: str, placement: str, draw: int = 0) -> tuple[str, str, list[str]]:
    """Build the artifact.

    Claim order is seeded by (item_id, draw) — two properties that must both hold:

      * IDENTICAL ACROSS TWINS at a given draw. If the target landed on a different label in each
        member, the label itself would carry the answer and the pairing defense would be void.
      * VARYING ACROSS DRAWS. Seeding by item id alone pinned each item's target to one position
        forever, so target position was confounded with item: tense-01 was always C2 and tense-02
        always C3, and a position effect could not be told apart from an item effect.
    """
    claim = item["claim_false"] if polarity == "inverted" else item["claim_true"]
    pool = [claim] + list(item["decoys"])
    order = list(range(len(pool)))
    random.Random(f"{item['id']}:{draw}").shuffle(order)   # same for both twins, varies by draw
    labelled = [f"[C{n+1}] {pool[i]}" for n, i in enumerate(order)]
    target = f"C{order.index(0) + 1}"
    decoys = [f"C{n+1}" for n, i in enumerate(order) if i != 0]

    doc = "\n".join(labelled)
    if placement == "in-diff":
        change = f"--- a/docs/design.md\n+++ b/docs/design.md\n@@\n+{claim}\n"
    else:
        change = ("--- a/docs/design.md\n+++ b/docs/design.md\n@@\n"
                  "+A troubleshooting section was added below.\n")
    body = (f"SOURCE (what the code does):\n{item['source_fact']}\n\n"
            f"CHANGE UNDER REVIEW:\n{change}\n"
            f"DOCUMENT:\n{doc}\n")
    return body, target, decoys


_LABEL = re.compile(r"\bC(?:LAIM)?\s*[-_.]?\s*(\d+)\b")
_VERDICTS = {"CONTRADICTED", "SUPPORTED", "NOT_DETERMINABLE"}


def _norm_label(k) -> str | None:
    """`[C2]`, `Claim 2`, `c2` all mean C2. A model naming the claim in a shape we failed to parse
    was previously read as SILENCE — and silence on the truthful twin scored as a correct clear,
    inflating discrimination. Normalise, then require the target to be present."""
    m = _LABEL.search(str(k).upper())
    return f"C{int(m.group(1))}" if m else None


def _norm_verdict(v) -> str | None:
    if isinstance(v, dict):                       # {"verdict": "..."} / {"v": "..."}
        v = next((x for x in v.values() if isinstance(x, str)), "")
    t = re.sub(r"[^A-Z_]", "", str(v).upper())
    return t if t in _VERDICTS else None


def one(client, model_key: str, item: dict, polarity: str, placement: str, regime: str, n: int) -> dict:
    body, target, decoys = render(item, polarity, placement, draw=n)
    prompt = f"{REGIMES[regime]}\n\n{body}\n{RESPONSE_CONTRACT}"
    row = {"model": model_key, "regime": regime, "placement": placement, "item_id": item["id"],
           "kind": item.get("kind", "pair"), "family": item.get("family"), "polarity": polarity,
           "draw": n, "target_claim": target, "decoy_claims": decoys,
           "flagged": [], "verdicts": {}, "self_report": None, "parse_ok": False,
           "in_tok": 0, "out_tok": 0, "contract": CONTRACT_VERSION, "raw": None,
           "target_gold": item["inverted_gold"] if polarity == "inverted" else item["truthful_gold"]}
    try:
        stop = None
        r = client.converse(
            modelId=MODELS[model_key],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": TEMPERATURE},
        )
        txt = r["output"]["message"]["content"][0]["text"]
        stop = r.get("stopReason")
        row["stop_reason"] = stop
        row["raw"] = txt            # stored verbatim: a parser change must never need a re-spend
        row["in_tok"] = r["usage"]["inputTokens"]
        row["out_tok"] = r["usage"]["outputTokens"]
        s = txt[txt.find("{"): txt.rfind("}") + 1]
        obj = json.loads(s)
        raw_v = (obj.get("verdicts") or {})
        v, unparsed = {}, []
        for k, val in raw_v.items():
            lk, lv = _norm_label(k), _norm_verdict(val)
            if lk is None or lv is None:
                unparsed.append(f"{k}={val}")
            else:
                v[lk] = lv
        row["verdicts"] = v
        row["unparsed_verdicts"] = unparsed
        row["flagged"] = [c for c, val in v.items() if val == "CONTRADICTED"]
        row["self_report"] = obj.get("self_report")
        # A verdict for the TARGET is required. Without it the model said nothing about the claim
        # under test, and treating that as "did not flag" scores silence as a correct clear.
        row["parse_ok"] = target in v
        if not row["parse_ok"]:
            row["error"] = f"no verdict for target {target}; got {sorted(v)} unparsed={unparsed}"
    except Exception as e:
        # M3: transport failure is NOT a parse failure. Parse-failure rate is a statistic about
        # model behaviour; contaminating it with API errors makes it uninterpretable.
        row["error"] = f"{type(e).__name__}: {e}"[:200]
        row["transport_error"] = True
    return row


def done_keys() -> set:
    if not DRAWS.exists():
        return set()
    return {(r["model"], r["regime"], r["placement"], r["item_id"], r["polarity"], r["draw"])
            for r in (json.loads(l) for l in DRAWS.read_text().splitlines() if l.strip())}


def main() -> None:
    import boto3

    smoke = "--smoke" in sys.argv
    budget = float(sys.argv[sys.argv.index("--budget") + 1]) if "--budget" in sys.argv else 5.0

    items = load_items()
    print(f"item digest sha256:{digest()[:16]}  ({len(items)} items)")

    frozen = REPO / "items" / "FROZEN.md"
    if frozen.exists():
        want = [l.split()[-1].strip() for l in frozen.read_text().splitlines() if "sha256:" in l]
        # Fail CLOSED. A FROZEN.md with no digest line previously skipped the check entirely and
        # fired the whole round. An unreadable freeze is a freeze failure, not an absent freeze.
        if not want:
            raise SystemExit("FROZEN.md exists but declares no sha256: line — refusing to fire")
        if len(want) > 1:
            raise SystemExit(f"FROZEN.md declares {len(want)} digests — ambiguous, refusing to fire")
        if want[0].removeprefix("sha256:") != digest():   # exact, not substring
            raise SystemExit(f"FREEZE MISMATCH — {want[0]} != sha256:{digest()}")
    elif not smoke:
        raise SystemExit("no items/FROZEN.md — freeze the item set before a measured round")

    models = list(MODELS) if smoke else list(MODELS)
    regimes = ["R0"] if smoke else list(REGIMES)
    places = ["out-of-diff"] if smoke else ["out-of-diff", "in-diff"]
    use = items[:2] if smoke else items
    n_draws = 1 if smoke else 5

    tasks = []
    have = done_keys()
    for m in models:
        for reg in regimes:
            for pl in places:
                for it in use:
                    pols = ["inverted"] if it.get("kind") == "reverse-single" else ["inverted", "truthful"]
                    for pol in pols:
                        for n in range(n_draws):
                            if (m, reg, pl, it["id"], pol, n) not in have:
                                tasks.append((m, it, pol, pl, reg, n))

    print(f"{len(tasks)} draws to run ({len(have)} already done). budget ${budget}")
    client = boto3.client("bedrock-runtime", region_name=REGION)
    DRAWS.parent.mkdir(exist_ok=True)
    unpriced = [m for m in models if m not in PRICES_2026_08_06]
    if unpriced:
        raise SystemExit(f"no price for {unpriced} — a budget cap that cannot price a draw cannot "
                         f"stop a run. Add rates or remove the model.")
    tok = {"in": 0, "out": 0}
    spent = [0.0]
    with DRAWS.open("a") as fh, ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(one, client, *t): t for t in tasks}
        for i, fut in enumerate(as_completed(futs), 1):
            row = fut.result()
            fh.write(json.dumps(row) + "\n"); fh.flush()
            tok["in"] += row["in_tok"]; tok["out"] += row["out_tok"]
            pin, pout = PRICES_2026_08_06[row["model"]]
            spent[0] += row["in_tok"] / 1e6 * pin + row["out_tok"] / 1e6 * pout
            if spent[0] > budget:
                print(f"  BUDGET ${budget} EXCEEDED at ${spent[0]:.2f} — cancelling queued draws; "
                      f"in-flight will finish. Re-run to resume.", flush=True)
                for f in futs:
                    f.cancel()
                break
            if i % 25 == 0:
                print(f"  {i}/{len(tasks)}  in={tok['in']} out={tok['out']}", flush=True)
    print(f"done. tokens in={tok['in']} out={tok['out']} spend=${spent[0]:.2f} -> {DRAWS}")


if __name__ == "__main__":
    main()
