"""
precare_graphs2.py
------------------
Displays a focused set of clinical outcome graphs from a PrecareReport
instance in a tkinter window.

Graphs shown (30-day and 90-day side by side):
  1. ROSC rate        — horizontal bar (running tally style)
  2. ROSC before PRECARE arrival   — pie chart
  3. ROSC on/after PRECARE arrival — pie chart
  4. Arterial lines inserted       — grouped bar (intra-arrest vs post-ROSC)
  5. Median time to art line       — bar with error range

Usage
-----
    from precare_graphs2 import open_outcomes_window
    from precare_DataStructure import PrecareReport

    report = PrecareReport.factory(custom_dates=False)
    # ... populate report fields ...
    open_outcomes_window(report)
"""

import tkinter as tk
from tkinter import messagebox

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Save path ─────────────────────────────────────────────────────────────────
# TODO: replace with the path supplied by the user in the wider application
SAVE_PATH = "/your/folder/path/here/PRECARE_outcomes.png"

# ── Palette ───────────────────────────────────────────────────────────────────
C30       = "#1A78C2"      # deep blue   — 30 days
C90       = "#E85D26"      # burnt orange — 90 days
C_YES     = "#2ECC71"      # green  — positive outcome
C_NO      = "#E74C3C"      # red    — negative outcome
C_NEUTRAL = "#BDC3C7"      # grey   — neutral / unknown
BG        = "#F7F9FC"
PANEL_BG  = "#FFFFFF"
GRID_COL  = "#E8ECF0"
TEXT_COL  = "#2C3E50"


def _style(ax, title: str, ylabel: str = ""):
    ax.set_facecolor(PANEL_BG)
    ax.set_title(title, fontsize=10, fontweight="bold", color=TEXT_COL, pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8, color=TEXT_COL)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    ax.yaxis.grid(True, color=GRID_COL, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID_COL)


def _safe(val, fallback=0):
    """Return val if not None, else fallback."""
    return val if val is not None else fallback


# ── Individual chart builders ─────────────────────────────────────────────────

def _draw_rosc_tally(ax, report):
    """
    Grouped bar chart showing ROSC rates for 30d and 90d side by side.
    Shows any ROSC and sustained ROSC (>20 min) as percentages,
    with the raw fraction labelled above each bar.
    """
    categories = ["Any ROSC", "Sustained ROSC\n(>20 min)"]

    # Percentages
    any_pct_30     = _safe(report.rosc_any_pct_30d)
    any_pct_90     = _safe(report.rosc_any_pct_90d)
    sus_pct_30     = _safe(report.rosc_sustained_pct_30d)
    sus_pct_90     = _safe(report.rosc_sustained_pct_90d)

    # Raw fractions for labels
    any_frac_30    = f"{_safe(report.rosc_any_num_30d)}/{_safe(report.rosc_any_den_30d)}"
    any_frac_90    = f"{_safe(report.rosc_any_num_90d)}/{_safe(report.rosc_any_den_90d)}"
    sus_frac_30    = f"{_safe(report.rosc_sustained_num_30d)}/{_safe(report.rosc_sustained_den_30d)}"
    sus_frac_90    = f"{_safe(report.rosc_sustained_num_90d)}/{_safe(report.rosc_sustained_den_90d)}"

    vals_30 = [any_pct_30, sus_pct_30]
    vals_90 = [any_pct_90, sus_pct_90]
    fracs_30 = [any_frac_30, sus_frac_30]
    fracs_90 = [any_frac_90, sus_frac_90]

    x = np.arange(len(categories))
    w = 0.32

    b30 = ax.bar(x - w/2, vals_30, w, color=C30, zorder=3, label="Last 30 Days")
    b90 = ax.bar(x + w/2, vals_90, w, color=C90, zorder=3, label="Last 90 Days")

    # Label each bar with percentage on top and fraction just above that
    for bar, pct, frac in zip(list(b30), vals_30, fracs_30):
        ax.text(bar.get_x() + bar.get_width() / 2, pct + 1.5,
                f"{pct:.0f}%\n({frac})",
                ha="center", va="bottom", fontsize=8,
                fontweight="bold", color=TEXT_COL)

    for bar, pct, frac in zip(list(b90), vals_90, fracs_90):
        ax.text(bar.get_x() + bar.get_width() / 2, pct + 1.5,
                f"{pct:.0f}%\n({frac})",
                ha="center", va="bottom", fontsize=8,
                fontweight="bold", color=TEXT_COL)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, 130)
    ax.set_ylabel("Percentage (%)", fontsize=8, color=TEXT_COL)
    ax.legend(fontsize=8, framealpha=0.9, edgecolor=GRID_COL)
    _style(ax, "ROSC Rates")


