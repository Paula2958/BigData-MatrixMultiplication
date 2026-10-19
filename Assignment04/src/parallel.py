import argparse
import time
from multiprocessing import Pool

from src.common import make_matrix, multiply_rows, checksum, split_rows


def worker(arguments):
    rows, b = arguments
    return multiply_rows(rows, b)


def run(n, workers):
    start = time.perf_counter()

    a = make_matrix(n)
    b = make_matrix(n, 3)
    chunks = split_rows(a, workers)

    with Pool(processes=workers) as pool:
        parts = pool.map(worker, [(chunk, b) for chunk in chunks])

    c = [row for part in parts for row in part]
    elapsed = time.perf_counter() - start

    return elapsed, checksum(c)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("workers", type=int)
    args = parser.parse_args()

    elapsed, result = run(args.n, args.workers)

    print("Method: parallel")
    print(f"Size: {args.n}")
    print(f"Workers: {args.workers}")
    print(f"Time: {elapsed:.6f} seconds")
    print(f"Checksum: {result}")
