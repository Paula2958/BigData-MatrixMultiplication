
import java.util.Arrays;
import java.util.Random;

/** Big Data Assignment 2: simple sequential Java implementations. */
public class MatrixStudy {

    // Same deterministic dense inputs used in Assignment 1.
    static long[][] denseInput(int n, int offset) {
        long[][] matrix = new long[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                matrix[i][j] = ((i * n + j + offset) % 10) + 1;
            }
        }
        return matrix;
    }

    static long[][] sparseInput(int n, int zerosPercent, long seed) {
        long[][] matrix = new long[n][n];
        int total = n * n;
        int nonzeros = (int) Math.round(total * (100 - zerosPercent) / 100.0);
        int[] positions = new int[total];
        for (int p = 0; p < total; p++) positions[p] = p;
        Random random = new Random(seed);
        for (int p = 0; p < nonzeros; p++) {
            int other = p + random.nextInt(total - p);
            int temp = positions[p];
            positions[p] = positions[other];
            positions[other] = temp;
            int location = positions[p];
            matrix[location / n][location % n] = 1 + location % 9;
        }
        return matrix;
    }

    static long[][] basic(long[][] a, long[][] b) {
        int n = a.length;
        long[][] c = new long[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                long sum = 0;
                for (int k = 0; k < n; k++) sum += a[i][k] * b[k][j];
                c[i][j] = sum;
            }
        }
        return c;
    }

    static long[][] reordered(long[][] a, long[][] b) {
        int n = a.length;
        long[][] c = new long[n][n];
        for (int i = 0; i < n; i++) {
            for (int k = 0; k < n; k++) {
                for (int j = 0; j < n; j++) c[i][j] += a[i][k] * b[k][j];
            }
        }
        return c;
    }

    static long[][] blocked(long[][] a, long[][] b, int blockSize) {
        int n = a.length;
        long[][] c = new long[n][n];
        for (int ii = 0; ii < n; ii += blockSize) {
            for (int kk = 0; kk < n; kk += blockSize) {
                for (int jj = 0; jj < n; jj += blockSize) {
                    for (int i = ii; i < Math.min(ii + blockSize, n); i++) {
                        for (int k = kk; k < Math.min(kk + blockSize, n); k++) {
                            for (int j = jj; j < Math.min(jj + blockSize, n); j++) {
                                c[i][j] += a[i][k] * b[k][j];
                            }
                        }
                    }
                }
            }
        }
        return c;
    }

    // CSR stores only nonzero values, their columns, and row boundaries.
    static class CSR {
        int n;
        int[] rowStart;
        int[] column;
        long[] value;

        CSR(int n, int[] rowStart, int[] column, long[] value) {
            this.n = n;
            this.rowStart = rowStart;
            this.column = column;
            this.value = value;
        }
    }

    static CSR toCSR(long[][] matrix) {
        int n = matrix.length;
        int count = countNonzero(matrix);
        int[] rowStart = new int[n + 1];
        int[] column = new int[count];
        long[] value = new long[count];
        int position = 0;
        for (int i = 0; i < n; i++) {
            rowStart[i] = position;
            for (int j = 0; j < n; j++) {
                if (matrix[i][j] != 0) {
                    column[position] = j;
                    value[position] = matrix[i][j];
                    position++;
                }
            }
        }
        rowStart[n] = position;
        return new CSR(n, rowStart, column, value);
    }

    // Simple CSR x CSR multiplication: accumulate one result row at a time.
    static CSR multiplyCSR(CSR a, CSR b) {
        int n = a.n;
        int[] rowStart = new int[n + 1];
        int[] column = new int[16];
        long[] value = new long[16];
        int count = 0;

        for (int i = 0; i < n; i++) {
            long[] row = new long[n];
            for (int p = a.rowStart[i]; p < a.rowStart[i + 1]; p++) {
                int k = a.column[p];
                for (int q = b.rowStart[k]; q < b.rowStart[k + 1]; q++) {
                    row[b.column[q]] += a.value[p] * b.value[q];
                }
            }
            for (int j = 0; j < n; j++) {
                if (row[j] != 0) {
                    if (count == column.length) {
                        column = Arrays.copyOf(column, column.length * 2);
                        value = Arrays.copyOf(value, value.length * 2);
                    }
                    column[count] = j;
                    value[count] = row[j];
                    count++;
                }
            }
            rowStart[i + 1] = count;
        }
        return new CSR(n, rowStart, Arrays.copyOf(column, count),
                       Arrays.copyOf(value, count));
    }

    static long[][] toDense(CSR matrix) {
        long[][] result = new long[matrix.n][matrix.n];
        for (int i = 0; i < matrix.n; i++) {
            for (int p = matrix.rowStart[i]; p < matrix.rowStart[i + 1]; p++) {
                result[i][matrix.column[p]] = matrix.value[p];
            }
        }
        return result;
    }

    static int countNonzero(long[][] matrix) {
        int count = 0;
        for (long[] row : matrix) for (long x : row) if (x != 0) count++;
        return count;
    }

    static long checksum(long[][] matrix) {
        long sum = 0;
        for (long[] row : matrix) for (long x : row) sum += x;
        return sum;
    }

    static long checksum(CSR matrix) {
        long sum = 0;
        for (long x : matrix.value) sum += x;
        return sum;
    }

    static long[][] multiply(String method, long[][] a, long[][] b, int tile) {
        switch (method) {
            case "basic": return basic(a, b);
            case "reordered": return reordered(a, b);
            case "blocked": return blocked(a, b, tile);
            default: throw new IllegalArgumentException("Unknown method: " + method);
        }
    }

    static void test() {
        long[][] a = {{1, 2}, {3, 4}};
        long[][] b = {{5, 6}, {7, 8}};
        long[][] expected = {{19, 22}, {43, 50}};
        for (String method : new String[]{"basic", "reordered", "blocked"}) {
            if (!Arrays.deepEquals(multiply(method, a, b, 2), expected))
                throw new AssertionError(method + " failed 2x2 test");
        }
        if (!Arrays.deepEquals(toDense(multiplyCSR(toCSR(a), toCSR(b))), expected))
            throw new AssertionError("CSR failed 2x2 test");

        for (int n : new int[]{1, 2, 5, 17, 32, 75}) {
            for (int sparsity : new int[]{0, 50, 75, 90, 95, 99, 100}) {
                long[][] x = sparsity == 0 ? denseInput(n, 0) : sparseInput(n, sparsity, 123);
                long[][] y = sparsity == 0 ? denseInput(n, 3) : sparseInput(n, sparsity, 456);
                long[][] reference = basic(x, y);
                for (String method : new String[]{"reordered", "blocked"}) {
                    if (!Arrays.deepEquals(multiply(method, x, y, 16), reference))
                        throw new AssertionError(method + " failed n=" + n);
                }
                if (!Arrays.deepEquals(toDense(multiplyCSR(toCSR(x), toCSR(y))), reference))
                    throw new AssertionError("CSR failed n=" + n + " sparsity=" + sparsity);
            }
        }
        System.out.println("PASS: all multiplication tests");
    }

    // Each invocation reports one measured run, after excluded warm-up runs.
    static void benchmark(String[] args) {
        String method = args[1];
        int n = Integer.parseInt(args[2]);
        int sparsity = Integer.parseInt(args[3]);
        long seed = Long.parseLong(args[4]);
        int warmups = Integer.parseInt(args[5]);
        int tile = Integer.parseInt(args[6]);

        long[][] a = sparsity == 0 ? denseInput(n, 0) : sparseInput(n, sparsity, seed);
        long[][] b = sparsity == 0 ? denseInput(n, 3) : sparseInput(n, sparsity, seed + 1);
        CSR ca = null, cb = null;
        double conversionMs = 0;
        if (method.equals("csr")) {
            long start = System.nanoTime();
            ca = toCSR(a);
            cb = toCSR(b);
            conversionMs = (System.nanoTime() - start) / 1e6;
        }

        for (int run = 0; run < warmups + 1; run++) {
            long start = System.nanoTime();
            long hash;
            int outputNnz;
            double elapsedMs;
            if (method.equals("csr")) {
                CSR c = multiplyCSR(ca, cb);
                elapsedMs = (System.nanoTime() - start) / 1e6;
                hash = checksum(c);
                outputNnz = c.value.length;
            } else {
                long[][] c = multiply(method, a, b, tile);
                elapsedMs = (System.nanoTime() - start) / 1e6;
                hash = checksum(c);
                outputNnz = countNonzero(c);
            }
            if (run == warmups) {
                System.out.printf(java.util.Locale.US,
                    "RESULT,%.6f,%.6f,%d,%d,%d,%d%n",
                    elapsedMs, conversionMs, countNonzero(a),
                    countNonzero(b), outputNnz, hash);
            }
        }
    }

    public static void main(String[] args) {
        if (args.length == 1 && args[0].equals("test")) test();
        else if (args.length == 7 && args[0].equals("bench")) benchmark(args);
        else System.out.println("Usage: java MatrixStudy test OR bench method n sparsity seed warmups tile");
    }
}
