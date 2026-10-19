def make_matrix(n, offset=0):
    return [
        [((i * n + j + offset) % 10) + 1 for j in range(n)]
        for i in range(n)
    ]


def multiply_rows(rows, b):
    n = len(b)
    result = []

    for row in rows:
        output_row = [0] * n

        for k in range(n):
            value = row[k]
            for j in range(n):
                output_row[j] += value * b[k][j]

        result.append(output_row)

    return result


def checksum(matrix):
    return sum(sum(row) for row in matrix)


def split_rows(a, workers):
    n = len(a)
    return [
        a[i * n // workers:(i + 1) * n // workers]
        for i in range(workers)
    ]
