#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static double elapsed(const struct timespec *a, const struct timespec *b) {
    return (double)(b->tv_sec - a->tv_sec) + (b->tv_nsec - a->tv_nsec) / 1e9;
}

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    int n = atoi(argv[1]);
    if (n < 1 || n > 10000) return 2;

    size_t cells = (size_t)n * n;
    int64_t *a = malloc(cells * sizeof(*a));
    int64_t *b = malloc(cells * sizeof(*b));
    int64_t *c = calloc(cells, sizeof(*c));
    if (!a || !b || !c) return 3;

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            size_t p = (size_t)i * n + j;
            a[p] = (int64_t)((p % 10) + 1);
            b[p] = (int64_t)(((p + 3) % 10) + 1);
        }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            int64_t total = 0;
            for (int k = 0; k < n; k++)
                total += a[(size_t)i * n + k] * b[(size_t)k * n + j];
            c[(size_t)i * n + j] = total;
        }

    clock_gettime(CLOCK_MONOTONIC, &end);

    int64_t checksum = 0;
    for (size_t p = 0; p < cells; p++) checksum += c[p];

    printf("RESULT,%d,%.9f,%lld\n", n, elapsed(&start, &end), (long long)checksum);

    free(a);
    free(b);
    free(c);
    return 0;
}
