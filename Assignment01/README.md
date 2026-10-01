# Assignment 1 — Basic Matrix Multiplication in Python, Java, and C

**Course:** Big Data  
**Degree:** BSc in Data Science and Engineering  
**University:** Universidad de Las Palmas de Gran Canaria  
**Academic year:** 2026–2027  

## 1. Overview

This repository contains the source code, experimental scripts, raw measurements, processed results, and figures for Assignment 1 of the Big Data course.

The study compares equivalent implementations of the classical dense matrix multiplication algorithm in:

- Python
- Java
- C

The purpose of the experiment is to investigate how matrix size and programming language affect execution time and memory usage under controlled experimental conditions.

## 2. Research Question

> How does the choice of programming language affect the execution time and memory usage of equivalent basic matrix multiplication implementations as matrix size increases?

The experiment focuses on the tested implementations and execution environment. The results should not be interpreted as a universal comparison of the three programming languages.

## 3. Algorithm

All three implementations use the classical triple-loop matrix multiplication algorithm with the same `i-j-k` loop order:

```text
for i = 0 ... n-1
    for j = 0 ... n-1
        sum = 0
        for k = 0 ... n-1
            sum += A[i][k] * B[k][j]
        C[i][j] = sum
```

For two square matrices of size `n × n`, the algorithm performs cubic arithmetic work:

```text
Time complexity: O(n^3)
Space required for the three matrices: O(n^2)
```

No optimized matrix multiplication libraries such as NumPy, BLAS, or similar alternatives are used for the multiplication kernel.

## 4. Implementations

The same logical algorithm is implemented independently in the three languages.

### Python

File:

```text
src/python/matrix_multiplication.py
```

The implementation uses Python built-in integers and lists of lists.

### Java

File:

```text
src/java/MatrixMultiplication.java
```

The implementation uses `long` values and two-dimensional Java arrays.

### C

File:

```text
src/c/matrix_multiplication.c
```

The implementation uses `int64_t` values and contiguous dynamically allocated matrices.

The C implementation is compiled using:

```bash
clang -O2 -std=c11 matrix_multiplication.c -o matrix_multiplication
```

These representations are logically comparable but are not identical at the physical memory-representation level. This distinction is considered when interpreting the memory results.

## 5. Input Generation

Matrices are generated deterministically so that equivalent logical inputs are used by all three implementations.

For matrix `A`:

```text
A[i][j] = ((i * n + j) % 10) + 1
```

For matrix `B`:

```text
B[i][j] = ((i * n + j + 3) % 10) + 1
```

Therefore, all matrix elements are integers in the range:

```text
1 ... 10
```

No random-number generator is required.

## 6. Correctness Validation

Correctness is checked before benchmarking.

The implementations include tests using:

- a known 2 × 2 multiplication,
- an identity matrix,
- a zero matrix.

For the known test:

```text
A = [[1, 2],
     [3, 4]]

B = [[5, 6],
     [7, 8]]
```

the expected result is:

```text
[[19, 22],
 [43, 50]]
```

During benchmarking, a checksum derived from the result matrix is also used to confirm that the three implementations produce equivalent results for the same matrix size.

## 7. Experimental Protocol

The multiplication kernel is the timed region.

The following operations occur before timing:

- generation of matrices `A` and `B`,
- allocation of output matrix `C`.

The timer therefore measures the matrix multiplication itself rather than input generation.

The result is consumed after execution through a checksum to prevent the computation from being treated as unused.

Each tested configuration contains five measured repetitions.

The raw measurements are preserved in the `results/` directory.

The primary runtime summary statistic is the median. Variability is represented using the first quartile (Q1), third quartile (Q3), and interquartile range:

```text
IQR = Q3 - Q1
```

A per-run execution-time limit is used so that excessively expensive configurations can be reported as timeouts rather than assigned artificial execution times.

## 8. Tested Matrix Sizes

The experimental dataset contains the following square matrix sizes:

```text
50 × 50
100 × 100
200 × 200
300 × 300
```

For each size, the Python, Java, and C implementations are evaluated using the same logical input matrices.

## 9. Memory Measurement

Memory consumption is measured using peak process resident set size (Peak RSS).

Peak RSS represents the maximum amount of resident memory used by the process during execution.

It includes more than the matrix elements themselves. Depending on the language, it can also include:

- interpreter/runtime memory,
- JVM overhead,
- object metadata,
- array metadata,
- allocation overhead.

