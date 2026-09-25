"""Figures: model dynamics (fig1, manuscript Fig. 3), robustness (fig2), alternatives (fig3)."""
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, to_hex
from _common import OUT, FIG
from rrm import Params, simulate
from rrm.claims import equilibrium
from rrm.scenarios import day, days, HEAVY, FRAGMENTATION, CALM, STREAM, DAY

BLUE, ORANGE, GRAY, INK, MUTED, PASS, FAIL = "#2a78d6", "#eb6834", "#9a9892", "#0b0b0b", "#52514e", "#2a78d6", "#e34948"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#c9c8c3", "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left"})
P = Params(); INIT = equilibrium(P)


def mean_run(lam, n=128):
    s = simulate(lam, P, n_seeds=n, mu1_0=INIT[0], mu2_0=INIT[1])
    return s["mu1"].mean(0), s["mu2"].mean(0)


def save(fig, name):
    fig.tight_layout(); fig.savefig(FIG / f"{name}.png", dpi=300); fig.savefig(FIG / f"{name}.pdf", metadata={"CreationDate": None}); plt.close(fig)


# ---- Figure 1: dynamics (manuscript Fig. 3) -------------------------------------
# Drawn at its final printed width (\textwidth ~ 6.8 in), so that LaTeX does not rescale it:
# panel titles 8 pt, axis labels 7 pt, ticks and legends 6 pt.
W, H = 6.8, 5.2
EDGE = "#c9c8c3"
FINAL = {"font.size": 7, "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
         "axes.titlesize": 8, "axes.linewidth": .6, "xtick.major.width": .6, "ytick.major.width": .6,
         "xtick.major.size": 2.5, "ytick.major.size": 2.5, "legend.handlelength": 1.8, "legend.labelspacing": .3}
SLATE, CYAN, MINT, LAV, PEACH = "#748DAE", "#9ECBD6", "#D1E6DD", "#DECEE4", "#FFECD3"
LAV_D, PEACH_D = "#A88FB4", "#E0A96A"          # darker tints of the same hues, for lines
RAMP = [to_hex(np.array(to_rgb(CYAN)) * (1 - f) + np.array(to_rgb(SLATE)) * f) for f in (0, 1/3, 2/3, 1)]
LW = [1.5, 1.15, .9, .65]                       # lighter = thicker, so overlapping curves stay visible
K = 0.65                                        # line widths scaled to the final size


