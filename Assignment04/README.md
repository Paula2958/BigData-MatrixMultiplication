
# Big Data — Individual Assignment 4

## Distributed Matrix Multiplication

Universidad de Las Palmas de Gran Canaria  
Degree in Data Science and Engineering  
Academic year: 2026–2027

## Objective

Investigate how increasing the quantity of strategies
influences matrix multiplication overall performance.

Three methods are in comparison:

1. Sequential matrix multiplication.
2. Shared-reminiscence parallel multiplication.
Three. Distributed multiplication using MPI.

## Implementation

Language: Python 3

Distributed framework: mpi4py (MPI)

All techniques use deterministic integer matrices and
the same row-based multiplication kernel.

MPI distributes rows of matrix A and proclaims
matrix B to the participating strategies.


## Dependencies

- Python 3
- MPI implementation (Open MPI or MPICH)
- mpi4py
- matplotlib

On macOS with Homebrew:

```bash
brew install open-mpi
python3 -m pip install -r requirements.txt
```

## Correctness tests

```bash
python3 -m unittest discover -s tests -v
```

## Run each implementation

Sequential:

```bash
python3 -m src.sequential 100
```

Parallel with two processes:

```bash
python3 -m src.parallel 100 2
```

Distributed with two MPI processes:

```bash
mpiexec -n 2 python3 -m src.distributed 100
```

## Run benchmarks

```bash
python3 scripts/run_benchmarks.py \
  --methods sequential parallel distributed \
  --sizes 100 200 400 \
  --workers 1 2 4 \
  --repetitions 5 \
  --warmups 1
```

The runner records raw results in:

results/raw_results.csv

## Analyse results

```bash
python3 scripts/analyze_results.py
python3 scripts/generate_figures.py
python3 scripts/generate_latex_table.py
```

The scripts produce:

- results/summary_results.csv
- figures/execution_time.png
- figures/speedup.png
- figures/efficiency.png
- figures/mpi_memory.png (when MPI data exists)
- docs/results_table.tex

## Experimental protocol

The benchmark measures execution after the Python
interpreter or MPI methods have commenced.

Input technology, multiplication, statistics distribution
and end result meeting are covered as relevant.

Process startup is excluded.

Five unbiased measured executions are gathered
in line with configuration, after one heat-up execution.

Median and interquartile variety are pronounced.

## Memory measurements

MPI procedures report their own height RSS.

These values are man or woman excessive-water marks,
now not simultaneous overall cluster reminiscence utilization.

For Python multiprocessing, the modern runner
does no longer measure overall peak employee memory.

## Limitations

MPI execution on one bodily pc isn't
equivalent to execution on a couple of machines.

The direction handout requires trainer permission
for a nearby-most effective distributed test.

The experiment uses Python item communique
in preference to optimised numerical MPI buffers.

## AI disclosure

AI assisted with code drafting, benchmarking
scripts and the structure.

The pupil has validated all effects and understand
the submitted implementations.
