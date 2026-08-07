"""Build the GATE-A cold-read packet. Blindness is enforced by construction, not by send-order.

WHY THIS EXISTS: the cold read was contaminated because the diagnostic reached the reader before
the sentences did. The ordering was correct and lived only in message discipline — the fourth
prose obligation this week that did not self-enforce. A gate whose blindness is disputable does not
gate; worse, it launders, because "the outside read cleared it" enters the record with no trace of
what the reader already knew.

This script reads EXACTLY ONE input file: items/_measure-blind.json (ids + sentences). It cannot
open the diagnostic, the split results, the band assignments or the candidate file, because it never
names them. It then re-checks its own output for leakage before writing.

    python3 -m harness.build_cold_read      # -> build/cold-read-packet.md, send verbatim
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "items" / "_measure-blind.json"          # the ONLY file this script may read
OUT = REPO / "build" / "cold-read-packet.md"

PROMPT = """For each pair below, the two sentences differ by one grammatical change.
Answer three things per pair.

1. Does sentence B assert something about how the system behaves NOW?
   Yes / no / genuinely both readings available.
2. Do A and B differ by more than that one change — dropped words, altered nouns,
   anything beyond the tense marking?
3. Does B read as a REQUIREMENT the system is under, as opposed to a prediction
   about a future change?

Answer for all 48 before reasoning about any of them as a set.
"""

# WHITELIST, not a blacklist. The first attempt scanned for forbidden vocabulary and refused on
# `cut` — which is a legitimate word in "Writes have been cut over to the new column". A blacklist
# cannot tell metadata from English, so it either false-positives on content or misses a field it
# was not told about. A whitelist of permitted LINE SHAPES cannot do either: anything that is not
# the fixed prompt, a blank, an id, or an A/B sentence is a leak by construction.
ID = re.compile(r"^m\d{2}$")
AB = re.compile(r"^  [AB]: \S.*$")


def build() -> str:
    items = json.loads(SOURCE.read_text())
    lines = [PROMPT, ""]
    for it in items:
        lines.append(f"{it['id']}")
        lines.append(f"  A: {it['claim_false']}")
        lines.append(f"  B: {it['claim_true']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    packet = build()

    # Self-check: every line is the fixed prompt, blank, an id, or an A/B sentence. Nothing else.
    allowed = set(PROMPT.splitlines())
    leaks = [l for l in packet.splitlines()
             if l.strip() and l not in allowed and not ID.match(l) and not AB.match(l)]
    if leaks:
        raise SystemExit(f"REFUSING — {len(leaks)} line(s) outside the permitted shapes: {leaks[:3]}")

    n = packet.count("\n  A: ")
    if n != len(json.loads(SOURCE.read_text())):
        raise SystemExit(f"REFUSING — {n} pairs rendered, source has "
                         f"{len(json.loads(SOURCE.read_text()))}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(packet)
    print(f"wrote {OUT} — {n} pairs, {len(packet.splitlines())} lines")
    print("  reads only items/_measure-blind.json; cannot see the diagnostic by construction")
    print("  leakage self-check: clean")
    print("\n  SEND THIS FILE VERBATIM AND NOTHING ELSE.")


if __name__ == "__main__":
    main()
