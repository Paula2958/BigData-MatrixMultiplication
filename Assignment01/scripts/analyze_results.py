import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SIZES = [50, 100, 200, 300]
LANGUAGES = ("python", "java", "c")


def read_groups(filename, value_column):
    groups = defaultdict(list)

    with (RESULTS / filename).open(newline="") as file:
        for row in csv.DictReader(file):
            if "status" in row and row["status"] != "success":
                continue

            key = (
                row["language"].lower(),
                int(row["matrix_size"])
            )
            groups[key].append(float(row[value_column]))

    return groups


def summary(values):
    if not values:
        raise ValueError("No measurements available.")

    values = sorted(values)
    median = statistics.median(values)

    # Median-of-halves quartiles.
    half = len(values) // 2
    lower = values[:half]
    upper = values[-half:]

    q1 = statistics.median(lower)
    q3 = statistics.median(upper)

    return median, q1, q3, q3 - q1


def main():
    runtime = read_groups(
        "raw_results.csv", "time_seconds"
    )
    memory = read_groups(
        "raw_memory_results.csv", "peak_rss_mib"
    )

    output = RESULTS / "summary_results.csv"

    with output.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "language",
            "matrix_size",
            "runtime_successful_runs",
            "median_time_seconds",
            "q1_time_seconds",
            "q3_time_seconds",
            "iqr_time_seconds",
            "median_peak_rss_mib",
            "q1_peak_rss_mib",
            "q3_peak_rss_mib",
            "iqr_peak_rss_mib",
            "theoretical_matrix_storage_mib",
            "theoretical_multiplications",
            "theoretical_additions"
        ])

        for n in SIZES:
            for language in LANGUAGES:
                key = (language, n)

                if key not in runtime or key not in memory:
                    raise ValueError(
                        f"Missing measurements: {key}"
                    )

                times = runtime[key]
                rss = memory[key]

                t_med, t_q1, t_q3, t_iqr = summary(times)
                m_med, m_q1, m_q3, m_iqr = summary(rss)

                storage = 3 * n * n * 8 / (1024 ** 2)

                writer.writerow([
                    language, n, len(times),
                    t_med, t_q1, t_q3, t_iqr,
                    m_med, m_q1, m_q3, m_iqr,
                    storage, n ** 3, n ** 3
                ])

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
