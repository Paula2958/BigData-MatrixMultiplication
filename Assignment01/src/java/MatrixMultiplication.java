public class MatrixMultiplication {

    public static long[][][] generateMatrices(int n) {

        long[][] A = new long[n][n];
        long[][] B = new long[n][n];

        for (int i = 0; i < n; i++) {

            for (int j = 0; j < n; j++) {

                A[i][j] = ((i * n + j) % 10) + 1;

                B[i][j] = ((i * n + j + 3) % 10) + 1;
            }
        }

        return new long[][][]{A, B};
    }


    public static long[][] createOutputMatrix(int n) {

        return new long[n][n];
    }


    public static void multiply(
            long[][] A,
            long[][] B,
            long[][] C) {

        int n = A.length;

        for (int i = 0; i < n; i++) {

            for (int j = 0; j < n; j++) {

                long total = 0;

                for (int k = 0; k < n; k++) {

                    total += A[i][k] * B[k][j];
                }

                C[i][j] = total;
            }
        }
    }


    public static boolean matricesEqual(
            long[][] A,
            long[][] B) {

        if (A.length != B.length) {
            return false;
        }

        for (int i = 0; i < A.length; i++) {

            if (A[i].length != B[i].length) {
                return false;
            }

            for (int j = 0; j < A[i].length; j++) {

                if (A[i][j] != B[i][j]) {
                    return false;
                }
            }
        }

        return true;
    }


    public static void runCorrectnessTests() {

        // Test 1: known result

        long[][] A1 = {
                {1, 2},
                {3, 4}
        };

        long[][] B1 = {
                {5, 6},
                {7, 8}
        };

        long[][] expected = {
                {19, 22},
                {43, 50}
        };

        long[][] C1 = createOutputMatrix(2);

        multiply(A1, B1, C1);

        if (!matricesEqual(C1, expected)) {

            throw new AssertionError(
                    "Known-result test failed."
            );
        }


        
        long[][] A2 = {
                {2, 4},
                {6, 8}
        };

        long[][] identity = {
                {1, 0},
                {0, 1}
        };

        long[][] C2 = createOutputMatrix(2);

        multiply(A2, identity, C2);

        if (!matricesEqual(C2, A2)) {

            throw new AssertionError(
                    "Identity test failed."
            );
        }


        // Test 3: zero matrix

        long[][] zero = {
                {0, 0},
                {0, 0}
        };

        long[][] C3 = createOutputMatrix(2);

        multiply(A2, zero, C3);

        if (!matricesEqual(C3, zero)) {

            throw new AssertionError(
                    "Zero-matrix test failed."
            );
        }

        System.out.println(
                "Correctness tests: PASSED"
        );
    }


    public static void benchmark(int n) {

        // Input generation occurs outside timing.

        long[][][] matrices = generateMatrices(n);

        long[][] A = matrices[0];
        long[][] B = matrices[1];

        // Output allocation occurs outside timing.

        long[][] C = createOutputMatrix(n);


        // ---------------------------------------------
        // Timed region begins
        // ---------------------------------------------

        long start = System.nanoTime();

        multiply(A, B, C);

        long end = System.nanoTime();

        // ---------------------------------------------
        // Timed region ends
        // ---------------------------------------------


        double elapsed =
                (end - start) / 1_000_000_000.0;


        

        long checksum = 0;

        for (int j = 0; j < n; j++) {

            checksum += C[0][j];
        }


        System.out.printf(
                "language=java,n=%d,"
                        + "time_seconds=%.9f,"
                        + "checksum=%d%n",
                n,
                elapsed,
                checksum
        );
    }


    public static void main(String[] args) {

        if (args.length != 1) {

            System.out.println(
                    "Usage:\n"
                            + "  java MatrixMultiplication test\n"
                            + "  java MatrixMultiplication "
                            + "<matrix_size>"
            );

            System.exit(1);
        }


        if (args[0].equals("test")) {

            runCorrectnessTests();

            return;
        }


        try {

            int n = Integer.parseInt(args[0]);

            if (n <= 0) {

                throw new NumberFormatException();
            }

            benchmark(n);

        } catch (NumberFormatException e) {

            System.out.println(
                    "Matrix size must be a positive integer."
            );

            System.exit(1);
        }
    }
}
