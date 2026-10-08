
# Big Data — Individual Assignment 1

## Basic Matrix Multiplication in Python, Java and C

This repository contains the source code, benchmark automation, correctness tests, raw measurements, analysis scripts and generated figures for Assignment 1 (ULPGC, Big Data, 2026–2027).

**Research question:** How does programming-language choice affect execution time and process-level memory usage for equivalent classical matrix multiplication implementations as matrix size increases?

## Algorithm

All three implementations use the same `i-j-k` triple loop:

```text
for i = 0 ... n-1
    for j = 0 ... n-1
        total = 0
        for k = 0 ... n-1
            total += A[i][k] * B[k][j]
        C[i][j] = total
```

The algorithm has O(n³) time complexity and O(n²) matrix storage.

No NumPy or BLAS matrix multiplication is used.

The input matrices are generated deterministically:

- `A[i][j] = ((i*n+j) % 10)+1`
- `B[i][j] = ((i*n+j+3) % 10)+1`

Python uses lists of built-in integers, Java uses `long[][]`, and C uses contiguous `int64_t` arrays.

The numerical values agree, but the physical memory representations differ.

## Experimental setup

Matrix sizes:

- 50
- 100
- 200
- 300

Five measured repetitions are performed per language and matrix size.

Execution time is summarized using:

- Median
- Interquartile range (IQR)

Memory is measured using Peak Resident Set Size (Peak RSS).

The C implementation is compiled with:

`clang -O2 -std=c11`

## Prerequisites

Run the complete experiment on Linux with:

- Python 3
- Java JDK 21 or newer
- Clang
- GNU `/usr/bin/time`
- Matplotlib

Install the Python plotting dependency from inside `Assignment01`:

```bash
python3 -m pip install -r requirements.txt
```

## Running the experiment

All commands below are executed from inside the `Assignment01` directory.

### 1. Test correctness

```bash
python3 scripts/test_correctness.py
```

The test compares the results against a reference calculation for six matrix sizes in all three languages.

### 2. Measure execution time

```bash
python3 scripts/run_benchmarks.py --repetitions 5 --timeout 30
```

This generates:

`results/raw_results.csv`

Input generation and output matrix allocation are excluded from the timed multiplication kernel.

Each measured invocation starts a new process. The Java measurements therefore do not establish steady-state JVM performance.

### 3. Measure memory usage

```bash
python3 scripts/run_memory_benchmarks.py --repetitions 5 --timeout 30
```

This generates:

`results/raw_memory_results.csv`

The script uses GNU `/usr/bin/time -v` and converts Peak RSS from KiB to MiB.

Peak RSS measures the complete process, not only the matrices.

### 4. Analyze results

```bash
python3 scripts/analyze_results.py
```

This generates:

`results/summary_results.csv`

The summary includes median, IQR, Q1 and Q3. Quartiles use the median-of-halves convention.

### 5. Generate graphs

```bash
python3 scripts/generate_figures.py
```

This generates:

- `figures/execution_time.png`
- `figures/execution_time_loglog.png`
- `figures/memory_usage.png`
- `figures/normalized_scaling.png`

The graphs are generated from measured results rather than hard-coded experimental values.

## Results files

After running the experiment, the results directory contains:

```text
results/
├── raw_results.csv
├── raw_memory_results.csv
├── summary_results.csv
└── environment.txt
```

The environment file records the operating system, Python version, Java version, Clang version and compiler settings.



## Experimental data provenance

The `results/` directory contains recorded benchmark measurements.

The raw CSV files are preserved as experimental evidence. The analysis and plotting scripts are designed to reproduce summary statistics and figures from those files.

The repository may contain subsequent corrections to the benchmarking code. Measurements obtained before a correction must not be represented as measurements obtained with the corrected implementation.

For a new experimental run, record the execution environment, compiler settings, program versions and measurement procedure. Compare the newly generated results against the accompanying scientific paper before replacing any reported values.

## Statistical methodology

Five measurements are used per language and matrix size.

The median represents the central execution-time or memory measurement.

The interquartile range is calculated as Q3 - Q1 using the median-of-halves convention.

Theoretical matrix-element storage assumes three n-by-n matrices with eight bytes per element:

3 * n * n * 8 bytes

This theoretical storage is different from Peak RSS, which measures resident memory for the complete process.

## Figure generation

The four figures are generated from `results/summary_results.csv`.

Run:

```bash
python3 scripts/generate_figures.py
```

The generated files are stored in `figures/`.

The scientific report may use its own PGFPlots figures, but both representations must use the same experimental data.


## Interpretation

The experiment investigates how matrix size and programming-language implementation affect execution time and process-level memory consumption.

The classical algorithm has O(n³) time complexity, but real execution times also depend on compilation, runtime overhead, memory representation and system effects.

The theoretical storage requirement for three matrices containing eight-byte elements is:

`3 * n * n * 8` bytes.

This value is not directly equivalent to measured Peak RSS.

## Limitations

The experiment evaluates only four matrix sizes, uses five repetitions per configuration and runs on one machine.

Python, Java and C use different physical data representations.

The C implementation is compiled with optimization enabled.

JVM warm-up and steady-state JIT performance are not isolated.

The results should not be interpreted as a universal ranking of programming languages.

## Important note about the scientific report

The experimental values depend on the machine used.

If new benchmarks are executed, the numerical results, environment description and graphs in the accompanying scientific paper must be checked and updated to match the recorded measurements.

## Generative AI disclosure

Generative AI assisted with experimental planning, code drafting, documentation and scripting.

The student remains responsible for reviewing the code, executing the experiments, validating the measurements, interpreting the results and defending the conclusions.

AI-generated text is not experimental evidence.
