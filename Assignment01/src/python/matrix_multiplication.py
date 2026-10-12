import sys
import time


def generate_matrix(n, offset):
    """Generate a deterministic n x n matrix."""
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            value = ((i * n + j + offset) % 10) + 1
            row.append(value)
        matrix.append(row)

    return matrix


def multiply_matrices(a, b):
    """Multiply two square matrices using three nested loops."""
    n = len(a)
    result = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            total = 0

            for k in range(n):
                total += a[i][k] * b[k][j]

            result[i][j] = total

    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python matrix_multiplication.py <size>")
        sys.exit(1)

    n = int(sys.argv[1])

    if n <= 0:
        raise ValueError("Matrix size must be positive.")

    a = generate_matrix(n, 0)
    b = generate_matrix(n, 3)

    start = time.perf_counter_ns()
    result = multiply_matrices(a, b)
    end = time.perf_counter_ns()

    elapsed_seconds = (end - start) / 1_000_000_000
    checksum = sum(sum(row) for row in result)

    print(f"RESULT,{n},{elapsed_seconds:.9f},{checksum}")


if __name__ == "__main__":
    main()
