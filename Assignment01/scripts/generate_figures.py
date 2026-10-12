import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

with (ROOT / "results/summary_results.csv").open(newline="") as f:
    data = list(csv.DictReader(f))

LANGUAGES = ("python", "java", "c")
COLORS = {
    "python": "#4263A3",
    "java": "#C47B40",
    "c": "#388576"
}
MARKERS = {
    "python": "o",
    "java": "s",
    "c": "^"
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white"
})


def get_values(language, column):
    rows = sorted(
        (r for r in data if r["language"] == language),
        key=lambda r: int(r["matrix_size"])
    )

    if len(rows) != 4:
        raise ValueError(f"Expected four sizes for {language}")

    return (
        [int(r["matrix_size"]) for r in rows],
        [float(r[column]) for r in rows]
    )


def setup_axes(ax, ylabel):
    ax.set_xlabel("Matrix dimension (n)")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.17)
    ax.set_axisbelow(True)
    ax.set_xticks([50, 100, 200, 300])


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=300)
    plt.close(fig)


# Figure 1: Execution time
fig, ax = plt.subplots(figsize=(7.4, 4.6))

for lang in LANGUAGES:
    x, y = get_values(lang, "median_time_seconds")
    ax.plot(
        x, y, marker=MARKERS[lang],
        color=COLORS[lang], linewidth=2,
        label=lang.capitalize()
    )

setup_axes(ax, "Median execution time (s)")
ax.set_ylim(bottom=0)
ax.legend(frameon=False)
save(fig, "execution_time.png")


# Figure 2: Log-log execution time
fig, ax = plt.subplots(figsize=(7.4, 4.6))

for lang in LANGUAGES:
    x, y = get_values(lang, "median_time_seconds")
    if any(value <= 0 for value in y):
        raise ValueError("Logarithmic times must be positive.")

    ax.plot(
        x, y, marker=MARKERS[lang],
        color=COLORS[lang], linewidth=2,
        label=lang.capitalize()
    )

ax.set_xscale("log")
ax.set_yscale("log")
setup_axes(ax, "Median execution time (s)")
ax.set_xticklabels(["50", "100", "200", "300"])
ax.legend(frameon=False)
save(fig, "execution_time_loglog.png")


# Figure 3: Peak RSS memory
fig, ax = plt.subplots(figsize=(7.4, 4.6))

for lang in LANGUAGES:
    x, y = get_values(lang, "median_peak_rss_mib")
    ax.plot(
        x, y, marker=MARKERS[lang],
        color=COLORS[lang], linewidth=2,
        label=lang.capitalize()
    )

setup_axes(ax, "Median Peak RSS (MiB)")
ax.set_ylim(bottom=0)
ax.legend(frameon=False)
save(fig, "memory_usage.png")


# Figure 4: Normalized scaling
fig, ax = plt.subplots(figsize=(7.4, 4.6))

for lang in LANGUAGES:
    x, y = get_values(lang, "median_time_seconds")
    if y[0] <= 0:
        raise ValueError("Invalid baseline.")

    normalized = [value / y[0] for value in y]

    ax.plot(
        x, normalized, marker=MARKERS[lang],
        color=COLORS[lang], linewidth=2,
        label=lang.capitalize()
    )

x = [50, 100, 200, 300]
theoretical = [(n / 50) ** 3 for n in x]

ax.plot(
    x, theoretical, "--", color="#777777",
    linewidth=2, label="Theoretical cubic growth"
)

setup_axes(ax, "Runtime relative to n = 50")
ax.set_ylim(bottom=0)
ax.legend(frameon=False)
save(fig, "normalized_scaling.png")

print("Four figures generated in figures/")
