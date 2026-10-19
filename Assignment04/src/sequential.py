import argparse
import time

from src.common import make_matrix, multiply_rows, checksum


def run(n):
    start = time.perf_counter()

    a = make_matrix(n)
    b = make_matrix(n, 3)
    c = multiply_rows(a, b)

    elapsed = time.perf_counter() - start
    return elapsed, checksum(c)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    args = parser.parse_args()

    elapsed, result = run(args.n)

    print(f"Method: sequential")
    print(f"Size: {args.n}")
    print(f"Time: {elapsed:.6f} seconds")
    print(f"Checksum: {result}")
