import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

with (RESULTS / "raw_results.csv").open() as file:
    rows = list(csv.DictReader(file))

groups = defaultdict(list)

for row in rows:
    key = (
        row["method"],
        int(row["n"]),
        int(row["workers"])
    )
    groups[key].append(row)

summary = []

for (method, n, workers), group in sorted(groups.items()):
    times = sorted(float(row["time_s"]) for row in group)

    if len({row["checksum"] for row in group}) != 1:
        raise ValueError("Inconsistent checksums")

    middle = len(times) // 2

    if len(times) >= 3:
        q1 = statistics.median(times[:middle])
        upper = times[middle + 1:] if len(times) % 2 else times[middle:]
        q3 = statistics.median(upper)
    else:
        q1 = min(times)
        q3 = max(times)

    def median_optional(field):
        values = [
            float(row[field])
            for row in group
            if row.get(field) not in ("", None)
        ]
        return statistics.median(values) if values else ""

    summary.append({
        "method": method,
        "n": n,
        "workers": workers,
        "repetitions": len(times),
        "median_s": statistics.median(times),
        "q1_s": q1,
        "q3_s": q3,
        "iqr_s": q3 - q1,
        "median_rss_mib": median_optional("peak_rss_mib"),
        "median_max_worker_rss_mib": median_optional(
            "max_worker_rss_mib"
        ),
        "median_sum_worker_rss_mib": median_optional(
            "sum_worker_rss_mib"
        ),
        "median_setup_s": median_optional("max_setup_s"),
        "median_distribution_s": median_optional(
            "max_distribution_s"
        ),
        "median_compute_s": median_optional("max_compute_s"),
        "median_collection_s": median_optional(
            "max_collection_s"
        )
    })

sequential_times = {
    row["n"]: row["median_s"]
    for row in summary
    if row["method"] == "sequential"
}

for row in summary:
    baseline = sequential_times.get(row["n"])
    if baseline:
        row["speedup"] = baseline / row["median_s"]
        row["efficiency"] = (
            row["speedup"] / row["workers"]
        )
    else:
        row["speedup"] = ""
        row["efficiency"] = ""

with (RESULTS / "summary_results.csv").open(
    "w", newline=""
) as file:
    writer = csv.DictWriter(
        file, fieldnames=summary[0].keys()
    )
    writer.writeheader()
    writer.writerows(summary)

print(f"Summarised {len(summary)} configurations")
