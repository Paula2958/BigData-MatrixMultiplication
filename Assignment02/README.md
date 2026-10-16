
# Big Data — Individual Assignment 2 (Java)

This assignment compares 3 sequential dense matrix multiplication methods
and a student-written sparse CSR method. Java 21 is used during.

## Methods

- `basic`: traditional i-j-k triple loop (Assignment 1 baseline).
- `reordered`: i-k-j loop order.
- `blocked`: three-level blocking off, with 32-element tiles.
- `csr`: compressed sparse row multiplication.

## Requirements

- Java JDK 21
- Python three
- GNU time (Linux)
- Matplotlib

## Run on Linux

```bash
mkdir -p construct
javac -d build src/MatrixStudy.Java
java -cp build MatrixStudy take a look at
python3 scripts/run_benchmarks.Py
python3 scripts/analyze_results.Py
python3 -m pip deploy -r necessities.Txt
python3 scripts/generate_figures.Py
```

The benchmark uses `/usr/bin/time` (GNU time).

It runs five separate JVM techniques in keeping with configuration,
with  excluded warm-usain each method.

Each JVM uses `-Xms64m -Xmx1024m`.

Each measured kernel includes its output allocation,
however now not input era or checksum.

CSR conversion is measured one after the other and excluded
from kernel time.

Peak RSS measures the complete JVM, now not simply the arrays.

Each uncooked CSV row has an unbiased RSS size.

## Results

The test uses:

- Matrix sizes: one hundred, 2 hundred, 400
- Sparsity: 50%, ninety%, ninety nine%
- Repetitions: 5
- Block length: 32

Raw measurements are in `consequences/raw_results.Csv`.

Summary statistics are in `consequences/summary_results.Csv`.

Environment data is in `effects/surroundings.Txt`.

Graphs are saved in `figures/`.

## Correctness

The source includes exams evaluating every approach
in opposition to the fundamental algorithm.

The exams use specific matrix equality.

The evaluation script additionally exams output checksums
and nonzero counts.

## Reproducibility

Results depend on the hardware, JVM compilation,
system load and experimental configuration.

## AI Disclosure

ChatGPT assisted with code drafting.

The pupil is responsible for understanding the code,
verifying effects and protecting the conclusions.
