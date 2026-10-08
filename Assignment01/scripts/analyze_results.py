
import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def quartiles(values):
    x = sorted(values)
    half = len(x) // 2
    lower = x[:half]
    upper = x[-half:]
    return statistics.median(lower), statistics.median(upper)


def main():
    grouped = defaultdict(list)

    for name, column, metric in [
        ('raw_results.csv', 'seconds', 'runtime'),
        ('raw_memory_results.csv', 'peak_rss_mib', 'memory')
    ]:
        with (ROOT / 'results' / name).open(newline='') as f:
            for row in csv.DictReader(f):
                grouped[(metric, row['language'], int(row['n']))].append(
                    float(row[column])
                )

    with (ROOT / 'results/summary_results.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'metric', 'language', 'n', 'repetitions',
            'median', 'iqr', 'q1', 'q3'
        ])

        for (metric, language, n), values in sorted(grouped.items()):
            q1, q3 = quartiles(values)
            writer.writerow([
                metric, language, n, len(values),
                statistics.median(values), q3 - q1, q1, q3
            ])

    print('Saved results/summary_results.csv')


if __name__ == '__main__':
    main()