def _draw_pie(ax, achieved, total, title, color_yes=C_YES, color_no=C_NO):
    """Generic pie chart: achieved vs not achieved."""
    not_achieved = max(total - achieved, 0)

    if total == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, fontsize=9, color=TEXT_COL)
        ax.axis("off")
    else:
        pct = achieved / total * 100
        sizes  = [achieved, not_achieved]
        colors = [color_yes, C_NEUTRAL]
        explode = (0.04, 0)

        wedges, texts, autotexts = ax.pie(
            sizes,
            explode=explode,
            colors=colors,
            autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
            startangle=90,
            wedgeprops={"linewidth": 1.5, "edgecolor": BG},
            textprops={"fontsize": 8, "color": TEXT_COL},
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_fontweight("bold")
            at.set_color("white")

        ax.text(0, -1.35, f"{achieved} of {total} patients",
                ha="center", fontsize=8, color=TEXT_COL)

    ax.set_title(title, fontsize=10, fontweight="bold",
                 color=TEXT_COL, pad=8)
    ax.set_facecolor(PANEL_BG)


def _draw_art_lines(ax, report):
    """Grouped bar: intra-arrest vs post-ROSC art line insertions, 30d and 90d."""
    categories  = ["Intra-arrest", "Post-ROSC"]
    vals_30d    = [_safe(report.art_line_intra_arrest_30d),
                   _safe(report.art_line_post_rosc_30d)]
    vals_90d    = [_safe(report.art_line_intra_arrest_90d),
                   _safe(report.art_line_post_rosc_90d)]

    x = np.arange(len(categories))
    w = 0.32
    b30 = ax.bar(x - w/2, vals_30d, w, color=C30, zorder=3, label="30 Days")
    b90 = ax.bar(x + w/2, vals_90d, w, color=C90, zorder=3, label="90 Days")

    for bar in list(b30) + list(b90):
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.1,
                    str(int(h)), ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=TEXT_COL)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, max(max(vals_30d), max(vals_90d)) * 1.35 + 1)
    ax.legend(fontsize=8, framealpha=0.8, edgecolor=GRID_COL)
    _style(ax, "Arterial Lines Inserted", "Count")


def _draw_art_line_time(ax, report):
    """
    Bar chart of median time to arterial line transduction,
    with range shown as error bars.
    """
    labels  = ["30 Days", "90 Days"]
    medians = [_safe(report.art_line_time_to_transduced_30d),
               _safe(report.art_line_time_to_transduced_90d)]
    lows    = [_safe(report.art_line_time_to_transduced_30d_low),
               _safe(report.art_line_time_to_transduced_90d_low)]
    highs   = [_safe(report.art_line_time_to_transduced_30d_high),
               _safe(report.art_line_time_to_transduced_90d_high)]

    colors  = [C30, C90]
    x       = np.arange(len(labels))

    for i, (med, lo, hi, col) in enumerate(zip(medians, lows, highs, colors)):
        err_lo = max(med - lo, 0)
        err_hi = max(hi - med, 0)
        ax.bar(x[i], med, 0.4, color=col, zorder=3,
               yerr=[[err_lo], [err_hi]],
               error_kw={"ecolor": TEXT_COL, "capsize": 6,
                         "elinewidth": 1.5, "capthick": 1.5},
               label=labels[i])
        ax.text(x[i], med + err_hi + 0.4,
                f"{med:.0f} min\n({lo:.0f}–{hi:.0f})",
                ha="center", va="bottom", fontsize=8,
                fontweight="bold", color=TEXT_COL)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    top = max(h + (h - l) for h, l in zip(highs, lows)) + 5
    ax.set_ylim(0, max(top, 5))
    _style(ax, "Median Time to Art Line\nTransduction (with range)", "Minutes")


