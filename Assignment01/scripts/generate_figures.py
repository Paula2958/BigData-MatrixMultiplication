import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

with (RESULTS / "summary_results.csv").open(newline="") as file:
    DATA = list(csv.DictReader(file))

COLORS = {
    "python": "#3769b4",
    "java": "#e67e22",
    "c": "#27a069"
}

MARKERS = {
    "python": "o",
    "java": "s",
    "c": "^"
}

LANGUAGES = ("python", "java", "c")


def series(language, column):
    rows = sorted(
        [
            row for row in DATA
            if row["language"].lower() == language
        ],
        key=lambda row: int(row["matrix_size"])
    )

    if not rows:
        raise ValueError(f"No data for {language}")

    x = [int(row["matrix_size"]) for row in rows]
    y = [float(row[column]) for row in rows]

    return x, y


def style(ax, ylabel, title):
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Matrix size (n)")
    ax.set_ylabel(ylabel)
    ax.set_xticks([50, 100, 200, 300])
    ax.grid(True, alpha=0.20)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save(fig, filename):
    fig.savefig(
        FIGURES / filename,
        dpi=220,
        bbox_inches="tight"
    )
    plt.close(fig)


# ---------------------------------------------------
# Figure 1: Execution time
# ---------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5.2))

for language in LANGUAGES:
    x, y = series(language, "median_time_seconds")
    ax.plot(
        x, y,
        marker=MARKERS[language],
        color=COLORS[language],
        linewidth=2.2,
        markersize=6,
        label=language.capitalize()
    )

style(
    ax,
    "Median execution time (seconds)",
    "Matrix Multiplication: Execution Time"
)
ax.set_ylim(bottom=0)
ax.legend(frameon=False)
save(fig, "execution_time.png")


# ---------------------------------------------------
# Figure 2: Log-log execution time
# ---------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5.2))

for language in LANGUAGES:
    x, y = series(language, "median_time_seconds")
    ax.plot(
        x, y,
        marker=MARKERS[language],
        color=COLORS[language],
        linewidth=2.2,
        markersize=6,
        label=language.capitalize()
    )

ax.set_xscale("log")
ax.set_yscale("log")

style(
    ax,
    "Median execution time (seconds, log scale)",
    "Execution Time: Log-Log Comparison"
)

ax.set_xticks([50, 100, 200, 300])
ax.set_xticklabels(["50", "100", "200", "300"])
ax.legend(frameon=False)

save(fig, "execution_time_loglog.png")


# ---------------------------------------------------
# Figure 3: Peak RSS
# ---------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5.2))

for language in LANGUAGES:
    x, y = series(language, "median_peak_rss_mib")
    ax.plot(
        x, y,
        marker=MARKERS[language],
        color=COLORS[language],
        linewidth=2.2,
        markersize=6,
        label=language.capitalize()
    )

style(
    ax,
    "Median Peak RSS (MiB)",
    "Process Memory Usage"
)
ax.set_ylim(bottom=0)
ax.legend(frameon=False)

save(fig, "memory_usage.png")


# ---------------------------------------------------
# Figure 4: Normalized scaling
# ---------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5.2))

for language in LANGUAGES:
    x, y = series(language, "median_time_seconds")

    baseline = y[0]
    if baseline <= 0:
        raise ValueError("Invalid runtime baseline")

    normalized = [value / baseline for value in y]

    ax.plot(
        x, normalized,
        marker=MARKERS[language],
        color=COLORS[language],
        linewidth=2.2,
        markersize=6,
        label=language.capitalize()
    )

x = [50, 100, 200, 300]
theory = [(n / 50) ** 3 for n in x]

ax.plot(
    x, theory,
    "--",
    color="#666666",
    linewidth=2.2,
    label="Theoretical O(n³)"
)

style(
    ax,
    "Runtime relative to n = 50",
    "Measured vs. Theoretical Cubic Growth"
)
ax.set_ylim(bottom=0)
ax.legend(frameon=False)

save(fig, "normalized_scaling.png")

print("Generated four figures successfully.")
