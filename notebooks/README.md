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

## What the notebook does not contain

No outcome measure. **No verdict draw has fired.** Nothing in it speaks to whether models catch
anything; that requires the verdict arm, which is blocked.
