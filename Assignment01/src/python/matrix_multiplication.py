import sys
import time


def generate_matrices(n):
    """
    Generate two deterministic n x n matrices.

    Values are restricted to the range 1..10 so that all
    implementations operate on the same logical input data.
    """
    A = [
        [((i * n + j) % 10) + 1 for j in range(n)]
        for i in range(n)
    ]

    B = [
        [((i * n + j + 3) % 10) + 1 for j in range(n)]
        for i in range(n)
    ]

    return A, B


def create_output_matrix(n):
    """Allocate the output matrix outside the timed region."""
    return [[0 for _ in range(n)] for _ in range(n)]


def multiply(A, B, C):
    """
    Classical matrix multiplication.

    Loop order: i-j-k
    Arithmetic complexity: O(n^3)
    """
    n = len(A)

    for i in range(n):
        for j in range(n):
            total = 0

            for k in range(n):
                total += A[i][k] * B[k][j]

            C[i][j] = total


def run_correctness_tests():
    """Run correctness tests before benchmarking."""

    # --------------------------------------------------
    # Test 1: known result
    # --------------------------------------------------

    A = [
        [1, 2],
        [3, 4]
    ]

    B = [
        [5, 6],
        [7, 8]
    ]

    expected = [
        [19, 22],
        [43, 50]
    ]

    C = create_output_matrix(2)
    multiply(A, B, C)

    assert C == expected

    # --------------------------------------------------
    # Test 2: identity matrix
    # --------------------------------------------------

    A = [
        [2, 4],
        [6, 8]
    ]

    identity = [
        [1, 0],
        [0, 1]
    ]

    C = create_output_matrix(2)
    multiply(A, identity, C)

    assert C == A

    # --------------------------------------------------
    # Test 3: zero matrix
    # --------------------------------------------------

    zero = [
        [0, 0],
        [0, 0]
    ]

    C = create_output_matrix(2)
    multiply(A, zero, C)

    assert C == zero

    print("Correctness tests: PASSED")


def benchmark(n):
    A, B = generate_matrices(n)

    # Output allocation is also outside the timed region.
    C = create_output_matrix(n)

    # --------------------------------------------------
    # Timed region begins
    # --------------------------------------------------

    start = time.perf_counter()

    multiply(A, B, C)

    end = time.perf_counter()

    # --------------------------------------------------
    # Timed region ends
    # --------------------------------------------------

    elapsed = end - start

    checksum = sum(C[0])

    print(
        f"language=python,"
        f"n={n},"
        f"time_seconds={elapsed:.9f},"
        f"checksum={checksum}"
    )


def main():
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python3 matrix_multiplication.py test\n"
            "  python3 matrix_multiplication.py <matrix_size>"
        )
        sys.exit(1)

    if sys.argv[1] == "test":
        run_correctness_tests()
        return

    try:
        n = int(sys.argv[1])

        if n <= 0:
            raise ValueError

    except ValueError:
        print("Matrix size must be a positive integer.")
        sys.exit(1)

    benchmark(n)


if __name__ == "__main__":
    main()
