import java.util.Locale;

public class MatrixMultiplication {

    public static long[][] generateMatrix(int n, int offset) {
        long[][] matrix = new long[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                matrix[i][j] = ((i * n + j + offset) % 10) + 1;
            }
        }

        return matrix;
    }

    public static long[][] multiplyMatrices(long[][] a, long[][] b) {
        int n = a.length;
        long[][] result = new long[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                long total = 0;

                for (int k = 0; k < n; k++) {
                    total += a[i][k] * b[k][j];
                }

                result[i][j] = total;
            }
        }

        return result;
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Usage: java MatrixMultiplication <size>");
            System.exit(1);
        }

        int n = Integer.parseInt(args[0]);

        if (n <= 0) {
            throw new IllegalArgumentException(
                "Matrix size must be positive."
            );
        }

        long[][] a = generateMatrix(n, 0);
        long[][] b = generateMatrix(n, 3);

        long start = System.nanoTime();
        long[][] result = multiplyMatrices(a, b);
        long end = System.nanoTime();

        double elapsedSeconds = (end - start) / 1e9;

        long checksum = 0;

        for (long[] row : result) {
            for (long value : row) {
                checksum += value;
            }
        }

        System.out.printf(
            Locale.US,
            "RESULT,%d,%.9f,%d%n",
            n,
            elapsedSeconds,
            checksum
        );
    }
}
