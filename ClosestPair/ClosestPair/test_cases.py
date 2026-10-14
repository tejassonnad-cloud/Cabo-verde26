"""
test_cases.py - Comprehensive Test Suite for Closest Pair of Points Algorithms.

Tests both Brute-Force O(N^2) and Divide-and-Conquer O(N log N) implementations
across all edge cases and varying inputs.
"""

import sys
import math
import random
import os

# Ensure current script directory is in sys.path for local module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Enable ANSI colors on Windows terminals if supported
if os.name == 'nt':
    os.system('')
    # Fix Unicode encoding for Windows terminals (cp1252 cannot render box-drawing characters)
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from brute_force import closest_pair_brute_force
from divide_conquer import closest_pair_dnc

TOLERANCE = 1e-9

# ANSI color codes for formatted terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_test(name, points, expected_dist=None, expect_exception=False):
    """
    Run brute force and divide-and-conquer on the same points, verify distances
    match within tolerance, verify against expected_dist if provided, and print
    formatted results.

    Args:
        name: Name / description of the test case
        points: List of (x, y) tuples or invalid input
        expected_dist: Expected minimum distance (optional)
        expect_exception: If True or if points has < 2 elements, expect ValueError

    Returns:
        bool: True if test passed, False otherwise
    """
    print(f"\n{BOLD}{'=' * 72}{RESET}")
    print(f"{CYAN}{BOLD}TEST: {name}{RESET}")
    print(f"{'-' * 72}")

    # Handle expected exception case (e.g., N < 2)
    if expect_exception or (points is not None and len(points) < 2):
        bf_raised = False
        dnc_raised = False
        bf_err_msg = ""
        dnc_err_msg = ""

        try:
            closest_pair_brute_force(points)
        except ValueError as e:
            bf_raised = True
            bf_err_msg = str(e)
        except Exception as e:
            bf_err_msg = f"Unexpected exception: {type(e).__name__}: {e}"

        try:
            closest_pair_dnc(points)
        except ValueError as e:
            dnc_raised = True
            dnc_err_msg = str(e)
        except Exception as e:
            dnc_err_msg = f"Unexpected exception: {type(e).__name__}: {e}"

        n_pts = len(points) if points is not None else 0
        print(f"  Input points count : {n_pts}")
        print(f"  Brute Force        : {'Raised ValueError (' + bf_err_msg + ')' if bf_raised else 'FAILED to raise ValueError'}")
        print(f"  Divide & Conquer   : {'Raised ValueError (' + dnc_err_msg + ')' if dnc_raised else 'FAILED to raise ValueError'}")

        if bf_raised and dnc_raised:
            print(f"  Status             : {GREEN}{BOLD}[ PASS ] Both algorithms correctly raised ValueError{RESET}")
            print(f"{'=' * 72}")
            return True
        else:
            print(f"  Status             : {RED}{BOLD}[ FAIL ] Expected ValueError was not raised by both algorithms{RESET}")
            print(f"{'=' * 72}")
            return False

    n = len(points)
    if n <= 10:
        print(f"  Points ({n})         : {points}")
    else:
        print(f"  Points ({n})         : [{points[0]}, {points[1]}, ... (showing 2 of {n}) ... {points[-1]}]")

    bf_dist, bf_pair = None, None
    dnc_dist, dnc_pair = None, None

    # Run Brute Force
    try:
        bf_res = closest_pair_brute_force(points)
        bf_dist, bf_pair = bf_res[0], bf_res[1]
    except Exception as e:
        print(f"  {RED}Brute Force raised unexpected exception: {e}{RESET}")

    # Run Divide and Conquer
    try:
        dnc_res = closest_pair_dnc(points)
        dnc_dist = dnc_res[0]
        dnc_pair = dnc_res[1]
    except Exception as e:
        print(f"  {RED}Divide & Conquer raised unexpected exception: {e}{RESET}")

    if bf_dist is None or dnc_dist is None:
        print(f"  Status             : {RED}{BOLD}[ FAIL ] Execution error occurred{RESET}")
        print(f"{'=' * 72}")
        return False

    print(f"  Brute Force result : dist = {bf_dist:.9f}, pair = {bf_pair}")
    print(f"  D&C result         : dist = {dnc_dist:.9f}, pair = {dnc_pair}")
    if expected_dist is not None:
        print(f"  Expected dist      : dist = {expected_dist:.9f}")

    dist_diff = abs(bf_dist - dnc_dist)
    algorithms_match = dist_diff < TOLERANCE

    expected_match = True
    if expected_dist is not None:
        expected_match = (abs(bf_dist - expected_dist) < TOLERANCE) and (abs(dnc_dist - expected_dist) < TOLERANCE)

    passed = algorithms_match and expected_match

    print(f"  Distance difference: {dist_diff:.2e} (tolerance = {TOLERANCE:.0e})")
    if passed:
        print(f"  Status             : {GREEN}{BOLD}[ PASS ] Both algorithms agreed within tolerance!{RESET}")
    else:
        failures = []
        if not algorithms_match:
            failures.append(f"Algorithms differ by {dist_diff:.6e}")
        if not expected_match:
            failures.append(f"Did not match expected distance {expected_dist:.9f}")
        print(f"  Status             : {RED}{BOLD}[ FAIL ] {'; '.join(failures)}{RESET}")

    print(f"{'=' * 72}")
    return passed


