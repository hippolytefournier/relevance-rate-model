"""Each claim made in Box 3 (and the parameters-of-use section) as a simulation check.

A claim returns: id, source, kind, statement (as written in the manuscript), criterion,
observed value, pass/fail.

Two quantities are distinguished:
  - the instantaneous error of the box, delta1 = R_t - mu1 (its negative is the momentary shortfall);
  - the MISMATCH INDEX used in the results: the expected shortfall of the rate the activity
    delivers below the current expectation, max(mu1 - lambda, 0), computed for each simulated
    trajectory and then averaged over trajectories and intervals (events per minute).

Kinds: `claim` (stated in the manuscript), `sanity` (validity check of the simulation),
`property` (model behaviour reported for transparency, not stated in the manuscript).
"""
import numpy as np
from .model import Params, simulate
from .scenarios import (day, days, spread, HEAVY, FRAGMENTATION, CALM, DENSE, STREAM, DAY, WAKE)

SESSION_INTO_CALM = [(770, 10)]    # ends 13:00, calm block 13:00-14:30
CORE = ["S1", "C3", "C4", "C4b", "C7", "C8", "C9"]   # claims the manuscript's argument rests on


def equilibrium(p, n_days=20, n_seeds=4):
    sim = simulate(days(*[day()] * n_days), p, n_seeds=n_seeds, seed=123)
    return float(sim["mu1"][:, -1].mean()), float(sim["mu2"][:, -1].mean())


def run(p, lam, init, n_seeds, seed=0, noise=True):
    """Returns (mu1 for every trajectory, mean mu1, mean mu2)."""
    sim = simulate(lam, p, n_seeds=n_seeds, seed=seed, mu1_0=init[0], mu2_0=init[1], noise=noise)
    return sim["mu1"], sim["mu1"].mean(0), sim["mu2"].mean(0)


def mismatch(lam, mu1_all, mask):
    """Mismatch index: per-trajectory positive shortfall, then averaged."""
    return float(np.mean(np.maximum(mu1_all[:, mask] - lam[mask], 0)))


def half_time(x, target):
    """Days until series x (per-minute) first reaches target."""
    idx = np.nonzero(x >= target)[0] if target >= x[0] else np.nonzero(x <= target)[0]
    return idx[0] / DAY if idx.size else float("inf")


def fall_time(p, init, stream, n_seeds):
    """1/e decay (min) of the excess expectation after a 10-min session, relative to no session."""
    lam = np.r_[np.full(120, CALM), np.full(10, stream), np.full(180, CALM)]
    _, m, _ = run(p, lam, init, n_seeds)
    _, m0, _ = run(p, np.full(lam.size, CALM), init, n_seeds)
    exc = m[130:] - m0[130:]
    below = np.nonzero(exc < exc[0] / np.e)[0]
    return int(below[0]) if below.size else 999


