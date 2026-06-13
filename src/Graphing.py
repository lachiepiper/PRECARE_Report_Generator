"""
precare_graphs.py
-----------------
Graphical outcomes report for WSLHD PRECARE.

Renders four charts in a single Tkinter window:
    1.  ROSC Rates                   – bar chart (% + absolute fraction labels)
    2.  ROSC & PRECARE Arrival       – two pie charts (30-day | 90-day)
    3.  Arterial Lines Inserted      – bar chart (counts)
    4.  Median Time to Art Line      – bar chart with range (IQR) error bars

Usage from another file
-----------------------
    from precare_graphs import open_graph
    from precare_DataStructure import PrecareReport

    report = PrecareReport()
    # … populate report fields …
    open_graph(report)          # opens the Tkinter window (blocking)

Dependencies
------------
    pip install matplotlib
    (tkinter ships with the standard CPython distribution)
"""

# ── Standard-library imports ─────────────────────────────────────────────────
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import date, timedelta

# ── Third-party imports ──────────────────────────────────────────────────────
import matplotlib
matplotlib.use("TkAgg")                     # use the Tk rendering back-end
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ── Typing ────────────────────────────────────────────────────────────────────
from typing import Optional

# ── Local import (the data-structure file must be on the Python path) ─────────
# from precare_DataStructure import PrecareReport   # uncomment if needed


# ═════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE
# ═════════════════════════════════════════════════════════════════════════════

WINDOW_BG         = "#D6EAF8"       # light blue – entire Tk window background
FIGURE_FACECOLOUR = "#D6EAF8"       # same colour for the Matplotlib figure
AXES_FACECOLOUR   = "#EBF5FB"       # slightly lighter blue for the chart area

COLOUR_30D        = "#2980B9"       # medium blue   – represents 30-day data
COLOUR_90D        = "#1A5276"       # dark blue     – represents 90-day data

# Pie-chart slice colours
PIE_BEFORE        = "#27AE60"       # green  – ROSC before PRECARE arrival
PIE_ON_AFTER      = "#2980B9"       # blue   – ROSC on or after PRECARE arrival
PIE_NEVER         = "#C0392B"       # red    – ROSC never achieved

GRID_COLOUR       = "#ABEBC6"       # very light mint grid lines


# ═════════════════════════════════════════════════════════════════════════════
# HELPER UTILITIES
# ═════════════════════════════════════════════════════════════════════════════

def _safe(value, default=0):
    """Return *value* if it is not None, otherwise *default*."""
    return value if value is not None else default


def _build_title(report) -> str:
    """
    Build the main window title string:
        "WSLHD PRECARE outcomes report [today-90days] to [today]"
    """
    today      = date.today()
    start_date = today - timedelta(days=90)

    # Format as DD/MM/YYYY (Australian convention)
    today_str = today.strftime("%d/%m/%Y")
    start_str = start_date.strftime("%d/%m/%Y")

    return f"WSLHD PRECARE outcomes report  {start_str}  to  {today_str}"


# ═════════════════════════════════════════════════════════════════════════════
# GRAPH 1 – ROSC RATES (bar chart, % with absolute fraction labels)
# ═════════════════════════════════════════════════════════════════════════════

