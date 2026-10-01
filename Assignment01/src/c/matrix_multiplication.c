#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>


static int64_t *allocate_matrix(int n)
{
    size_t elements = (size_t)n * (size_t)n;

    return calloc(elements, sizeof(int64_t));
}


static void generate_matrices(
    int64_t *A,
    int64_t *B,
    int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            size_t index =
                (size_t)i * (size_t)n + (size_t)j;

            int64_t logical_index =
                (int64_t)i * (int64_t)n
                + (int64_t)j;

            A[index] =
                (logical_index % 10) + 1;

            B[index] =
                ((logical_index + 3) % 10) + 1;
        }
    }
}


static void multiply(
    const int64_t *A,
    const int64_t *B,
    int64_t *C,
    int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            int64_t total = 0;

            for (int k = 0; k < n; k++)
            {
                total +=
                    A[(size_t)i * n + k]
                    *
                    B[(size_t)k * n + j];
            }

            C[(size_t)i * n + j] = total;
        }
    }
}


static double elapsed_seconds(
    struct timespec start,
    struct timespec end)
{
    return
        (double)(end.tv_sec - start.tv_sec)
        +
        (double)(end.tv_nsec - start.tv_nsec)
        / 1000000000.0;
}


static int matrices_equal(
    const int64_t *A,
    const int64_t *B,
    int n)
{
    size_t elements =
        (size_t)n * (size_t)n;

    for (size_t i = 0; i < elements; i++)
    {
        if (A[i] != B[i])
        {
            return 0;
        }
    }

    return 1;
}


static void run_correctness_tests(void)
{
    const int n = 2;


    /* Test 1: known result */

    int64_t A1[] = {
        1, 2,
        3, 4
    };

    int64_t B1[] = {
        5, 6,
        7, 8
    };

    int64_t expected[] = {
        19, 22,
        43, 50
    };

    int64_t C1[4] = {0};

    multiply(A1, B1, C1, n);

    if (!matrices_equal(C1, expected, n))
    {
        fprintf(
            stderr,
            "Known-result test failed.\n"
        );

        exit(EXIT_FAILURE);
    }


    /* Test 2: identity matrix */

    int64_t A2[] = {
        2, 4,
        6, 8
    };

    int64_t identity[] = {
        1, 0,
        0, 1
    };

    int64_t C2[4] = {0};

    multiply(A2, identity, C2, n);

    if (!matrices_equal(C2, A2, n))
    {
        fprintf(
            stderr,
            "Identity test failed.\n"
        );

        exit(EXIT_FAILURE);
    }


    /* Test 3: zero matrix */

    int64_t zero[] = {
        0, 0,
        0, 0
    };

    int64_t C3[4] = {0};

    multiply(A2, zero, C3, n);

    if (!matrices_equal(C3, zero, n))
    {
        fprintf(
            stderr,
            "Zero-matrix test failed.\n"
        );

        exit(EXIT_FAILURE);
    }


    printf("Correctness tests: PASSED\n");
}


static void benchmark(int n)
{
    int64_t *A = allocate_matrix(n);
    int64_t *B = allocate_matrix(n);
    int64_t *C = allocate_matrix(n);


    if (A == NULL || B == NULL || C == NULL)
    {
        fprintf(
            stderr,
            "Memory allocation failed.\n"
        );

        free(A);
        free(B);
        free(C);

        exit(EXIT_FAILURE);
    }


    

    generate_matrices(A, B, n);


    struct timespec start;
    struct timespec end;


    /* ---------------------------------------------
       Timed region begins
       --------------------------------------------- */

    clock_gettime(CLOCK_MONOTONIC, &start);

    multiply(A, B, C, n);

    clock_gettime(CLOCK_MONOTONIC, &end);

    /* ---------------------------------------------
       Timed region ends
       --------------------------------------------- */


    double elapsed =
        elapsed_seconds(start, end);


    /* Consume result after timing. */

    int64_t checksum = 0;

    for (int j = 0; j < n; j++)
    {
        checksum += C[j];
    }


    printf(
        "language=c,n=%d,"
        "time_seconds=%.9f,"
        "checksum=%lld\n",
        n,
        elapsed,
        (long long)checksum
    );


    free(A);
    free(B);
    free(C);
}


int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(
            stderr,
            "Usage:\n"
            "  %s test\n"
            "  %s <matrix_size>\n",
            argv[0],
            argv[0]
        );

        return EXIT_FAILURE;
    }


    if (strcmp(argv[1], "test") == 0)
    {
        run_correctness_tests();

        return EXIT_SUCCESS;
    }


    char *endptr;

    long value =
        strtol(argv[1], &endptr, 10);


    if (
        *argv[1] == '\0'
        || *endptr != '\0'
        || value <= 0
    )
    {
        fprintf(
            stderr,
            "Matrix size must be a positive integer.\n"
        );

        return EXIT_FAILURE;
    }


    benchmark((int)value);

    return EXIT_SUCCESS;
}
