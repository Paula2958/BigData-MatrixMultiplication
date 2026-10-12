import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def calculate_statistics(values):
    values = sorted(values)

    if len(values) < 5:
        raise ValueError("At least five measurements required.")

    median = statistics.median(values)
    half = len(values) // 2

    q1 = statistics.median(values[:half])
    q3 = statistics.median(values[-half:])

    return median, q1, q3, q3 - q1


def main():
    groups = defaultdict(lambda: {
        "time": [],
        "memory": []
    })

    with (RESULTS / "raw_results.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            key = (
                row["language"],
                int(row["matrix_size"])
            )
            groups[key]["time"].append(
                float(row["time_seconds"])
            )
            groups[key]["memory"].append(
                float(row["peak_rss_mib"])
            )

    output = RESULTS / "summary_results.csv"

    with output.open("w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "language",
            "matrix_size",
            "repetitions",
            "median_time_seconds",
            "q1_time_seconds",
            "q3_time_seconds",
            "iqr_time_seconds",
            "median_peak_rss_mib",
            "q1_peak_rss_mib",
            "q3_peak_rss_mib",
            "iqr_peak_rss_mib",
            "theoretical_storage_mib",
            "multiplications",
            "accumulator_additions"
        ])

        for (language, n), values in sorted(groups.items()):
            t = calculate_statistics(values["time"])
            m = calculate_statistics(values["memory"])

            storage = 3 * n * n * 8 / (1024 ** 2)

            writer.writerow([
                language, n, len(values["time"]),
                *t, *m, storage, n ** 3, n ** 3
            ])

    print(f"Summary saved to {output}")


if __name__ == "__main__":
    main()
