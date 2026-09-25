"""Evaluate all claims across parameter values, one by one and jointly.

Two designs:
  one-at-a-time  each parameter at x0.5 and x2 of its reference value, others at reference (10 settings)
  random         64 settings drawn log-uniformly within [x0.5, x2] of every reference value (seed 2026)
"""
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from _common import OUT, write_csv
from rrm import Params, claims

REF = Params()
VARIED = ["w1_low", "w1_high", "surprise_threshold", "surprise_smoothing", "w_down0", "mu_star", "w2"]
N_RANDOM = 64


def settings():
    out = [("reference", {})]
    for k in VARIED:
        for f in (0.5, 2.0):
            v = getattr(REF, k) * f
            if k in ("w1_high", "surprise_smoothing"):
                v = min(v, 0.95)
            out.append((f"one-at-a-time {k} x{f}", {k: v}))
    rng = np.random.default_rng(2026)
    for i in range(N_RANDOM):
        kw = {k: getattr(REF, k) * 2 ** rng.uniform(-1, 1) for k in VARIED}
        kw["w1_high"] = min(kw["w1_high"], 0.95); kw["surprise_smoothing"] = min(kw["surprise_smoothing"], 0.95)
        out.append((f"random {i + 1:02d}", kw))
    return out


def one(item):
    name, kw = item
    res = claims.evaluate(REF.with_(**kw), n_seeds=8)
    row = dict(setting=name, **{k: round(getattr(REF.with_(**kw), k), 6) for k in VARIED})
    row.update({r["id"]: int(r["passed"]) for r in res if r["kind"] != "property"})
    row["core_joint"] = int(all(r["passed"] for r in res if r["core"]))
    row["all_joint"] = int(all(r["passed"] for r in res if r["kind"] != "property"))
    return row, res


if __name__ == "__main__":
    items = settings()
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2))) as ex:
        out = list(ex.map(one, items))
    rows = [r for r, _ in out]
    write_csv(OUT / "robustness.csv", rows)
    meta = {r["id"]: r for r in out[0][1] if r["kind"] != "property"}
    meta["core_joint"] = dict(kind="joint", statement="All core claims jointly (" + ", ".join(claims.CORE) + ")")
    meta["all_joint"] = dict(kind="joint", statement="All claims jointly")
    summary = []
    for i, m in meta.items():
        rnd = [r[i] for r in rows if r["setting"].startswith("random")]
        oat_fail = [r["setting"].replace("one-at-a-time ", "") for r in rows if r["setting"].startswith("one-at") and not r[i]]
        summary.append(dict(id=i, kind=m["kind"], statement=m["statement"],
                            pass_rate_random=round(sum(rnd) / len(rnd), 3),
                            one_at_a_time_failures="; ".join(oat_fail) or "none"))
    write_csv(OUT / "robustness_summary.csv", summary)
    for s in summary:
        print(f"{s['id']:3s} {s['pass_rate_random']:.2f}  OAT fails: {s['one_at_a_time_failures']}")
    print(f"{len(rows)} settings")