# ── Main figure builder ───────────────────────────────────────────────────────

def build_outcomes_figure(report) -> plt.Figure:
    """
    Build and return a matplotlib Figure populated from the given PrecareReport.

    Layout  (2 rows × 3 cols):
      [0,0] ROSC tally (spans both cols 0–1)   [0,2] Art lines bar
      [1,0] Pie: ROSC before PRECARE            [1,1] Pie: ROSC on/after PRECARE   [1,2] Art line time
    """
    fig = plt.figure(figsize=(16, 11), facecolor=BG)
    fig.suptitle(report.report_title(),
                 fontsize=15, fontweight="bold", color=TEXT_COL, y=0.98)

    gs = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.55, wspace=0.38,
        left=0.07, right=0.97, top=0.92, bottom=0.16,
    )

    # Row 0 ───────────────────────────────────────────────────────────────────
    # ROSC tally — spans columns 0 and 1
    ax_rosc = fig.add_subplot(gs[0, 0:2])
    _draw_rosc_tally(ax_rosc, report)

    # Art lines bar — column 2
    ax_al = fig.add_subplot(gs[0, 2])
    _draw_art_lines(ax_al, report)

    # Row 1 ───────────────────────────────────────────────────────────────────
    # Calculate denominators for the pie charts
    # Values for the three ROSC outcome segments
    never_30  = _safe(report.rosc_never_30d)
    before_30 = _safe(report.rosc_before_precare_30d)
    after_30  = _safe(report.rosc_on_after_precare_30d)

    never_90  = _safe(report.rosc_never_90d)
    before_90 = _safe(report.rosc_before_precare_90d)
    after_90  = _safe(report.rosc_on_after_precare_90d)

    pie_colors  = [C_NO, C30, C_YES]   # never=red, before=blue, on/after=green
    pie_labels  = ["Never achieved ROSC", "ROSC before PRECARE", "ROSC on/after PRECARE"]

    def _draw_rosc_pie(ax, never, before, after, title):
        sizes = [never, before, after]
        total = sum(sizes)
        if total > 0:
            wedges, _, autotexts = ax.pie(
                sizes,
                colors=pie_colors,
                autopct=lambda p: f"{p:.0f}%" if p > 4 else "",
                startangle=90,
                wedgeprops={"linewidth": 1.5, "edgecolor": BG},
                textprops={"fontsize": 9, "color": "white", "fontweight": "bold"},
            )
            for at in autotexts:
                at.set_color("white")
                at.set_fontweight("bold")
            ax.legend(
                wedges,
                [f"{pie_labels[0]}  ({never})",
                 f"{pie_labels[1]}  ({before})",
                 f"{pie_labels[2]}  ({after})"],
                loc="lower center",
                bbox_to_anchor=(0.5, -0.22),
                fontsize=7.5,
                framealpha=0.9,
                edgecolor=GRID_COL,
                ncol=1,
            )
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, fontsize=9, color=TEXT_COL)
            ax.axis("off")
        ax.set_title(title, fontsize=10, fontweight="bold", color=TEXT_COL, pad=8)
        ax.set_facecolor(PANEL_BG)

    # Pie: 30 day ROSC breakdown — column 0
    ax_pie1 = fig.add_subplot(gs[1, 0])
    _draw_rosc_pie(ax_pie1, never_30, before_30, after_30, "ROSC Outcome\nLast 30 Days")

    # Pie: 90 day ROSC breakdown — column 1
    ax_pie2 = fig.add_subplot(gs[1, 1])
    _draw_rosc_pie(ax_pie2, never_90, before_90, after_90, "ROSC Outcome\nLast 90 Days")

    # Art line time — column 2
    ax_alt = fig.add_subplot(gs[1, 2])
    _draw_art_line_time(ax_alt, report)

    return fig


