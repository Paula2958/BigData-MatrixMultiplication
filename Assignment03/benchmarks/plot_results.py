#!/usr/bin/env python3

import csv
import pathlib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]

with (ROOT / "benchmarks/results/summary_results.csv").open() as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise SystemExit(
        "No benchmark data. Run run_benchmarks.py first."
    )

figdir = ROOT / "figures"
figdir.mkdir(exist_ok=True)

metrics = [
    ("median_seconds", "Median runtime (s)", "execution_time"),
    ("speedup", "Speedup vs sequential", "speedup"),
    ("efficiency", "Efficiency", "efficiency"),
    (
        "median_peak_rss_kib",
        "Median peak process RSS (KiB)",
        "memory_usage"
    )
]

for metric, ylabel, name in metrics:
    fig, ax = plt.subplots(figsize=(8, 5))

    configs = sorted({
        (r["method"], int(r["threads"]))
        for r in rows
    })

    for method, p in configs:
        if metric in ("speedup", "efficiency"):
            if method == "sequential":
                continue

        group = sorted(
            (
                r for r in rows
                if r["method"] == method
                and int(r["threads"]) == p
                and r[metric] != ""
            ),
            key=lambda r: int(r["n"])
        )

        if group:
            ax.plot(
                [int(r["n"]) for r in group],
                [float(r[metric]) for r in group],
                marker="o",
                label=(
                    method if method == "sequential"
                    else f"parallel p={p}"
                )
            )

    if metric in ("speedup", "efficiency"):
        ax.axhline(1, linestyle="--", linewidth=1)

    ax.set(
        xlabel="Matrix side length n",
        ylabel=ylabel,
        title=name.replace("_", " ").title()
    )

    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    fig.savefig(figdir / (name + ".png"), dpi=180)
    plt.close(fig)

print("Generated four figures in", figdir)
