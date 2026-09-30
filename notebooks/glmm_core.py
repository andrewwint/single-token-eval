"""Maximum-likelihood logistic mixed models by Gauss-Hermite quadrature. numpy + scipy only.

Written for `mixed_model.ipynb` because lme4 is not available in the analysis environment. The
likelihood is integrated numerically (the approach behind lme4's `glmer(nAGQ > 1)`), not
approximated by penalised quasi-likelihood, so log-likelihoods support likelihood-ratio tests.

Data are cells: k YES out of n draws for one (item, model) pair. Draws inside a cell are exchangeable
given the random effects, so a binomial cell carries the same likelihood as its n Bernoulli rows (up
to a constant that is identical across every model fitted to the same data).

  level 1  ordinary logistic                 k_ij ~ Bin(n_ij, logit^-1(x_ij b))
  level 2  random intercept for item          ... logit^-1(x_ij b + u_i),         u_i  ~ N(0, s_u^2)
  level 3  + random intercept for cell        ... logit^-1(x_ij b + u_i + v_ij),  v_ij ~ N(0, s_v^2)

i = item (sentence), j = model. Level 3 is draws within (item x model) cells within items: v_ij is
what one model does with one sentence beyond its own baseline and the sentence's shared pull.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln, log_expit, logsumexp

_X, _W = np.polynomial.hermite.hermgauss(30)
NODES = np.sqrt(2.0) * _X               # standard-normal nodes
LOGW = np.log(_W / np.sqrt(np.pi))      # standard-normal log-weights
LATENT_RESID = np.pi ** 2 / 3           # level-1 residual variance on the latent logistic scale


def _cell_ll(eta, k, n):
    """Binomial log-likelihood without the combinatorial constant; broadcasts over eta."""
    return k * log_expit(eta) + (n - k) * log_expit(-eta)


def fit(k, n, X, item, levels=2):
    """ML fit. k, n: per-cell counts; X: fixed-effect design (cells x p); item: integer codes."""
    k = np.asarray(k, float)[:, None]
    n = np.asarray(n, float)[:, None]
    X = np.asarray(X, float)
    item = np.asarray(item)
    n_items = item.max() + 1
    p = X.shape[1]
    const = (gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)).sum()

    def negll(theta):
        eta = (X @ theta[:p])[:, None]
        if levels == 1:
            return -_cell_ll(eta, k, n).sum()
        su = np.exp(theta[p])
        eta_u = eta + su * NODES[None, :]                        # cells x u-nodes
        if levels == 2:
            cell_u = _cell_ll(eta_u, k, n)                       # cells x u-nodes
        else:
            sv = np.exp(theta[p + 1])
            e3 = eta_u[:, :, None] + sv * NODES[None, None, :]   # cells x u x v
            cell_u = logsumexp(_cell_ll(e3, k[:, :, None], n[:, :, None]) + LOGW, axis=2)
        item_u = np.zeros((n_items, len(NODES)))
        np.add.at(item_u, item, cell_u)                          # sum cells within item
        return -logsumexp(item_u + LOGW, axis=1).sum()

    b0 = minimize(lambda t: -_cell_ll((X @ t)[:, None], k, n).sum(), np.zeros(p), method="BFGS").x
    start = np.concatenate([b0, np.full(levels - 1, np.log(1.0))])
    res = minimize(negll, start, method="BFGS", options={"gtol": 1e-5, "maxiter": 500})
    theta = res.x
    cov = np.linalg.pinv(_hessian(negll, theta))
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    out = {"beta": theta[:p], "se": se[:p], "loglik": -res.fun + const, "converged": bool(res.success),
           "n_params": len(theta), "theta": theta, "cov": cov}
    if levels >= 2:
        out["sigma_item"] = float(np.exp(theta[p]))
    if levels == 3:
        out["sigma_cell"] = float(np.exp(theta[p + 1]))
    return out


def blup_item(k, n, X, item, res):
    """Posterior mean of each item's random intercept (the per-sentence 'reads as present' pull),
    for the two-level model. Integrates the same quadrature used in the fit."""
    k = np.asarray(k, float)[:, None]; n = np.asarray(n, float)[:, None]
    item = np.asarray(item); p = X.shape[1]
    eta = (np.asarray(X, float) @ res["beta"])[:, None]
    su = res["sigma_item"]
    cell_u = _cell_ll(eta + su * NODES[None, :], k, n)
    item_u = np.zeros((item.max() + 1, len(NODES)))
    np.add.at(item_u, item, cell_u)
    post = item_u + LOGW
    post = np.exp(post - logsumexp(post, axis=1, keepdims=True))
    return post @ (su * NODES)


def _hessian(f, x, h=1e-4):
    m = len(x)
    H = np.zeros((m, m))
    for i in range(m):
        for j in range(i, m):
            ei = np.zeros(m); ei[i] = h
            ej = np.zeros(m); ej[j] = h
            H[i, j] = H[j, i] = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * h * h)
    return H
