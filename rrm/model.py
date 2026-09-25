"""Two-level predictive-coding model of the relevance rate (manuscript, Box 3).

Notation follows the box.

    R_t      observed relevance rate in interval t (concern-relevant events / min)
    mu1      current expectation (ongoing activity)
    mu2      habitual expectation (daily life as a whole; never receives R_t)

    delta1 = R_t - mu1                     upward error, level 1
    delta2 = mu1 - mu2                     error travelling in both directions

    mu1 <- mu1 + w1 * delta1 - w_down * delta2
    mu2 <- mu2 + w2 * delta2

The weights depend on relative precision (the precision of the incoming signal relative to
that of the prediction; precision = inverse variance). This is an illustrative model inspired by predictive
coding: the weights are set or switched, not derived from an explicit representation of
uncertainty. None of the values is measured.

    w1      high (w1_high) when the recent errors reveal a surprising INCREASE in the rate and
            the current error is itself positive; low (w1_low) otherwise. Negative errors are
            therefore always revised slowly: this is the model's hypothesis that expectations
            about concern-relevant events resist downward revision (by extension of findings on
            Pavlovian extinction for threat- and positive-relevant stimuli).
            Surprise s = smoothed delta1^2 / (mu1 / dt): the squared error relative to the
            variance of an observed rate predicted at mu1, under the assumption that events
            arrive at random (Poisson). The direction of change
            is the sign of the smoothed error over the same window.
    w_down  larger in calm activities (few events inform mu1), smaller in dense ones:
            w_down = w_down0 / (1 + mu1 / mu_star).
    w2      small: mu2 changes over days.

A single current expectation is carried across activities (no context-specific reset),
as argued in the main text.

Alternative mechanisms (used to show what the box's choices do):
    surprise_mode = "both"       surprising changes in either direction speed up revision
    surprise_mode = "sustained"  surprise from the smoothed mean error, both directions
    surprise_mode = "sign"       w1 set by the sign of each error (w1_high if delta1 > 0)
    precision_down = False       fixed downward weight w_down0
"""
from dataclasses import dataclass, asdict, replace
import numpy as np


@dataclass(frozen=True)
class Params:
    w1_low: float = 1 / 20          # upward weight without surprising increase
    w1_high: float = 0.7            # upward weight under surprising increase
    surprise_threshold: float = 10.0
    surprise_smoothing: float = 0.3  # per-interval smoothing (window of a few minutes)
    w_down0: float = 1 / 20         # downward weight when evidence is absent
    mu_star: float = 0.25           # rate (events/min) at which w_down is halved
    w2: float = 1 / (3 * 1440)      # habitual level: time constant ~ days
    dt: float = 1.0                 # interval length (min)
    surprise_mode: str = "increase"  # "increase" | "both" | "sustained" | "sign"
    precision_down: bool = True

    def with_(self, **kw):
        return replace(self, **kw)

    def as_dict(self):
        return asdict(self)


def simulate(lam, params=Params(), n_seeds=8, seed=0, mu1_0=None, mu2_0=None, noise=True):
    """Simulate the model on a sequence of true rates `lam` (events/min, one value per interval).

    Returns a dict of arrays with shape (n_seeds, T): mu1, mu2, w1, R.
    Seeds are simulated in parallel (independent Poisson draws).
    """
    p = params
    lam = np.asarray(lam, float)
    T = lam.size
    rng = np.random.default_rng(seed)
    if noise:
        R = rng.poisson(lam * p.dt, size=(n_seeds, T)) / p.dt
    else:
        R = np.broadcast_to(lam, (n_seeds, T)).astype(float)

    mu1 = np.full(n_seeds, lam[:60].mean() if mu1_0 is None else mu1_0, float)
    mu2 = mu1.copy() if mu2_0 is None else np.full(n_seeds, mu2_0, float)
    s = np.ones(n_seeds)          # smoothed surprise
    ebar = np.zeros(n_seeds)      # smoothed error (direction of change)
    a = p.surprise_smoothing

    out_mu1 = np.empty((n_seeds, T)); out_mu2 = np.empty((n_seeds, T)); out_w1 = np.empty((n_seeds, T))
    for t in range(T):
        delta1 = R[:, t] - mu1
        delta2 = mu1 - mu2
        var = np.maximum(mu1, 1e-9) / p.dt           # predicted variance of the observed rate
        ebar = (1 - a) * ebar + a * delta1

        if p.surprise_mode in ("increase", "both"):
            s = (1 - a) * s + a * delta1 ** 2 / var
            surprised = s > p.surprise_threshold
            if p.surprise_mode == "increase":
                surprised &= (ebar > 0) & (delta1 > 0)
            w1 = np.where(surprised, p.w1_high, p.w1_low)
        elif p.surprise_mode == "sustained":
            s = ebar ** 2 / (var * a / (2 - a))
            w1 = np.where(s > p.surprise_threshold, p.w1_high, p.w1_low)
        elif p.surprise_mode == "sign":
            w1 = np.where(delta1 > 0, p.w1_high, p.w1_low)
        else:
            raise ValueError(p.surprise_mode)

        w_down = p.w_down0 / (1 + mu1 / p.mu_star) if p.precision_down else np.full(n_seeds, p.w_down0)

        mu1 = mu1 + w1 * delta1 - w_down * delta2
        mu2 = mu2 + p.w2 * delta2
        mu1 = np.maximum(mu1, 1e-6)                 # a rate cannot be negative

        out_mu1[:, t] = mu1; out_mu2[:, t] = mu2; out_w1[:, t] = w1
    return dict(mu1=out_mu1, mu2=out_mu2, w1=out_w1, R=R)
