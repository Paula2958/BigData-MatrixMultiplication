
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

with (ROOT / 'results/summary_results.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))

colors = {
    'Python': '#3769b4',
    'Java': '#e67e22',
    'C': '#27a069'
}


def values(metric, language):
    matches = sorted(
        (
            r for r in rows
            if r['metric'] == metric and r['language'] == language
        ),
        key=lambda r: int(r['n'])
    )
    return (
        [int(r['n']) for r in matches],
        [float(r['median']) for r in matches]
    )


def plot(name, metric, ylabel, loglog=False, normalized=False):
    fig, ax = plt.subplots(figsize=(8, 5.2), layout='constrained')

    for lang in ('Python', 'Java', 'C'):
        x, y = values(metric, lang)

        if normalized:
            y = [v / y[0] for v in y]

        ax.plot(
            x, y, '-o',
            linewidth=2.3,
            label=lang,
            color=colors[lang]
        )

    if normalized:
        x = values('runtime', 'Python')[0]
        ax.plot(
            x,
            [(n / x[0]) ** 3 for n in x],
            '--',
            linewidth=2,
            color='#666666',
            label='Theoretical O(n³)'
        )

    if loglog:
        ax.set_xscale('log')
        ax.set_yscale('log')

    ax.set_xlabel('Matrix size (n)')
    ax.set_ylabel(ylabel)
    ax.set_xticks(
        [50, 100, 200, 300],
        labels=['50', '100', '200', '300']
    )
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)

    fig.savefig(ROOT / 'figures' / name, dpi=200)
    plt.close(fig)


plot(
    'execution_time.png',
    'runtime',
    'Median execution time (s)'
)

plot(
    'execution_time_loglog.png',
    'runtime',
    'Median execution time (s)',
    loglog=True
)

plot(
    'memory_usage.png',
    'memory',
    'Median Peak RSS (MiB)'
)

plot(
    'normalized_scaling.png',
    'runtime',
    'Runtime relative to n=50',
    normalized=True
)

print('Saved four figures in figures/')
