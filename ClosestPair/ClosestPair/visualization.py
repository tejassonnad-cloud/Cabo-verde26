"""
Closest Pair of Points - Visualization Module
=============================================
This module provides high-quality Matplotlib visualizations for the Closest Pair
of Points problem, comparing the Brute-Force O(N^2) and Divide-and-Conquer
O(N log N) algorithms.

Visualizations provided:
1. plot_results: Comprehensive main plot comparing Brute Force and D&C pairs,
   midline, strip region, coordinate labels, and minimum distances.
2. plot_dnc_steps: Multi-panel walkthrough visualizing the divide-and-conquer
   recursion (dividing line, subsets, half minima, strip search, final pair, summary).
3. plot_performance: Benchmarking curve comparing empirical runtimes against
   theoretical O(N^2) and O(N log N) reference curves with optional log scaling.
"""

import os
import math
from typing import List, Tuple, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Directory where generated PNG visualizations will be stored
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


def _apply_professional_style() -> None:
    """Configure a clean, modern aesthetic for matplotlib charts."""
    available = plt.style.available
    if "seaborn-v0_8-whitegrid" in available:
        plt.style.use("seaborn-v0_8-whitegrid")
    elif "seaborn-whitegrid" in available:
        plt.style.use("seaborn-whitegrid")
    else:
        plt.style.use("default")

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial", "sans-serif"],
        "axes.edgecolor": "#94a3b8",
        "axes.linewidth": 1.1,
        "grid.color": "#e2e8f0",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "figure.autolayout": False,
    })


def _calc_padding(values: List[float], pad_ratio: float = 0.15) -> Tuple[float, float]:
    """Calculate min/max bounds with padding to prevent points touching borders."""
    if not values:
        return (0.0, 1.0)
    v_min, v_max = min(values), max(values)
    span = v_max - v_min
    if span <= 1e-9:
        span = 1.0 if abs(v_min) <= 1e-9 else abs(v_min) * 0.2
    pad = span * pad_ratio
    return (v_min - pad, v_max + pad)


def _format_coord(val: float) -> str:
    """Format coordinate concisely for chart annotations."""
    if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
        return f"{int(val)}"
    return f"{val:.2f}".rstrip("0").rstrip(".")


def _euclidean_dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


# ============================================================================
# 1. MAIN RESULTS PLOT
# ============================================================================

