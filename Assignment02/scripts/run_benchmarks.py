
import csv
import platform
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
RESULTS = ROOT / "results"
BUILD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

DENSE_SIZES = [100, 200, 400]
SPARSE_SIZES = [100, 200, 400]
SPARSITIES = [50, 90, 99]
REPETITIONS = 5
WARMUPS = 2
TILE = 32

subprocess.run(["javac", "-d", str(BUILD), str(ROOT / "src/MatrixStudy.java")], check=True)
subprocess.run(["java", "-cp", str(BUILD), "MatrixStudy", "test"], check=True)

configurations = []
for n in DENSE_SIZES:
    for method in ["basic", "reordered", "blocked"]:
        configurations.append(("dense", method, n, 0))
for n in SPARSE_SIZES:
    for sparsity in SPARSITIES:
        for method in ["reordered", "csr"]:
            configurations.append(("sparse", method, n, sparsity))

columns = ["part", "method", "n", "sparsity_pct", "repetition", "seed",
           "time_ms", "conversion_ms", "a_nnz", "b_nnz", "c_nnz",
           "checksum", "peak_rss_mib"]

with (RESULTS / "raw_results.csv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    for part, method, n, sparsity in configurations:
        seed = 20261015 + 17 * n + sparsity
        print(part, method, "n=", n, "zeros=", sparsity, flush=True)
        for repetition in range(1, REPETITIONS + 1):
            command = ["/usr/bin/time", "-v", "java", "-Xms64m", "-Xmx1024m",
                       "-cp", str(BUILD), "MatrixStudy", "bench", method,
                       str(n), str(sparsity), str(seed), str(WARMUPS), str(TILE)]
            process = subprocess.run(command, capture_output=True, text=True,
                                     timeout=45, check=True)
            result = next(line for line in process.stdout.splitlines()
                          if line.startswith("RESULT,"))
            values = result.split(",")[1:]
            memory = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)",
                               process.stderr)
            if memory is None:
                raise RuntimeError("GNU time did not report peak RSS")
            writer.writerow(dict(zip(columns, [part, method, n, sparsity,
                repetition, seed, *values, float(memory.group(1)) / 1024])))
        file.flush()

with (RESULTS / "environment.txt").open("w") as file:
    file.write(f"Operating system: {platform.platform()}\n")
    file.write(f"Warm-ups: {WARMUPS}; measured independent processes: {REPETITIONS}\n")
    file.write(f"Dense sizes: {DENSE_SIZES}; sparse sizes: {SPARSE_SIZES}\n")
    file.write(f"Sparsities: {SPARSITIES}; tile size: {TILE}\n")
    file.write("Kernel timing includes result allocation; excludes input creation, "
               "CSR conversion and checksum.\n")
    file.write("CSR conversion is recorded separately; peak RSS covers entire JVM.\n")
    for command in [["java", "-version"], ["python3", "--version"], ["lscpu"]]:
        p = subprocess.run(command, capture_output=True, text=True)
        file.write("\n$ " + " ".join(command) + "\n" + p.stdout + p.stderr)

print("Finished. Results saved in results/raw_results.csv")
