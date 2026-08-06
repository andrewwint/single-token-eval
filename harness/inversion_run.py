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


def render(item: dict, polarity: str, placement: str) -> tuple[str, str, list[str]]:
    """Build the artifact. Claim order is shuffled per item but IDENTICAL across twins — if the
    target landed on a different label in each member, the label itself would carry the answer."""
    claim = item["claim_false"] if polarity == "inverted" else item["claim_true"]
    pool = [claim] + list(item["decoys"])
    order = list(range(len(pool)))
    random.Random(item["id"]).shuffle(order)          # seeded by item id: same order for both twins
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


def one(client, model_key: str, item: dict, polarity: str, placement: str, regime: str, n: int) -> dict:
    body, target, decoys = render(item, polarity, placement)
    prompt = f"{REGIMES[regime]}\n\n{body}\n{RESPONSE_CONTRACT}"
    row = {"model": model_key, "regime": regime, "placement": placement, "item_id": item["id"],
           "kind": item.get("kind", "pair"), "family": item.get("family"), "polarity": polarity,
           "draw": n, "target_claim": target, "decoy_claims": decoys,
           "flagged": [], "verdicts": {}, "self_report": None, "parse_ok": False,
           "in_tok": 0, "out_tok": 0, "contract": CONTRACT_VERSION, "raw": None,
           "target_gold": item["inverted_gold"] if polarity == "inverted" else item["truthful_gold"]}
    try:
        r = client.converse(
            modelId=MODELS[model_key],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": TEMPERATURE},
        )
        txt = r["output"]["message"]["content"][0]["text"]
        row["raw"] = txt            # stored verbatim: a parser change must never need a re-spend
        row["in_tok"] = r["usage"]["inputTokens"]
        row["out_tok"] = r["usage"]["outputTokens"]
        s = txt[txt.find("{"): txt.rfind("}") + 1]
        obj = json.loads(s)
        v = {str(k).strip().upper(): str(val).strip().upper()
             for k, val in (obj.get("verdicts") or {}).items()}
        row["verdicts"] = v
        # `flagged` is the derived binary view the scorer consumes: judged CONTRADICTED.
        row["flagged"] = [c for c, val in v.items() if val == "CONTRADICTED"]
        row["self_report"] = obj.get("self_report")
        row["parse_ok"] = bool(v)
    except Exception as e:                       # a bad draw is recorded, never silently dropped
        row["error"] = f"{type(e).__name__}: {e}"[:200]
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
        want = [l.split()[-1] for l in frozen.read_text().splitlines() if "sha256:" in l]
        if want and digest() not in want[0]:
            raise SystemExit(f"FREEZE MISMATCH — items changed since freeze. {want[0]} != {digest()}")
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
    tok = {"in": 0, "out": 0}
    with DRAWS.open("a") as fh, ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(one, client, *t): t for t in tasks}
        for i, fut in enumerate(as_completed(futs), 1):
            row = fut.result()
            fh.write(json.dumps(row) + "\n"); fh.flush()
            tok["in"] += row["in_tok"]; tok["out"] += row["out_tok"]
            if i % 25 == 0:
                print(f"  {i}/{len(tasks)}  in={tok['in']} out={tok['out']}", flush=True)
    ok = sum(1 for _ in [])  # counted below from the file to include prior runs
    print(f"done. tokens in={tok['in']} out={tok['out']} -> {DRAWS}")


if __name__ == "__main__":
    main()
