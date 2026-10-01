import csv
import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ============================================================
# EXPERIMENTAL CONFIGURATION
# ============================================================


MATRIX_SIZES = [50, 100, 200, 300, 400, 500, 750, 1000]
REPETITIONS = 5
JAVA_WARMUPS = 3
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

JAVA_FILE = (
    JAVA_DIR
    / "MatrixMultiplication.java"
)

C_DIR = (
    ASSIGNMENT_DIR
    / "src"
    / "c"
)

C_FILE = (
    C_DIR
    / "matrix_multiplication.c"
)

C_EXECUTABLE = (
    C_DIR
    / "matrix_multiplication"
)

RESULTS_DIR = (
    ASSIGNMENT_DIR
    / "results"
)

RAW_RESULTS_FILE = (
    RESULTS_DIR
    / "raw_results.csv"
)

ENVIRONMENT_FILE = (
    RESULTS_DIR
    / "environment.txt"
)


# ============================================================
# COMMAND EXECUTION
# ============================================================

def run_command(command, cwd=None, timeout=None):
    """
    Execute a command and return its standard output.
    """

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True
    )

    return result.stdout.strip()


# ============================================================
# ENVIRONMENT INFORMATION
# ============================================================

def safe_command(command):
    """
    Execute an environment-information command without
    terminating the benchmark if the information cannot
    be obtained.
    """

    try:
        return run_command(command)

    except Exception as error:
        return f"Unavailable ({error})"


def record_environment():
    """
    Record hardware, operating-system and software information
    required to describe the experimental environment.
    """

    lines = []

    lines.append(
        "ASSIGNMENT 1 - EXPERIMENTAL ENVIRONMENT"
    )
    lines.append("=" * 45)

    lines.append(
        f"Recorded: {datetime.now().isoformat()}"
    )

    lines.append("")

    # --------------------------------------------------------
    # System
    # --------------------------------------------------------

    lines.append("SYSTEM")

    lines.append(
        f"Operating system: {platform.platform()}"
    )
    lines.append(
        f"System: {platform.system()}"
    )
    lines.append(
        f"OS release: {platform.release()}"
    )
    lines.append(
        f"Architecture: {platform.machine()}"
    )
    lines.append(
        f"Logical processors: {os.cpu_count()}"
    )


    # --------------------------------------------------------
    # macOS hardware information
    # --------------------------------------------------------

    if platform.system() == "Darwin":

        cpu = safe_command(
            ["sysctl", "-n", "machdep.cpu.brand_string"]
        )
        # Apple Silicon systems may not provide
        # machdep.cpu.brand_string.
        if cpu.startswith("Unavailable"):

            cpu = safe_command(
                ["sysctl", "-n", "hw.model"]
            )
        lines.append(
            f"CPU/model: {cpu}"
        )
        physical_cores = safe_command(
            ["sysctl", "-n", "hw.physicalcpu"]
        )
        lines.append(
            f"Physical cores: {physical_cores}"
        )
        memory = safe_command(
            ["sysctl", "-n", "hw.memsize"]
        )

        try:
            memory_gib = (
                int(memory) / (1024 ** 3)
            )
            lines.append(
                f"Physical memory: "
                f"{memory_gib:.2f} GiB"
            )
        except ValueError:
            lines.append(
                f"Physical memory: {memory}"
            )


    # --------------------------------------------------------
    # Software
    # --------------------------------------------------------

    lines.append("")
    lines.append("SOFTWARE")

    lines.append(
        "Python: "
        + safe_command(
            [sys.executable, "--version"]
        )
    )


    
    try:

        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True
        )
        java_version = (
            result.stderr.strip()
            or result.stdout.strip()
        )
        lines.append("Java:")
        lines.append(java_version)

    except Exception as error:

        lines.append(
            f"Java: Unavailable ({error})"
        )

    lines.append("C compiler:")

    lines.append(
        safe_command(
            ["clang", "--version"]
        )
    )


    # --------------------------------------------------------
    # Experimental configuration
    # --------------------------------------------------------

    lines.append("")
    lines.append("EXPERIMENTAL SETTINGS")

    lines.append(
        f"Matrix sizes: {MATRIX_SIZES}"
    )
    lines.append(
        f"Measured repetitions: {REPETITIONS}"
    )
    lines.append(
        f"Java warm-up runs: {JAVA_WARMUPS}"
    )
    lines.append(
        f"Per-run timeout: {TIMEOUT_SECONDS} s"
    )
    lines.append(
        "Algorithm: classical triple-loop "
        "matrix multiplication"
    )
    lines.append(
        "Loop order: i-j-k"
    )
    lines.append(
        "Input values: deterministic integers 1..10"
    )
    lines.append(
        "Input generation: outside timed region"
    )
    lines.append(
        "Output allocation: outside timed region"
    )
    lines.append(
        "Timing boundary: multiplication kernel only"
    )
    lines.append(
        "C compiler flags: -O2 -std=c11"
    )
    lines.append(
        "Python numeric representation: built-in int"
    )
    lines.append(
        "Java numeric representation: long"
    )
    lines.append(
        "C numeric representation: int64_t"
    )
    ENVIRONMENT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


