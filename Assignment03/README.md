
# Assignment 3 — Parallel Matrix Multiplication

**Big Data | Academic Year 2026–2027**  
**Degree in Data Science and Engineering**  
**Universidad de Las Palmas de Gran Canaria (ULPGC)**

## 1. Project Overview

This task investigates the performance and scalability of
shared-memory parallel matrix multiplication the use of C and OpenMP.

It is the third man or woman task for the Big Data path.

The experiment compares an equal sequential implementation
with an OpenMP parallel implementation, varying the matrix length
and the number of threads.

The predominant objective is to decide while parallel execution
presents a overall performance gain and the way correctly the
to be had computational sources are used.

### Research Question

How does the range of OpenMP threads affect execution time,
memory consumption, speedup and parallel efficiency for dense
square matrix multiplication?

### Hypothesis

Parallel execution is predicted to improve performance for
sufficiently massive matrices due to the fact unbiased output rows
may be computed concurrently.

However, thread-control overhead, memory bandwidth
limitations and aid competition may additionally lessen efficiency,
specifically for small matrices or excessive thread counts.

---

## 2. Project Structure

```text
BigData-Assignment03/
├── src/
│   └── matrix.c
├── benchmarks/
│   ├── run_benchmarks.py
│   ├── plot_results.py
│   └── results/
│       ├── raw_results.csv
│       ├── summary_results.csv       
│       └── execution_summary.csv
├── figures/
│   ├── execution_time.png
│   ├── speedup.png
│   ├── efficiency.png
│   └── memory_usage.png
├── Makefile
├── requirements.txt
├── .gitignore
└── README.md
```

The source code, measurement data, figures and environment
information are included to support reproducibility.

---

## 3. Technologies

The assignment makes use of:

- C11 for the multiplication implementations.
- OpenMP for shared-reminiscence parallel execution.
- GCC for compilation.
- Python three for benchmark automation.
- Matplotlib for performance visualisation.
  
No outside matrix multiplication library is used.

---

## 4. Matrix Multiplication Implementations

### 4.1 Sequential Implementation

The sequential baseline implements classical dense
matrix multiplication using three nested loops.

For square matrices A and B of size n x n:

C[i][j] = sum(A[i][k] * B[k][j])

The implementation uses the i-k-j loop order.

Its arithmetic complexity is:

O(n^3)

### 4.2 Parallel Implementation

The parallel implementation uses the same algorithm,
numeric type, storage layout and loop ordering.

Parallelism is introduced through the OpenMP directive:

```c
#pragma omp parallel for schedule(static)
```

The outer loop distributes output rows throughout threads.

Each thread writes to unbiased rows of matrix C.

Consequently, the implementation avoids concurrent writes
to the identical output factors and does now not require locks
or atomic operations.

### 4.3 Fair Comparison

Both implementations use:

- The same enter matrices.
- Double-precision floating-point mathematics.
- Row-foremost contiguous storage.
- The equal i-k-j multiplication algorithm.
- Identical compilation optimisation settings.
- The identical kernel timing limitations.

The parallel implementation is also examined with one thread
to discover possible OpenMP overhead.

---

## 5. Experimental Methodology

### 5.1 Matrix Sizes

The following square matrix sizes were evaluated:

| n | Matrix dimensions |
|---|---|
| 128 | 128 x 128 |
| 256 | 256 x 256 |
| 512 | 512 x 512 |
| 768 | 768 x 768 |
| 1024 | 1024 x 1024 |

### 5.2 Thread Configurations

The parallel implementation was tested using:

- 1 thread
- 2 threads
- 4 threads
- 8 threads

A separate sequential baseline became also measured.

The 8-thread configuration exceeds the five logical
processors seen within the recorded surroundings and must
be interpreted as an oversubscribed configuration.

### 5.3 Input Generation

Input matrices are generated using a deterministic
xorshift64* pseudorandom generator.

The documented seed is:

20261109 + n

Matrix values are double-precision numbers in the range
[0, 1], with increments of 0.001.

