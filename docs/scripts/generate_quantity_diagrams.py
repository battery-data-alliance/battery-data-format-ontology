"""
Generate SVG reference diagrams for BDF capacity and energy quantity classes.

Produces two figures:
  docs/assets/img/quantities/capacity_quantities.svg
  docs/assets/img/quantities/energy_quantities.svg

Each figure has five panels:
  1. Voltage and current (protocol reference)
  2. charging_XXX and discharging_XXX (unsigned cumulative accumulators)
  3. net_XXX  = charging − discharging  (signed, cumulative from test start)
  4. cumulative_XXX = ∫ I dt  (signed direct integral; identical to net)
  5. step_XXX  (unsigned, resets to zero at each step boundary)

Run from the repository root:
  python docs/scripts/generate_quantity_diagrams.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
OUT_DIR = Path("docs/assets/img/quantities")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Protocol definition
# ---------------------------------------------------------------------------
# Five-step protocol:  DCH → REST → CHG → REST → DCH
# Times in hours; currents in A; voltage via a simple RC-SOC model.

STEPS = [
    # (label,      duration_h,  current_A)
    ("CC\_DCH",    1.0,        -2.0),
    ("REST",       0.5,         0.0),
    ("CC\_CHG",    1.5,        +1.5),
    ("REST",       0.5,         0.0),
    ("CC\_DCH",    0.8,        -2.0),
]
CAPACITY_AH = 2.0   # nominal cell capacity
R_OHMS      = 0.05  # internal resistance for voltage model

# ---------------------------------------------------------------------------
# Build time-series arrays
# ---------------------------------------------------------------------------
DT_H = 1 / 360   # 10-second steps in hours

t_list, I_list, step_list = [], [], []
step_idx = 0
for label, dur, cur in STEPS:
    n = max(1, round(dur / DT_H))
    t_list.append(np.linspace(
        sum(d for _, d, _ in STEPS[:step_idx]),
        sum(d for _, d, _ in STEPS[:step_idx]) + dur,
        n, endpoint=False,
    ))
    I_list.append(np.full(n, cur))
    step_list.append(np.full(n, step_idx))
    step_idx += 1

t = np.concatenate(t_list)          # hours
I = np.concatenate(I_list)          # amperes
step_arr = np.concatenate(step_list)

# Voltage via simple SOC model
soc = np.zeros(len(t))
soc[0] = 0.75
for i in range(1, len(t)):
    soc[i] = np.clip(soc[i - 1] + I[i - 1] * DT_H / CAPACITY_AH, 0.0, 1.0)
OCV = 3.0 + 1.5 * soc              # linear OCV model  3.0–4.5 V
V   = OCV + I * R_OHMS             # terminal voltage

# Step boundary times (in hours)
step_boundaries = [0.0] + list(np.cumsum([d for _, d, _ in STEPS]))

# Step centre times and labels (for annotations)
step_centres = [(step_boundaries[i] + step_boundaries[i + 1]) / 2
                for i in range(len(STEPS))]
step_labels  = [lbl for lbl, _, _ in STEPS]

# ---------------------------------------------------------------------------
# Derived quantities — capacity
# ---------------------------------------------------------------------------
charging_cap    = np.cumsum(np.maximum(I, 0.0) * DT_H)          # monotone ↑
discharging_cap = np.cumsum(np.maximum(-I, 0.0) * DT_H)         # monotone ↑
net_cap         = charging_cap - discharging_cap                  # signed
cumulative_cap  = np.cumsum(I * DT_H)                            # signed ∫I dt

step_cap = np.zeros(len(t))
for i, s in enumerate(step_arr):
    mask = (step_arr == s) & (np.arange(len(t)) <= i)
    step_cap[i] = np.sum(np.abs(I[mask]) * DT_H)

# ---------------------------------------------------------------------------
# Derived quantities — energy  (W·h)
# ---------------------------------------------------------------------------
P = V * I   # instantaneous power (signed)

charging_energy    = np.cumsum(np.maximum(P, 0.0) * DT_H)
discharging_energy = np.cumsum(np.maximum(-P, 0.0) * DT_H)
net_energy         = charging_energy - discharging_energy
cumulative_energy  = np.cumsum(P * DT_H)

step_energy = np.zeros(len(t))
for i, s in enumerate(step_arr):
    mask = (step_arr == s) & (np.arange(len(t)) <= i)
    step_energy[i] = np.sum(np.abs(P[mask]) * DT_H)

# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------
COLOURS = {
    "charge":      "#c0392b",   # red
    "discharge":   "#2980b9",   # blue
    "net":         "#27ae60",   # green
    "cumulative":  "#8e44ad",   # purple
    "step":        "#e67e22",   # orange
    "voltage":     "#2c3e50",   # near-black
    "current":     "#7f8c8d",   # grey
    "zero":        "#bdc3c7",   # light grey for zero line
}

plt.rcParams.update({
    "font.family":        "sans-serif",
    "font.size":          9,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.linewidth":     0.8,
    "lines.linewidth":    1.6,
    "grid.linewidth":     0.4,
    "grid.alpha":         0.5,
    "legend.frameon":     False,
    "legend.fontsize":    8,
    "figure.dpi":         150,
})


def _add_step_lines(ax, boundaries, labels, y_top):
    """Vertical dashed step-boundary lines and step labels."""
    for x in boundaries[1:-1]:
        ax.axvline(x, color="#95a5a6", linewidth=0.8, linestyle="--", zorder=0)
    for xc, lbl in zip(
        [(boundaries[i] + boundaries[i + 1]) / 2 for i in range(len(labels))],
        labels,
    ):
        ax.text(xc, y_top, lbl, ha="center", va="bottom",
                fontsize=7, color="#7f8c8d")


def _zero_line(ax):
    ax.axhline(0, color=COLOURS["zero"], linewidth=0.8, zorder=0)


def _format_time_axis(ax, t_max):
    ax.set_xlim(0, t_max)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
    ax.set_xlabel("Test time / h", labelpad=3)


# ---------------------------------------------------------------------------
# Figure builder
# ---------------------------------------------------------------------------

def make_figure(quantity: str) -> None:
    """
    quantity: 'capacity' or 'energy'
    """
    is_cap = quantity == "capacity"
    unit   = "A·h" if is_cap else "W·h"
    sym    = "Q"   if is_cap else "E"

    if is_cap:
        chg  = charging_cap
        dch  = discharging_cap
        net  = net_cap
        cum  = cumulative_cap
        stp  = step_cap
        ymax_cd  = max(charging_cap.max(), discharging_cap.max()) * 1.15
        ymin_net = net_cap.min() * 1.3
        ymax_net = net_cap.max() * 1.3
        ymax_stp = step_cap.max() * 1.3
        name_chg = "charging_capacity_ah"
        name_dch = "discharging_capacity_ah"
        name_net = "net_capacity_ah"
        name_cum = "cumulative_capacity_ah"
        name_stp = "step_capacity_ah"
    else:
        chg  = charging_energy
        dch  = discharging_energy
        net  = net_energy
        cum  = cumulative_energy
        stp  = step_energy
        ymax_cd  = max(charging_energy.max(), discharging_energy.max()) * 1.15
        ymin_net = net_energy.min() * 1.3
        ymax_net = net_energy.max() * 1.3
        ymax_stp = step_energy.max() * 1.3
        name_chg = "charging_energy_wh"
        name_dch = "discharging_energy_wh"
        name_net = "net_energy_wh"
        name_cum = "cumulative_energy_wh"
        name_stp = "step_energy_wh"

    t_max = t[-1]
    label_y_offset = 0.04  # fraction of axes height for step labels

    fig, axes = plt.subplots(
        5, 1, figsize=(7, 10),
        gridspec_kw={"hspace": 0.55, "height_ratios": [1.2, 1, 1, 1, 1]},
    )

    # ------------------------------------------------------------------
    # Panel 1 — voltage and current (protocol reference)
    # ------------------------------------------------------------------
    ax = axes[0]
    ax2 = ax.twinx()
    ax.plot(t, V, color=COLOURS["voltage"], label="Voltage")
    ax2.plot(t, I, color=COLOURS["current"], linestyle="--", label="Current")
    ax2.axhline(0, color=COLOURS["zero"], linewidth=0.6, zorder=0)
    ax.set_ylabel("Voltage / V", color=COLOURS["voltage"])
    ax2.set_ylabel("Current / A", color=COLOURS["current"])
    ax.tick_params(axis="y", colors=COLOURS["voltage"])
    ax2.tick_params(axis="y", colors=COLOURS["current"])
    ax.set_xlim(0, t_max)
    ax.set_title("Protocol reference", fontsize=9, loc="left", pad=4)
    _add_step_lines(ax, step_boundaries, step_labels,
                    ax.get_ylim()[1] if ax.get_ylim()[1] != 0 else 4.2)
    ax.set_xticks([])

    # ------------------------------------------------------------------
    # Panel 2 — charging and discharging (unsigned cumulative)
    # ------------------------------------------------------------------
    ax = axes[1]
    ax.plot(t, chg, color=COLOURS["charge"],    label=f"``{name_chg}``")
    ax.plot(t, dch, color=COLOURS["discharge"], label=f"``{name_dch}``")
    ax.set_ylim(0, ymax_cd)
    ax.set_ylabel(unit)
    ax.legend(loc="upper left")
    ax.set_title("Charging and discharging accumulators (unsigned, monotone ↑)",
                 fontsize=9, loc="left", pad=4)
    _add_step_lines(ax, step_boundaries, step_labels, ymax_cd)
    ax.set_xticks([])

    # ------------------------------------------------------------------
    # Panel 3 — net  (signed)
    # ------------------------------------------------------------------
    ax = axes[2]
    ax.plot(t, net, color=COLOURS["net"], label=f"``{name_net}``")
    _zero_line(ax)
    ax.fill_between(t, net, 0, where=net >= 0,
                    alpha=0.12, color=COLOURS["charge"])
    ax.fill_between(t, net, 0, where=net < 0,
                    alpha=0.12, color=COLOURS["discharge"])
    lim = max(abs(ymin_net), abs(ymax_net))
    ax.set_ylim(-lim, lim)
    ax.set_ylabel(unit)
    ax.legend(loc="upper left")
    ax.set_title(f"Net {quantity} = charging − discharging  (signed)",
                 fontsize=9, loc="left", pad=4)
    _add_step_lines(ax, step_boundaries, step_labels, lim)
    ax.set_xticks([])

    # ------------------------------------------------------------------
    # Panel 4 — cumulative ∫ I dt  (signed)
    # ------------------------------------------------------------------
    ax = axes[3]
    ax.plot(t, cum, color=COLOURS["cumulative"], label=f"``{name_cum}``")
    _zero_line(ax)
    ax.fill_between(t, cum, 0, where=cum >= 0,
                    alpha=0.12, color=COLOURS["charge"])
    ax.fill_between(t, cum, 0, where=cum < 0,
                    alpha=0.12, color=COLOURS["discharge"])
    ax.set_ylim(-lim, lim)
    ax.set_ylabel(unit)
    ax.legend(loc="upper left")
    ax.set_title(f"Cumulative {quantity} = ∫ I dt from test start  (signed)",
                 fontsize=9, loc="left", pad=4)
    _add_step_lines(ax, step_boundaries, step_labels, lim)
    ax.set_xticks([])

    # ------------------------------------------------------------------
    # Panel 5 — step  (unsigned, resets per step)
    # ------------------------------------------------------------------
    ax = axes[4]
    ax.plot(t, stp, color=COLOURS["step"], label=f"``{name_stp}``")
    ax.set_ylim(0, ymax_stp)
    ax.set_ylabel(unit)
    ax.legend(loc="upper left")
    ax.set_title(f"Step {quantity}  (unsigned, resets to 0 at each step transition)",
                 fontsize=9, loc="left", pad=4)
    _add_step_lines(ax, step_boundaries, step_labels, ymax_stp)
    _format_time_axis(ax, t_max)

    # ------------------------------------------------------------------
    # Shared annotation
    # ------------------------------------------------------------------
    fig.suptitle(
        f"BDF {quantity.capitalize()} Quantities\n"
        f"Protocol: CC\_DCH → REST → CC\_CHG → REST → CC\_DCH",
        fontsize=10, y=0.995,
    )

    out_path = OUT_DIR / f"{quantity}_quantities.svg"
    fig.savefig(out_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    make_figure("capacity")
    make_figure("energy")
    print("Done.")