def smooth(y, w=121):
    """Light centred moving average (w minutes) for the day-scale panels: removes the
    within-day steps left by individual sessions, keeps the daily cycle."""
    k = np.ones(w) / w; yp = np.pad(y, w // 2, mode="edge")
    return np.convolve(yp, k, mode="valid")


with plt.rc_context(FINAL):
    fig, ax = plt.subplots(2, 2, figsize=(W, H))
    lam = day([(770, 10)]); m1, m2 = mean_run(lam); m1n, _ = mean_run(day())
    x = np.arange(DAY) / 60; sl = slice(600, 1000); a = ax[0, 0]
    a.fill_between(x[sl], 0, lam[sl], step="post", color=MINT, lw=0, label="Rate delivered by the activity")
    a.plot(x[sl], m2[sl], color=LAV_D, lw=1.3*K, ls=(0, (1, 1.5)), label="Habitual expectation")
    a.plot(x[sl], m1n[sl], color=CYAN, lw=1.2*K, ls=(0, (4, 2)), label="Current expectation, no session")
    a.plot(x[sl], m1[sl], color=SLATE, lw=1.6*K, label="Current expectation, session 12:50")
    a.annotate("mismatch\n(after-effect)", xy=(13.4, 2.3), xytext=(14.0, 4.0), color=MUTED, fontsize=6,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=.5))
    a.set_ylim(0, 12); a.set_yticks(range(0, 13, 2))
    a.set_title("A  One session, then a calm activity"); a.set_xlabel("Time of day (h)"); a.set_ylabel("Events / min")
    a.legend(frameon=False, loc="upper right")

    lamH = days(*[day(HEAVY)] * 14, *[day()] * 14); _, bH = mean_run(lamH, 32); bH = smooth(bH)
    _, bN = mean_run(days(*[day()] * 28), 32); bN = smooth(bN)
    xd = np.arange(lamH.size) / DAY; a = ax[1, 0]
    a.plot(xd, bH, color=LAV_D, lw=1.4*K, label="Pattern of use"); a.plot(xd, bN, color=PEACH_D, lw=1.4*K, label="Never used")
    a.axvline(14, color=EDGE, lw=.5, zorder=0)
    a.text(0.3, 3.35, "16 × 10 min / day", color=MUTED, fontsize=6); a.text(14.3, 3.35, "no use", color=MUTED, fontsize=6)
    a.set_ylim(0, 3.6); a.set_title("C  A pattern of use, then no use")
    a.set_xlabel("Day"); a.set_ylabel("Events / min"); a.legend(frameon=False, loc="lower right")

    END = 780; a = ax[0, 1]; t = np.arange(0, 86)
    a.fill_between(t, 0, day()[END + t], step="post", color=MINT, lw=0, label="Rate delivered (calm activity)")
    for L, c, lw in zip((160, 40, 10, 5), RAMP, LW):
        m, _ = mean_run(day([(END - L, L)])); a.plot(t, m[END + t], color=c, lw=lw, label=f"{L}-min session")
    a.set_xlim(0, 85); a.set_ylim(0, 12); a.set_yticks(range(0, 13, 2)); a.set_title("B  Sessions of varying length")
    a.set_xlabel("Minutes since the end of the session"); a.set_ylabel("Events / min")
    a.legend(frameon=False, loc="upper right")

    a = ax[1, 1]
    a.plot(xd, bN, color=PEACH_D, lw=1.2*K, ls=(0, (4, 2)), label="never used")
    for (k, s), c in zip(FRAGMENTATION.items(), RAMP):
        _, b = mean_run(days(*[day(s)] * 14, *[day()] * 14), 32); a.plot(xd, smooth(b), color=c, lw=1.4*K, label=k.replace(" x ", " × "))
    a.axvline(14, color=EDGE, lw=.5, zorder=0)
    a.text(0.3, 3.35, "same 160 min / day", color=MUTED, fontsize=6); a.text(14.3, 3.35, "no use", color=MUTED, fontsize=6)
    h, l = a.get_legend_handles_labels()
    a.legend(h[1:] + h[:1], l[1:] + l[:1], frameon=False, loc="lower right", ncol=2, columnspacing=1.0)
    a.set_ylim(0, 3.6); a.set_title("D  Same 160 min per day, more fragmented")
    a.set_xlabel("Day"); a.set_ylabel("Events / min")
    for a in (ax[1, 0], ax[1, 1]):
        x0 = a.get_xlim()[0]; left, right = a.texts[0], a.texts[1]; right.set_x(14 + left.get_position()[0] - x0)
    fig.tight_layout(h_pad=1.2, w_pad=1.5)
    fig.savefig(FIG / "fig1_dynamics.png", dpi=300); fig.savefig(FIG / "fig1_dynamics.pdf", metadata={"CreationDate": None}); plt.close(fig)

# ---- Figure 2: robustness ----------------------------------------------------------
rows = list(csv.DictReader(open(OUT / "robustness_summary.csv")))
SHORT = {"C1": "Current expectation tracks the activity", "C2": "Habitual lies between calm and dense",
         "S1": "Noise does not inflate the expectation (validity)", "C11": "Calm activities fall short even without use",
         "C3": "Fast rise on entering the stream", "C4": "Slow fall after leaving (after-effect)",
         "C4b": "Denser streams do not shorten the after-effect", "C5": "Mismatch larger if next activity is calm",
         "C6": "Each session adds a little to habitual", "C7": "Habitual rises with the number of sessions",
         "C8": "Mismatch with no recent session", "C9": "Persistence fades over days when use stops",
         "C10": "No sag of expectation during long use", "P1": "Within-session rate raises habitual",
         "P2": "Ordinary sessions reach the ceiling", "P3": "Fragmentation raises habitual (up to a ceiling)",
         "P4": "Chronicity raises habitual, then saturates", "P5": "Fragmentation raises the all-day mean",
         "core_joint": "Core claims jointly (S1 C3 C4 C4b C7 C8 C9)", "all_joint": "All claims jointly"}