The same logical inputs are used for the sequential and
parallel implementations at each matrix size.

### 5.4 Timing Protocol

Execution time is measured using CLOCK_MONOTONIC.

The measured place consists of the matrix multiplication
kernel but excludes:

- Matrix allocation.
- Input era.
- Output initialisation.
- Checksum calculation.

One untimed heat-up multiplication is completed earlier than
every timed measurement.

Five measured repetitions are amassed in keeping with configuration.

The execution order is randomised inside each repetition.


### 5.5 Statistical Analysis

For every configuration, the experiment reviews:

- Median execution time.
- Interquartile variety (IQR).
- Median top process resident reminiscence.
- Speedup.
- Parallel performance.

The median is used to reduce sensitivity to surprisingly
slow or rapid observations.

### 5.6 Memory Measurement

Memory usage is received the use of:

getrusage(RUSAGE_SELF)

The stated ru_maxrss price represents height process
resident memory, expressed in KiB on Linux.

This measurement includes process allocations and warm-up
interest and does no longer isolate the reminiscence consumption of
the multiplication kernel.

### 5.7 Correctness Validation

The implementations are tested using:

- Known 2 x 2 multiplication consequences.
- Identity matrix multiplication.
- Zero matrix multiplication.
- Sequential and parallel weighted checksum comparisons.

The benchmark assessments numerical agreement between
sequential and parallel consequences using declared tolerances.

---

## 6. Execution Environment

The recorded experiment was executed in a Linux virtual
environment with the following visible characteristics:

| Component | Configuration |
|---|---|
| Operating system | Linux 6.18.57 |
| Architecture | x86_64 |
| Processor | Intel Xeon Platinum 8573C |
| Visible logical CPUs | 5 |
| Virtualisation | KVM |
| Compiler | GCC 14.2.0 |
| Python | 3.13.5 |
| Available RAM reported | Approximately 5.8 GiB |

The execution environment is a virtualised server and
is not the same physical machine used in Assignment 1.

The complete environment information is available in:

environment.txt

### Compiler Configuration

```bash
gcc -O2 -std=c11 -Wall -Wextra \
    -fopenmp -fno-tree-vectorize \
    src/matrix.c -o matrix -lm
```

Automatic tree vectorisation is disabled to focus the
experiment on the effects of thread-level parallelism.

---

## 7. Installation and Compilation

### Requirements

A system with:

- GCC with OpenMP support.
- Python 3.
- GNU Make.
- Python packages listed in requirements.txt.

On Debian or Ubuntu:

```bash
sudo apt update
sudo apt install build-essential python3 python3-pip
```

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Compile the C implementation:

```bash
make clean
make
```

Run correctness tests:

```bash
make test
```

Expected successful test message:

```text
PASS: known product, identity, zero, sequential and parallel
```

---

## 8. Running the Benchmarks

Execute from the repository root:

```bash
python3 benchmarks/run_benchmarks.py \
    --sizes 128 256 512 768 1024 \
    --threads 1 2 4 8 \
    --reps 5 \
    --seed 20261109
```

The express 8-thread configuration is blanketed
to reproduce the recorded oversubscription experiment.

For a new system, thread counts need to be decided on
in step with its available hardware.

The benchmark generates:

- benchmarks/results/raw_results.csv
- benchmarks/results/summary_results.csv
- benchmarks/results/failures.csv
- environment.txt

The execution_summary.csv file provides an additional
summary of completed and failed executions.

---

## 9. Performance Metrics

### Execution Time

The median runtime is calculated from five measurements
for each configuration.

### Speedup

Speedup is defined as:

S(p) = Tseq / Tp

where:

- Tseq is the median sequential runtime.
- Tp is the median parallel runtime with p threads.

### Parallel Efficiency

Efficiency is defined as:

E(p) = S(p) / p

Efficiency measures the achieved speedup relative to
the number of threads.

Values above 1 may occur in noisy experiments and should
not automatically be interpreted as superlinear scaling.

---

## 10. Experimental Results

The experiment contains:

- 5 matrix sizes.
- 5 implementation/thread configurations per size.
- 5 repetitions per configuration.

