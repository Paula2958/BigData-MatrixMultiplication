import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ASSIGNMENT_DIR = SCRIPT_DIR.parent

RESULTS_DIR = ASSIGNMENT_DIR / "results"

RUNTIME_FILE = RESULTS_DIR / "raw_results.csv"

MEMORY_FILE = RESULTS_DIR / "raw_memory_results.csv"

SUMMARY_FILE = RESULTS_DIR / "summary_results.csv"


# ============================================================
# QUARTILES
# ============================================================

def percentile(values, p):
    """
    Compute percentile using linear interpolation.

    p must be between 0 and 1.
    """

    ordered = sorted(values)

    if not ordered:
        return math.nan

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * p

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower]
        + fraction
        * (ordered[upper] - ordered[lower])
    )


def calculate_statistics(values):

    if not values:

        return {
            "count": 0,
            "median": math.nan,
            "q1": math.nan,
            "q3": math.nan,
            "iqr": math.nan,
            "min": math.nan,
            "max": math.nan
        }

    q1 = percentile(values, 0.25)
    q3 = percentile(values, 0.75)

    return {
        "count": len(values),

        "median":
            statistics.median(values),

        "q1":
            q1,

        "q3":
            q3,

        "iqr":
            q3 - q1,

        "min":
            min(values),

        "max":
            max(values)
    }


# ============================================================
# RUNTIME DATA
# ============================================================