# =====================================================================
# INDIVIDUAL TEST CASE IMPLEMENTATIONS
# =====================================================================

def test_1_n_less_than_2():
    """1. N < 2: points = [(1,2)] -> should raise ValueError from both algorithms."""
    points = [(1, 2)]
    return run_test("1. N < 2 (Validation Check)", points, expect_exception=True)


def test_2_n_equals_2():
    """2. N = 2: points = [(0,0), (3,4)] -> distance = 5.0"""
    points = [(0, 0), (3, 4)]
    return run_test("2. N = 2 (Minimal Valid Pair)", points, expected_dist=5.0)


def test_3_duplicate_points():
    """3. Duplicate points: points = [(2,3), (5,7), (2,3)] -> distance = 0.0"""
    points = [(2, 3), (5, 7), (2, 3)]
    return run_test("3. Duplicate Points (Distance Zero)", points, expected_dist=0.0)


def test_4_collinear_points():
    """4. Collinear points: points = [(1,1), (2,2), (3,3), (10,10)] -> closest dist = sqrt(2)"""
    points = [(1, 1), (2, 2), (3, 3), (10, 10)]
    return run_test("4. Collinear Points", points, expected_dist=math.sqrt(2))


def test_5_same_x_coordinate():
    """5. Same x-coordinate: points = [(2,1), (2,5), (2,8)] -> closest is (2,5)-(2,8), dist = 3.0"""
    points = [(2, 1), (2, 5), (2, 8)]
    return run_test("5. Points Sharing Same X-Coordinate", points, expected_dist=3.0)


def test_6_same_y_coordinate():
    """6. Same y-coordinate: points = [(1,4), (5,4), (10,4)] -> closest is (1,4)-(5,4), dist = 4.0"""
    points = [(1, 4), (5, 4), (10, 4)]
    return run_test("6. Points Sharing Same Y-Coordinate", points, expected_dist=4.0)


def test_7_negative_coordinates():
    """7. Negative coordinates: points = [(-2,-3), (-5,4), (3,-1)] -> compute and verify agreement"""
    points = [(-2, -3), (-5, 4), (3, -1)]
    # Pair (-2,-3) and (3,-1): dist = sqrt((3 - -2)^2 + (-1 - -3)^2) = sqrt(25 + 4) = sqrt(29)
    return run_test("7. Negative Coordinates", points, expected_dist=math.sqrt(29))


def test_8_floating_point_coordinates():
    """8. Floating-point coordinates: points = [(1.5, 2.7), (3.1, 4.9), (1.6, 2.8)] -> verify agreement"""
    points = [(1.5, 2.7), (3.1, 4.9), (1.6, 2.8)]
    # Pair (1.5, 2.7) and (1.6, 2.8): dist = sqrt((0.1)^2 + (0.1)^2) = sqrt(0.02)
    return run_test("8. Floating-Point Coordinates", points, expected_dist=math.sqrt(0.02))


def test_9_multiple_pairs_same_distance():
    """9. Multiple pairs same distance: points = [(0,0), (1,0), (2,0), (3,0)] -> multiple pairs with dist=1"""
    points = [(0, 0), (1, 0), (2, 0), (3, 0)]
    return run_test("9. Multiple Pairs with Same Distance", points, expected_dist=1.0)


