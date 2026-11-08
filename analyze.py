"""Summarise results.csv for the Task 2 report.

Run with:   python analyze.py            (reads results.csv)
            python analyze.py other.csv  (reads another file)

Uses only the standard library.  If matplotlib happens to be installed, it also
saves fitts_chart.png.  The text summary is printed and saved to
analysis_summary.txt - copy the numbers from there into your report.
"""

import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["time"] = float(row["time_seconds"])
        row["ease"] = int(row["ease_rating"])
        row["misses_n"] = int(row["misses"] or 0)
    return rows


def group(rows, key):
    buckets = defaultdict(list)
    for row in rows:
        buckets[key(row)].append(row)
    return buckets


def mean(values):
    values = list(values)
    return statistics.fmean(values) if values else float("nan")


def table(title, buckets, order=None, extra=None):
    """Format a 'mean time / mean ease / n' table for one grouping."""
    lines = [f"  {title}", f"    {'group':<14}{'n':>5}{'mean time (s)':>16}{'mean ease':>12}"
             + (f"{extra[0]:>14}" if extra else "")]
    keys = order or sorted(buckets)
    for key in keys:
        if key not in buckets:
            continue
        items = buckets[key]
        line = (f"    {str(key):<14}{len(items):>5}{mean(r['time'] for r in items):>16.3f}"
                f"{mean(r['ease'] for r in items):>12.2f}")
        if extra:
            line += f"{extra[1](items):>14.2f}"
        lines.append(line)
    return "\n".join(lines)


def fit_line(xs, ys):
    """Least-squares y = a + b*x and Pearson r (None if not enough spread)."""
    if len(xs) < 3 or len(set(xs)) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    b = sxy / sxx
    return my - b * mx, b, sxy / math.sqrt(sxx * syy)


CONTRAST_ORDER = ["High", "Medium", "Low"]
SIZE_ORDER = ["Small", "Medium", "Large"]