# ── Save callback ─────────────────────────────────────────────────────────────

def _save_report(fig):
    """Save the figure to the hardcoded SAVE_PATH and show a confirmation."""
    try:
        fig.savefig(SAVE_PATH, dpi=150, bbox_inches="tight", facecolor=BG)
        messagebox.showinfo("Saved", f"Report saved to:\n{SAVE_PATH}")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Could not save report:\n{e}")


# ── Public entry point ────────────────────────────────────────────────────────

def open_outcomes_window(report, master=None):
    """
    Open the outcomes graph window.

    Parameters
    ----------
    report : PrecareReport
        A populated PrecareReport instance.
    master : tk.Widget, optional
        Parent widget. If None, a new Tk root window is created.
        Pass your existing root or frame when embedding in a larger app.
    """
    own_root = master is None
    root = tk.Tk() if own_root else tk.Toplevel(master)
    root.title("PRECARE — Clinical Outcomes")
    root.configure(bg=BG)
    root.minsize(900, 620)      # prevents the window being resized so small the button disappears

    fig = build_outcomes_figure(report)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    # fill=BOTH + expand=True lets the canvas grow, but the button frame
    # is packed first (side=BOTTOM) so it always gets its space first
    btn_frame = tk.Frame(root, bg="#EAECEE", pady=8)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    save_btn = tk.Button(
        btn_frame,
        text="💾  Save Report",
        command=lambda: _save_report(fig),
        font=("Helvetica", 11, "bold"),
        bg=C30, fg="white",
        activebackground="#135a94", activeforeground="white",
        relief=tk.FLAT, padx=20, pady=7, cursor="hand2",
    )
    save_btn.pack()

    if own_root:
        root.mainloop()


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from precare_DataStructure import PrecareReport

    r = PrecareReport.factory(custom_dates=False)

    # Dispatch
    r.patients_with_interventions_30d = 5
    r.patients_with_interventions_90d = 24

    # Cardiac arrests (denominators for pies)
    r.cardiac_arrests_30d = 6
    r.cardiac_arrests_90d = 29

    # ROSC rates
    r.rosc_any_num_30d = 6;  r.rosc_any_den_30d = 6;  r.rosc_any_pct_30d = 100.0
    r.rosc_any_num_90d = 21; r.rosc_any_den_90d = 34; r.rosc_any_pct_90d = 61.76

    # ROSC timing breakdown
    r.rosc_before_precare_30d    = 0;  r.rosc_before_precare_90d    = 3
    r.rosc_on_after_precare_30d  = 4;  r.rosc_on_after_precare_90d  = 15

    # Arterial lines
    r.art_line_intra_arrest_30d = 2;  r.art_line_intra_arrest_90d = 8
    r.art_line_post_rosc_30d    = 2;  r.art_line_post_rosc_90d    = 7

    # Median time to art line transduced
    r.art_line_time_to_transduced_30d      = 8.0
    r.art_line_time_to_transduced_30d_low  = 8.0
    r.art_line_time_to_transduced_30d_high = 8.0
    r.art_line_time_to_transduced_90d      = 13.0
    r.art_line_time_to_transduced_90d_low  = 8.0
    r.art_line_time_to_transduced_90d_high = 34.0

    open_outcomes_window(r)