# ============================================================
# COMPILATION
# ============================================================

def compile_programs():

    print("\nCompiling Java...")

    run_command(
        [
            "javac",
            JAVA_FILE.name
        ],
        cwd=JAVA_DIR
    )

    print("Java compilation: PASSED")


    print("\nCompiling C...")

    run_command(
        [
            "clang",
            "-O2",
            "-std=c11",
            C_FILE.name,
            "-o",
            C_EXECUTABLE.name
        ],
        cwd=C_DIR
    )

    print("C compilation: PASSED")


# ============================================================
# CORRECTNESS
# ============================================================

def correctness_tests():

    print("\nRunning correctness tests...")

    python_output = run_command(
        [
            sys.executable,
            str(PYTHON_FILE),
            "test"
        ]
    )

    java_output = run_command(
        [
            "java",
            "MatrixMultiplication",
            "test"
        ],
        cwd=JAVA_DIR
    )

    c_output = run_command(
        [
            str(C_EXECUTABLE),
            "test"
        ],
        cwd=C_DIR
    )

    print(f"Python: {python_output}")
    print(f"Java:   {java_output}")
    print(f"C:      {c_output}")


    outputs = {
        "Python": python_output,
        "Java": java_output,
        "C": c_output
    }


    for language, output in outputs.items():

        if "PASSED" not in output:

            raise RuntimeError(
                f"{language} correctness tests failed."
            )


    print(
        "\nAll correctness tests: PASSED"
    )


# ============================================================
# OUTPUT PARSING
# ============================================================

OUTPUT_PATTERN = re.compile(
    r"language=(\w+),"
    r"n=(\d+),"
    r"time_seconds=([0-9.]+),"
    r"checksum=(-?\d+)"
)


def parse_output(output):

    match = OUTPUT_PATTERN.search(output)

    if match is None:

        raise ValueError(
            "Unexpected benchmark output:\n"
            + output
        )


    return {
        "language": match.group(1),
        "matrix_size": int(match.group(2)),
        "time_seconds": float(match.group(3)),
        "checksum": int(match.group(4))
    }


# ============================================================
# INDIVIDUAL IMPLEMENTATIONS
# ============================================================

def run_python(n):

    output = run_command(
        [
            sys.executable,
            str(PYTHON_FILE),
            str(n)
        ],
        timeout=TIMEOUT_SECONDS
    )

    return parse_output(output)


def run_java(n):

    output = run_command(
        [
            "java",
            "MatrixMultiplication",
            str(n)
        ],
        cwd=JAVA_DIR,
        timeout=TIMEOUT_SECONDS
    )

    return parse_output(output)


def run_c(n):

    output = run_command(
        [
            str(C_EXECUTABLE),
            str(n)
        ],
        cwd=C_DIR,
        timeout=TIMEOUT_SECONDS
    )

    return parse_output(output)


