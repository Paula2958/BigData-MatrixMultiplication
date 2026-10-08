
# Big Data — Matrix Multiplication Benchmark

**Universidad de Las Palmas de Gran Canaria**  
**Degree:** Data Science and Engineering  
**Course:** Big Data (2026–2027)  
**Student:** Paula Hernández Varela

## Project overview

This repository contains an experimental comparison of the classical dense matrix multiplication algorithm implemented in Python, Java and C.

The experiment investigates execution time, memory consumption and scalability as matrix size increases.

The implementations use the same basic triple-loop algorithm, without optimized matrix multiplication libraries.

## Assignment 1

The complete project is available in:

[Assignment01](Assignment01/)

The folder contains:

- Python, Java and C implementations
- Correctness validation
- Automated execution-time benchmarks
- Peak RSS memory measurements
- Raw experimental CSV files
- Statistical analysis
- Four figures
- Reproducibility instructions

## Main findings

The classical algorithm has O(n³) time complexity and O(n²) matrix storage requirements.

In the recorded experimental environment, C achieved the lowest median execution times, Java was intermediate, and pure Python required the longest execution times.

These results describe the tested implementations and are not a universal ranking of programming languages.

## Reproducibility

See the [Assignment 1 README](Assignment01/README.md) for instructions to compile, test, benchmark and analyze the implementations.

## AI disclosure

Generative AI tools assisted with code development, experimental planning and documentation. The student is responsible for validating the implementations, measurements and conclusions.
