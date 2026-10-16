
"""Make simple figures directly from measured summary CSV."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "results/summary_results.csv").open() as file:
    data = list(csv.DictReader(file))
(ROOT / "figures").mkdir(exist_ok=True)

def graph(filename, part, methods, xfield, yfield, xlabel, ylabel, size=None):
    plt.figure(figsize=(7, 4))
    for method in methods:
        rows = [r for r in data if r["part"] == part and r["method"] == method
                and (size is None or int(r["n"]) == size)]
        rows.sort(key=lambda r: float(r[xfield]))
        plt.plot([float(r[xfield]) for r in rows],
                 [float(r[yfield]) for r in rows], marker="o", label=method)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ROOT / "figures" / filename, dpi=160)
    plt.close()

graph("dense_time.png", "dense", ["basic", "reordered", "blocked"],
      "n", "median_ms", "Matrix size (n)", "Median time (ms)")
graph("dense_memory.png", "dense", ["basic", "reordered", "blocked"],
      "n", "median_rss_mib", "Matrix size (n)", "Median peak RSS (MiB)")
graph("sparse_time.png", "sparse", ["reordered", "csr"],
      "sparsity_pct", "median_ms", "Zero entries (%)", "Median time (ms)", size=400)
graph("sparse_memory.png", "sparse", ["reordered", "csr"],
      "sparsity_pct", "median_rss_mib", "Zero entries (%)", "Median peak RSS (MiB)", size=400)
print("Saved four graphs in figures/")
