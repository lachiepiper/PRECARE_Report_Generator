import tkinter as tk
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ── Colour palette ────────────────────────────────────────────────────────────
C30  = "#2196F3"
C90  = "#FF7043"
GRID = "#E0E0E0"
BG   = "#FAFAFA"

# ── Helpers ───────────────────────────────────────────────────────────────────
def to_min(mmss):
    m, s = map(int, mmss.split(":"))
    return m + s / 60

def style_ax(ax, title):
    ax.set_facecolor(BG)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

legend_patches = [
    mpatches.Patch(color=C30, label="Last 30 Days"),
    mpatches.Patch(color=C90, label="Last 90 Days"),
]

w = 0.32  # bar width

# ── Build figure ──────────────────────────────────────────────────────────────
def build_figure():
    fig = plt.figure(figsize=(18, 16), facecolor=BG)
    fig.suptitle("PRECARE Activity Report", fontsize=18, fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(3, 3, figure=fig,
                           hspace=0.55, wspace=0.38,
                           left=0.06, right=0.97, top=0.93, bottom=0.05)

    # ── 1. Patient Volume ────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "Patient Volume")
    labels = ["Patients with\nInterventions", "Cardiac Arrest\nCases"]

    vals30 = [5, 6];  vals90 = [24, 29]

    x = np.arange(len(labels))
    b30 = ax1.bar(x - w/2, vals30, w, color=C30, zorder=3)
    b90 = ax1.bar(x + w/2, vals90, w, color=C90, zorder=3)
    for bar in list(b30) + list(b90):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
                 str(int(bar.get_height())), ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax1.set_xticks(x); ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_ylabel("Count"); ax1.set_ylim(0, 36)
    ax1.legend(handles=legend_patches, fontsize=8)

    # ── 2. ROSC Rates ────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "ROSC Rates (%)")
    labels_r = ["Any ROSC", "Sustained ROSC\n(>20 min)"]
    pct30 = [100.0, 50.0];  pct90 = [61.76, 35.29]
    x = np.arange(len(labels_r))
    b30r = ax2.bar(x - w/2, pct30, w, color=C30, zorder=3)
    b90r = ax2.bar(x + w/2, pct90, w, color=C90, zorder=3)
    for bar, num, den in zip(list(b30r) + list(b90r),
                              [6, 3, 21, 12], [6, 6, 34, 34]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                 f"{num}/{den}\n({bar.get_height():.0f}%)",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax2.set_xticks(x); ax2.set_xticklabels(labels_r, fontsize=9)
    ax2.set_ylabel("Percentage (%)"); ax2.set_ylim(0, 130)
    ax2.legend(handles=legend_patches, fontsize=8)

    # ── 3. Aeromedical Interventions ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    style_ax(ax3, "Aeromedical Interventions")
    interventions = ["RSI", "Thoracostomy", "Fem Art\nLine", "Radial Art\nLine",
                     "Assisted\nETT", "Echo /\nUS", "Intra-arrest\nTOE", "TTE", "POC\nABG"]
    i30 = [0, 0, 2, 2, 0, 2, 0, 1, 0]
    i90 = [1, 0, 10, 6, 0, 12, 6, 6, 2]
    x = np.arange(len(interventions))
    ax3.bar(x - w/2, i30, w, color=C30, zorder=3)
    ax3.bar(x + w/2, i90, w, color=C90, zorder=3)
    ax3.set_xticks(x); ax3.set_xticklabels(interventions, fontsize=7)
    ax3.set_ylabel("Count"); ax3.set_ylim(0, 16)
    ax3.legend(handles=legend_patches, fontsize=8)

    # ── 4. Arterial Lines ────────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    style_ax(ax4, "Arterial Lines")
    al_labels = ["Intra-arrest\nInsertions", "Post-ROSC\nInsertions"]
    al30 = [2, 2];  al90 = [8, 7]
    x = np.arange(len(al_labels))
    b30 = ax4.bar(x - w/2, al30, w, color=C30, zorder=3)
    b90 = ax4.bar(x + w/2, al90, w, color=C90, zorder=3)
    for bar in list(b30) + list(b90):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                 str(int(bar.get_height())), ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax4.set_xticks(x); ax4.set_xticklabels(al_labels, fontsize=9)
    ax4.set_ylabel("Count"); ax4.set_ylim(0, 12)
    ax4.legend(handles=legend_patches, fontsize=8)

    # ── 5. Time to Key Events ────────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    style_ax(ax5, "Median Times to Key Events (min)")
    te_labels = ["Arrival to Art\nLine Transduced", "Arrest to\nROSC"]
    te30 = [8.0, 17.5];  te90 = [13.0, 19.5]
    x = np.arange(len(te_labels))
    b30 = ax5.bar(x - w/2, te30, w, color=C30, zorder=3)
    b90 = ax5.bar(x + w/2, te90, w, color=C90, zorder=3)
    for bar, val in zip(list(b30) + list(b90), te30 + te90):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax5.set_xticks(x); ax5.set_xticklabels(te_labels, fontsize=9)
    ax5.set_ylabel("Minutes"); ax5.set_ylim(0, 27)
    ax5.legend(handles=legend_patches, fontsize=8)

    # row 1 col 2 intentionally left empty

    # ── 6. Dispatch → Departure ──────────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 0])
    style_ax(ax6, "Median: Dispatch → Departure")
    vals30 = [to_min("00:30")];  vals90 = [to_min("01:00")]
    x = np.arange(1)
    b30 = ax6.bar(x - w/2, vals30, w, color=C30, zorder=3)
    b90 = ax6.bar(x + w/2, vals90, w, color=C90, zorder=3)
    for bar, lbl in zip(list(b30), ["0:30"]):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 lbl, ha="center", va="bottom", fontsize=10, fontweight="bold")
    for bar, lbl in zip(list(b90), ["1:00"]):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 lbl, ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax6.set_xticks([]); ax6.set_ylabel("Minutes"); ax6.set_ylim(0, 2.0)
    ax6.legend(handles=legend_patches, fontsize=8)

    # ── 7. Dispatch → Arrival ────────────────────────────────────────────────
    ax7 = fig.add_subplot(gs[2, 1])
    style_ax(ax7, "Median: Dispatch → Arrival")
    vals30 = [to_min("26:00")];  vals90 = [to_min("18:00")]
    x = np.arange(1)
    b30 = ax7.bar(x - w/2, vals30, w, color=C30, zorder=3)
    b90 = ax7.bar(x + w/2, vals90, w, color=C90, zorder=3)
    for bar, lbl in zip(list(b30), ["26:00"]):
        ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 lbl, ha="center", va="bottom", fontsize=10, fontweight="bold")
    for bar, lbl in zip(list(b90), ["18:00"]):
        ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 lbl, ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax7.set_xticks([]); ax7.set_ylabel("Minutes"); ax7.set_ylim(0, 33)
    ax7.legend(handles=legend_patches, fontsize=8)

    # ── 8. 000 Call → Patient ────────────────────────────────────────────────
    ax8 = fig.add_subplot(gs[2, 2])
    style_ax(ax8, "Median: 000 Call → Patient")
    vals30 = [to_min("00:28")];  vals90 = [to_min("00:27")]
    x = np.arange(1)
    b30 = ax8.bar(x - w/2, vals30, w, color=C30, zorder=3)
    b90 = ax8.bar(x + w/2, vals90, w, color=C90, zorder=3)
    for bar, lbl in zip(list(b30), ["0:28"]):
        ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 lbl, ha="center", va="bottom", fontsize=10, fontweight="bold")
    for bar, lbl in zip(list(b90), ["0:27"]):
        ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 lbl, ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax8.set_xticks([]); ax8.set_ylabel("Minutes"); ax8.set_ylim(0, 0.6)
    ax8.legend(handles=legend_patches, fontsize=8)

    return fig


# ── Save callback ─────────────────────────────────────────────────────────────
def save_report(fig):
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG image", "*.png"), ("PDF document", "*.pdf"), ("All files", "*.*")],
        initialfile="PRECARE_activity_report",
        title="Save Report As",
    )
    if not path:
        return
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    messagebox.showinfo("Saved", f"Report saved to:\n{path}")


# ── Main window ───────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.title("PRECARE Activity Report")
    root.configure(bg="#F0F0F0")

    fig = build_figure()

    # Embed matplotlib figure in tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Save button
    btn_frame = tk.Frame(root, bg="#F0F0F0", pady=8)
    btn_frame.pack(fill=tk.X)
    save_btn = tk.Button(
        btn_frame,
        text="💾  Save Report",
        command=lambda: save_report(fig),
        font=("Helvetica", 12, "bold"),
        bg="#2196F3", fg="white",
        activebackground="#1565C0", activeforeground="white",
        relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
    )
    save_btn.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