def _draw_rosc_rates(ax, report):
    """
    Draw a grouped bar chart comparing 30-day vs 90-day ROSC-at-any-time rates.

    Each bar shows the percentage on its face.
    The absolute fraction (numerator/denominator) is shown above the bar.
    """
    ax.set_facecolor(AXES_FACECOLOUR)
    ax.set_title("ROSC Rates", fontsize=13, fontweight="bold", pad=10)

    # ── Pull values from the report ──────────────────────────────────────────
    pct_30  = _safe(report.rosc_any_pct_30d,  0.0)
    pct_90  = _safe(report.rosc_any_pct_90d,  0.0)
    num_30  = _safe(report.rosc_any_num_30d,   0)
    den_30  = _safe(report.rosc_any_den_30d,   0)
    num_90  = _safe(report.rosc_any_num_90d,   0)
    den_90  = _safe(report.rosc_any_den_90d,   0)

    # ── Bar positions ────────────────────────────────────────────────────────
    categories = ["ROSC at\nAny Time"]
    x          = [0]          # single category; bars sit side-by-side at x=0
    bar_width  = 0.30

    bar_30 = ax.bar(
        [xi - bar_width / 2 for xi in x],
        [pct_30],
        width=bar_width,
        color=COLOUR_30D,
        label="Last 30 Days",
        zorder=3,
    )
    bar_90 = ax.bar(
        [xi + bar_width / 2 for xi in x],
        [pct_90],
        width=bar_width,
        color=COLOUR_90D,
        label="Last 90 Days",
        zorder=3,
    )

    # ── Percentage labels centred inside each bar ────────────────────────────
    for bar, pct in zip(bar_30, [pct_30]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"{pct:.1f}%",
            ha="center", va="center",
            color="white", fontsize=11, fontweight="bold",
        )
    for bar, pct in zip(bar_90, [pct_90]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"{pct:.1f}%",
            ha="center", va="center",
            color="white", fontsize=11, fontweight="bold",
        )

    # ── Absolute fraction labels above each bar ──────────────────────────────
    LABEL_OFFSET = 2.5      # percentage points above bar top

    for bar, num, den in zip(bar_30, [num_30], [den_30]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + LABEL_OFFSET,
            f"{num}/{den}",
            ha="center", va="bottom",
            color=COLOUR_30D, fontsize=10, fontweight="bold",
        )
    for bar, num, den in zip(bar_90, [num_90], [den_90]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + LABEL_OFFSET,
            f"{num}/{den}",
            ha="center", va="bottom",
            color=COLOUR_90D, fontsize=10, fontweight="bold",
        )

    # ── Axes formatting ──────────────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel("ROSC Rate (%)", fontsize=10)
    ax.set_ylim(0, 110)
    ax.yaxis.grid(True, color=GRID_COLOUR, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ═════════════════════════════════════════════════════════════════════════════
# GRAPH 2 – ROSC & PRECARE ARRIVAL (two pie charts)
# ═════════════════════════════════════════════════════════════════════════════

def _draw_rosc_pie(ax, before, on_after, never, period_label):
    """
    Draw a single pie chart for one time period.

    Parameters
    ----------
    ax           : Matplotlib Axes object
    before       : int – ROSC before PRECARE arrival
    on_after     : int – ROSC on or after PRECARE arrival
    never        : int – ROSC never achieved
    period_label : str – e.g. "Last 30 Days"
    """
    ax.set_facecolor(AXES_FACECOLOUR)
    ax.set_title(period_label, fontsize=11, fontweight="bold", pad=8)

    values = [before, on_after, never]
    labels = [
        "ROSC Before\nPRECARE Arrival",
        "ROSC On / After\nPRECARE Arrival",
        "ROSC Not\nAchieved",
    ]
    colours = [PIE_BEFORE, PIE_ON_AFTER, PIE_NEVER]

    total = sum(values)

    if total == 0:
        # No data – display a placeholder
        ax.text(
            0.5, 0.5,
            "No data\navailable",
            ha="center", va="center",
            transform=ax.transAxes,
            fontsize=11, color="#555555",
        )
        ax.axis("off")
        return

    # Build autopct string: "X.X%\n(count)"
    def make_autopct(values):
        def autopct(pct):
            absolute = round(pct / 100 * total)
            return f"{pct:.1f}%\n(n={absolute})"
        return autopct

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,            # labels handled via legend
        colors=colours,
        autopct=make_autopct(values),
        startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
        textprops=dict(fontsize=9),
    )

    # Make autopct text white for readability on coloured wedges
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(9)

    # Legend below the pie
    legend_patches = [
        mpatches.Patch(color=colours[i], label=f"{labels[i]}")
        for i in range(len(labels))
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.28),
        fontsize=8,
        ncol=1,
        framealpha=0.8,
    )


