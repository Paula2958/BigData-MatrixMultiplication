
import argparse
import csv
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZES = [50, 100, 200, 300]
LANGUAGES = ("python", "java", "c")


def prepare():
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
    commands = {
        "python": [
            sys.executable,
            str(ROOT / "src/python/matrix_multiplication.py"),
            str(n)
        ],
        "java": [
            "java", "-cp", str(build),
            "MatrixMultiplication", str(n)
        ],
        "c": [
            str(build / "matrix_c"), str(n)
        ]
    }
    return commands[language]


def run(cmd, timeout=30):
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout
    )

    lines = [
        line for line in process.stdout.splitlines()
        if line.startswith("RESULT,")
    ]

    if len(lines) != 1:
        raise RuntimeError(
            f"Expected one RESULT line: {process.stdout}"
        )

    _, n, seconds, checksum = lines[0].split(",")

    return int(n), float(seconds), int(checksum)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("Repetitions must be positive.")

    build = prepare()
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    rows = []
    checksums = {}

    for n in SIZES:
        for language in LANGUAGES:
            cmd = command(language, n, build)

            # Independent warm-up invocation.
            run(cmd, args.timeout)

            for repetition in range(1, args.repetitions + 1):
                size, seconds, checksum = run(
                    cmd, args.timeout
                )

                if size != n:
                    raise RuntimeError("Matrix size mismatch.")

                if n in checksums and checksums[n] != checksum:
                    raise RuntimeError(
                        f"Checksum mismatch: {language}, n={n}"
                    )

                checksums[n] = checksum

                rows.append([
                    language, n, repetition,
                    seconds, checksum
                ])

                print(
                    f"{language:6} n={n:3} "
                    f"run={repetition} time={seconds:.9f}s"
                )

    output = results_dir / "raw_results.csv"

    with output.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "language", "matrix_size", "repetition",
            "time_seconds", "checksum"
        ])
        writer.writerows(rows)

    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
