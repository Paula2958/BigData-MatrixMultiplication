import argparse
import csv
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZES = [50, 100, 200, 300]
LANGUAGES = ("python", "java", "c")


def prepare():
    """Compile Java and C once before the experiments."""
    build = ROOT / "build"
    build.mkdir(exist_ok=True)

    subprocess.run([
        "javac", "-d", str(build),
        str(ROOT / "src/java/MatrixMultiplication.java")
    ], check=True)

    subprocess.run([
        "clang", "-O2", "-std=c11",
        str(ROOT / "src/c/matrix_multiplication.c"),
        "-o", str(build / "matrix_c")
    ], check=True)

    return build


def command(language, n, build):
    if language == "python":
        return [
            sys.executable,
            str(ROOT / "src/python/matrix_multiplication.py"),
            str(n)
        ]

    if language == "java":
        return [
            "java", "-cp", str(build),
            "MatrixMultiplication", str(n)
        ]

    if language == "c":
        return [str(build / "matrix_c"), str(n)]

    raise ValueError(f"Unknown language: {language}")


def parse_result(output):
    lines = [
        line for line in output.splitlines()
        if line.startswith("RESULT,")
    ]

    if len(lines) != 1:
        raise ValueError("Expected exactly one RESULT line.")

    parts = lines[0].split(",")

    if len(parts) != 4:
        raise ValueError("Invalid RESULT format.")

    return int(parts[1]), float(parts[2]), int(parts[3])


def run_program(cmd, timeout=30):
    process = subprocess.run(
        cmd, capture_output=True, text=True,
        check=True, timeout=timeout
    )
    return parse_result(process.stdout)


def measure_process(cmd, timeout=30):
    process = subprocess.run(
        ["/usr/bin/time", "-v", *cmd],
        capture_output=True, text=True,
        check=True, timeout=timeout
    )

    n, seconds, checksum = parse_result(process.stdout)

    match = re.search(
        r"Maximum resident set size \(kbytes\):\s*(\d+)",
        process.stderr
    )

    if not match:
        raise RuntimeError("GNU time did not report Peak RSS.")

    peak_rss_mib = int(match.group(1)) / 1024

    return n, seconds, checksum, peak_rss_mib


def save_environment(repetitions, timeout):
    output = ROOT / "results/environment.txt"

    with output.open("w") as f:
        f.write(f"OS: {platform.platform()}\n")
        f.write(f"Architecture: {platform.machine()}\n")
        f.write(f"Processor: {platform.processor()}\n")
        f.write(f"Logical CPUs: {os.cpu_count()}\n")
        f.write(f"Python: {sys.version.split()[0]}\n")

        for name, cmd in [
            ("Java", ["java", "-version"]),
            ("Clang", ["clang", "--version"]),
            ("GNU time", ["/usr/bin/time", "--version"])
        ]:
            p = subprocess.run(
                cmd, capture_output=True, text=True
            )
            lines = (p.stdout + p.stderr).splitlines()
            f.write(f"{name}: {lines[0] if lines else 'unknown'}\n")

        f.write("C compiler flags: -O2 -std=c11\n")
        f.write(f"Matrix sizes: {SIZES}\n")
        f.write(f"Measured repetitions: {repetitions}\n")
        f.write("Warm-up: 1 fresh process per configuration\n")
        f.write(f"Per-process timeout: {timeout} seconds\n")
        f.write("Timing: multiplication kernel only\n")
        f.write("Memory: complete process Peak RSS\n")
        f.write("Input values: deterministic integers 1 to 10\n")
        f.write("Seed: not required (no random generator)\n")
        f.write("Loop order: i-j-k\n")
        f.write("Java: new JVM process for every repetition\n")
        f.write("Execution order: n, then language, then repetition\n")
        f.write("Total-memory budget: 1024 MiB Peak RSS per run\n")
        f.write("Host CPU load and background tasks: not controlled\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if args.repetitions < 5:
        parser.error("At least five repetitions are required.")

    if args.timeout <= 0:
        parser.error("Timeout must be positive.")

    if not Path("/usr/bin/time").exists():
        raise RuntimeError("GNU /usr/bin/time is required.")

    build = prepare()
    results = ROOT / "results"
    results.mkdir(exist_ok=True)

    rows = []
    expected_checksums = {}

    for n in SIZES:
        for language in LANGUAGES:
            cmd = command(language, n, build)

            # One independent warm-up process.
            warm_n, _, warm_checksum = run_program(
                cmd, args.timeout
            )
            if warm_n != n:
                raise RuntimeError("Warm-up size mismatch.")

            if n in expected_checksums:
                if warm_checksum != expected_checksums[n]:
                    raise RuntimeError("Warm-up checksum mismatch.")
            else:
                expected_checksums[n] = warm_checksum

            for repetition in range(1, args.repetitions + 1):
                size, seconds, checksum, rss = measure_process(
                    cmd, args.timeout
                )

                if size != n:
                    raise RuntimeError("Matrix size mismatch.")

                if checksum != expected_checksums[n]:
                    raise RuntimeError("Checksum mismatch.")

                if rss > 1024:
                    raise RuntimeError(
                        "Memory budget exceeded: 1024 MiB"
                    )

                rows.append([
                    language, n, repetition,
                    seconds, rss, checksum
                ])

                print(
                    f"{language:6} n={n:3} "
                    f"run={repetition} "
                    f"time={seconds:.6f}s "
                    f"RSS={rss:.2f} MiB",
                    flush=True
                )

    output = results / "raw_results.csv"

    with output.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "language", "matrix_size", "repetition",
            "time_seconds", "peak_rss_mib", "checksum"
        ])
        writer.writerows(rows)

    save_environment(args.repetitions, args.timeout)
    print(f"\nSaved {len(rows)} measurements to {output}")


if __name__ == "__main__":
    main()
