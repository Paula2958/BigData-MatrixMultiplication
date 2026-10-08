
public class MatrixMultiplication {
    static long[][] matrix(int n, int offset) {
        long[][] a = new long[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                a[i][j] = ((i * n + j + offset) % 10) + 1;
        return a;
    }

    static void multiply(long[][] a, long[][] b, long[][] c) {
        int n = a.length;
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                long total = 0;
                for (int k = 0; k < n; k++)
                    total += a[i][k] * b[k][j];
                c[i][j] = total;
            }
    }

    public static void main(String[] args) {
        int n = Integer.parseInt(args[0]);
        long[][] a = matrix(n, 0), b = matrix(n, 3), c = new long[n][n];
        long start = System.nanoTime();
        multiply(a, b, c);
        double seconds = (System.nanoTime() - start) / 1e9;
        long checksum = 0;
        for (long[] row : c)
            for (long value : row) checksum += value;
        System.out.printf(java.util.Locale.US, "RESULT,%d,%.9f,%d%n", n, seconds, checksum);
    }
}