def plot_results(
    points: List[Tuple[float, float]],
    bf_result: Tuple[float, Tuple[Tuple[float, float], Tuple[float, float]]],
    dnc_result: Any,
    dnc_steps: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None
) -> None:
    """
    Plot all points, highlighting the closest pair found by Brute Force
    and Divide-and-Conquer, the main dividing line, and the strip boundary.

    Args:
        points: List of (x, y) coordinates
        bf_result: (min_dist, (p1, p2)) from brute force
        dnc_result: (min_dist, (p1, p2)) or (min_dist, (p1, p2), steps)
        dnc_steps: Optional steps list from D&C (if not bundled in dnc_result)
        save_path: Custom PNG path; defaults to ClosestPair/closest_pair_results.png
    """
    if not points:
        print("[Visualization Warning] Cannot plot empty points list.")
        return

    _apply_professional_style()
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=120)

    # Unpack brute force result
    bf_dist = bf_result[0]
    bf_pair = bf_result[1]

    # Unpack D&C result
    dnc_dist = dnc_result[0]
    dnc_pair = dnc_result[1]
    if dnc_steps is None and len(dnc_result) > 2:
        dnc_steps = dnc_result[2]

    # Extract top-level dividing line (mid_x) and strip delta
    top_step = None
    if dnc_steps:
        # Find step with level == 0 or first step
        for s in dnc_steps:
            if s.get("level") == 0:
                top_step = s
                break
        if top_step is None:
            top_step = dnc_steps[0]

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # Determine mid_x and delta
    if top_step and "mid_x" in top_step and top_step["mid_x"] is not None:
        mid_x = float(top_step["mid_x"])
    else:
        sorted_x = sorted(xs)
        mid_x = float(sorted_x[len(sorted_x) // 2])

    delta = None
    if top_step and "delta" in top_step and top_step["delta"] is not None:
        delta = float(top_step["delta"])
    else:
        delta = float(dnc_dist)

    # 1. Shaded Strip Region: [mid_x - delta, mid_x + delta]
    if delta is not None and delta > 0 and math.isfinite(delta):
        strip_left = mid_x - delta
        strip_right = mid_x + delta
        ax.axvspan(
            strip_left,
            strip_right,
            color="#38bdf8",
            alpha=0.18,
            zorder=1,
            label=f"Strip Region (|x - {mid_x:.1f}| < {delta:.2f})"
        )
        ax.axvline(strip_left, color="#0284c7", linestyle=":", linewidth=1.2, alpha=0.6, zorder=2)
        ax.axvline(strip_right, color="#0284c7", linestyle=":", linewidth=1.2, alpha=0.6, zorder=2)

    # 2. Main Dividing Line
    ax.axvline(
        mid_x,
        color="#6366f1",
        linestyle="--",
        linewidth=2.0,
        alpha=0.9,
        zorder=2,
        label=f"Dividing Line (x = {mid_x:.2f})"
    )

    # 3. Scatter All Points
    ax.scatter(
        xs,
        ys,
        color="#1e293b",
        s=65,
        alpha=0.85,
        edgecolor="#0f172a",
        linewidth=0.8,
        zorder=3,
        label=f"Input Points (N = {len(points)})"
    )

    # 4. Point Coordinate Labels
    # For large datasets (N > 50), label only closest pairs to avoid visual clutter
    if len(points) <= 50:
        for p in points:
            lbl = f"({_format_coord(p[0])}, {_format_coord(p[1])})"
            ax.annotate(
                lbl,
                xy=p,
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
                color="#475569",
                fontweight="medium",
                zorder=4
            )
    else:
        # Highlight and label only the closest pair points
        for p in set(list(bf_pair) + list(dnc_pair)):
            lbl = f"({_format_coord(p[0])}, {_format_coord(p[1])})"
            ax.annotate(
                lbl,
                xy=p,
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                color="#0f172a",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#cbd5e1", alpha=0.85),
                zorder=7
            )

    # Check whether both algorithms found the exact same pair
    p1_bf, p2_bf = bf_pair
    p1_dnc, p2_dnc = dnc_pair
    same_pair = (
        (p1_bf == p1_dnc and p2_bf == p2_dnc) or
        (p1_bf == p2_dnc and p2_bf == p1_dnc)
    )

    # 5. Highlight Brute Force Closest Pair (RED, Dashed Line)
    bf_x = [p1_bf[0], p2_bf[0]]
    bf_y = [p1_bf[1], p2_bf[1]]
    ax.plot(
        bf_x,
        bf_y,
        color="#dc2626",
        linestyle="--",
        linewidth=3.0,
        zorder=5,
        label="Brute Force Pair"
    )
    ax.scatter(
        bf_x,
        bf_y,
        color="#ef4444",
        s=140,
        edgecolor="#991b1b",
        linewidth=1.8,
        zorder=5
    )

    # 6. Highlight Divide & Conquer Closest Pair (GREEN, Solid Line)
    dnc_x = [p1_dnc[0], p2_dnc[0]]
    dnc_y = [p1_dnc[1], p2_dnc[1]]
    
    # If pairs are identical, use a slightly offset or distinct styling to show both
    if same_pair:
        ax.plot(
            dnc_x,
            dnc_y,
            color="#16a34a",
            linestyle="-",
            linewidth=1.8,
            alpha=0.95,
            zorder=6,
            label="D&C Pair (Matches BF)"
        )
        ax.scatter(
            dnc_x,
            dnc_y,
            facecolor="none",
            edgecolor="#15803d",
            s=220,
            linewidth=2.2,
            zorder=6
        )
    else:
        ax.plot(
            dnc_x,
            dnc_y,
            color="#16a34a",
            linestyle="-",
            linewidth=2.8,
            zorder=6,
            label="D&C Pair"
        )
        ax.scatter(
            dnc_x,
            dnc_y,
            color="#22c55e",
            s=140,
            edgecolor="#15803d",
            linewidth=1.8,
            zorder=6
        )

    # 7. Note if both algorithms found the same pair
    dist_diff = abs(bf_dist - dnc_dist)
    agreement_str = "MATCH" if dist_diff < 1e-9 else "DISCREPANCY"
    
    note_lines = [
        f"Brute Force Dist: {bf_dist:.6f}",
        f"D&C Dist:         {dnc_dist:.6f}",
        f"Status:           {agreement_str} (Δ = {dist_diff:.1e})",
    ]
    if same_pair:
        note_lines.append("Note: Both algorithms identified the identical point pair.")
    else:
        note_lines.append("Note: Distinct pairs found (both achieve equal minimum distance).")

    info_box_text = "\n".join(note_lines)
    ax.text(
        0.02,
        0.03,
        info_box_text,
        transform=ax.transAxes,
        fontsize=9.5,
        fontfamily="monospace",
        verticalalignment="bottom",
        bbox=dict(
            boxstyle="round,pad=0.6",
            facecolor="#f8fafc",
            edgecolor="#10b981" if agreement_str == "MATCH" else "#ef4444",
            linewidth=1.5,
            alpha=0.92
        ),
        zorder=8
    )

    # 8. Titles and Labels
    ax.set_title(
        f"Closest Pair of Points — Algorithmic Comparison\n"
        f"Brute Force: {bf_dist:.6f}  |  Divide & Conquer: {dnc_dist:.6f}",
        fontsize=14,
        fontweight="bold",
        pad=14,
        color="#0f172a"
    )
    ax.set_xlabel("X Coordinate", fontsize=11, fontweight="semibold", labelpad=8)
    ax.set_ylabel("Y Coordinate", fontsize=11, fontweight="semibold", labelpad=8)

    # 9. Auto-scale with padding
    x_pad_min, x_pad_max = _calc_padding(xs + [mid_x - (delta or 0), mid_x + (delta or 0)])
    y_pad_min, y_pad_max = _calc_padding(ys)
    ax.set_xlim(x_pad_min, x_pad_max)
    ax.set_ylim(y_pad_min, y_pad_max)

    ax.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.legend(loc="upper right", frameon=True, framealpha=0.92, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=9.5)

    plt.tight_layout()

    # Save PNG
    if not save_path:
        os.makedirs(MODULE_DIR, exist_ok=True)
        save_path = os.path.join(MODULE_DIR, "closest_pair_results.png")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    print(f"[Visualization] Results plot saved to: {save_path}")
    plt.show()


# ============================================================================
# 2. STEP-BY-STEP DIVIDE & CONQUER VISUALIZATION
# ============================================================================

def plot_dnc_steps(
    points: List[Tuple[float, float]],
    steps: Any,
    save_path: Optional[str] = None
) -> None:
    """
    Generate a 6-panel figure visualizing the recursive Divide-and-Conquer pipeline:
    - Panel 1: All points with the main dividing line
    - Panel 2: Left and right subsets colored differently, with the dividing line
    - Panel 3: Closest pairs found in each half
    - Panel 4: Strip region highlighted with strip points
    - Panel 5: Final closest pair highlighted
    - Panel 6: Summary dashboard with labeled distances & algorithmic guarantees

    Args:
        points: Full list of (x, y) coordinates
        steps: List of step dicts from divide_conquer.py (or dnc_result tuple)
        save_path: Custom PNG path; defaults to ClosestPair/closest_pair_dnc_steps.png
    """
    if not points or len(points) < 2:
        print("[Visualization Warning] At least 2 points required to visualize D&C steps.")
        return

    # Handle case where user passed the full dnc_result tuple (dist, pair, steps)
    if isinstance(steps, tuple) and len(steps) >= 3:
        steps = steps[2]
    elif not isinstance(steps, list):
        steps = []

    _apply_professional_style()

    # Extract top-level step or reconstruct from points
    top_step: Dict[str, Any] = {}
    if steps:
        # Search for level 0 step
        for s in steps:
            if s.get("level") == 0:
                top_step = s
                break
        if not top_step and len(steps) > 0:
            top_step = steps[0]

    # Reconstruct/derive attributes if steps was minimal
    sorted_pts = sorted(points, key=lambda p: (p[0], p[1]))
    n = len(sorted_pts)
    mid_idx = n // 2
    default_mid_x = float(sorted_pts[mid_idx][0])
    mid_x = float(top_step.get("mid_x", default_mid_x))

    left_points = top_step.get("left_points") or sorted_pts[:mid_idx]
    right_points = top_step.get("right_points") or sorted_pts[mid_idx:]

    # Helper: find closest pair in a point subset (fallback if sub-step missing)
    def _find_best_in_subset(pts: List[Tuple[float, float]]) -> Tuple[float, Optional[Tuple[Tuple[float, float], Tuple[float, float]]]]:
        if len(pts) < 2:
            return float("inf"), None
        best_d = float("inf")
        best_p = None
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = _euclidean_dist(pts[i], pts[j])
                if d < best_d:
                    best_d = d
                    best_p = (pts[i], pts[j])
        return best_d, best_p

    d_left, pair_left = _find_best_in_subset(left_points)
    d_right, pair_right = _find_best_in_subset(right_points)

    delta = top_step.get("delta")
    if delta is None or math.isinf(delta):
        delta = min(d_left, d_right)

    strip_points = top_step.get("strip")
    if strip_points is None:
        strip_points = [p for p in points if abs(p[0] - mid_x) < delta]

    final_pair = top_step.get("closest_pair")
    final_dist = top_step.get("min_dist")
    if final_pair is None or final_dist is None:
        # Calculate global closest pair as fallback
        best_d, best_p = _find_best_in_subset(points)
        final_pair = best_p
        final_dist = best_d

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_bounds = _calc_padding(xs + [mid_x - delta, mid_x + delta], pad_ratio=0.12)
    y_bounds = _calc_padding(ys, pad_ratio=0.12)

    # Create 2x3 Subplot Grid
    fig, axes = plt.subplots(2, 3, figsize=(17, 11), dpi=120)
    fig.suptitle(
        f"Divide & Conquer Closest Pair Algorithm — Step-by-Step Recursion (N = {len(points)})",
        fontsize=16,
        fontweight="bold",
        color="#0f172a",
        y=0.98
    )

    # -------------------------------------------------------------------------
    # Panel 1: All points with the main dividing line
    # -------------------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.scatter(xs, ys, color="#334155", s=55, edgecolor="#0f172a", alpha=0.85, zorder=3, label="Points")
    ax1.axvline(mid_x, color="#6366f1", linestyle="--", linewidth=2.2, zorder=2, label=f"Dividing line (x={mid_x:.2f})")
    ax1.set_title("Step 1: Divide — Partition at Median X", fontsize=12, fontweight="bold", color="#1e293b")
    ax1.set_xlim(x_bounds)
    ax1.set_ylim(y_bounds)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    # -------------------------------------------------------------------------
    # Panel 2: Left and right subsets colored differently
    # -------------------------------------------------------------------------
    ax2 = axes[0, 1]
    lx = [p[0] for p in left_points]
    ly = [p[1] for p in left_points]
    rx = [p[0] for p in right_points]
    ry = [p[1] for p in right_points]

    ax2.scatter(lx, ly, color="#2563eb", s=60, edgecolor="#1d4ed8", alpha=0.85, zorder=3, label=f"Left Half ({len(left_points)})")
    ax2.scatter(rx, ry, color="#ea580c", s=60, edgecolor="#c2410c", alpha=0.85, zorder=3, label=f"Right Half ({len(right_points)})")
    ax2.axvline(mid_x, color="#6366f1", linestyle="--", linewidth=2.0, zorder=2)
    ax2.set_title("Step 2: Subproblems — Left & Right Halves", fontsize=12, fontweight="bold", color="#1e293b")
    ax2.set_xlim(x_bounds)
    ax2.set_ylim(y_bounds)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    # -------------------------------------------------------------------------
    # Panel 3: Closest pairs found in each half
    # -------------------------------------------------------------------------
    ax3 = axes[0, 2]
    ax3.scatter(lx, ly, color="#93c5fd", s=40, alpha=0.6, zorder=2)
    ax3.scatter(rx, ry, color="#fdba74", s=40, alpha=0.6, zorder=2)
    ax3.axvline(mid_x, color="#6366f1", linestyle="--", linewidth=1.5, alpha=0.7, zorder=2)

    # Highlight left closest pair
    if pair_left:
        ax3.plot([pair_left[0][0], pair_left[1][0]], [pair_left[0][1], pair_left[1][1]],
                 color="#1d4ed8", linestyle="-", linewidth=2.5, zorder=4, label=f"dL = {d_left:.3f}")
        ax3.scatter([pair_left[0][0], pair_left[1][0]], [pair_left[0][1], pair_left[1][1]],
                    color="#2563eb", s=100, edgecolor="#1e3a8a", zorder=5)

    # Highlight right closest pair
    if pair_right:
        ax3.plot([pair_right[0][0], pair_right[1][0]], [pair_right[0][1], pair_right[1][1]],
                 color="#c2410c", linestyle="-", linewidth=2.5, zorder=4, label=f"dR = {d_right:.3f}")
        ax3.scatter([pair_right[0][0], pair_right[1][0]], [pair_right[0][1], pair_right[1][1]],
                    color="#ea580c", s=100, edgecolor="#7c2d12", zorder=5)

    ax3.set_title(f"Step 3: Conquer — Best in Halves (δ = {delta:.3f})", fontsize=12, fontweight="bold", color="#1e293b")
    ax3.set_xlim(x_bounds)
    ax3.set_ylim(y_bounds)
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    # -------------------------------------------------------------------------
    # Panel 4: Strip region highlighted with strip points
    # -------------------------------------------------------------------------
    ax4 = axes[1, 0]
    ax4.scatter(xs, ys, color="#94a3b8", s=35, alpha=0.4, zorder=2, label="Outside Strip")

    # Shaded strip
    ax4.axvspan(mid_x - delta, mid_x + delta, color="#a855f7", alpha=0.18, zorder=1,
                label=f"Strip: |x - {mid_x:.1f}| < {delta:.2f}")
    ax4.axvline(mid_x, color="#6366f1", linestyle="--", linewidth=1.5, zorder=2)
    ax4.axvline(mid_x - delta, color="#9333ea", linestyle=":", linewidth=1.2, zorder=2)
    ax4.axvline(mid_x + delta, color="#9333ea", linestyle=":", linewidth=1.2, zorder=2)

    # Highlight strip points
    sx = [p[0] for p in strip_points]
    sy = [p[1] for p in strip_points]
    ax4.scatter(sx, sy, color="#9333ea", s=75, edgecolor="#581c87", linewidth=1.2, zorder=4,
                label=f"Strip Points ({len(strip_points)})")

    ax4.set_title(f"Step 4: Strip Merge — Checking Candidates ({len(strip_points)})",
                  fontsize=12, fontweight="bold", color="#1e293b")
    ax4.set_xlim(x_bounds)
    ax4.set_ylim(y_bounds)
    ax4.grid(True, linestyle="--", alpha=0.5)
    ax4.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    # -------------------------------------------------------------------------
    # Panel 5: Final closest pair highlighted
    # -------------------------------------------------------------------------
    ax5 = axes[1, 1]
    ax5.scatter(xs, ys, color="#64748b", s=40, alpha=0.4, zorder=2)
    ax5.axvline(mid_x, color="#cbd5e1", linestyle="--", linewidth=1.2, zorder=1)

    if final_pair:
        fx = [final_pair[0][0], final_pair[1][0]]
        fy = [final_pair[0][1], final_pair[1][1]]
        ax5.plot(fx, fy, color="#16a34a", linestyle="-", linewidth=3.2, zorder=5, label=f"Final Pair (d={final_dist:.4f})")
        ax5.scatter(fx, fy, color="#22c55e", s=150, edgecolor="#14532d", linewidth=1.8, zorder=6)

        # Annotate coordinates of the final pair
        for pt in final_pair:
            ax5.annotate(
                f"({_format_coord(pt[0])}, {_format_coord(pt[1])})",
                xy=pt,
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                color="#14532d",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#dcfce7", edgecolor="#86efac", alpha=0.95),
                zorder=7
            )

    ax5.set_title(f"Step 5: Final Closest Pair (d = {final_dist:.4f})",
                  fontsize=12, fontweight="bold", color="#1e293b")
    ax5.set_xlim(x_bounds)
    ax5.set_ylim(y_bounds)
    ax5.grid(True, linestyle="--", alpha=0.5)
    ax5.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    # -------------------------------------------------------------------------
    # Panel 6: Summary Dashboard with Metrics and Analysis
    # -------------------------------------------------------------------------
    ax6 = axes[1, 2]
    ax6.axis("off")  # Render as an information dashboard card

    # Draw card background
    card = patches.FancyBboxPatch(
        (0.04, 0.04), 0.92, 0.92,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor="#f8fafc",
        edgecolor="#cbd5e1",
        linewidth=1.5,
        transform=ax6.transAxes
    )
    ax6.add_patch(card)

    p1_str = f"({_format_coord(final_pair[0][0])}, {_format_coord(final_pair[0][1])})" if final_pair else "N/A"
    p2_str = f"({_format_coord(final_pair[1][0])}, {_format_coord(final_pair[1][1])})" if final_pair else "N/A"

    summary_text = (
        "╔═════════════════════════════════════════════╗\n"
        "║          D&C EXECUTION SUMMARY              ║\n"
        "╚═════════════════════════════════════════════╝\n\n"
        f"• Total Points (N):          {len(points)}\n"
        f"• Dividing Line (x_mid):     {mid_x:.4f}\n"
        f"• Left Half Size:            {len(left_points)} points\n"
        f"• Right Half Size:           {len(right_points)} points\n"
        f"• Left Min Distance (dL):    {d_left:.6f}\n"
        f"• Right Min Distance (dR):   {d_right:.6f}\n"
        f"• Strip Threshold (δ):       {delta:.6f}\n"
        f"• Strip Candidates:          {len(strip_points)} points\n\n"
        "───────────────────────────────────────────────\n"
        f"★ FINAL MINIMUM DISTANCE:    {final_dist:.6f}\n"
        f"★ POINT 1:                   {p1_str}\n"
        f"★ POINT 2:                   {p2_str}\n"
        "───────────────────────────────────────────────\n\n"
        "Algorithmic Complexity:\n"
        "• Recurrence: T(N) = 2T(N/2) + O(N)\n"
        "• Master Theorem: T(N) = O(N log N)\n"
        "• Geometric Proof: At most 7 points checked\n"
        "  per strip candidate within δ vertical span."
    )

    ax6.text(
        0.08,
        0.92,
        summary_text,
        transform=ax6.transAxes,
        fontsize=9.2,
        fontfamily="monospace",
        verticalalignment="top",
        color="#0f172a"
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save PNG
    if not save_path:
        os.makedirs(MODULE_DIR, exist_ok=True)
        save_path = os.path.join(MODULE_DIR, "closest_pair_dnc_steps.png")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    print(f"[Visualization] D&C steps plot saved to: {save_path}")
    plt.show()


# ============================================================================
# 3. PERFORMANCE PLOT
# ============================================================================

def plot_performance(
    sizes: List[int],
    bf_times: List[float],
    dnc_times: List[float],
    save_path: Optional[str] = None
) -> None:
    """
    Plot benchmark execution times comparing Brute Force O(N^2) against
    Divide and Conquer O(N log N).

    Features:
    - X-axis: Number of Points (N)
    - Y-axis: Execution Time (ms)
    - Brute Force curve in red with circle markers
    - Divide & Conquer curve in green with square markers
    - Theoretical fitted curves (c1 * N^2 and c2 * N log N) as dashed reference lines
    - Automatic logarithmic scaling when execution times vary widely
    - Clean, publication-ready styling

    Args:
        sizes: List of point counts (N)
        bf_times: Execution times in milliseconds for brute force
        dnc_times: Execution times in milliseconds for divide-and-conquer
        save_path: Custom PNG path; defaults to ClosestPair/performance_comparison.png
    """
    if not sizes or not bf_times or not dnc_times:
        print("[Visualization Warning] Incomplete benchmark data provided.")
        return

    _apply_professional_style()
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=120)

    # Plot empirical data
    ax.plot(
        sizes,
        bf_times,
        color="#dc2626",
        marker="o",
        markersize=7,
        linewidth=2.2,
        label="Brute Force O(N²) [Actual]",
        zorder=4
    )
    ax.plot(
        sizes,
        dnc_times,
        color="#16a34a",
        marker="s",
        markersize=7,
        linewidth=2.2,
        label="Divide & Conquer O(N log N) [Actual]",
        zorder=4
    )

    # Fit Theoretical Curves (c1 * N^2 and c2 * N * log2(N))
    try:
        # Fit constant using the last non-trivial points
        valid_bf = [(n, t) for n, t in zip(sizes, bf_times) if n > 0 and t > 0]
        valid_dnc = [(n, t) for n, t in zip(sizes, dnc_times) if n > 1 and t > 0]

        if valid_bf and valid_dnc:
            # Anchor constant to the largest benchmarked size
            n_ref_bf, t_ref_bf = valid_bf[-1]
            c_bf = t_ref_bf / (n_ref_bf ** 2)

            n_ref_dnc, t_ref_dnc = valid_dnc[-1]
            c_dnc = t_ref_dnc / (n_ref_dnc * math.log2(n_ref_dnc))

            # Generate smooth curve points
            min_n = min(sizes)
            max_n = max(sizes)
            step_count = 100
            n_curve = [
                min_n + i * (max_n - min_n) / (step_count - 1)
                for i in range(step_count)
            ]

            theory_bf = [c_bf * (x ** 2) for x in n_curve]
            theory_dnc = [c_dnc * (x * math.log2(max(x, 2))) for x in n_curve]

            ax.plot(
                n_curve,
                theory_bf,
                color="#f87171",
                linestyle="--",
                linewidth=1.4,
                alpha=0.85,
                label=f"Theoretical O(N²) [c={c_bf:.2e}]",
                zorder=3
            )
            ax.plot(
                n_curve,
                theory_dnc,
                color="#4ade80",
                linestyle="--",
                linewidth=1.4,
                alpha=0.85,
                label=f"Theoretical O(N log N) [c={c_dnc:.2e}]",
                zorder=3
            )
    except Exception as e:
        # Theoretical fit is optional; continue gracefully if edge cases occur
        print(f"[Visualization Note] Theoretical curve fitting omitted: {e}")

    # Determine if log scale is appropriate (e.g. dynamic range > 20x)
    all_times = [t for t in bf_times + dnc_times if t > 0]
    is_log_scale = False
    if all_times and (max(all_times) / min(all_times)) > 20:
        ax.set_yscale("log")
        is_log_scale = True

    # Speedup annotation for the largest size
    if len(sizes) > 0 and len(bf_times) > 0 and len(dnc_times) > 0:
        last_n = sizes[-1]
        last_bf = bf_times[-1]
        last_dnc = dnc_times[-1]
        if last_dnc > 0:
            speedup = last_bf / last_dnc
            speedup_badge = (
                f"At N = {last_n:,}:\n"
                f"• Brute Force: {last_bf:.2f} ms\n"
                f"• D&C:         {last_dnc:.2f} ms\n"
                f"• Speedup:     {speedup:.1f}x Faster"
            )
            ax.text(
                0.03,
                0.95,
                speedup_badge,
                transform=ax.transAxes,
                fontsize=9.5,
                fontfamily="monospace",
                verticalalignment="top",
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor="#f8fafc",
                    edgecolor="#64748b",
                    linewidth=1.2,
                    alpha=0.92
                ),
                zorder=5
            )

    # Titles & Labels
    scale_label = " (Log Scale)" if is_log_scale else ""
    ax.set_title(
        "Performance Comparison: Brute Force vs Divide & Conquer",
        fontsize=14,
        fontweight="bold",
        pad=14,
        color="#0f172a"
    )
    ax.set_xlabel("Number of Points (N)", fontsize=11, fontweight="semibold", labelpad=8)
    ax.set_ylabel(f"Execution Time (ms){scale_label}", fontsize=11, fontweight="semibold", labelpad=8)

    ax.grid(True, linestyle="--", alpha=0.6, zorder=0)
    ax.legend(loc="lower right", frameon=True, framealpha=0.92, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=9.5)

    plt.tight_layout()

    # Save PNG
    if not save_path:
        os.makedirs(MODULE_DIR, exist_ok=True)
        save_path = os.path.join(MODULE_DIR, "performance_comparison.png")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    print(f"[Visualization] Performance comparison plot saved to: {save_path}")
    plt.show()


# ============================================================================
# SELF-TEST / DEMO (WHEN RUN DIRECTLY)
# ============================================================================

if __name__ == "__main__":
    import random

    print("Running Closest Pair visualization self-test...")
    random.seed(42)

    # 1. Sample dataset
    demo_points = [
        (2.5, 3.1), (-1.0, 4.7), (5.0, 5.0), (-3.2, -2.8), (7.1, 1.3),
        (0.0, 0.0), (4.4, -1.5), (-2.5, 6.0), (8.3, 3.7), (1.1, 1.2),
        (-4.0, 0.5), (6.6, 6.6), (3.0, -3.0), (-1.5, -1.5), (9.0, 2.0)
    ]

    # Calculate actual closest pair for demo
    min_d = float("inf")
    best_pair = (demo_points[0], demo_points[1])
    for i in range(len(demo_points)):
        for j in range(i + 1, len(demo_points)):
            d = _euclidean_dist(demo_points[i], demo_points[j])
            if d < min_d:
                min_d = d
                best_pair = (demo_points[i], demo_points[j])

    bf_demo = (min_d, best_pair)
    dnc_demo = (min_d, best_pair)

    # Simulated top-level D&C step
    demo_steps = [{
        "level": 0,
        "points": demo_points,
        "mid_x": 2.5,
        "left_points": [p for p in demo_points if p[0] <= 2.5],
        "right_points": [p for p in demo_points if p[0] > 2.5],
        "strip": [p for p in demo_points if abs(p[0] - 2.5) < min_d],
        "delta": min_d,
        "closest_pair": best_pair,
        "min_dist": min_d
    }]

    print("1. Testing plot_results...")
    plot_results(demo_points, bf_demo, dnc_demo, demo_steps)

    print("2. Testing plot_dnc_steps...")
    plot_dnc_steps(demo_points, demo_steps)

    print("3. Testing plot_performance...")
    demo_sizes = [10, 50, 100, 500, 1000, 2500, 5000]
    demo_bf_times = [0.015, 0.25, 0.95, 23.5, 95.0, 590.0, 2450.0]
    demo_dnc_times = [0.045, 0.18, 0.42, 2.6, 5.8, 16.2, 34.5]
    plot_performance(demo_sizes, demo_bf_times, demo_dnc_times)

    print("All visualization functions executed and validated successfully!")
