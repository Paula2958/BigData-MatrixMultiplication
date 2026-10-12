import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/python"))

from matrix_multiplication import multiply_matrices
from run_benchmarks import prepare, command, run_program


def reference_checksum(n):
    """Independent reference using a different loop order."""
    a = [[(i * n + j) % 10 + 1 for j in range(n)]
         for i in range(n)]
    b = [[(i * n + j + 3) % 10 + 1 for j in range(n)]
         for i in range(n)]

    total = 0
    for i in range(n):
        for k in range(n):
            for j in range(n):
                total += a[i][k] * b[k][j]

    return total


def test_known_matrices():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    expected = [[19, 22], [43, 50]]

    assert multiply_matrices(a, b) == expected

    identity = [[1, 0], [0, 1]]
    zero = [[0, 0], [0, 0]]

    assert multiply_matrices(a, identity) == a
    assert multiply_matrices(a, zero) == zero

    print("PASS: known matrix, identity and zero tests")


def test_languages():
    build = prepare()
    sizes = [1, 2, 3, 5, 10, 50]

    for n in sizes:
        expected = reference_checksum(n)

        for language in ("python", "java", "c"):
            size, seconds, checksum = run_program(
                command(language, n, build),
                timeout=30
            )

            assert size == n
            assert seconds >= 0
            assert checksum == expected, (
                f"Incorrect result: {language}, n={n}"
            )

    print("PASS: 18 cross-language checksum tests")


if __name__ == "__main__":
    test_known_matrices()
    test_languages()
    print("All correctness tests passed.")
