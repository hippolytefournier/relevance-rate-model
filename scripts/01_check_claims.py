"""Check every claim of Box 3 (and the parameters-of-use section) at the reference parameters."""
from _common import OUT, write_csv, write_json, md_table
from rrm import Params, claims

p = Params()
res = claims.evaluate(p, n_seeds=16)
for r in res:
    r["result"] = "PASS" if r["passed"] else "FAIL"
    print(f"[{r['result']}] {r['id']:3s} {r['value']}")

write_json(OUT / "params_reference.json", p.as_dict())
for r in res:
    r["core"] = "yes" if r["core"] else ""
write_csv(OUT / "claims.csv", res, ["id", "kind", "core", "source", "statement", "criterion", "value", "result"])
with open(OUT / "claims.md", "w") as f:
    f.write("# Claim checks at the reference parameters\n\n")
    f.write("Parameters: `outputs/params_reference.json`. 16 Poisson seeds, averaged.\n\n")
    f.write(md_table(res, ["id", "kind", "core", "statement", "criterion", "value", "result"],
                     ["ID", "Kind", "Core", "Statement", "Criterion", "Observed", "Result"]))
    f.write("\n\nKinds: `claim` = stated in the manuscript; `sanity` = validity check of the simulation; "
            "`property` = model behaviour reported for transparency. Core = claims the manuscript's argument rests on. "
            "Mismatch index = per-trajectory max(mu1 - lambda, 0), averaged.\n")
