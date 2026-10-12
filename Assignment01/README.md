# Matrix Multiplication Performance: Python, Java and C

**Big Data — Individual Assignment 1**  
Universidad de Las Palmas de Gran Canaria  
Degree in Data Science and Engineering  
Academic year 2026–2027

## Overview

This challenge investigates how programming-language preference affects the execution time, memory consumption and scalability of classical dense matrix multiplication.

The equal simple algorithm is carried out in Python, Java and C, the use of three nested loops and no optimized matrix multiplication libraries.

## Research question

How does the choice of programming language have an effect on execution time and memory usage as the size of a matrix multiplication problem increases?

## Hypothesis

All implementations have theoretical time complexity O(n³), but their practical performance will vary because of language execution models, compilation and memory representation.

## Project structure

- `src/python/` — Python implementation
- `src/java/` — Java implementation
- `src/c/` — C implementation
- `scripts/test_correctness.py` — correctness validation
- `scripts/run_benchmarks.py` — runtime and memory measurements
- `scripts/analyze_results.py` — statistical analysis
- `scripts/generate_figures.py` — visualization
- `results/` — raw measurements, summaries and environment
- `figures/` — generated graphs

## Algorithm

All three implementations use the classical i-j-k loop order:

```text
for i in range(n):
    for j in range(n):
        total = 0
        for k in range(n):
            total += A[i][k] * B[k][j]
        C[i][j] = total
```

The time complexity is O(n³), while storage for the three matrices grows as O(n²).

## Input generation

The input matrices are square and contain deterministic integer values from 1 to 10.

A[i][j] = ((i*n + j) % 10) + 1

B[i][j] = ((i*n + j + 3) % 10) + 1

No random seed is needed because no random generator is used.

The same logical inputs are used in every language.

Python uses lists of built-in integers, Java uses long[][], and C uses contiguous int64_t arrays.

## Experimental design

Matrix dimensions: 50, a hundred, 2 hundred, three hundred.

Five measured repetitions are accomplished for each language and size.

One impartial warm-up invocation is carried out before the measured repetitions.

Execution time covers handiest the multiplication operation, such as creation of the output matrix in Python and Java.

Input generation and checksum calculation are excluded from the timed location.

The C output matrix is allocated earlier than timing. Therefore, output allocation isn't dealt with identically throughout languages; that is a hassle of the assessment.

Memory is measured using GNU time's maximum resident set size (Peak RSS), which incorporates the entire manner and its runtime.

Each measurement uses a fresh technique. Java regular-country JIT performance isn't isolated.

C is compiled the usage of Clang with -O2 -std=c11.

## Experimental limits

- Timeout: 30 seconds in step with process
- Memory price range: 1024 MiB Peak RSS in step with method
- Repetitions: 5
- Correctness ought to be established before benchmarking

## Requirements

A Linux environment with:

- Python 3
- Java JDK
- Clang
- GNU /usr/bin/time
- Matplotlib

Install the Python plotting dependency:

```bash
python3 -m pip install -r requirements.txt
```

## Reproducing the experiment

All commands must be run from the repository root.

### 1. Validate correctness

```bash
python3 scripts/test_correctness.py
```

### 2. Run benchmarks

```bash
python3 scripts/run_benchmarks.py
```

This produces:

- results/raw_results.csv
- results/environment.txt

### 3. Analyze measurements

```bash
python3 scripts/analyze_results.py
```

This produces:

- results/summary_results.csv

### 4. Generate figures

```bash
python3 scripts/generate_figures.py
```

This produces:

- figures/execution_time.png
- figures/execution_time_loglog.png
- figures/memory_usage.png
- figures/normalized_scaling.png

## Statistical methodology

The median is used as the significant measurement.

The interquartile range is calculated as Q3 - Q1.

Q1 and Q3 follow the median-of-halves conference.

Raw measurements are retained to make the analysis reproducible.

## Figures

The four figures examine:

1. Median execution time
2. Execution time using logarithmic axes
3. Peak RSS reminiscence utilization
four. Normalized runtime against theoretical cubic growth

All figures are generated from the experimental CSV records.

## Interpretation and limitations

The test compares specific implementations beneath precise execution conditions.

The implementations have equal mathematical operations however specific memory representations and runtime overhead.

Peak RSS isn't always equivalent to the theoretical garage requirement of the matrices.

Short runtimes, technique startup effects, compiler optimizations, caching and JVM conduct may additionally have an impact on measured results.

The execution order is fixed instead of randomized.

Consequently, the results ought to now not be interpreted as a prevalent rating of programming languages.

## Scientific report

The scientific report is developed after the implementations and results have been established.

It provides the studies question, theoretical history, methodology, experimental consequences, discussion, barriers and conclusions.

## AI disclosure

Generative AI assisted with making plans and code drafting.

The scholar is answerable for the implementations, executing the experiments, checking correctness, validating the outcomes and decoding the findings.
