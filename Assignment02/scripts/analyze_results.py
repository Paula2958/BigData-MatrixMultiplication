
"""Summarise the five independent benchmark repetitions."""
import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "results/raw_results.csv").open() as file:
    rows = list(csv.DictReader(file))

groups = defaultdict(list)
for row in rows:
    key = (row["part"], row["method"], int(row["n"]), int(row["sparsity_pct"]))
    groups[key].append(row)

summary = []
for (part, method, n, sparsity), group in sorted(groups.items()):
    times = sorted(float(row["time_ms"]) for row in group)
    memory = sorted(float(row["peak_rss_mib"]) for row in group)
    # Tukey's hinges for five observations: medians of halves, excluding center.
    middle = len(times) // 2
    q1 = statistics.median(times[:middle])
    q3 = statistics.median(times[middle + 1:])
    if len({row["checksum"] for row in group}) != 1:
        raise ValueError(f"Inconsistent output checksum: {part}, {method}, {n}")
    summary.append({
        "part": part, "method": method, "n": n, "sparsity_pct": sparsity,
        "repetitions": len(group), "median_ms": statistics.median(times),
        "q1_ms": q1, "q3_ms": q3, "iqr_ms": q3 - q1,
        "median_rss_mib": statistics.median(memory),
        "min_rss_mib": min(memory), "max_rss_mib": max(memory),
        "median_conversion_ms": statistics.median(float(r["conversion_ms"]) for r in group),
        "a_nnz": group[0]["a_nnz"], "b_nnz": group[0]["b_nnz"],
        "c_nnz": group[0]["c_nnz"], "checksum": group[0]["checksum"]
    })

# Same logical inputs must produce identical outputs for all compared methods.
for part, n, sparsity in {(r["part"], r["n"], r["sparsity_pct"]) for r in summary}:
    matching = [r for r in summary if (r["part"], r["n"], r["sparsity_pct"]) == (part, n, sparsity)]
    if len({(r["checksum"], r["c_nnz"]) for r in matching}) != 1:
        raise ValueError(f"Methods disagree at {part}, n={n}, zeros={sparsity}%")

with (ROOT / "results/summary_results.csv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)
print(f"Validated and summarised {len(summary)} configurations")
