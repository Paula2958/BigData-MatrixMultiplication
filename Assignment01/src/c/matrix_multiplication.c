#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>


double elapsed_seconds(struct timespec start,
                       struct timespec end) {
    double seconds = (double)(end.tv_sec - start.tv_sec);
    double nanoseconds = (double)(end.tv_nsec - start.tv_nsec);

    return seconds + nanoseconds / 1e9;
}


void generate_matrix(int64_t *matrix, int n, int offset) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            size_t index = (size_t)i * n + j;
            matrix[index] = (int64_t)((index + offset) % 10) + 1;
        }
    }
}


void multiply_matrices(const int64_t *a,
                       const int64_t *b,
                       int64_t *result,
                       int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int64_t total = 0;

            for (int k = 0; k < n; k++) {
                total += a[(size_t)i * n + k]
                       * b[(size_t)k * n + j];
            }

            result[(size_t)i * n + j] = total;
        }
    }
}


int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: ./matrix_c <size>\n");
        return 1;
    }

    int n = atoi(argv[1]);

    if (n <= 0 || n > 10000) {
        fprintf(stderr, "Invalid matrix size.\n");
        return 1;
    }

    size_t elements = (size_t)n * n;

    int64_t *a = malloc(elements * sizeof(int64_t));
    int64_t *b = malloc(elements * sizeof(int64_t));
    int64_t *result = calloc(elements, sizeof(int64_t));

    if (a == NULL || b == NULL || result == NULL) {
        fprintf(stderr, "Memory allocation failed.\n");
        free(a);
        free(b);
        free(result);
        return 1;
    }

    generate_matrix(a, n, 0);
    generate_matrix(b, n, 3);

    struct timespec start, end;

    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) {
        fprintf(stderr, "Timer failed.\n");
        free(a);
        free(b);
        free(result);
        return 1;
    }

    multiply_matrices(a, b, result, n);

    if (clock_gettime(CLOCK_MONOTONIC, &end) != 0) {
        fprintf(stderr, "Timer failed.\n");
        free(a);
        free(b);
        free(result);
        return 1;
    }

    double seconds = elapsed_seconds(start, end);

    int64_t checksum = 0;

    for (size_t i = 0; i < elements; i++) {
        checksum += result[i];
    }

    printf(
        "RESULT,%d,%.9f,%lld\n",
        n,
        seconds,
        (long long)checksum
    );

    free(a);
    free(b);
    free(result);

    return 0;
}