def analyse(rows):
    out = []
    ident = [r for r in rows if r["task_type"] == "Identification"]
    fitts = [r for r in rows if r["task_type"] == "Target Hitting"]
    people = sorted({r["participant_id"] for r in rows})
    out.append(f"Participants: {len(people)} ({', '.join(people)})")
    out.append(f"Rows: {len(rows)}  (Identification {len(ident)}, Target Hitting {len(fitts)})")

    # ---------------------------------------------------------- identification
    out.append("\n=== IDENTIFICATION TASK ===")
    if ident:
        out.append(table("By contrast", group(ident, lambda r: r["contrast"]), CONTRAST_ORDER))
        out.append(table("By size", group(ident, lambda r: r["size_scale"]), SIZE_ORDER))
        out.append(table("By brightness (%)", group(ident, lambda r: int(r["brightness_pct"]))))
        out.append(table("By figure", group(ident, lambda r: r["stimulus"])))
        out.append("  Answers given:")
        for key, items in sorted(group(ident, lambda r: (r["stimulus"], r["response"])).items()):
            out.append(f"    {key[0]:<14}{key[1]:<10}{len(items)}")
    else:
        out.append("  (no identification data yet)")

    # ------------------------------------------------------------ target hitting
    out.append("\n=== TARGET-HITTING TASK (Fitts' Law) ===")
    if not fitts:
        out.append("  (no target-hitting data yet)")
        return "\n".join(out), None

    for row in fitts:
        row["width"] = int(row["target_diameter_px"])
        row["dist"] = int(row["distance_px"])
        row["index_of_difficulty"] = math.log2(row["dist"] / row["width"] + 1)

    miss_rate = (lambda items: mean(r["misses_n"] for r in items))
    extra = ("mean misses", miss_rate)
    by_width = group(fitts, lambda r: r["width"])
    by_dist = group(fitts, lambda r: r["dist"])
    out.append(table("By target diameter (px)", by_width, extra=extra))
    out.append(table("By distance (px)", by_dist, extra=extra))

    out.append("  Mean time (s): rows = distance (px), columns = target diameter (px)")
    widths = sorted(by_width)
    out.append("    " + f"{'':<10}" + "".join(f"{w:>9}" for w in widths))
    for dist in sorted(by_dist):
        cells = []
        for width in widths:
            cell = [r["time"] for r in fitts if r["dist"] == dist and r["width"] == width]
            cells.append(f"{mean(cell):>9.3f}" if cell else f"{'-':>9}")
        out.append("    " + f"{dist:<10}" + "".join(cells))

    out.append(table("By contrast (all targets)", group(fitts, lambda r: r["contrast"]),
                     CONTRAST_ORDER, extra=extra))
    out.append(table("By size scale", group(fitts, lambda r: r["size_scale"]), SIZE_ORDER,
                     extra=extra))
    out.append(table("By brightness (%)", group(fitts, lambda r: int(r["brightness_pct"])),
                     extra=extra))

    # Fitts' Law check: MT = a + b * log2(D/W + 1)
    xs = [r["index_of_difficulty"] for r in fitts]
    ys = [r["time"] for r in fitts]
    fit = fit_line(xs, ys)
    out.append("\n  Fitts' Law check:  MT = a + b * log2(D/W + 1)")
    if fit:
        a, b, r_value = fit
        out.append(f"    a = {a:.3f} s,  b = {b:.3f} s/bit,  r = {r_value:.2f}  (n = {len(xs)})")
        out.append("    -> " + ("time rises with difficulty, as Fitts' Law predicts."
                                if b > 0 else "time did NOT rise with difficulty - check data."))
    else:
        out.append("    not enough varied trials to fit a line.")

    # Plain-language verdicts
    width_means = {w: mean(r["time"] for r in items) for w, items in by_width.items()}
    dist_means = {d: mean(r["time"] for r in items) for d, items in by_dist.items()}
    ws, ds = sorted(width_means), sorted(dist_means)
    out.append("\n  Plain-language findings")
    out.append(f"    Larger targets faster?   {width_means[ws[0]]:.3f}s (smallest) -> "
               f"{width_means[ws[-1]]:.3f}s (largest): "
               f"{'YES' if width_means[ws[-1]] < width_means[ws[0]] else 'NO'}")
    out.append(f"    Shorter distance faster? {dist_means[ds[0]]:.3f}s (nearest) -> "
               f"{dist_means[ds[-1]]:.3f}s (farthest): "
               f"{'YES' if dist_means[ds[0]] < dist_means[ds[-1]] else 'NO'}")
    return "\n".join(out), (xs, ys, fit)


def save_chart(points, folder):
    """Optional scatter plot of movement time against index of difficulty."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    xs, ys, fit = points
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(xs, ys, alpha=0.6)
    if fit:
        a, b, _ = fit
        lo, hi = min(xs), max(xs)
        ax.plot([lo, hi], [a + b * lo, a + b * hi], color="crimson")
    ax.set_xlabel("Index of difficulty  log2(D/W + 1)  [bits]")
    ax.set_ylabel("Movement time (s)")
    ax.set_title("Target hitting: time vs difficulty")
    fig.tight_layout()
    path = folder / "fitts_chart.png"
    fig.savefig(path, dpi=150)
    return path


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "results.csv"
    if not path.exists():
        sys.exit(f"{path} not found - run app.py and collect some data first.")
    rows = load(path)
    if not rows:
        sys.exit(f"{path} has no data rows yet.")
    text, points = analyse(rows)
    print(text)
    summary = HERE / "analysis_summary.txt"
    summary.write_text(text + "\n", encoding="utf-8")
    print(f"\nSaved {summary.name}")
    if points:
        chart = save_chart(points, HERE)
        if chart:
            print(f"Saved {chart.name}")


if __name__ == "__main__":
    main()
