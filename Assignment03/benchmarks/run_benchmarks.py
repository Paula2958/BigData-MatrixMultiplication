
#!/usr/bin/env python3

import argparse
import csv
import os
import platform
import subprocess
import sys
import pathlib
import statistics
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"

FIELDS = [
    "method", "n", "threads", "seed",
    "repetition", "seconds", "peak_rss_kib",
    "checksum"
]


def command(*args):
    return subprocess.run(
        args, cwd=ROOT, text=True,
        capture_output=True, check=True
    ).stdout.strip()


def environment():
    lines = [
        "Platform: " + platform.platform(),
        "Python: " + sys.version.splitlines()[0],
        "Compiler: " + command("gcc", "--version").splitlines()[0],
        "Build: gcc -O2 -std=c11 -Wall -Wextra "
        "-fopenmp -fno-tree-vectorize",
        "Timing: CLOCK_MONOTONIC; input allocation excluded; "
        "C zero-initialization excluded",
        "Warmup: one untimed multiplication per process; "
        "samples: one measured multiplication per process",
        "Memory: getrusage ru_maxrss peak process RSS "
        "(KiB on Linux); includes warmup and allocations",
        "RNG: xorshift64*; values in [0,1] increments "
        "of 0.001; double precision",
        "OMP_DYNAMIC=FALSE; OMP_PROC_BIND=FALSE; "
        "static row scheduling",
        "Logical processors (OS): " + str(os.cpu_count())
    ]

    for args in [
        ("lscpu",),
        ("free", "-h"),
        ("uname", "-a")
    ]:
        try:
            lines.append(
                "\n$ " + " ".join(args) + "\n" + command(*args)
            )
        except Exception as exc:
            lines.append(str(exc))

    (ROOT / "environment.txt").write_text(
        "\n".join(lines) + "\n"
    )


def median(xs):
    return statistics.median(xs)


def quartiles(xs):
    s = sorted(xs)
    half = len(s) // 2

    return (
        median(s[:half]),
        median(s[(half + 1 if len(s) % 2 else half):])
    )


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--sizes", nargs="+", type=int,
        default=[128, 256, 512, 768, 1024]
    )
    ap.add_argument(
        "--threads", nargs="+", type=int, default=None
    )
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261109)
    ap.add_argument(
        "--max-seconds-per-run", type=float, default=120
    )

    args = ap.parse_args()

    if args.reps < 5:
        print(
            "WARNING: fewer than five repetitions "
            "must be justified in report",
            file=sys.stderr
        )

    if args.reps < 2 or args.seed < 1:
        ap.error("reps >= 2 and positive seed required")

    available = os.cpu_count() or 1

    threads = args.threads or [
        p for p in (1, 2, 4, 8) if p <= available
    ]

    if any(p < 1 for p in threads):
        ap.error("thread counts must be positive")

    subprocess.run(["make", "all"], cwd=ROOT, check=True)
    subprocess.run(
        [str(ROOT / "matrix"), "--test"], check=True
    )

    environment()
    RESULTS.mkdir(exist_ok=True, parents=True)

    raw = RESULTS / "raw_results.csv"
    rows = []
    failures = []

    jobs = [("sequential", 1)] + [
        ("parallel", p) for p in sorted(set(threads))
    ]

    with raw.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        f.flush()

        for n in args.sizes:
            for r in range(1, args.reps + 1):
                order = jobs[:]
                random.Random(args.seed + n + r).shuffle(order)

                for method, p in order:
                    try:
                        result = subprocess.run(
                            [
                                str(ROOT / "matrix"),
                                method, str(n), str(p),
                                str(args.seed + n), str(r)
                            ],
                            cwd=ROOT,
                            env={
                                **os.environ,
                                "OMP_DYNAMIC": "FALSE",
                                "OMP_PROC_BIND": "FALSE"
                            },
                            text=True,
                            capture_output=True,
                            timeout=args.max_seconds_per_run,
                            check=True
                        )

                        line = result.stdout.strip()
                        values = next(csv.reader([line]))

                        if len(values) != len(FIELDS):
                            raise ValueError("Invalid CSV output")

                        row = dict(zip(FIELDS, values))
                        w.writerow(row)
                        f.flush()
                        rows.append(row)

                        print(
                            f"{method:10s} n={n:4d} "
                            f"p={p:2d} rep={r} "
                            f"{float(row['seconds']):.5f}s",
                            flush=True
                        )

                    except (
                        subprocess.TimeoutExpired,
                        subprocess.CalledProcessError,
                        ValueError
                    ) as exc:
                        failures.append(
                            (method, n, p, r, str(exc))
                        )
                        print(
                            "FAILED:", failures[-1],
                            file=sys.stderr
                        )

            for r in range(1, args.reps + 1):
                base = next(
                    (
                        float(x["checksum"])
                        for x in rows
                        if x["n"] == str(n)
                        and x["method"] == "sequential"
                        and x["repetition"] == str(r)
                    ),
                    None
                )

                if base is None:
                    continue

                for x in rows:
                    if (
                        x["n"] == str(n)
                        and x["repetition"] == str(r)
                        and x["method"] == "parallel"
                    ):
                        value = float(x["checksum"])

                        if abs(value - base) > (
                            1e-8 + 1e-10 * abs(base)
                        ):
                            raise RuntimeError(
                                f"Correctness failed: {x}"
                            )

    with (RESULTS / "failures.csv").open(
        "w", newline=""
    ) as f:
        w = csv.writer(f)
        w.writerow([
            "method", "n", "threads",
            "repetition", "error"
        ])
        w.writerows(failures)

    groups = {}

    for x in rows:
        key = (
            int(x["n"]),
            x["method"],
            int(x["threads"])
        )
        groups.setdefault(key, []).append(x)

    summary = []

    for (n, m, p), items in sorted(groups.items()):
        times = [float(x["seconds"]) for x in items]
        rss = [int(x["peak_rss_kib"]) for x in items]
        q1, q3 = quartiles(times)

        summary.append({
            "n": n,
            "method": m,
            "threads": p,
            "repetitions": len(items),
            "median_seconds": median(times),
            "iqr_seconds": q3 - q1,
            "median_peak_rss_kib": median(rss),
            "speedup": "",
            "efficiency": ""
        })

    for x in summary:
        base = next(
            (
                b for b in summary
                if b["n"] == x["n"]
                and b["method"] == "sequential"
            ),
            None
        )

        if x["method"] == "parallel" and base:
            x["speedup"] = (
                base["median_seconds"] / x["median_seconds"]
            )
            x["efficiency"] = (
                x["speedup"] / x["threads"]
            )

    with (RESULTS / "summary_results.csv").open(
        "w", newline=""
    ) as f:
        fields = list(summary[0]) if summary else ["n"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summary)

    print(
        "Saved", raw,
        "and summary_results.csv; failures:",
        len(failures)
    )


if __name__ == "__main__":
    main()
