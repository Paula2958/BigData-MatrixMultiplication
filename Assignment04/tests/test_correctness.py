import unittest

from src.common import make_matrix, multiply_rows, checksum
from src.parallel import run as parallel_run
from src.sequential import run as sequential_run


class TestMatrixMultiplication(unittest.TestCase):

    def test_known_result(self):
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        expected = [[19, 22], [43, 50]]
        self.assertEqual(multiply_rows(a, b), expected)

    def test_identity(self):
        a = [[2, 4], [6, 8]]
        identity = [[1, 0], [0, 1]]
        self.assertEqual(multiply_rows(a, identity), a)

    def test_zero(self):
        a = [[1, 2], [3, 4]]
        zero = [[0, 0], [0, 0]]
        self.assertEqual(multiply_rows(a, zero), zero)

    def test_parallel_matches_sequential(self):
        for n in [1, 2, 5, 10, 20]:
            _, sequential_hash = sequential_run(n)
            for workers in [1, 2, 4]:
                _, parallel_hash = parallel_run(n, workers)
                self.assertEqual(sequential_hash, parallel_hash)


if __name__ == "__main__":
    unittest.main()