def _draw_rosc_pie_group(ax_left, ax_right, report):
    """
    Draw both 30-day and 90-day ROSC/PRECARE-arrival pie charts
    in the two axes provided.
    """
    # Shared super-title is added by the caller at figure level

    # 30-day values
    before_30  = _safe(report.rosc_before_precare_30d, 0)
    on_after_30 = _safe(report.rosc_on_after_precare_30d, 0)
    never_30   = _safe(report.rosc_never_30d, 0)

    # 90-day values
    before_90  = _safe(report.rosc_before_precare_90d, 0)
    on_after_90 = _safe(report.rosc_on_after_precare_90d, 0)
    never_90   = _safe(report.rosc_never_90d, 0)

    _draw_rosc_pie(ax_left,  before_30, on_after_30, never_30, "Last 30 Days")
    _draw_rosc_pie(ax_right, before_90, on_after_90, never_90, "Last 90 Days")


# ═════════════════════════════════════════════════════════════════════════════
# GRAPH 3 – ARTERIAL LINES INSERTED (grouped bar chart, counts)
# ═════════════════════════════════════════════════════════════════════════════

def _draw_arterial_lines(ax, report):
    """
    Draw a grouped bar chart comparing 30-day vs 90-day counts for:
      • Radial Arterial Lines
      • Femoral Arterial Lines
    """
    ax.set_facecolor(AXES_FACECOLOUR)
    ax.set_title("Number of Arterial Lines Inserted", fontsize=13, fontweight="bold", pad=10)

    # ── Data ────────────────────────────────────────────────────────────────
    radial_30  = _safe(report.radial_art_line_30d, 0)
    radial_90  = _safe(report.radial_art_line_90d, 0)
    fem_30     = _safe(report.fem_art_line_30d,    0)
    fem_90     = _safe(report.fem_art_line_90d,    0)

    # ── Bar layout ──────────────────────────────────────────────────────────
    categories  = ["Radial Arterial Line", "Femoral Arterial Line"]
    x           = [0, 1]
    bar_width   = 0.30

    bars_30 = ax.bar(
        [xi - bar_width / 2 for xi in x],
        [radial_30, fem_30],
        width=bar_width,
        color=COLOUR_30D,
        label="Last 30 Days",
        zorder=3,
    )
    bars_90 = ax.bar(
        [xi + bar_width / 2 for xi in x],
        [radial_90, fem_90],
        width=bar_width,
        color=COLOUR_90D,
        label="Last 90 Days",
        zorder=3,
    )

    # ── Count labels above bars ──────────────────────────────────────────────
    LABEL_OFFSET = 0.05     # units above bar top

    for bar in bars_30:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + LABEL_OFFSET,
            str(int(height)),
            ha="center", va="bottom",
            color=COLOUR_30D, fontsize=10, fontweight="bold",
        )
    for bar in bars_90:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + LABEL_OFFSET,
            str(int(height)),
            ha="center", va="bottom",
            color=COLOUR_90D, fontsize=10, fontweight="bold",
        )

    # ── Axes formatting ──────────────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel("Number of Lines Inserted", fontsize=10)
    max_val = max(radial_30, radial_90, fem_30, fem_90, 1)
    ax.set_ylim(0, max_val * 1.35)
    ax.yaxis.grid(True, color=GRID_COLOUR, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ═════════════════════════════════════════════════════════════════════════════
# GRAPH 4 – MEDIAN TIME TO ARTERIAL LINE (bar + error bars for range)
# ═════════════════════════════════════════════════════════════════════════════

def _draw_art_line_time(ax, report):
    """
    Draw a bar chart showing median time from PRECARE arrival to arterial-line
    transduced, with asymmetric error bars representing the reported range.

    Bar height  = median value  (decimal minutes)
    Error bars  = low / high range values
    """
    ax.set_facecolor(AXES_FACECOLOUR)
    ax.set_title(
        "Median Time to Arterial Line\nTransduced After PRECARE Arrival",
        fontsize=13, fontweight="bold", pad=10,
    )

    # ── Data ────────────────────────────────────────────────────────────────
    median_30 = _safe(report.art_line_time_to_transduced_30d,      0.0)
    low_30    = _safe(report.art_line_time_to_transduced_30d_low,  0.0)
    high_30   = _safe(report.art_line_time_to_transduced_30d_high, 0.0)

    median_90 = _safe(report.art_line_time_to_transduced_90d,      0.0)
    low_90    = _safe(report.art_line_time_to_transduced_90d_low,  0.0)
    high_90   = _safe(report.art_line_time_to_transduced_90d_high, 0.0)

    # Asymmetric error bars: [below-bar, above-bar]
    err_30 = [[median_30 - low_30], [high_30 - median_30]]
    err_90 = [[median_90 - low_90], [high_90 - median_90]]

    # Guard against negative error values (can arise when data is None/0)
    err_30 = [[max(0, v) for v in side] for side in err_30]
    err_90 = [[max(0, v) for v in side] for side in err_90]

    # ── Bar layout ──────────────────────────────────────────────────────────
    categories = ["Median Time\nto Art Line\nTransduced"]
    x          = [0]
    bar_width  = 0.30

    bar_30 = ax.bar(
        [xi - bar_width / 2 for xi in x],
        [median_30],
        width=bar_width,
        color=COLOUR_30D,
        label="Last 30 Days",
        zorder=3,
        yerr=err_30,
        error_kw=dict(
            elinewidth=2,
            ecolor="#1A5276",
            capsize=7,
            capthick=2,
            zorder=4,
        ),
    )
    bar_90 = ax.bar(
        [xi + bar_width / 2 for xi in x],
        [median_90],
        width=bar_width,
        color=COLOUR_90D,
        label="Last 90 Days",
        zorder=3,
        yerr=err_90,
        error_kw=dict(
            elinewidth=2,
            ecolor="#85C1E9",
            capsize=7,
            capthick=2,
            zorder=4,
        ),
    )

    # ── Median value labels above (or inside) each bar ───────────────────────
    def _fmt_min(val):
        """Format decimal minutes as 'M:SS' for display."""
        total_seconds = round(val * 60)
        mins  = total_seconds // 60
        secs  = total_seconds % 60
        return f"{mins}:{secs:02d} min"

    LABEL_OFFSET = max(high_30, high_90, 0.01) * 0.08  # dynamic offset

    for bar, median, low, high in zip(bar_30, [median_30], [low_30], [high_30]):
        # Label: median inside bar, range below the top cap
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            _fmt_min(median),
            ha="center", va="center",
            color="white", fontsize=9, fontweight="bold",
        )
        # Values annotation above error bar cap
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            high + LABEL_OFFSET,
            f"{_fmt_min(low)} – {_fmt_min(high)}",
            ha="center", va="bottom",
            color=COLOUR_30D, fontsize=8,
        )

    for bar, median, low, high in zip(bar_90, [median_90], [low_90], [high_90]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            _fmt_min(median),
            ha="center", va="center",
            color="white", fontsize=9, fontweight="bold",
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            high + LABEL_OFFSET,
            f"{_fmt_min(low)} – {_fmt_min(high)}",
            ha="center", va="bottom",
            color=COLOUR_90D, fontsize=8,
        )

    # ── Axes formatting ──────────────────────────────────────────────────────
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel("Time (decimal minutes)", fontsize=10)
    top_limit = max(high_30, high_90, 1) * 1.6
    ax.set_ylim(0, top_limit)
    ax.yaxis.grid(True, color=GRID_COLOUR, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ═════════════════════════════════════════════════════════════════════════════
# SAVE CHART FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def _save_chart(figure):
    """
    Open a file-save dialogue and write the current figure to the chosen path.

    Supported formats: PNG, PDF, SVG (all handled transparently by Matplotlib).
    """
    file_path = filedialog.asksaveasfilename(
        title="Save PRECARE Outcomes Chart",
        initialfile="PRECARE Report Data"
        defaultextension=".png",
        filetypes=[
            ("PNG image",        "*.png"),
            ("PDF document",     "*.pdf"),
            ("SVG vector image", "*.svg"),
            ("All files",        "*.*"),
        ],
    )

    if not file_path:
        # User cancelled the dialogue – do nothing
        return

    try:
        figure.savefig(
            file_path,
            dpi=200,
            bbox_inches="tight",
            facecolor=FIGURE_FACECOLOUR,
        )
        messagebox.showinfo(
            "Chart Saved",
            f"Chart successfully saved to:\n{file_path}",
        )
    except Exception as exc:
        messagebox.showerror(
            "Save Error",
            f"Could not save chart.\n\nError details:\n{exc}",
        )


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT  –  open_graph()
# ═════════════════════════════════════════════════════════════════════════════

def open_graph(report):
    """
    Build and display the WSLHD PRECARE outcomes report window.

    Parameters
    ----------
    report : PrecareReport
        A populated (or partially populated) PrecareReport instance.
        Fields that are None will display as zeros.

    The window is modal (Tkinter mainloop); execution resumes in the calling
    script only after the user closes the window.
    """

    # ── Build the report title with date range ───────────────────────────────
    title_text = _build_title(report)

    # ── Create Tk root window ────────────────────────────────────────────────
    root = tk.Tk()
    root.title("WSLHD PRECARE Outcomes Report")
    root.configure(bg=WINDOW_BG)

    # Request a large window; the layout will scale to fill it
    root.geometry("1300x860")
    root.minsize(900, 640)

    # ── Main heading label ───────────────────────────────────────────────────
    heading_label = tk.Label(
        root,
        text=title_text,
        font=("Helvetica", 14, "bold"),
        bg=WINDOW_BG,
        fg="#1A3F6B",       # deep navy text
        wraplength=1250,    # wrap if window is narrow
        justify="center",
        pady=8,
    )
    heading_label.pack(side=tk.TOP, fill=tk.X, padx=15)

    # ── Thin separator line ──────────────────────────────────────────────────
    separator = tk.Frame(root, height=2, bg="#2980B9")
    separator.pack(fill=tk.X, padx=15, pady=(0, 4))

    # ── Create Matplotlib figure ─────────────────────────────────────────────
    #
    # Layout:
    #   Row 0 (top):    [ Graph 1: ROSC Rates ] [ Graph 2a: Pie 30d ] [ Graph 2b: Pie 90d ]
    #   Row 1 (bottom): [ Graph 3: Art Lines  ] [ Graph 4: Art Line Time (wide)            ]
    #
    # We use a 2×3 grid and merge the bottom-right two cells for Graph 4.

    figure = plt.Figure(
        figsize=(14, 8.5),
        facecolor=FIGURE_FACECOLOUR,
        tight_layout=False,
    )

    # Adjust subplot spacing to avoid chart/label collisions
    figure.subplots_adjust(
        left=0.06,
        right=0.97,
        top=0.90,
        bottom=0.12,
        hspace=0.55,
        wspace=0.38,
    )

    # -- Row 0: three columns -------------------------------------------------
    ax_rosc_bar   = figure.add_subplot(2, 3, 1)   # Graph 1
    ax_pie_30d    = figure.add_subplot(2, 3, 2)   # Graph 2a
    ax_pie_90d    = figure.add_subplot(2, 3, 3)   # Graph 2b

    # -- Row 1: left cell + merged middle-right cells -------------------------
    ax_art_lines  = figure.add_subplot(2, 3, 4)   # Graph 3

    # Merge positions 5 and 6 for Graph 4 (wider bar + annotation)
    ax_art_time   = figure.add_subplot(2, 3, (5, 6))  # Graph 4

    # ── Super-title for the two pie charts ───────────────────────────────────
    # The two pie axes occupy subplot positions 2 and 3 in a 2×3 grid.
    # We calculate the midpoint between their left and right edges in figure
    # coordinates so the title is perfectly centred between the two pies,
    # regardless of the subplot spacing settings above.
    ax_pie_30d.figure.canvas.draw()   # ensure axes positions are finalised
    bbox_left  = ax_pie_30d.get_position()
    bbox_right = ax_pie_90d.get_position()
    pie_centre_x = (bbox_left.x0 + bbox_right.x1) / 2
    pie_top_y    = bbox_left.y1 + 0.04   # sit just above the pie axes

    figure.text(
        pie_centre_x, pie_top_y,
        "ROSC Timing Relative to PRECARE Arrival",
        ha="center", va="bottom",
        fontsize=13, fontweight="bold",
        color="#1A3F6B",
    )

    # ── Draw each graph ──────────────────────────────────────────────────────
    _draw_rosc_rates(ax_rosc_bar, report)
    _draw_rosc_pie_group(ax_pie_30d, ax_pie_90d, report)
    _draw_arterial_lines(ax_art_lines, report)
    _draw_art_line_time(ax_art_time, report)

    # ── Embed figure in Tk window ────────────────────────────────────────────
    canvas = FigureCanvasTkAgg(figure, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.configure(bg=WINDOW_BG)
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))
    canvas.draw()

    # ── Top Right Save Button ────────────────────────────────────────────────
    save_button = tk.Button(
        root,
        text="💾  Save Chart",
        font=("Helvetica", 11, "bold"),
        bg="#2980B9",
        fg="white",
        activebackground="#1A5276",
        activeforeground="white",
        relief=tk.FLAT,
        padx=20,
        pady=6,
        cursor="hand2",
        command=lambda: _save_chart(figure),
    )
    # Use absolute positioning so the header stays perfectly centered
    save_button.place(relx=1.0, rely=0.0, x=-15, y=10, anchor="ne")

    # ── Start Tk event loop ──────────────────────────────────────────────────
    root.mainloop()


