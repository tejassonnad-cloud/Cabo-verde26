"""
Closest Pair of Points — Interactive CLI Entry Point
Comparative Analysis between Brute Force O(N^2) and Divide & Conquer O(N log N)
"""

import os
import sys
import csv
import random
import time

# Ensure current script directory is in sys.path for local module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Fix Unicode encoding for Windows terminals (cp1252 cannot render box-drawing characters)
if os.name == 'nt':
    os.system('')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from brute_force import closest_pair_brute_force
from divide_conquer import closest_pair_dnc
from visualization import plot_results, plot_dnc_steps


def print_menu():
    """Display the interactive main menu."""
    menu_text = """
╔══════════════════════════════════════════════════════════╗
║     CLOSEST PAIR OF POINTS — COMPARATIVE ANALYSIS        ║
╠══════════════════════════════════════════════════════════╣
║  1. Generate random points                               ║
║  2. Enter points manually                                ║
║  3. Read points from CSV file                            ║
║  4. Run all test cases                                   ║
║  5. Run performance benchmark                            ║
║  6. Exit                                                 ║
╚══════════════════════════════════════════════════════════╝"""
    print(menu_text)


def format_pair(pair):
    """Format a pair of points for clean display."""
    p1, p2 = pair
    return f"({p1[0]}, {p1[1]}) and ({p2[0]}, {p2[1]})"


