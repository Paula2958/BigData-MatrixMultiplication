import subprocess
from run_benchmarks import prepare, command, run


def expected_checksum(n):
    a = [[((i*n+j) % 10)+1 for j in range(n)] for i in range(n)]
    b = [[((i*n+j+3) % 10)+1 for j in range(n)] for i in range(n)]
    return sum(sum(a[i][k] * b[k][j] for k in range(n)) for i in range(n) for j in range(n))


def main():
    build = prepare()
    for n in (1, 2, 3, 5, 10, 50):
        expected = expected_checksum(n)
        for lang in ('Python', 'Java', 'C'):
            _, _, actual = run(command(lang, n, build), 20)
            assert actual == expected, (lang, n, actual, expected)

    print('PASS: all 18 cross-language checksum checks')


if __name__ == '__main__':
    main()