# ═════════════════════════════════════════════════════════════════════════════
# STANDALONE TEST – run this file directly to see sample data
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Quick smoke-test with synthetic data so you can verify the layout without
    needing the full data-pipeline to be running.

    Replace the values below with real data when integrating.
    """

    # Import the dataclass – adjust the path / module name if yours differs
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))

    # Create a dummy report using a plain namespace so the file is self-contained
    # (swap this out for your real PrecareReport import when integrating)
    from types import SimpleNamespace

    report = SimpleNamespace(
        # ── ROSC Rates ──────────────────────────────────────────────────────
        rosc_any_num_30d  = 7,
        rosc_any_den_30d  = 12,
        rosc_any_pct_30d  = 58.3,

        rosc_any_num_90d  = 34,
        rosc_any_den_90d  = 52,
        rosc_any_pct_90d  = 65.4,

        # ── ROSC & PRECARE Arrival ───────────────────────────────────────────
        rosc_before_precare_30d    = 3,
        rosc_on_after_precare_30d  = 4,
        rosc_never_30d             = 5,

        rosc_before_precare_90d    = 14,
        rosc_on_after_precare_90d  = 20,
        rosc_never_90d             = 18,

        # ── Arterial Lines ───────────────────────────────────────────────────
        radial_art_line_30d  = 5,
        radial_art_line_90d  = 21,
        fem_art_line_30d     = 2,
        fem_art_line_90d     = 9,

        # ── Arterial Line Time ───────────────────────────────────────────────
        art_line_time_to_transduced_30d       = 7.5,
        art_line_time_to_transduced_30d_low   = 5.0,
        art_line_time_to_transduced_30d_high  = 11.0,

        art_line_time_to_transduced_90d       = 8.2,
        art_line_time_to_transduced_90d_low   = 4.5,
        art_line_time_to_transduced_90d_high  = 13.5,
    )

    open_graph(report)