RUNNERS = {
    "python": run_python,
    "java": run_java,
    "c": run_c
}


# ============================================================
# JAVA WARM-UP
# ============================================================

def java_warmup(n):

    print(
        f"Java warm-up: "
        f"{JAVA_WARMUPS} unmeasured runs"
    )

    for warmup in range(
        1,
        JAVA_WARMUPS + 1
    ):

        try:

            run_java(n)

            print(
                f"  warm-up "
                f"{warmup}/{JAVA_WARMUPS}: OK"
            )

        except subprocess.TimeoutExpired:

            print(
                "  Java warm-up exceeded "
                "the runtime budget."
            )

            return False


    return True


# ============================================================
# CHECKSUM VALIDATION
# ============================================================

def validate_checksums(results):

    successful = [
        result
        for result in results
        if result["status"] == "success"
    ]


    # A cross-language comparison requires all three
    # implementations to have completed successfully.

    if len(successful) != 3:
        return


    checksums = {
        result["language"]:
        result["checksum"]
        for result in successful
    }


    if len(set(checksums.values())) != 1:

        raise RuntimeError(
            "Cross-language checksum mismatch: "
            f"{checksums}"
        )


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
# BENCHMARK
# ============================================================

def benchmark():

    fieldnames = [
        "language",
        "matrix_size",
        "repetition",
        "time_seconds",
        "checksum",
        "status"
    ]


    with RAW_RESULTS_FILE.open(
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

            print(
                "\n"
                + "=" * 50
            )

            print(
                f"MATRIX SIZE: {n} x {n}"
            )

            print(
                "=" * 50
            )


            # Java JIT warm-up.
            java_warmup(n)


            for repetition in range(
                1,
                REPETITIONS + 1
            ):

                print(
                    f"\nMeasured repetition "
                    f"{repetition}/{REPETITIONS}"
                )


                order = execution_order(
                    repetition
                )

                print(
                    "Execution order: "
                    + " -> ".join(order)
                )


                current_results = []


                for language in order:

                    print(
                        f"  {language}: ",
                        end="",
                        flush=True
                    )


                    try:

                        result = (
                            RUNNERS[language](n)
                        )

                        row = {
                            "language":
                                result["language"],

                            "matrix_size":
                                result["matrix_size"],

                            "repetition":
                                repetition,

                            "time_seconds":
                                f"{result['time_seconds']:.9f}",

                            "checksum":
                                result["checksum"],

                            "status":
                                "success"
                        }

                        print(
                            f"{result['time_seconds']:.6f} s"
                        )


                    except subprocess.TimeoutExpired:

                        row = {
                            "language":
                                language,

                            "matrix_size":
                                n,

                            "repetition":
                                repetition,

                            "time_seconds":
                                "",

                            "checksum":
                                "",

                            "status":
                                "timeout"
                        }

                        print(
                            f"TIMEOUT "
                            f"(>{TIMEOUT_SECONDS} s)"
                        )


                    except Exception as error:

                        row = {
                            "language":
                                language,

                            "matrix_size":
                                n,

                            "repetition":
                                repetition,

                            "time_seconds":
                                "",

                            "checksum":
                                "",

                            "status":
                                "error"
                        }

                        print(
                            f"ERROR: {error}"
                        )


                    writer.writerow(row)

                    csv_file.flush()

                    current_results.append(row)


                validate_checksums(
                    current_results
                )


                if all(
                    result["status"] == "success"
                    for result in current_results
                ):

                    print(
                        "  Cross-language checksum: MATCH"
                    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Assignment 1"
    )

    print(
        "Basic Matrix Multiplication "
        "Benchmark"
    )

    print("=" * 45)


    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    record_environment()

    compile_programs()

    correctness_tests()

    benchmark()


    print("\n" + "=" * 45)

    print(
        "Benchmark completed."
    )

    print(
        "\nRaw measurements:"
    )

    print(
        RAW_RESULTS_FILE
    )

    print(
        "\nExperimental environment:"
    )

    print(
        ENVIRONMENT_FILE
    )


if __name__ == "__main__":
    main()
