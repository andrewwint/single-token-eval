# Single-token inversions — a discipline and a fixture class

Two outputs of one insight, from the baton 1.1.2 fix: the tense flip `no longer depends` → `will no longer
depend` inverted a sentence between a *false present enforcement claim* and an *honest future statement* — and
a careful independent reviewer read it wrong. That one-token inversion is the seed of both a review
**discipline** and a **fixture class**.

**The conceptual core (preserve above all):** an honesty claim is a *semantic assertion*, and its truth can
flip on a single token exactly the way a conditional flips on one operator. So **prose claims deserve
code-level review rigor — because they invert on single tokens the same way code does.** This is the
"treat prose + schema + hook as one unit" principle in its sharpest form.

---

## 1. The discipline: `baseline-established` (catches `cross-version-artifact`)

Named for the *failure it prevents*, not the action it prescribes — the way `self-disposition` and
`spoofed-signoff` name failures, because that's what makes a reviewer reach for it at the right moment.

- **The check — `baseline-established`:** no divergence finding without an established canonical baseline and
  pinned versions for every artifact compared.
- **The failure it catches — `cross-version-artifact`:** reporting a benign cross-version difference (an
  install lagging its dev source; a released version behind an unreleased one) as a regression or
  contradiction.
- **The reviewer's trigger:** *"I'm about to conclude drift/contradiction"* → *"have I pinned which artifact is
  canonical, and what version each other one is?"*
- **The asymmetry (state it in the guidance — it's the motivator):** *a cross-version diff will almost always
  look like a bug and usually isn't. The cost of pinning the baseline is one check; the cost of skipping it is
  damaging a coherent build.* That sentence is what makes a reviewer run the check instead of trusting the
  plausible-looking diff.

**Keep the drift-vigilance itself.** The discipline is "pin the baseline *before* concluding," not "stop
looking for drift." A reviewer that stops flagging drift because one was a false alarm is worse than one that
flags and verifies. The check adds a step ahead of the conclusion; it does not remove the vigilance.

*Provenance: a real false alarm — an install (1.1.1) read as a regression against its dev source
(1.2.0-candidate), when it was a benign version lag. Being folded into the 1.2.0 verify guidance,
cold-read-reviewed, source edit for approval.*

---

## 2. The fixture class: single-token inversions (an FC-family member)

**The family** — one token changes, meaning inverts, diff is nearly invisible:

| Kind | Inversion |
|---|---|
| operators | `<` / `>`, `==` / `!=` |
| modals | `must` / `must not`, `may` / `must` |
| quantifiers | `all` / `any`, `and` / `or` |
| polarity | an inserted or dropped `not` |
| tense / aspect | `is` / `will be`, present-claim vs future-capability |

**Unifying property: maximum semantic leverage, minimum visual footprint.**

**Why it's a natural FC member, not a side study.** It's the *most dangerous* defect class and the *most
discriminating* fixture class for the **same reason** — it survives a surface read and inverts truth. That
alignment is rare and valuable: the fixture is hard for precisely the mechanism reason we want to measure. A
directed reviewer reading the happy path walks past a flipped `<`; a reviewer that re-derives the invariant
from source catches it. So it tests **source-derivation, not diff-scanning** — the exact axis FC-1/FC-2
already circle. It sharpens that axis rather than opening a new one.

**Why it matters for Passet specifically.** Passet's brand *is* single-token-honest — "designed to" vs "does,"
"closed" vs "closed on the validated config." The defect class this fixture probes is the exact class Passet's
own positioning discipline exists to prevent. The study would measure the reviewer on the failure mode the
product's own honesty rules are built around. That's a tight, motivated study, not a generic one.

---

## 3. Two design traps (make-or-break — build clean)

**A. Cold-read-clean is hardest here, and it's make-or-break.** A single-token inversion trivially telegraphs
— a comment, a test name, a variable, a commit message, or the *surrounding* code making the "correct"
direction obvious from context. If anything hints at the right direction, you're measuring "did the reviewer
read the hint," not "did the reviewer catch the inversion." This class needs the **strictest** version of the
no-answer-key invariant — arguably an independent adversarial pass whose *only* job is *"does anything here
reveal the correct token direction?"* It is the class where a leaked answer key is both most tempting and most
fatal, because the defect is so small that any tell dominates it.

**B. Placement selects the axis — so it's a reusable primitive, not one fixture.** An inversion *in the change
under review* measures directed-review thoroughness (engage-reliability). A pre-existing inversion in a line
*outside* the diff measures source-derivation. The same technique instruments *either* axis depending on where
the token sits. So place it deliberately for the axis you're measuring — and treat "single-token inversion" as
a **reusable adversarial primitive across the whole FC set**, not a single fixture. The flexibility is a
feature only if placement is deliberate rather than incidental.

---

*Status: parked as an FC-family candidate; promote when the fixture-set work resumes (after FC-2 / the release
path). The `baseline-established` discipline folds into the 1.2.0 verify guidance now.*