rows.sort(key=lambda r: float(r["pass_rate_random"]))
fig, a = plt.subplots(figsize=(8.5, 6.2)); y = np.arange(len(rows))
pr = [float(r["pass_rate_random"]) for r in rows]
a.barh(y, pr, color=[ORANGE if r["id"].endswith("joint") else (BLUE if v >= 0.9 else "#86b6ef") for r, v in zip(rows, pr)], height=0.65)
a.set_yticks(y); a.set_yticklabels([SHORT[r['id']] if r['id'].endswith('joint') else f"{r['id']}  {SHORT.get(r['id'], r['statement'][:45])}" for r in rows], fontsize=8)
for j, v in enumerate(pr):
    a.text(v + 0.01, j, f"{100 * v:.0f}%", va="center", fontsize=7, color=INK)
a.set_xlim(0, 1.1); a.set_xlabel("Share of 64 random settings passing\n(every parameter drawn within ×0.5 to ×2 of its reference value)")
a.set_title("Robustness of each claim")
save(fig, "fig2_robustness")

# ---- Figure 3: alternatives and downward-weight frontier ----------------------------
long = list(csv.DictReader(open(OUT / "alternatives_long.csv")))
models = list(dict.fromkeys(r["model"] for r in long)); ids = list(dict.fromkeys(r["id"] for r in long))
M = np.array([[next(r["passed"] == "True" for r in long if r["model"] == m and r["id"] == i) for i in ids] for m in models])
fig, ax = plt.subplots(1, 2, figsize=(14, 3.4), gridspec_kw=dict(width_ratios=[2.1, 1.1]))
a = ax[0]
for r_, m in enumerate(models):
    for c_, i in enumerate(ids):
        ok = M[r_, c_]
        a.add_patch(plt.Rectangle((c_ + .06, r_ + .06), .88, .88, color=PASS if ok else FAIL, alpha=.85 if ok else .9, lw=0))
        a.text(c_ + .5, r_ + .52, "✓" if ok else "✗", ha="center", va="center", color="white", fontsize=9)
a.set_xlim(0, len(ids)); a.set_ylim(len(models), 0)
a.set_xticks(np.arange(len(ids)) + .5); a.set_xticklabels(ids, fontsize=8)
a.set_yticks(np.arange(len(models)) + .5); a.set_yticklabels(models, fontsize=8)
a.tick_params(length=0); [s.set_visible(False) for s in a.spines.values()]
a.set_title("A  Claims passed by the Box 3 model and by alternative mechanisms")
fr = list(csv.DictReader(open(OUT / "downward_weight_frontier.csv")))
fixed = [r for r in fr if r["downward_weight"].startswith("fixed")]; ref = [r for r in fr if not r["downward_weight"].startswith("fixed")][0]
a = ax[1]
xs = [float(r["c10_expectation_after_60min_pct"]) for r in fixed]; ys = [float(r["c8_mismatch_no_session"]) for r in fixed]
a.plot(xs, ys, "-o", color=GRAY, ms=5, lw=1.5, label="Fixed downward weight")
for r, x_, y_ in zip(fixed, xs, ys):
    a.annotate(r["downward_weight"].replace("fixed ", ""), (x_, y_), textcoords="offset points", xytext=(4, 4), fontsize=7, color=MUTED)
a.plot([float(ref["c10_expectation_after_60min_pct"])], [float(ref["c8_mismatch_no_session"])], "o", color=BLUE, ms=9, label="Precision-weighted (Box 3)")
a.axvline(90, color=MUTED, lw=.8, ls=(0, (3, 2))); a.text(90.5, 0.02, "C10 criterion", fontsize=7, color=MUTED)
a.set_xlabel("Expectation after 60 min of use (% of stream rate)"); a.set_ylabel("Mismatch on waking, no recent session")
a.set_title("B  Downward weight, fixed or precision-weighted"); a.legend(frameon=False, fontsize=7, loc="upper right")
save(fig, "fig3_alternatives")
print("figures written to", FIG)