Consequently, Peak RSS must not be interpreted as the exact storage occupied only by the matrices.

For reference, the theoretical storage of three dense `n × n` matrices containing 8-byte elements is:

```text
3 × n^2 × 8 bytes
```

The theoretical value is included in the processed results as a reference rather than as a replacement for measured process memory.

## 10. Repository Structure

```text
Assignment01/
├── README.md
│
├── src/
│   ├── python/
│   │   └── matrix_multiplication.py
│   ├── java/
│   │   └── MatrixMultiplication.java
│   └── c/
│       └── matrix_multiplication.c
│
├── scripts/
│   ├── run_benchmarks.py
│   ├── run_memory_benchmarks.py
│   ├── analyze_results.py
│   └── generate_figures.py
│
├── results/
│   ├── environment.txt
│   ├── raw_results.csv
│   ├── raw_memory_results.csv
│   └── summary_results.csv
│
└── figures/
    ├── execution_time.png
    ├── execution_time_loglog.png
    ├── memory_usage.png
    └── normalized_scaling.png
```

## 11. Reproducing the Experiment

Run all commands from the `Assignment01` directory unless otherwise specified.

### Python correctness test

```bash
python3 src/python/matrix_multiplication.py test
```

### Java compilation

```bash
cd src/java
javac MatrixMultiplication.java
cd ../..
```

### Java correctness test

```bash
java -cp src/java MatrixMultiplication test
```

### C compilation

```bash
clang -O2 -std=c11 src/c/matrix_multiplication.c -o src/c/matrix_multiplication
```

### C correctness test

```bash
./src/c/matrix_multiplication test
```

### Runtime benchmark

The complete runtime benchmark can be executed with:

```bash
python3 scripts/run_benchmarks.py
```

The script creates:

```text
results/raw_results.csv
results/environment.txt
```

### Memory benchmark

Run:

```bash
python3 scripts/run_memory_benchmarks.py
```

This creates:

```text
results/raw_memory_results.csv
```

### Statistical analysis

Run:

```bash
python3 scripts/analyze_results.py
```

This generates:

```text
results/summary_results.csv
```

### Generate figures

Matplotlib is required for figure generation.

Install it, if necessary, with:

```bash
python3 -m pip install matplotlib
```

Then run:

```bash
python3 scripts/generate_figures.py
```

The generated figures are stored in:

```text
figures/
```

## 12. Result Files

### `raw_results.csv`

Contains the individual runtime measurements for every language, matrix size, and repetition.

Main fields include:

```text
language
matrix_size
repetition
time_seconds
checksum
status
```

### `raw_memory_results.csv`

Contains the individual Peak RSS measurements.

### `summary_results.csv`

Contains the processed statistics used for analysis, including:

- number of successful runs,
- timeouts and errors,
- median execution time,
- Q1 and Q3,
- execution-time IQR,
- minimum and maximum time,
- median Peak RSS,
- memory variability,
- theoretical matrix storage,
- theoretical arithmetic-operation counts.

### `environment.txt`

Documents the execution environment and experimental configuration associated with the measurements.

## 13. Figures

The repository contains four automatically generated figures.

### Execution time

`figures/execution_time.png`

Median execution time against matrix size, including variability.

### Log-log execution time

`figures/execution_time_loglog.png`

Log-log representation used to inspect runtime growth as matrix size increases.

### Memory usage

`figures/memory_usage.png`

Median Peak RSS as a function of matrix size.

### Normalized scaling

`figures/normalized_scaling.png`

Comparison between measured runtime growth and the theoretical cubic growth associated with the classical matrix multiplication algorithm.

## 14. Reproducibility Notes

The measurements contained in this repository correspond to the execution environment documented in:

```text
results/environment.txt
```

Execution times and process memory consumption are environment-dependent. Results obtained on another processor, operating system, compiler, Python implementation, or JVM may differ.

Therefore, conclusions drawn from these measurements apply to the tested implementations and documented experimental conditions rather than to Python, Java, or C universally.

## 15. Generative AI Disclosure

Generative AI tools were used to support the planning and development of this assignment, including assistance with experimental design, code drafting and debugging, analysis-script development, documentation, and language revision.

The experimental methodology, source code, measurements, generated figures, interpretation, and references must be reviewed and validated by the student. Generative AI output is not treated as experimental evidence.