def test_10_large_n():
    """10. Large N: Generate 5000 random points, verify agreement."""
    print(f"\n{YELLOW}Generating 5,000 random points in range [-5000, 5000] for stress test...{RESET}")
    random.seed(42)
    points = [(random.uniform(-5000.0, 5000.0), random.uniform(-5000.0, 5000.0)) for _ in range(5000)]
    return run_test("10. Large N (5000 Random Points)", points)


def test_11_all_same_point():
    """11. All same point: points = [(5,5), (5,5), (5,5)] -> distance = 0"""
    points = [(5, 5), (5, 5), (5, 5)]
    return run_test("11. All Same Point (All Duplicates)", points, expected_dist=0.0)


def test_12_random_stress_test():
    """12. Random stress test: Run 20 random tests with N between 10 and 200, verify agreement each time."""
    print(f"\n{BOLD}{'=' * 72}{RESET}")
    print(f"{CYAN}{BOLD}TEST 12: Random Stress Test (20 trials, N ∈ [10, 200]){RESET}")
    print(f"{'-' * 72}")

    random.seed(12345)
    all_trials_passed = True
    trials_passed_count = 0
    total_trials = 20

    for i in range(1, total_trials + 1):
        n_pts = random.randint(10, 200)
        pts = [(random.uniform(-1000.0, 1000.0), random.uniform(-1000.0, 1000.0)) for _ in range(n_pts)]

        try:
            bf_res = closest_pair_brute_force(pts)
            bf_dist = bf_res[0]
            dnc_res = closest_pair_dnc(pts)
            dnc_dist = dnc_res[0]
            diff = abs(bf_dist - dnc_dist)

            if diff < TOLERANCE:
                trials_passed_count += 1
                status = f"{GREEN}PASS{RESET}"
            else:
                all_trials_passed = False
                status = f"{RED}FAIL (diff={diff:.2e}){RESET}"
        except Exception as e:
            all_trials_passed = False
            status = f"{RED}ERROR ({e}){RESET}"

        print(f"  Trial {i:02d}/{total_trials:02d} (N={n_pts:3d}) : BF={bf_dist:.6f}, DNC={dnc_dist:.6f} -> [{status}]")

    print(f"{'-' * 72}")
    if all_trials_passed:
        print(f"  Result             : {GREEN}{BOLD}[ PASS ] All 20/20 random stress trials passed!{RESET}")
    else:
        print(f"  Result             : {RED}{BOLD}[ FAIL ] Only {trials_passed_count}/20 random stress trials passed.{RESET}")
    print(f"{'=' * 72}")
    return all_trials_passed


def run_all_tests():
    """Run all 12 test suites and print a colored summary."""
    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║            CLOSEST PAIR OF POINTS — TEST SUITE VERIFICATION          ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")

    test_functions = [
        ("Test 1: N < 2", test_1_n_less_than_2),
        ("Test 2: N = 2", test_2_n_equals_2),
        ("Test 3: Duplicate Points", test_3_duplicate_points),
        ("Test 4: Collinear Points", test_4_collinear_points),
        ("Test 5: Same X-Coordinate", test_5_same_x_coordinate),
        ("Test 6: Same Y-Coordinate", test_6_same_y_coordinate),
        ("Test 7: Negative Coordinates", test_7_negative_coordinates),
        ("Test 8: Floating-Point Coordinates", test_8_floating_point_coordinates),
        ("Test 9: Multiple Pairs Same Distance", test_9_multiple_pairs_same_distance),
        ("Test 10: Large N (5000 points)", test_10_large_n),
        ("Test 11: All Same Point", test_11_all_same_point),
        ("Test 12: Random Stress Test (20 trials)", test_12_random_stress_test),
    ]

    passed = 0
    failed = 0
    total = len(test_functions)

    for test_name, test_fn in test_functions:
        try:
            success = test_fn()
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n{RED}{BOLD}FATAL EXCEPTION in {test_name}: {e}{RESET}")
            failed += 1

    print(f"\n{BOLD}============ TEST SUMMARY ============{RESET}")
    if failed == 0:
        print(f"{GREEN}{BOLD}Passed: {passed} / {total}{RESET}")
        print(f"{GREEN}{BOLD}Failed: {failed}{RESET}")
        print(f"{GREEN}{BOLD}ALL TESTS PASSED!{RESET}")
    else:
        print(f"{YELLOW}{BOLD}Passed: {passed} / {total}{RESET}")
        print(f"{RED}{BOLD}Failed: {failed}{RESET}")
    print(f"{BOLD}======================================{RESET}\n")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
