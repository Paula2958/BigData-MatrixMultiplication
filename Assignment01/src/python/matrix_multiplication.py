
import sys
import time


def matrix(n, offset):
    return [[((i * n + j + offset) % 10) + 1 for j in range(n)] for i in range(n)]


def multiply(a, b, c):
    n = len(a)
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += a[i][k] * b[k][j]
            c[i][j] = total


def main():
    n = int(sys.argv[1])
    a, b = matrix(n, 0), matrix(n, 3)
    c = [[0] * n for _ in range(n)]
    start = time.perf_counter_ns()
    multiply(a, b, c)
    seconds = (time.perf_counter_ns() - start) / 1e9
    checksum = sum(map(sum, c))
    print(f"RESULT,{n},{seconds:.9f},{checksum}")


if __name__ == '__main__':
    main()
