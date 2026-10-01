import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ASSIGNMENT_DIR = SCRIPT_DIR.parent

RESULTS_DIR = ASSIGNMENT_DIR / "results"
FIGURES_DIR = ASSIGNMENT_DIR / "figures"

SUMMARY_FILE = RESULTS_DIR / "summary_results.csv"


# ============================================================
# LOAD SUMMARY DATA
# ============================================================

def load_results():

    data = defaultdict(list)

    with SUMMARY_FILE.open(
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if not row["median_time_seconds"]:
                continue

            language = row["language"]

            data[language].append({
                "n": int(row["matrix_size"]),

                "median_time":
                    float(row["median_time_seconds"]),

                "q1_time":
                    float(row["q1_time_seconds"]),

                "q3_time":
                    float(row["q3_time_seconds"]),

                "iqr_time":
                    float(row["iqr_time_seconds"]),

                "median_memory":
                    (
                        float(row["median_peak_rss_mib"])
                        if row["median_peak_rss_mib"]
                        else None
                    ),

                "q1_memory":
                    (
                        float(row["q1_peak_rss_mib"])
                        if row["q1_peak_rss_mib"]
                        else None
                    ),

                "q3_memory":
                    (
                        float(row["q3_peak_rss_mib"])
                        if row["q3_peak_rss_mib"]
                        else None
                    ),

                "theoretical_memory":
                    float(
                        row[
                            "theoretical_matrix_storage_mib"
                        ]
                    )
            })

    for language in data:

        data[language].sort(
            key=lambda item: item["n"]
        )

    return data


# ============================================================
# EXECUTION-TIME FIGURE
# ============================================================

def execution_time_plot(data):

    plt.figure(figsize=(8, 5))

    for language, values in data.items():

        n = [
            item["n"]
            for item in values
        ]

        median = [
            item["median_time"]
            for item in values
        ]

        lower_error = [
            item["median_time"]
            - item["q1_time"]
            for item in values
        ]

        upper_error = [
            item["q3_time"]
            - item["median_time"]
            for item in values
        ]

        plt.errorbar(
            n,
            median,
            yerr=[
                lower_error,
                upper_error
            ],
            marker="o",
            capsize=4,
            label=language.capitalize()
        )

    plt.xlabel(
        "Matrix size n"
    )

    plt.ylabel(
        "Execution time (seconds)"
    )

    plt.title(
        "Matrix Multiplication Execution Time"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output = (
        FIGURES_DIR
        / "execution_time.png"
    )

    plt.savefig(
        output,
        dpi=300
    )

    plt.close()


# ============================================================
# LOG-LOG EXECUTION-TIME FIGURE
# ============================================================

def execution_time_loglog_plot(data):

    plt.figure(figsize=(8, 5))

    for language, values in data.items():

        n = [
            item["n"]
            for item in values
        ]

        median = [
            item["median_time"]
            for item in values
        ]

        plt.loglog(
            n,
            median,
            marker="o",
            label=language.capitalize()
        )

    plt.xlabel(
        "Matrix size n (log scale)"
    )

    plt.ylabel(
        "Execution time in seconds (log scale)"
    )

    plt.title(
        "Execution-Time Scaling"
    )

    plt.legend()

    plt.grid(
        True,
        which="both",
        alpha=0.3
    )

    plt.tight_layout()

    output = (
        FIGURES_DIR
        / "execution_time_loglog.png"
    )

    plt.savefig(
        output,
        dpi=300
    )

    plt.close()


# ============================================================
# MEMORY FIGURE
# ============================================================

def memory_plot(data):

    plt.figure(figsize=(8, 5))

    for language, values in data.items():

        filtered = [
            item
            for item in values
            if item["median_memory"] is not None
        ]

        if not filtered:
            continue

        n = [
            item["n"]
            for item in filtered
        ]

        memory = [
            item["median_memory"]
            for item in filtered
        ]

        lower_error = [
            item["median_memory"]
            - item["q1_memory"]
            for item in filtered
        ]

        upper_error = [
            item["q3_memory"]
            - item["median_memory"]
            for item in filtered
        ]

        plt.errorbar(
            n,
            memory,
            yerr=[
                lower_error,
                upper_error
            ],
            marker="o",
            capsize=4,
            label=language.capitalize()
        )

    plt.xlabel(
        "Matrix size n"
    )

    plt.ylabel(
        "Peak RSS (MiB)"
    )

    plt.title(
        "Peak Process Memory Usage"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output = (
        FIGURES_DIR
        / "memory_usage.png"
    )

    plt.savefig(
        output,
        dpi=300
    )

    plt.close()


# ============================================================
# NORMALIZED SCALING FIGURE
# ============================================================

def normalized_scaling_plot(data):

    plt.figure(figsize=(8, 5))

    for language, values in data.items():

        if not values:
            continue

        baseline_n = values[0]["n"]
        baseline_time = values[0]["median_time"]

        measured_scaling = [
            item["median_time"] / baseline_time
            for item in values
        ]

        n_values = [
            item["n"]
            for item in values
        ]

        plt.plot(
            n_values,
            measured_scaling,
            marker="o",
            label=f"{language.capitalize()} measured"
        )


    # Theoretical O(n^3) reference
    all_n = sorted({
        item["n"]
        for values in data.values()
        for item in values
    })

    if all_n:

        n0 = all_n[0]

        theoretical = [
            (n / n0) ** 3
            for n in all_n
        ]

        plt.plot(
            all_n,
            theoretical,
            linestyle="--",
            label="Theoretical O(n³)"
        )


    plt.xlabel(
        "Matrix size n"
    )

    plt.ylabel(
        "Runtime relative to smallest tested n"
    )

    plt.title(
        "Measured vs. Cubic Runtime Growth"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output = (
        FIGURES_DIR
        / "normalized_scaling.png"
    )

    plt.savefig(
        output,
        dpi=300
    )

    plt.close()


# ============================================================
# MAIN
# ============================================================

def main():

    if not SUMMARY_FILE.exists():

        raise FileNotFoundError(
            f"Summary results not found:\n"
            f"{SUMMARY_FILE}"
        )

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data = load_results()

    execution_time_plot(data)

    execution_time_loglog_plot(data)

    memory_plot(data)

    normalized_scaling_plot(data)

    print(
        "Figures generated successfully:"
    )

    print(
        FIGURES_DIR
        / "execution_time.png"
    )

    print(
        FIGURES_DIR
        / "execution_time_loglog.png"
    )

    print(
        FIGURES_DIR
        / "memory_usage.png"
    )

    print(
        FIGURES_DIR
        / "normalized_scaling.png"
    )


if __name__ == "__main__":
    main()
