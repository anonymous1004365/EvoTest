"""Generate the RQ3 unsmoothed cumulative detection curve.

This plot uses per-bug 0/1 detection flags from `rq3_curve_data.json` instead
of the smooth summary curve used by `plot_rq3_curve.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "rq3_curve_data.json"

METHODS = [
    ("EvoTest", "#1b9e77", 2.4),
    ("Panta", "#d95f02", 2.0),
    ("HITS", "#7570b3", 2.0),
    ("Vanilla LLM", "#e7298a", 2.0),
    ("EvoSuite", "#66a61e", 1.8),
    ("Randoop", "#666666", 1.8),
]


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
    }
)


def cumulative(flags: list[int]) -> np.ndarray:
    return np.cumsum(np.asarray(flags, dtype=float))


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    total_bugs = int(data["total_bugs"])

    fig, axes = plt.subplots(1, 2, figsize=(9.9, 3.9))
    x_bugs = np.arange(1, total_bugs + 1)

    for name, color, width in METHODS:
        item = data["series"][name]
        y = cumulative(item["flags"])
        minutes_per_bug = float(item["minutes_per_bug"])
        x_hours = x_bugs * minutes_per_bug / 60.0

        axes[0].plot(
            x_bugs,
            y,
            label=name,
            color=color,
            linewidth=width,
            drawstyle="steps-post",
        )
        axes[1].plot(
            x_hours,
            y,
            label=name,
            color=color,
            linewidth=width,
            drawstyle="steps-post",
        )

    axes[0].set_title("(a) Detection Accumulation")
    axes[0].set_xlabel("Bugs Processed")
    axes[0].set_ylabel("Cumulative Detections")
    axes[0].set_xlim(0, total_bugs)
    axes[0].set_ylim(0, 520)
    axes[0].grid(True, alpha=0.22, linewidth=0.6)
    axes[0].legend(loc="upper left", frameon=False)

    axes[1].set_title("(b) Detection vs. Time Cost")
    axes[1].set_xlabel("Estimated Serial Time (hours)")
    axes[1].set_ylabel("Cumulative Detections")
    axes[1].set_xlim(0, 165)
    axes[1].set_ylim(0, 520)
    axes[1].grid(True, alpha=0.22, linewidth=0.6)
    axes[1].legend(loc="lower right", frameon=False)

    fig.tight_layout(w_pad=2.2)
    fig.savefig(ROOT / "fig_rq3_curve_unsmoothed.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "fig_rq3_curve_unsmoothed.png", bbox_inches="tight", dpi=300)


if __name__ == "__main__":
    main()