def run_analysis(points):
    """
    Run comparative analysis on a list of points using both
    Brute Force and Divide & Conquer algorithms.
    """
    if len(points) < 2:
        print("\nError: At least 2 points are required to find the closest pair.")
        return

    # 1. Print all input points
    print("\n" + "=" * 50)
    print("                  INPUT POINTS                    ")
    print("=" * 50)
    print(f"Total points count: N = {len(points)}")
    if len(points) <= 30:
        for idx, pt in enumerate(points, 1):
            print(f"  P{idx}: ({pt[0]}, {pt[1]})")
    else:
        for idx in range(12):
            print(f"  P{idx+1}: ({points[idx][0]}, {points[idx][1]})")
        print(f"  ... [{len(points) - 24} intermediate points omitted for readability] ...")
        for idx in range(len(points) - 12, len(points)):
            print(f"  P{idx+1}: ({points[idx][0]}, {points[idx][1]})")

    # 2. Run brute force with timing
    t0_bf = time.perf_counter()
    bf_dist, bf_pair = closest_pair_brute_force(points)
    t1_bf = time.perf_counter()
    bf_time_ms = (t1_bf - t0_bf) * 1000.0

    # 3. Run Divide and Conquer with timing
    t0_dnc = time.perf_counter()
    dnc_dist, dnc_pair, dnc_steps = closest_pair_dnc(points)
    t1_dnc = time.perf_counter()
    dnc_time_ms = (t1_dnc - t0_dnc) * 1000.0

    # 4. Print formatted output exactly as specified
    tolerance = 1e-9
    results_match = abs(bf_dist - dnc_dist) < tolerance
    match_str = "YES" if results_match else "NO"

    print("\n══════════════════════════════════════════════════")
    print("                BRUTE FORCE RESULTS               ")
    print("══════════════════════════════════════════════════")
    print(f"Minimum distance: {bf_dist:.6f}")
    print(f"Closest pair: {format_pair(bf_pair)}")
    print(f"Execution time: {bf_time_ms:.4f} ms")

    print("\n══════════════════════════════════════════════════")
    print("            DIVIDE AND CONQUER RESULTS            ")
    print("══════════════════════════════════════════════════")
    print(f"Minimum distance: {dnc_dist:.6f}")
    print(f"Closest pair: {format_pair(dnc_pair)}")
    print(f"Execution time: {dnc_time_ms:.4f} ms")

    print("\n══════════════════════════════════════════════════")
    print("               VERIFICATION                       ")
    print("══════════════════════════════════════════════════")
    print(f"Results Match: {match_str}")
    if not results_match:
        print(f"Difference: {abs(bf_dist - dnc_dist):.12e} (tolerance: {tolerance})")

    # 5. Ask if user wants to see visualization (y/n)
    while True:
        choice = input("\nDo you want to see the visualization? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            try:
                print("Displaying visualizations...")
                bf_result = (bf_dist, bf_pair)
                dnc_result = (dnc_dist, dnc_pair, dnc_steps)
                plot_results(points, bf_result, dnc_result, dnc_steps)
                plot_dnc_steps(points, dnc_steps)
            except Exception as e:
                print(f"Visualization notice: {e}")
            break
        elif choice in ['n', 'no']:
            break
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")


def handle_random_points():
    """Option 1: Generate random points within user-specified bounds."""
    print("\n--- 1. Generate Random Points ---")
    while True:
        n_str = input("Enter number of points (N >= 2): ").strip()
        try:
            n = int(n_str)
            if n < 2:
                print("Error: N must be at least 2. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer >= 2.")

    range_str = input("Enter coordinate range [min, max] (default: -100 to 100): ").strip()
    min_val, max_val = -100.0, 100.0
    if range_str:
        try:
            cleaned = range_str.replace("to", ",").replace(";", ",")
            parts = [float(p.strip()) for p in cleaned.split(",") if p.strip()]
            if len(parts) == 2 and parts[0] < parts[1]:
                min_val, max_val = parts[0], parts[1]
            else:
                print(f"Invalid range specification. Using default: [{min_val}, {max_val}].")
        except ValueError:
            print(f"Could not parse numeric range. Using default: [{min_val}, {max_val}].")

    print(f"Generating {n} random points with coordinates in [{min_val}, {max_val}]...")
    points = [
        (round(random.uniform(min_val, max_val), 4), round(random.uniform(min_val, max_val), 4))
        for _ in range(n)
    ]
    run_analysis(points)


def handle_manual_points():
    """Option 2: Manually enter points as x,y pairs."""
    print("\n--- 2. Enter Points Manually ---")
    while True:
        n_str = input("Enter number of points (N >= 2): ").strip()
        try:
            n = int(n_str)
            if n < 2:
                print("Error: N must be at least 2. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer >= 2.")

    points = []
    print(f"Enter {n} points as 'x,y' or 'x y' (e.g., 2.5, 3.1):")
    for i in range(n):
        while True:
            pt_str = input(f"Point {i + 1}/{n}: ").strip()
            if not pt_str:
                continue
            try:
                delimiter = "," if "," in pt_str else None
                parts = [float(val.strip()) for val in pt_str.split(delimiter) if val.strip()]
                if len(parts) != 2:
                    print("  Error: Please provide exactly two numbers: x and y.")
                    continue
                points.append((parts[0], parts[1]))
                break
            except ValueError:
                print("  Error: Invalid numbers. Please re-enter x and y.")

    run_analysis(points)


def handle_csv_points():
    """Option 3: Read points from a CSV file."""
    print("\n--- 3. Read Points from CSV File ---")
    filename_input = input("Enter CSV filename [default: sample_points.csv]: ").strip()
    filename = filename_input if filename_input else "sample_points.csv"

    # Search in working directory, script directory, or absolute path
    file_path = filename
    if not os.path.isabs(file_path):
        candidate = os.path.join(SCRIPT_DIR, file_path)
        if os.path.exists(candidate):
            file_path = candidate

    if not os.path.exists(file_path):
        print(f"Error: File '{filename}' was not found.")
        return

    points = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for line_no, row in enumerate(reader, 1):
                if not row or not any(field.strip() for field in row):
                    continue
                # Handle possible header row (e.g. 'x,y' or 'X,Y')
                if line_no == 1:
                    try:
                        float(row[0])
                        float(row[1])
                    except ValueError:
                        # Non-numeric header row detected, skip it
                        continue
                if len(row) < 2:
                    print(f"Warning: Skipping line {line_no}: requires at least 2 columns.")
                    continue
                try:
                    x = float(row[0].strip())
                    y = float(row[1].strip())
                    points.append((x, y))
                except ValueError:
                    print(f"Warning: Skipping line {line_no} due to invalid numeric data: {row}")
    except Exception as e:
        print(f"Error reading CSV file '{filename}': {e}")
        return

    if len(points) < 2:
        print(f"Error: CSV contains only {len(points)} valid point(s). Minimum 2 required.")
        return

    print(f"Successfully loaded {len(points)} points from '{os.path.basename(file_path)}'.")
    run_analysis(points)


def handle_run_tests():
    """Option 4: Run all automated test cases."""
    print("\n" + "=" * 50)
    print("                RUNNING ALL TEST CASES            ")
    print("=" * 50)
    try:
        import test_cases
        test_cases.run_all_tests()
    except ImportError:
        print("Error: 'test_cases.py' could not be found in the project directory.")
    except Exception as e:
        print(f"Error executing test suite: {e}")


def handle_run_benchmark():
    """Option 5: Run the performance benchmarking suite."""
    print("\n" + "=" * 50)
    print("           RUNNING PERFORMANCE BENCHMARK          ")
    print("=" * 50)
    try:
        import benchmark
        benchmark.run_benchmark()
    except ImportError:
        print("Error: 'benchmark.py' could not be found in the project directory.")
    except Exception as e:
        print(f"Error executing benchmark suite: {e}")


def main():
    """Main CLI application loop."""
    print("Welcome to the Closest Pair of Points Comparative Analysis Tool.")
    while True:
        print_menu()
        choice = input("\nEnter choice (1-6): ").strip()
        if choice == "1":
            handle_random_points()
        elif choice == "2":
            handle_manual_points()
        elif choice == "3":
            handle_csv_points()
        elif choice == "4":
            handle_run_tests()
        elif choice == "5":
            handle_run_benchmark()
        elif choice == "6":
            print("\nExiting Closest Pair Analysis. Thank you!")
            sys.exit(0)
        else:
            print("Invalid option. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
