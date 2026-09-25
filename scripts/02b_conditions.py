"""For claims that do not hold in every random setting, find the parameters they depend on.

For each such claim and each parameter, compare the pass rate among random settings whose
value lies below vs above the reference (log scale).
"""
import csv, math
from _common import OUT, write_csv
from rrm import Params

REF = Params()
rows = [r for r in csv.DictReader(open(OUT / "robustness.csv")) if r["setting"].startswith("random")]
summary = list(csv.DictReader(open(OUT / "robustness_summary.csv")))
params = ["w1_low", "w1_high", "surprise_threshold", "surprise_smoothing", "w_down0", "mu_star", "w2"]

out = []
for s in summary:
    if float(s["pass_rate_random"]) >= 0.9:
        continue
    cid = s["id"]
    for k in params:
        ref = getattr(REF, k)
        lo = [int(r[cid]) for r in rows if math.log(float(r[k]) / ref) < 0]
        hi = [int(r[cid]) for r in rows if math.log(float(r[k]) / ref) >= 0]
        out.append(dict(id=cid, statement=s["statement"], parameter=k,
                        pass_rate_below_reference=round(sum(lo) / len(lo), 2),
                        pass_rate_above_reference=round(sum(hi) / len(hi), 2),
                        difference=round(sum(hi) / len(hi) - sum(lo) / len(lo), 2)))
write_csv(OUT / "robustness_conditions.csv", out)
for cid in dict.fromkeys(o["id"] for o in out):
    top = sorted([o for o in out if o["id"] == cid], key=lambda o: -abs(o["difference"]))[:2]
    print(cid, "; ".join(f"{o['parameter']}: {o['pass_rate_below_reference']} below vs {o['pass_rate_above_reference']} above" for o in top))
