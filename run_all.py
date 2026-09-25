"""Reproduce every output of the repository (about 5-15 min depending on the number of cores)."""
import platform, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ["01_check_claims.py", "03_alternatives.py", "02_robustness.py", "02b_conditions.py", "04_figures.py"]

t0 = time.time()
for s in STEPS:
    print(f"\n=== {s} ===", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / s)], check=True, cwd=ROOT / "scripts")

import numpy, matplotlib
(ROOT / "outputs" / "environment.txt").write_text(
    f"python {platform.python_version()}\nnumpy {numpy.__version__}\nmatplotlib {matplotlib.__version__}\n"
    f"platform {platform.platform()}\nruntime {time.time() - t0:.0f} s\n")
print(f"\nDone in {time.time() - t0:.0f} s")