def load_runtime_results():

    data = defaultdict(list)

    statuses = defaultdict(
        lambda: {
            "success": 0,
            "timeout": 0,
            "error": 0
        }
    )


    with RUNTIME_FILE.open(
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            language = row["language"]

            n = int(row["matrix_size"])

            status = row["status"]

            key = (language, n)


            if status in statuses[key]:

                statuses[key][status] += 1


            if (
                status == "success"
                and row["time_seconds"]
            ):

                data[key].append(
                    float(
                        row["time_seconds"]
                    )
                )


    return data, statuses


# ============================================================
# MEMORY DATA
# ============================================================

def load_memory_results():

    data = defaultdict(list)

    statuses = defaultdict(
        lambda: {
            "success": 0,
            "timeout": 0,
            "error": 0
        }
    )


    with MEMORY_FILE.open(
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            language = row["language"]

            n = int(row["matrix_size"])

            status = row["status"]

            key = (language, n)


            if status in statuses[key]:

                statuses[key][status] += 1


            if (
                status == "success"
                and row["peak_rss_mib"]
            ):

                data[key].append(
                    float(
                        row["peak_rss_mib"]
                    )
                )


    return data, statuses


# ============================================================
# THEORETICAL WORK
# ============================================================

def theoretical_operations(n):
    """
    Classical matrix multiplication performs n^3
    scalar multiplications and approximately n^3
    accumulation additions.
    """

    multiplications = n ** 3
    additions = n ** 3

    return multiplications, additions


# ============================================================
# THEORETICAL MATRIX STORAGE
# ============================================================

def theoretical_matrix_memory_mib(n):
    """
    Reference storage for three dense n x n matrices
    with 8-byte elements:

        A + B + C = 3 * n^2 * 8 bytes

    This is NOT equivalent to measured peak RSS.
    """

    bytes_required = (
        3 * n * n * 8
    )

    mib = (
        bytes_required
        / (1024 ** 2)
    )

    return mib


# ============================================================
# SUMMARY GENERATION
# ============================================================

def create_summary():

    runtime_data, runtime_status = (
        load_runtime_results()
    )

    memory_data, memory_status = (
        load_memory_results()
    )


    all_keys = sorted(
        set(runtime_data.keys())
        | set(memory_data.keys())
        | set(runtime_status.keys())
        | set(memory_status.keys()),
        key=lambda item: (
            item[1],
            item[0]
        )
    )


    fieldnames = [

        "language",
        "matrix_size",

        "runtime_successful_runs",
        "runtime_timeouts",
        "runtime_errors",

        "median_time_seconds",
        "q1_time_seconds",
        "q3_time_seconds",
        "iqr_time_seconds",
        "min_time_seconds",
        "max_time_seconds",

        "memory_successful_runs",
        "memory_timeouts",
        "memory_errors",

        "median_peak_rss_mib",
        "q1_peak_rss_mib",
        "q3_peak_rss_mib",
        "iqr_peak_rss_mib",
        "min_peak_rss_mib",
        "max_peak_rss_mib",

        "theoretical_matrix_storage_mib",

        "theoretical_multiplications",
        "theoretical_additions"
    ]


    with SUMMARY_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as output:

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames
        )

        writer.writeheader()


        for language, n in all_keys:

            runtime_stats = (
                calculate_statistics(
                    runtime_data[
                        (language, n)
                    ]
                )
            )

            memory_stats = (
                calculate_statistics(
                    memory_data[
                        (language, n)
                    ]
                )
            )


            multiplications, additions = (
                theoretical_operations(n)
            )


            theoretical_memory = (
                theoretical_matrix_memory_mib(n)
            )


            row = {

                "language":
                    language,

                "matrix_size":
                    n,


                # Runtime

                "runtime_successful_runs":
                    runtime_stats["count"],

                "runtime_timeouts":
                    runtime_status[
                        (language, n)
                    ]["timeout"],

                "runtime_errors":
                    runtime_status[
                        (language, n)
                    ]["error"],

                "median_time_seconds":
                    format_value(
                        runtime_stats["median"]
                    ),

                "q1_time_seconds":
                    format_value(
                        runtime_stats["q1"]
                    ),

                "q3_time_seconds":
                    format_value(
                        runtime_stats["q3"]
                    ),

                "iqr_time_seconds":
                    format_value(
                        runtime_stats["iqr"]
                    ),

                "min_time_seconds":
                    format_value(
                        runtime_stats["min"]
                    ),

                "max_time_seconds":
                    format_value(
                        runtime_stats["max"]
                    ),


                # Memory

                "memory_successful_runs":
                    memory_stats["count"],

                "memory_timeouts":
                    memory_status[
                        (language, n)
                    ]["timeout"],

                "memory_errors":
                    memory_status[
                        (language, n)
                    ]["error"],

                "median_peak_rss_mib":
                    format_value(
                        memory_stats["median"]
                    ),

                "q1_peak_rss_mib":
                    format_value(
                        memory_stats["q1"]
                    ),

                "q3_peak_rss_mib":
                    format_value(
                        memory_stats["q3"]
                    ),

                "iqr_peak_rss_mib":
                    format_value(
                        memory_stats["iqr"]
                    ),

                "min_peak_rss_mib":
                    format_value(
                        memory_stats["min"]
                    ),

                "max_peak_rss_mib":
                    format_value(
                        memory_stats["max"]
                    ),


                # Theoretical references

                "theoretical_matrix_storage_mib":
                    f"{theoretical_memory:.6f}",

                "theoretical_multiplications":
                    multiplications,

                "theoretical_additions":
                    additions
            }


            writer.writerow(row)


# ============================================================
# FORMATTING
# ============================================================

def format_value(value):

    if math.isnan(value):
        return ""

    return f"{value:.9f}"


# ============================================================
# CONSOLE SUMMARY
# ============================================================

def print_summary():

    print(
        "\nSUMMARY OF EXPERIMENTAL RESULTS"
    )

    print("=" * 70)


    with SUMMARY_FILE.open(
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            print(
                f"{row['language']:>6} | "
                f"n={row['matrix_size']:>4} | "
                f"time median="
                f"{row['median_time_seconds']:>12} s | "
                f"RSS median="
                f"{row['median_peak_rss_mib']:>12} MiB"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    if not RUNTIME_FILE.exists():

        raise FileNotFoundError(
            f"Runtime results not found:\n"
            f"{RUNTIME_FILE}"
        )


    if not MEMORY_FILE.exists():

        raise FileNotFoundError(
            f"Memory results not found:\n"
            f"{MEMORY_FILE}"
        )


    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    create_summary()

    print_summary()


    print(
        "\nSummary written to:"
    )

    print(
        SUMMARY_FILE
    )


if __name__ == "__main__":
    main()
