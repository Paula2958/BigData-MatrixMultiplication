import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

with (ROOT / "results/summary_results.csv").open() as file:
    rows = list(csv.DictReader(file))

methods = ["sequential", "parallel", "distributed"]


def save_figure(filename, ylabel):
    plt.xlabel("Matrix size (n)")
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / filename, dpi=160)
    plt.close()


plt.figure(figsize=(8, 5))

for method in methods:
    worker_counts = sorted({
        int(row["workers"])
        for row in rows if row["method"] == method
    })

    for workers in worker_counts:
        selected = sorted(
            [row for row in rows
             if row["method"] == method
             and int(row["workers"]) == workers],
            key=lambda row: int(row["n"])
        )

        plt.plot(
            [int(row["n"]) for row in selected],
            [float(row["median_s"]) for row in selected],
            marker="o",
            label=f"{method} ({workers} processes)"
        )

save_figure("execution_time.png", "Median time (seconds)")


largest_n = max(int(row["n"]) for row in rows)

for metric, filename, ylabel in [
    ("speedup", "speedup.png", "Speedup"),
    ("efficiency", "efficiency.png", "Efficiency")
]:
    plt.figure(figsize=(7, 4))

    for method in ["parallel", "distributed"]:
        selected = sorted(
            [row for row in rows
             if row["method"] == method
             and int(row["n"]) == largest_n
             and row[metric] != ""],
            key=lambda row: int(row["workers"])
        )

        if selected:
            plt.plot(
                [int(row["workers"]) for row in selected],
                [float(row[metric]) for row in selected],
                marker="o",
                label=method
            )

    plt.xlabel("Number of processes")
    plt.ylabel(ylabel)
    plt.title(f"Strong scaling, n={largest_n}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / filename, dpi=160)
    plt.close()


selected = [
    row for row in rows
    if row["method"] == "distributed"
    and int(row["n"]) == largest_n
    and row["median_max_worker_rss_mib"] != ""
]

if selected:
    selected.sort(key=lambda row: int(row["workers"]))
    plt.figure(figsize=(7, 4))
    plt.plot(
        [int(row["workers"]) for row in selected],
        [float(row["median_max_worker_rss_mib"]) for row in selected],
        marker="o"
    )
    plt.xlabel("Number of MPI processes")
    plt.ylabel("Maximum per-rank peak RSS (MiB)")
    plt.title(f"MPI memory, n={largest_n}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES / "mpi_memory.png", dpi=160)
    plt.close()

print("Figures saved in figures/")
