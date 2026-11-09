
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <sys/resource.h>
#include <omp.h>

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

static uint64_t rng(uint64_t *s) {
    *s ^= *s >> 12;
    *s ^= *s << 25;
    *s ^= *s >> 27;
    return *s * UINT64_C(2685821657736338717);
}

static void fill(double *a, size_t count, uint64_t seed) {
    if (!seed) seed = 1;

    for (size_t i = 0; i < count; i++) {
        a[i] = (double)(rng(&seed) % 1001) / 1000.0;
    }
}

static void sequential(
    const double *a,
    const double *b,
    double *c,
    int n
) {
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            double v = a[(size_t)i * n + k];

            for (int j = 0; j < n; j++) {
                c[(size_t)i * n + j] +=
                    v * b[(size_t)k * n + j];
            }
        }
    }
}

static void parallel(
    const double *a,
    const double *b,
    double *c,
    int n
) {
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            double v = a[(size_t)i * n + k];

            for (int j = 0; j < n; j++) {
                c[(size_t)i * n + j] +=
                    v * b[(size_t)k * n + j];
            }
        }
    }
}

static int test(void) {
    double a[] = {1, 2, 3, 4};
    double b[] = {5, 6, 7, 8};
    double want[] = {19, 22, 43, 50};
    double c[4] = {0};

    sequential(a, b, c, 2);

    for (int i = 0; i < 4; i++) {
        if (fabs(c[i] - want[i]) > 1e-12)
            return 1;
    }

    memset(c, 0, sizeof(c));
    omp_set_num_threads(2);
    parallel(a, b, c, 2);

    for (int i = 0; i < 4; i++) {
        if (fabs(c[i] - want[i]) > 1e-12)
            return 2;
    }

    double id[] = {1, 0, 0, 1};
    double zero[] = {0, 0, 0, 0};

    memset(c, 0, sizeof(c));
    parallel(a, id, c, 2);

    for (int i = 0; i < 4; i++) {
        if (fabs(c[i] - a[i]) > 1e-12)
            return 3;
    }

    memset(c, 0, sizeof(c));
    parallel(a, zero, c, 2);

    for (int i = 0; i < 4; i++) {
        if (c[i] != 0)
            return 4;
    }

    puts("PASS: known product, identity, zero, "
         "sequential and parallel");

    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--test") == 0)
        return test();

    if (argc != 6) {
        fprintf(stderr,
            "Usage: %s sequential|parallel "
            "N THREADS SEED REPETITION\n", argv[0]);
        return 2;
    }

    int par = strcmp(argv[1], "parallel") == 0;

    if (!par && strcmp(argv[1], "sequential") != 0)
        return 2;

    int n = atoi(argv[2]);
    int p = atoi(argv[3]);
    int rep = atoi(argv[5]);
    uint64_t seed = strtoull(argv[4], NULL, 10);

    if (n < 1 || n > 12000 || p < 1 ||
        rep < 1 || !seed)
        return 2;

    if ((size_t)n > SIZE_MAX / (size_t)n / sizeof(double))
        return 2;

    size_t count = (size_t)n * n;

    double *a = malloc(count * sizeof(double));
    double *b = malloc(count * sizeof(double));
    double *c = calloc(count, sizeof(double));

    if (!a || !b || !c) {
        fprintf(stderr, "Allocation failure\n");
        free(a);
        free(b);
        free(c);
        return 3;
    }

    fill(a, count, seed);
    fill(b, count, seed + 17);

    omp_set_dynamic(0);
    omp_set_num_threads(p);

    // Untimed warm-up
    if (par)
        parallel(a, b, c, n);
    else
        sequential(a, b, c, n);

    memset(c, 0, count * sizeof(double));

    // Timed multiplication kernel
    double t0 = now();

    if (par)
        parallel(a, b, c, n);
    else
        sequential(a, b, c, n);

    double seconds = now() - t0;

    double checksum = 0;

    for (size_t i = 0; i < count; i++) {
        checksum += c[i] * (1.0 + (i % 97) * 0.001);
    }

    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);

    printf("%s,%d,%d,%llu,%d,%.9f,%ld,%.17g\n",
        par ? "parallel" : "sequential",
        n,
        par ? p : 1,
        (unsigned long long)seed,
        rep,
        seconds,
        usage.ru_maxrss,
        checksum
    );

    free(a);
    free(b);
    free(c);

    return 0;
}
