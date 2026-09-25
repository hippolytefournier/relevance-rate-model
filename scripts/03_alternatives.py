"""What the box's choices do: compare with the mechanisms it does not adopt.

Part 1, alternative mechanisms (each changes one element of the reference model):
  A1  learning rate set by the sign of each error instead of by surprise
  A2  surprise detected from the sustained mean error, in both directions
  A3  surprising changes in either direction speed up revision (decreases included)
  A4  no downward prediction (w_down = 0): two separate filters, no hierarchy

Part 2, fixed versus precision-weighted downward weight: a scan of fixed weights, all other
parameters at reference, showing the trade-off between persistence in calm activities (C8)
and tracking of the stream during use (C10).
"""
from _common import OUT, write_csv, md_table
from rrm import Params, claims

REF = Params()
ALTERNATIVES = {
    "Reference (Box 3)": REF,
    "A1 sign-dependent learning rate": REF.with_(surprise_mode="sign"),
    "A2 long-window surprise, both directions": REF.with_(surprise_mode="sustained"),
    "A3 surprise speeds up decreases too": REF.with_(surprise_mode="both"),
    "A4 no downward prediction": REF.with_(w_down0=0.0),
}

rows, long = [], []
for name, p in ALTERNATIVES.items():
    res = [r for r in claims.evaluate(p, n_seeds=8) if r["kind"] != "property"]
    d = {r["id"]: r for r in res}
    failed = [r["id"] for r in res if not r["passed"]]
    rows.append(dict(model=name, passed=sum(r["passed"] for r in res), of=len(res), failed=" ".join(failed) or "none",
                     noise_inflation=d["S1"]["value"], fall_8=d["C4"]["value"], fall_by_rate=d["C4b"]["value"],
                     no_session_mismatch=d["C8"]["value"]))
    for r in res:
        long.append(dict(model=name, **{k: r[k] for k in ("id", "value", "passed")}))
    print(f"{name:42s} {rows[-1]['passed']}/{rows[-1]['of']}  failed: {rows[-1]['failed']}")

write_csv(OUT / "alternatives.csv", rows)
write_csv(OUT / "alternatives_long.csv", long)

# Part 2 -----------------------------------------------------------------------------
frontier = []
settings = [("fixed", w) for w in (0.004, 0.007, 0.010, 0.013, 1 / 60, 0.025)] + [("precision-weighted (reference)", None)]
for kind, w in settings:
    p = REF if w is None else REF.with_(precision_down=False, w_down0=w)
    d = {r["id"]: r for r in claims.evaluate(p, n_seeds=16)}
    frontier.append(dict(downward_weight=kind if w is None else f"fixed {w:.4f}",
                         c8_mismatch_no_session=float(d["C8"]["value"].split()[0]),
                         c8_same_without_use=float(d["C8"]["value"].split()[2]),
                         c10_expectation_after_60min_pct=float(d["C10"]["value"].rstrip("%")),
                         all_claims_passed=sum(r["passed"] for r in d.values() if r["kind"] != "property")))
    print(frontier[-1])
write_csv(OUT / "downward_weight_frontier.csv", frontier)

with open(OUT / "alternatives.md", "w") as f:
    f.write("# Alternative mechanisms\n\n")
    f.write(md_table(rows, ["model", "passed", "of", "failed", "noise_inflation", "fall_8", "fall_by_rate", "no_session_mismatch"],
                     ["Model", "Passed", "Of", "Failed", "S1 noise inflation", "C4 fall (stream 8)", "C4b fall (streams 4/16/32)", "C8 mismatch, no session"]))
    f.write("\n\n# Fixed versus precision-weighted downward weight\n\n")
    f.write(md_table(frontier, ["downward_weight", "c8_mismatch_no_session", "c8_same_without_use", "c10_expectation_after_60min_pct", "all_claims_passed"],
                     ["Downward weight", "C8 mismatch on waking, after 14 days of use", "same, never used", "C10 expectation after 60 min of use (%)", "Claims passed"]))
    f.write("\n\nA fixed weight trades persistence in calm activities (C8) against tracking of the stream (C10). "
            "None of the fixed values examined (0.004 to 0.025), with other parameters at reference, passes every claim; "
            "the precision-weighted weight obtains both. "
            "This result depends on the mismatch index being computed per trajectory; with an index computed after averaging "
            "trajectories, a fixed weight of about 0.007 also passes every claim, with a persistence effect about half as large.\n")
