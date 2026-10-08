
import argparse
import csv
import re
import subprocess
from pathlib import Path

from run_benchmarks import (
    ROOT, SIZES, LANGUAGES,
    prepare, command, run
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("Repetitions must be positive.")

    if not Path("/usr/bin/time").exists():
        raise RuntimeError(
            "GNU /usr/bin/time is required on Linux."
        )

    build = prepare()
    rows = []
    expected = {}

    for n in SIZES:
        for language in LANGUAGES:
            cmd = command(language, n, build)

            # Separate invocation, not JVM steady-state warm-up.
            run(cmd, args.timeout)

            for repetition in range(1, args.repetitions + 1):
                process = subprocess.run(
                    ["/usr/bin/time", "-v", *cmd],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=args.timeout
                )

                match = re.search(
                    r"Maximum resident set size "
                    r"\(kbytes\):\s*(\d+)",
                    process.stderr
                )

                if match is None:
                    raise RuntimeError(
                        "Peak RSS was not reported."
                    )

                result_lines = [
                    line for line in process.stdout.splitlines()
                    if line.startswith("RESULT,")
                ]

                if len(result_lines) != 1:
                    raise RuntimeError(
                        "Invalid program output."
                    )

                _, size, _, checksum = (
                    result_lines[0].split(",")
                )

                size = int(size)
                checksum = int(checksum)

                if size != n:
                    raise RuntimeError("Matrix size mismatch.")

                if n in expected and checksum != expected[n]:
                    raise RuntimeError("Checksum mismatch.")

                expected[n] = checksum

                peak_rss_mib = int(match.group(1)) / 1024

                rows.append([
                    language, n, repetition,
                    peak_rss_mib, "success"
                ])

                print(
                    f"{language:6} n={n:3} "
                    f"run={repetition} "
                    f"RSS={peak_rss_mib:.3f} MiB"
                )

    output = ROOT / "results/raw_memory_results.csv"

    with output.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "language", "matrix_size", "repetition",
            "peak_rss_mib", "status"
        ])
        writer.writerows(rows)

    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
