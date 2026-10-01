import csv
import platform
import subprocess
import sys
from pathlib import Path


# ============================================================
# EXPERIMENTAL CONFIGURATION
# ============================================================

MATRIX_SIZES = [50, 100, 200, 300, 400, 500, 750, 1000]

REPETITIONS = 5

TIMEOUT_SECONDS = 120


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ASSIGNMENT_DIR = SCRIPT_DIR.parent

PYTHON_FILE = (
    ASSIGNMENT_DIR
    / "src"
    / "python"
    / "matrix_multiplication.py"
)

JAVA_DIR = (
    ASSIGNMENT_DIR
    / "src"
    / "java"
)

C_DIR = (
    ASSIGNMENT_DIR
    / "src"
    / "c"
)

C_EXECUTABLE = (
    C_DIR
    / "matrix_multiplication"
)

RESULTS_DIR = (
    ASSIGNMENT_DIR
    / "results"
)

OUTPUT_FILE = (
    RESULTS_DIR
    / "raw_memory_results.csv"
)


# ============================================================
# PEAK RSS MEASUREMENT
# ============================================================

def measure_peak_rss(command, cwd=None):
    """
    Execute a program with macOS /usr/bin/time -l.

    The reported 'maximum resident set size' is collected
    and converted from bytes to MiB.
    """

    result = subprocess.run(
        ["/usr/bin/time", "-l"] + command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
        )

    peak_rss_bytes = None

    for line in result.stderr.splitlines():

        if "maximum resident set size" in line:

            value = line.strip().split()[0]

            peak_rss_bytes = int(value)

            break

    if peak_rss_bytes is None:

        raise RuntimeError(
            "Maximum resident set size "
            "could not be obtained."
        )

    peak_rss_mib = (
        peak_rss_bytes / (1024 ** 2)
    )

    return peak_rss_mib


# ============================================================
# LANGUAGE RUNNERS
# ============================================================

def run_python(n):

    return measure_peak_rss(
        [
            sys.executable,
            str(PYTHON_FILE),
            str(n)
        ]
    )


def run_java(n):

    return measure_peak_rss(
        [
            "java",
            "MatrixMultiplication",
            str(n)
        ],
        cwd=JAVA_DIR
    )


def run_c(n):

    return measure_peak_rss(
        [
            str(C_EXECUTABLE),
            str(n)
        ],
        cwd=C_DIR
    )


RUNNERS = {
    "python": run_python,
    "java": run_java,
    "c": run_c
}


# ============================================================
# EXECUTION ORDER
# ============================================================

def execution_order(repetition):

    orders = [
        ["python", "java", "c"],
        ["java", "c", "python"],
        ["c", "python", "java"]
    ]

    return orders[
        (repetition - 1) % len(orders)
    ]


# ============================================================
# MEMORY BENCHMARK
# ============================================================

def benchmark():

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "language",
        "matrix_size",
        "repetition",
        "peak_rss_mib",
        "status"
    ]


    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()


        for n in MATRIX_SIZES:

            print("\n" + "=" * 50)

            print(
                f"MEMORY TEST: {n} x {n}"
            )

            print("=" * 50)


            for repetition in range(
                1,
                REPETITIONS + 1
            ):

                print(
                    f"\nRepetition "
                    f"{repetition}/{REPETITIONS}"
                )


                for language in execution_order(
                    repetition
                ):

                    print(
                        f"  {language}: ",
                        end="",
                        flush=True
                    )


                    try:

                        memory = (
                            RUNNERS[language](n)
                        )

                        row = {
                            "language":
                                language,

                            "matrix_size":
                                n,

                            "repetition":
                                repetition,

                            "peak_rss_mib":
                                f"{memory:.6f}",

                            "status":
                                "success"
                        }

                        print(
                            f"{memory:.2f} MiB"
                        )


                    except subprocess.TimeoutExpired:

                        row = {
                            "language":
                                language,

                            "matrix_size":
                                n,

                            "repetition":
                                repetition,

                            "peak_rss_mib":
                                "",

                            "status":
                                "timeout"
                        }

                        print("TIMEOUT")


                    except Exception as error:

                        row = {
                            "language":
                                language,

                            "matrix_size":
                                n,

                            "repetition":
                                repetition,

                            "peak_rss_mib":
                                "",

                            "status":
                                "error"
                        }

                        print(
                            f"ERROR: {error}"
                        )


                    writer.writerow(row)

                    csv_file.flush()


# ============================================================
# MAIN
# ============================================================

def main():

    if platform.system() != "Darwin":

        raise RuntimeError(
            "This script is configured for macOS "
            "because it uses /usr/bin/time -l."
        )


    print(
        "Assignment 1"
    )

    print(
        "Peak Memory Benchmark"
    )

    print("=" * 45)


    benchmark()


    print("\n" + "=" * 45)

    print(
        "Memory benchmark completed."
    )

    print(
        "\nRaw memory measurements:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