Total measurements: 125.

Recorded execution summary:

| Metric | Value |
|---|---:|
| Total executions | 125 |
| Successful executions | 125 |
| Failed executions | 0 |
| Timeouts | 0 |

### Results for n = 1024

| Implementation | Median time (s) | Speedup | Efficiency |
|---|---:|---:|---:|
| Sequential | 1.138915 | 1.000 | N/A |
| Parallel 1 thread | 1.321354 | 0.862 | 86.2% |
| Parallel 2 threads | 0.733625 | 1.552 | 77.6% |
| Parallel 4 threads | 0.523973 | 2.174 | 54.3% |
| Parallel 8 threads | 0.420361 | 2.709 | 33.9% |

The 8-thread configuration accomplished the bottom
located median runtime at n = 1024.

However, this configuration become oversubscribed, and the
measurements show sizable variability.

Therefore, the outcomes do now not set up that 8 threads
would be most efficient on some other device or below exceptional
resource constraints.

---

## 11. Generating Figures

Run:

```bash
python3 benchmarks/plot_results.py
```

The following figures are generated:

### Execution Time

`figures/execution_time.png`

Shows median execution time against matrix size.

### Speedup

`figures/speedup.png`

Shows speedup relative to the sequential baseline.

### Parallel Efficiency

`figures/efficiency.png`

Shows speedup divided by the number of threads.

### Memory Usage

`figures/memory_usage.png`

Shows median peak process RSS for each configuration.

---

## 12. Generating the PDF Report

Run:

```bash
python3 report/generate_report.py \
    --author "STUDENT NAME"
```

The script generates:

report/Assignment03_Report.pdf

A complete academic report can also be maintained
separately in Overleaf using LaTeX.

---

## 13. Discussion

The consequences indicate that parallel execution can reduce
matrix multiplication runtime.

For n = 1024, the observed median runtime reduced from
1.138915 seconds sequentially to 0.420361 seconds with
8 OpenMP threads.

This corresponds to a speedup of about 2.Seventy one.

However, efficiency decreases because the number of threads
increases, demonstrating that the observed acceleration
isn't always proportional to the range of threads.

The parallel implementation with one thread become slower
than the sequential baseline for n = 1024.

This is consistent with possible OpenMP overhead, despite the fact that
the determined distinction additionally reflects dimension variability.

The effects should be interpreted with caution due to the fact the
test become performed in a virtualised surroundings with
constrained CPU resources and with out fixed processor affinity.

---

## 14. Limitations

The main limitations are:

1. Only five repetitions were collected per configuration.

2. Several configurations showed substantial timing
   variability.

3. The eight-thread configuration exceeded the visible
   logical processor count.

4. Peak process RSS includes allocation and warm-up memory.

5. CPU affinity was not fixed.

6. SIMD vectorisation was not investigated.

7. The largest tested matrix was 1024 x 1024.

The conclusions are restricted to the recorded
implementation, hardware and experimental conditions.

---

## 15. Conclusions

Shared-memory parallel matrix multiplication can reduce
execution time relative to an equal sequential
implementation.

For the most important examined matrix, the bottom located median
runtime become obtained with eight OpenMP threads.

Nevertheless, parallel efficiency reduced as thread
depend improved, and the consequences exhibited great
variability.

The experiment demonstrates the importance of comparing
each speedup and efficiency instead of assuming that
additional threads always produce proportional gains.

Further work need to repeat the measurements on committed
hardware, control CPU affinity and investigate larger
matrix sizes and elective SIMD vectorisation.

---

## 16. References

[1] OpenMP Architecture Review Board.
OpenMP API Specification.
https://www.openmp.org/specifications/

[2] Linux man-pages project.
getrusage(2).
https://man7.org/linux/man-pages/man2/getrusage.2.html

[3] Linux man-pages project.
clock_gettime(2).
https://man7.org/linux/man-pages/man2/clock_gettime.2.html

---

## 17. AI Assistance Disclosure

AI assisted with source-code drafting.
