import argparse
import csv
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

FIELDS = [
    "method", "n", "workers", "repetition", "time_s",
    "checksum", "peak_rss_mib", "rss_scope",
    "max_worker_rss_mib", "sum_worker_rss_mib",
    "max_setup_s", "max_distribution_s",
    "max_compute_s", "max_collection_s"
]


def run_once(method, n, workers, timeout):
    if method == "distributed":
        command = [
            "mpiexec", "-n", str(workers),
            sys.executable, "-m", "src.distributed", str(n)
        ]
    else:
        command = [
            sys.executable, "-m", f"src.{method}", str(n)
        ]
        if method == "parallel":
            command.append(str(workers))

    use_gnu_time = (
        platform.system() == "Linux"
        and Path("/usr/bin/time").exists()
    )

    full_command = (
        ["/usr/bin/time", "-v"] + command
        if use_gnu_time else command
    )

    process = subprocess.run(
        full_command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    if process.returncode != 0:
        raise RuntimeError(
            "Command failed:\n" + " ".join(command)
            + "\n" + process.stderr[-3000:]
        )

    if method == "distributed":
        lines = [
            line.removeprefix("RESULT ")
            for line in process.stdout.splitlines()
            if line.startswith("RESULT ")
        ]
        if len(lines) != 1:
            raise RuntimeError(
                "MPI result missing:\n" + process.stdout
            )
        result = json.loads(lines[0])
    else:
        def extract(label):
            match = re.search(
                rf"^{label}:\s*(.+)$",
                process.stdout,
                re.MULTILINE
            )
            if not match:
                raise RuntimeError(
                    f"Missing {label}:\n{process.stdout}"
                )
            return match.group(1)

        result = {
            "method": method,
            "n": n,
            "workers": workers,
            "time_s": float(extract("Time").split()[0]),
            "checksum": int(extract("Checksum"))
        }

    result["peak_rss_mib"] = ""
    result["rss_scope"] = "not measured"

    if use_gnu_time:
        match = re.search(
            r"Maximum resident set size \(kbytes\):\s*(\d+)",
            process.stderr
        )
        if match:
            result["peak_rss_mib"] = int(match.group(1)) / 1024
            result["rss_scope"] = (
                "whole sequential process"
                if method == "sequential"
                else "parent process only"
                if method == "parallel"
                else "MPI launcher only"
            )

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--methods", nargs="+",
        choices=["sequential", "parallel", "distributed"],
        default=["sequential", "parallel", "distributed"]
    )
    parser.add_argument(
        "--sizes", nargs="+", type=int,
        default=[100, 200, 400]
    )
    parser.add_argument(
        "--workers", nargs="+", type=int,
        default=[1, 2, 4]
    )
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    if "distributed" in args.methods:
        if not shutil.which("mpiexec"):
            parser.error("MPI is not installed or mpiexec is missing")

    if args.repetitions < 5:
        print("Warning: fewer than five repetitions")

    with (RESULTS / "raw_results.csv").open(
        "w", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for n in args.sizes:
            reference_checksum = None

            for method in args.methods:
                counts = (
                    [1] if method == "sequential"
                    else args.workers
                )

                for workers in counts:
                    print(
                        f"Running {method}, n={n}, "
                        f"workers={workers}",
                        flush=True
                    )

                    for repetition in range(
                        -args.warmups, args.repetitions
                    ):
                        result = run_once(
                            method, n, workers, args.timeout
                        )

                        if reference_checksum is None:
                            reference_checksum = result["checksum"]

                        if result["checksum"] != reference_checksum:
                            raise AssertionError(
                                f"Incorrect result: {method}, "
                                f"n={n}, workers={workers}"
                            )

                        if repetition >= 0:
                            result["repetition"] = repetition + 1
                            writer.writerow({
                                field: result.get(field, "")
                                for field in FIELDS
                            })
                            file.flush()

    with (RESULTS / "environment.txt").open("w") as file:
        file.write(f"Platform: {platform.platform()}\n")
        file.write(f"Python: {sys.version}\n")
        file.write(f"Logical processors: {os.cpu_count()}\n")
        file.write(f"Configuration: {vars(args)}\n")
        file.write(
            "Timings exclude interpreter/MPI startup. "
            "They include input generation, multiplication, "
            "communication and result assembly as applicable.\n"
        )
        file.write(
            "MPI worker RSS values are individual process "
            "high-water marks; their sum is not simultaneous "
            "cluster memory consumption.\n"
        )

    print("Saved results/raw_results.csv")


if __name__ == "__main__":
    main()
