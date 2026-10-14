"""
benchmark.py - Performance Benchmarking Module for Closest Pair of Points.

Conducts rigorous timing experiments comparing Brute Force O(N^2) against
Divide and Conquer O(N log N) across varying input sizes N, prints a comparative
analysis table, and generates graphical performance plots.
"""

import time
import random
import os
import sys

# Ensure current script directory is in sys.path for local module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Enable ANSI colors on Windows terminals if supported
if os.name == 'nt':
    os.system('')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from brute_force import closest_pair_brute_force
from divide_conquer import closest_pair_dnc
from visualization import plot_performance

# Benchmark configurations
BENCHMARK_SIZES = [10, 50, 100, 500, 1000, 5000, 10000]
COORDINATE_RANGE = (-1000.0, 1000.0)
TOLERANCE = 1e-9


def generate_random_points(n, coord_range=COORDINATE_RANGE):
    """Generate n random 2D points within the given coordinate range."""
    return [
        (random.uniform(coord_range[0], coord_range[1]), random.uniform(coord_range[0], coord_range[1]))
        for _ in range(n)
    ]


def run_benchmark(sizes=None):
    """
    Run performance benchmark across all specified input sizes.
    Measures execution time with time.perf_counter(), computes averages in ms,
    verifies result agreement, prints a formatted table, displays comparative
    analysis, and generates performance visualization.
    """
    if sizes is None:
        sizes = BENCHMARK_SIZES

    print("\n" + "=" * 62)
    print("      CLOSEST PAIR OF POINTS — PERFORMANCE BENCHMARK       ")
    print("=" * 62)
    print(f"Benchmarking sizes N = {sizes}")
    print("Executing multiple trials per size to compute stable averages...\n")

    bf_times = []
    dnc_times = []

    # Table Header
    print("╔══════════╦═══════════════════╦══════════════════╦══════════╗")
    print("║    N     ║ Brute Force (ms)  ║    D&C (ms)      ║  Match   ║")
    print("╠══════════╬═══════════════════╬══════════════════╬══════════╣")

    for n in sizes:
        points = generate_random_points(n)

        # Determine number of trials based on input size
        if n <= 100:
            bf_trials = 5
            dnc_trials = 5
        elif n <= 1000:
            bf_trials = 3
            dnc_trials = 5
        elif n == 5000:
            bf_trials = 2
            dnc_trials = 3
        else:  # n >= 10000
            bf_trials = 1
            dnc_trials = 3

        # Benchmark Brute Force
        bf_total_sec = 0.0
        bf_dist = None
        for _ in range(bf_trials):
            start = time.perf_counter()
            res = closest_pair_brute_force(points)
            end = time.perf_counter()
            bf_total_sec += (end - start)
            bf_dist = res[0]

        avg_bf_ms = (bf_total_sec / bf_trials) * 1000.0
        bf_times.append(avg_bf_ms)

        # Benchmark Divide and Conquer
        dnc_total_sec = 0.0
        dnc_dist = None
        for _ in range(dnc_trials):
            start = time.perf_counter()
            res = closest_pair_dnc(points)
            end = time.perf_counter()
            dnc_total_sec += (end - start)
            dnc_dist = res[0]

        avg_dnc_ms = (dnc_total_sec / dnc_trials) * 1000.0
        dnc_times.append(avg_dnc_ms)

        # Verification check within tolerance
        match_str = "YES" if abs(bf_dist - dnc_dist) < TOLERANCE else "NO"

        # Formatted row output
        print(f"║ {n:>8d} ║ {avg_bf_ms:>17.4f} ║ {avg_dnc_ms:>16.4f} ║ {match_str:^8s} ║")

    print("╚══════════╩═══════════════════╩══════════════════╩══════════╝")

    # Comparative Analysis
    print("\n" + "=" * 62)
    print("               COMPARATIVE ANALYSIS               ")
    print("=" * 62)
    print("""
| Algorithm        | Time Complexity | Space Complexity | Approach                         |
|------------------|-----------------|------------------|----------------------------------|
| Brute Force      | O(N²)           | O(1) auxiliary   | Compare every pair               |
| Divide & Conquer | O(N log N)      | O(N)             | Divide, solve recursively, merge |

Why D&C is faster for large N:
The Brute Force algorithm computes the Euclidean distance between all N(N - 1) / 2 pairs.
As N grows, this quadratic growth becomes prohibitive:
- For N = 1,000  : ~500,000 comparisons
- For N = 10,000 : ~50,000,000 comparisons
- For N = 100,000: ~5,000,000,000 comparisons

In contrast, the Divide-and-Conquer algorithm:
1. Splits points at median x-coordinate into two balanced subproblems of size N/2.
2. Recursively solves both halves, yielding delta = min(dL, dR).
3. Merges the halves by examining a vertical strip of width 2*delta centered at the divider.
4. By geometric packing, each point inside the strip has at most 7 candidate neighbors
   within delta in the y-direction. Hence, strip processing is strictly O(N).

Applying the Master Theorem (Case 2):
    T(N) = 2T(N/2) + O(N)  ==>  T(N) = O(N log N)

For N = 10,000, N log2(N) ≈ 133,000 operations, which is nearly 400x fewer operations
than Brute Force!

Why Brute Force may be acceptable for small N:
For small inputs (e.g., N ≤ 50):
1. Overhead: Divide-and-Conquer involves recursive call stacks, array slicing, median finding,
   and strip filtering, which introduce constant-factor overhead.
2. Simplicity & Cache Locality: Brute Force executes a tight, simple nested loop that is
   highly cache-friendly with zero recursion overhead.
3. Therefore, for tiny N, Brute Force is often equally fast or even faster, which is why
   Divide-and-Conquer uses Brute Force as its base case for subproblems with N ≤ 3.
""")

    # Generate Performance Visualization Plot
    print("Generating performance chart via plot_performance()...")
    try:
        plot_performance(sizes, bf_times, dnc_times)
        print("Performance plot generated and saved successfully.")
    except Exception as e:
        print(f"Notice: plot_performance encountered an error ({e}).")
        print("If running in a non-GUI or headless environment, ensure matplotlib has an active backend.")

    return sizes, bf_times, dnc_times


if __name__ == '__main__':
    run_benchmark()