def evaluate(p=Params(), n_seeds=8):
    init = equilibrium(p)
    C = []

    def claim(cid, source, statement, criterion, value, passed, kind="claim"):
        C.append(dict(id=cid, source=source, kind=kind, statement=statement,
                      criterion=criterion, value=value, passed=bool(passed), core=cid in CORE))

    # --- No use --------------------------------------------------------------------
    lam = days(*[day()] * 7)
    mu1_all, mu1, mu2 = run(p, lam, init, n_seeds)
    _, mu1_nf, _ = run(p, lam, init, 1, noise=False)
    d = slice(6 * DAY, 7 * DAY); l, m = lam[d], mu1[d]
    ends = lambda r: [m[i] for i in range(DAY - 20) if l[i] == r and l[i + 20] != r]
    calm_end, dense_end = np.mean(ends(CALM)), np.mean(ends(DENSE))
    claim("C1", "Box 3, Two expectations", "The current expectation concerns the ongoing activity (low in calm, higher in dense activities).",
          "late in blocks, current expectation lower in calm than in dense activities",
          f"calm {calm_end:.2f} vs dense {dense_end:.2f} (true {CALM} vs {DENSE})", calm_end < dense_end)
    claim("C2", "Box 3, Two expectations", "The habitual expectation concerns daily life as a whole.",
          "habitual expectation lies between calm and dense rates",
          f"{mu2[-1]:.2f} (24-h mean rate {l.mean():.2f})", CALM < mu2[-1] < DENSE)
    infl = m.mean() / mu1_nf[d].mean()
    claim("S1", "Validity check", "Poisson noise does not inflate the expectation (false alarms of the surprise rule stay rare).",
          "without use, 24-h mean expectation with noise within 10% of the same model without noise",
          f"ratio {infl:.3f}", abs(infl - 1) < 0.10, kind="sanity")
    calm_mask = np.zeros(lam.size, bool); calm_mask[d] = l == CALM
    base_calm = float(np.mean(np.maximum(mu1_nf[calm_mask] - lam[calm_mask], 0)))
    claim("C11", "Box 3, Errors travel up, predictions travel down", "A calm activity may fall slightly short of what is expected, even without social media use.",
          "without use or noise, mismatch index in calm activities > 0.05 events/min",
          f"{base_calm:.2f} events/min", base_calm > 0.05)

    # --- One session ------------------------------------------------------------------
    _, mA, bA = run(p, day(SESSION_INTO_CALM), init, n_seeds)
    _, m0, b0 = run(p, day(), init, n_seeds)

    def rise(start):
        """Share of the gap to the stream's rate closed after 2 min of a 10-min session."""
        _, m_, _ = run(p, day([(start, 10)]), init, n_seeds)
        pre = m_[start - 1]
        return float((m_[start + 1] - pre) / (STREAM - pre))
    r_calm, r_dense = rise(640), rise(770)
    claim("C3", "Box 3, Calibration and after-effect", "Entering the stream is highly surprising, so the current expectation quickly approaches the stream's rate (calibration).",
          "after 2 min in the stream, >= 60% of the gap closed (session starting from a calm activity; from a dense one reported)",
          f"from calm {100 * r_calm:.0f}%; from dense {100 * r_dense:.0f}%", r_calm >= 0.6)
    tau = fall_time(p, init, STREAM, n_seeds)
    claim("C4", "Box 3, Calibration and after-effect", "After the stream is left, the current expectation falls back only gradually (after-effect).",
          "excess expectation after a 10-min session decays to 1/e in 15-90 min", f"{tau} min", 15 <= tau <= 90)
    taus = {r: fall_time(p, init, r, n_seeds) for r in (4.0, 16.0, 32.0)}
    claim("C4b", "Box 3, Calibration and after-effect", "Leaving the stream is surprising too, but this does not speed up the fall: a denser stream does not shorten the after-effect.",
          "1/e decay >= 15 min after streams at 4, 16 and 32 events/min",
          " / ".join(f"{int(r)}: {t} min" for r, t in taus.items()), all(t >= 15 for t in taus.values()))
    base = np.r_[np.full(120, CALM), np.full(10, STREAM)]
    lc, ld = np.r_[base, np.full(90, CALM)], np.r_[base, np.full(90, DENSE)]
    mcA, _, _ = run(p, lc, init, n_seeds); mdA, _, _ = run(p, ld, init, n_seeds)
    after = np.zeros(lc.size, bool); after[130:160] = True
    mmA, mmB = mismatch(lc, mcA, after), mismatch(ld, mdA, after)
    claim("C5", "Box 3, Calibration and after-effect", "The mismatch is largest when the next activity is calm.",
          "same session and preceding activity: mismatch index in the next 30 min larger if that activity is calm than dense",
          f"calm {mmA:.2f} vs dense {mmB:.2f} events/min", mmA > mmB)

    # --- Sessions and the habitual expectation ------------------------------------------
    def habitual(sessions, n, rate=STREAM, ns=max(2, n_seeds // 2)):
        l_ = days(*[day(sessions, rate)] * n)
        m_all, m_, b_ = run(p, l_, init, ns)
        return b_, m_all, m_, l_
    dmu2 = (bA[-1] - b0[-1]) / b0[-1]
    b1, *_ = habitual([(750, 10)], 28); bn, *_ = habitual([], 28)
    daily = b1[-1] / bn[-1] - 1
    claim("C6", "Box 3, Persistence", "Each session adds a little to the habitual expectation.",
          "one isolated session: < 5% by the end of the day; one session a day for 28 days: > 5%",
          f"isolated +{100 * dmu2:.1f}%; one a day for 28 days +{100 * daily:.0f}%", dmu2 < 0.05 and daily > 0.05)
    counts = {k: habitual(spread(k, 10), 7)[0][-1] for k in (1, 4, 8, 16)}
    cv = list(counts.values())
    claim("C7", "Box 3, Persistence", "The habitual expectation rises over days with the number of sessions.",
          "after 7 days, habitual expectation rises with 1 < 4 < 8 < 16 sessions of 10 min per day",
          " / ".join(f"{k}: {v:.2f}" for k, v in counts.items()), all(np.diff(cv) > 0))
    gaps = {g: habitual([(450 + (10 + g) * k, 10) for k in range(8)], 7)[0][-1] for g in (10, 30, 110)}  # all 8 sessions within the day
    claim("M1", "Model property", "At equal number and length, sessions that overlap add less to the habitual expectation than spaced ones.",
          "8 x 10 min per day, gaps of 10 / 30 / 110 min (reported, not stated in the manuscript)",
          " / ".join(f"gap {g} min: {v:.2f}" for g, v in gaps.items()), True, kind="property")

    lamH = days(*[day(HEAVY)] * 14, *[day()] * 14); lamN = days(*[day()] * 28)
    mH_all, _, bH = run(p, lamH, init, n_seeds); mN_all, _, bN = run(p, lamN, init, n_seeds)
    first = HEAVY[0][0]; msk = np.zeros(lamH.size, bool); msk[13 * DAY + WAKE:13 * DAY + first] = True
    mmH, mmN = mismatch(lamH, mH_all, msk), mismatch(lamN, mN_all, msk)
    claim("C8", "Box 3, Persistence", "A raised habitual expectation holds the current expectation above what calm activities deliver, even with no recent session.",
          "after 14 days of 16 x 10 min/day, mismatch index on waking (before any session) > 2 x no-use and > 0.1 events/min",
          f"{mmH:.2f} vs {mmN:.2f} events/min", mmH > 2 * mmN and mmH > 0.1)
    end_use = 14 * DAY - 1; rise_amt = bH[end_use] - bN[end_use]
    t_half_dn = half_time(bH[14 * DAY:] - bN[14 * DAY:], 0.5 * rise_amt)
    calm = lambda k: np.r_[np.zeros(k * DAY, bool), day() == CALM, np.zeros(lamH.size - (k + 1) * DAY, bool)]
    mm_use, mm_abs = mismatch(lamH, mH_all, calm(13)), mismatch(lamH, mH_all, calm(16))
    claim("C9", "Box 3, Persistence", "This persistence fades when the pattern of use changes, over days rather than minutes.",
          "after use stops, habitual half-recovery between 1 and 14 days; calm mismatch index lower after 3 days",
          f"half-recovery {t_half_dn:.1f} d; calm mismatch {mm_use:.2f} -> {mm_abs:.2f}",
          1 <= t_half_dn <= 14 and mm_abs < mm_use)
    _, m60, _ = run(p, day([(600, 60)]), init, n_seeds)
    plateau = m60[659] / STREAM
    claim("C10", "Box 3, Precision", "The downward weight is smaller in dense activities, so the habitual expectation does not hold the current one down during use.",
          "after 60 min in the stream, current expectation >= 90% of the stream's rate", f"{100 * plateau:.0f}%", plateau >= 0.9)

    # --- Parameters of use (main text) ---------------------------------------------------
    hv = [habitual(spread(8, 10), 7, rate=r)[0][-1] for r in (4.0, 8.0, 16.0)]
    claim("P1", "Main text, parameters of use", "A higher within-session relevance rate raises the habitual expectation.",
          "stream at 4 / 8 / 16 events/min -> higher habitual expectation after 7 days",
          " / ".join(f"{v:.2f}" for v in hv), hv[0] < hv[1] < hv[2])
    peaks = {}
    for L in (2, 5, 10, 20, 40):
        _, m_, _ = run(p, day([(770, L)]), init, n_seeds); peaks[L] = m_[770 + L - 1] / STREAM
    claim("P2", "Main text, parameters of use", "Session length raises the expectation until a ceiling that sessions of ordinary duration already reach.",
          "a 10-min session reaches >= 90% of the level reached by a 40-min session",
          " / ".join(f"{L} min {100 * v:.0f}%" for L, v in peaks.items()), peaks[10] >= 0.9 * peaks[40])
    fr = {k: habitual(v, 7) for k, v in FRAGMENTATION.items()}
    fv = [fr[k][0][-1] for k in FRAGMENTATION]
    claim("P3", "Main text, parameters of use", "At equal total time, fragmentation raises the habitual expectation (up to a ceiling).",
          "habitual after 7 days: 1x160 < 4x40 < 16x10 (32x5 reported)",
          " / ".join(f"{k} {v:.2f}" for k, v in zip(FRAGMENTATION, fv)), fv[0] < fv[1] < fv[2])
    ch = [habitual(HEAVY, n)[0][-1] for n in (1, 3, 7, 14, 28)]
    claim("P4", "Main text, parameters of use", "Chronicity raises the habitual expectation, which then saturates.",
          "habitual rises over 1/3/7/14 days; gain 14->28 d smaller than 3->7 d",
          " / ".join(f"{n} d {v:.2f}" for n, v in zip((1, 3, 7, 14, 28), ch)),
          ch[0] < ch[1] < ch[2] < ch[3] and (ch[4] - ch[3]) < (ch[2] - ch[1]))
    last = slice(6 * DAY, 7 * DAY)
    ratio = fr["16 x 10 min"][2][last].mean() / fr["1 x 160 min"][2][last].mean()
    claim("P5", "Main text, parameters of use", "At equal total time, fragmented use raises the current expectation averaged over the whole day.",
          "all-day mean current expectation >= 1.2 x higher for 16 x 10 min than for 1 x 160 min",
          f"fragmented / concentrated = {ratio:.2f}", ratio >= 1.2)
    return C
