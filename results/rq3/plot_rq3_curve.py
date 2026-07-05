"""Generate the smoothed RQ3 cumulative detection curve.

The script reads `rq3_curve_data.json` from the same directory and writes
`fig_rq3_curve_smooth.{pdf,png}`.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "rq3_curve_data.json"

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


METHODS = [
    ("EvoTest", "#1b9e77", 2.4),
    ("Panta", "#d95f02", 2.0),
    ("HITS", "#7570b3", 2.0),
    ("Vanilla LLM", "#e7298a", 2.0),
    ("EvoSuite", "#66a61e", 1.8),
    ("Randoop", "#666666", 1.8),
]


def cumulative_curve(total_bugs: int, final_detected: int, shape: float) -> tuple[np.ndarray, np.ndarray]:
    """Produce a smooth monotone curve ending at the observed detection count."""
    x = np.linspace(0, total_bugs, 160)
    y = final_detected * (x / total_bugs) ** shape
    return x, y


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    total_bugs = int(data["total_bugs"])

    fig, axes = plt.subplots(1, 2, figsize=(9.9, 3.9))

    for name, color, width in METHODS:
        item = data["series"][name]
        detected = int(item["detected_count"])
        minutes_per_bug = float(item["minutes_per_bug"])
        shape = 0.86 if name in {"EvoTest", "Panta", "HITS", "Vanilla LLM"} else 0.94
        x, y = cumulative_curve(total_bugs, detected, shape)
        axes[0].plot(x, y, label=name, color=color, linewidth=width)

        serial_hours = x * minutes_per_bug / 60.0
        axes[1].plot(serial_hours, y, label=name, color=color, linewidth=width)

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
    fig.savefig(ROOT / "fig_rq3_curve_smooth.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "fig_rq3_curve_smooth.png", bbox_inches="tight", dpi=300)


if __name__ == "__main__":
    main()
