
#!/usr/bin/env python3

import argparse
import csv
import pathlib
from xml.sax.saxutils import escape

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

ROOT = pathlib.Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument("--author", default="[STUDENT NAME]")
args = parser.parse_args()

results_path = ROOT / "benchmarks/results/summary_results.csv"

if results_path.exists():
    with results_path.open() as f:
        rows = list(csv.DictReader(f))
else:
    rows = []

styles = getSampleStyleSheet()
story = []


def paragraph(text, style="BodyText"):
    story.append(Paragraph(escape(text), styles[style]))
    story.append(Spacer(1, 8))


def heading(text):
    paragraph(text, "Heading1")


paragraph(
    "Assignment 3: Parallel Matrix Multiplication "
    "and Thread Scaling", "Title"
)
paragraph(
    "Big Data | Data Science and Engineering | "
    "ULPGC | 2026-2027", "Heading2"
)
paragraph("Author: " + args.author)

if not rows:
    paragraph("DRAFT: EXPERIMENTAL RESULTS PENDING")

heading("Abstract")
paragraph(
    "This study investigates shared-memory parallel matrix "
    "multiplication using C and OpenMP. Equivalent sequential "
    "and parallel implementations are compared across matrix "
    "sizes and thread counts. Execution time, peak process "
    "resident memory, speedup and efficiency are evaluated "
    "using controlled measurements."
)

heading("1. Introduction and Research Objective")
paragraph(
    "Research question: How does OpenMP thread count affect "
    "runtime, memory consumption, speedup and efficiency "
    "for dense matrix multiplication?"
)
paragraph(
    "Hypothesis: Parallel execution should improve performance "
    "for sufficiently large matrices, while thread-management "
    "overhead may outweigh its benefits for smaller matrices."
)

heading("2. Background")
paragraph(
    "Classical dense matrix multiplication has cubic arithmetic "
    "complexity O(n^3). OpenMP supports shared-memory parallelism "
    "by distributing independent iterations among threads."
)
paragraph(
    "The implementation uses static row scheduling. Each thread "
    "writes to distinct rows of the output matrix, avoiding "
    "concurrent writes to the same elements."
)
paragraph(
    "Speedup S(p) = Tseq / Tp. "
    "Parallel efficiency E(p) = S(p) / p. "
    "Both quantities use median execution times."
)

heading("3. Methodology")
paragraph(
    "Both implementations use C, double-precision values, "
    "row-major arrays and the same i-k-j loop order. "
    "The parallel implementation uses OpenMP parallel for "
    "with static scheduling."
)
paragraph(
    "Inputs are generated using a deterministic xorshift64* "
    "generator with seed 20261109+n. Matrix elements lie "
    "between 0 and 1 in increments of 0.001."
)
)
paragraph(
    "Each configuration uses five measured repetitions by "
    "default. An untimed warm-up precedes each measurement. "
    "CLOCK_MONOTONIC measures the multiplication kernel, "
    "excluding allocation, input generation, output "
    "initialisation and checksum calculation."
)
paragraph(
    "Peak process resident memory is measured with getrusage. "
    "On Linux, ru_maxrss is reported in KiB. The metric "
    "includes memory used during warm-up and is not "
    "an isolated kernel-memory measurement."
)
paragraph(
    "Correctness is tested using a known 2x2 multiplication, "
    "identity and zero matrices, and sequential-versus-parallel "
    "weighted checksum comparisons."
)
paragraph(
    "The experimental environment, including CPU, RAM, "
    "operating system, compiler and processor counts, "
    "is recorded in environment.txt."
)

heading("4. Experimental Results")

if not rows:
    paragraph(
        "No experimental measurements are available yet. "
        "Execute the benchmark on the target Linux machine "
        "and regenerate this report."
    )
else:
    table_data = [[
        "n", "Method", "p", "Runs",
        "Median (s)", "IQR (s)", "RSS (KiB)",
        "Speedup", "Efficiency"
    ]]

    def fmt(row, key, digits=3):
        value = row.get(key, "")
        return f"{float(value):.{digits}f}" if value else "-"

    for r in rows:
        table_data.append([
            r["n"],
            r["method"][:3],
            r["threads"],
            r["repetitions"],
            fmt(r, "median_seconds", 5),
            fmt(r, "iqr_seconds", 5),
            fmt(r, "median_peak_rss_kib", 0),
            fmt(r, "speedup", 2),
            fmt(r, "efficiency", 2)
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[30, 40, 20, 30, 62, 60, 66, 50, 52]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.2, colors.lightgrey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(table)

    for name in [
        "execution_time",
        "speedup",
        "efficiency",
        "memory_usage"
    ]:
        path = ROOT / "figures" / (name + ".png")

        if path.exists():
            story.append(Spacer(1, 12))
            figure_title = Paragraph(
                name.replace("_", " ").title(),
                styles["Heading2"]
            )
            figure = Image(
                str(path),
                width=6.3 * inch,
                height=3.94 * inch
            )
            story.append(KeepTogether([figure_title, figure]))

    failures_path = ROOT / "benchmarks/results/failures.csv"

    if failures_path.exists():
        with failures_path.open() as f:
            failures = list(csv.DictReader(f))
        paragraph(
            f"Recorded failed or timed-out runs: {len(failures)}. "
            "See failures.csv for details."
        )

heading("5. Discussion")
paragraph(
    "PENDING STUDENT ANALYSIS: Interpret the actual runtime "
    "and memory measurements. Discuss the effect of matrix "
    "size and thread count, speedup, efficiency, variability "
    "and potential hardware bottlenecks. Distinguish measured "
    "observations from possible explanations."
)

heading("6. Conclusions")
paragraph(
    "PENDING STUDENT ANALYSIS: Identify the best-performing "
    "thread configurations, the largest feasible matrix size, "
    "the observed scalability limits and the limitations "
    "of the experimental setup. Replace this text before "
    "submitting the report."
)

heading("7. References")
paragraph(
    "[1] OpenMP Architecture Review Board, "
    "OpenMP Application Programming Interface Specification. "
    "https://www.openmp.org/specifications/"
)
paragraph(
    "[2] Linux man-pages project, getrusage(2). "
    "https://man7.org/linux/man-pages/man2/getrusage.2.html"
)
paragraph(
    "[3] Linux man-pages project, clock_gettime(2). "
    "https://man7.org/linux/man-pages/man2/clock_gettime.2.html"
)

heading("8. Reproducibility")
paragraph(
    "Source code, benchmark automation, raw measurements, "
    "summary statistics, environment information and "
    "plot-generation scripts are provided in the "
    "Assignment 3 GitHub repository."
)

heading("AI Assistance Disclosure")
paragraph(
    "AI was used with the purpose of aiding " 
    "in the code developing context "
    "and helped understand key information."
)

output = ROOT / "report/Assignment03_Report.pdf"

doc = SimpleDocTemplate(
    str(output),
    pagesize=(595, 842),
    leftMargin=42,
    rightMargin=42,
    topMargin=42,
    bottomMargin=42
)

doc.build(story)

print("Generated:", output)
