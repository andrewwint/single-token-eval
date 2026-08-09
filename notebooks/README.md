# notebooks

`analysis.ipynb` is a **build artifact**. `build_notebook.py` is the source.

```bash
../.venv-analysis/bin/python build_notebook.py
../.venv-analysis/bin/jupyter nbconvert --to notebook --execute --inplace analysis.ipynb
```

Keeping the source as a `.py` means the notebook regenerates deterministically and reviews as a
diff rather than as JSON with embedded outputs. Figures in `figures/` are written from the same
figure objects the analysis cells produce, so an article figure cannot drift from the cell that
generated it.

**Every number in every figure is computed from the loaded artifacts.** No constant is carried over
from the diagnostic docs — the notebook re-derives the panel offsets, the between-model share, the
item variance share, the pairwise correlations, the STOP condition, the construction test and the
band fill from `results/round1-candidate-splits.json` and `items/candidates-round1.json`.

Environment: `.venv-analysis` (python 3.14.2, numpy 2.5.1, scipy 1.18.0, matplotlib 3.11.1).
Seed 20260806, the same one pinned in the pre-registration.

## Schematics are fenced

The notebook ends with a **schematic** — a redraw of Cockburn's communication-effectiveness curves.
It is a drawing, not a measurement: its coordinates are hand-chosen and nothing in it derives from
this study.

It is separated four ways, because one way is not enough for someone skimming a figure directory:
a banner cell, a `schematic-` filename prefix, its own `figures/schematic/` directory, and a red
caption inside the image itself. Anything reusing it must carry the *after Cockburn* attribution.

## What the notebook does not contain

No outcome measure. **No verdict draw has fired.** Nothing in it speaks to whether models catch
anything; that requires the verdict arm, which is blocked.
