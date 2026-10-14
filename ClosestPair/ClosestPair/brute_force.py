"""
Closest Pair of Points — Brute Force Implementation
====================================================
Complexity:
    Time:  O(N^2)
    Space: O(1) auxiliary

This module provides the exhaustive pairwise comparison approach to find
the closest pair of points on a 2D Euclidean plane.
"""

import math
from typing import List, Tuple, Sequence, Any


def euclidean_distance(p1: Sequence[float], p2: Sequence[float]) -> float:
    """
    Calculate Euclidean distance between two 2D points.

    Args:
        p1: First point coordinate (x1, y1)
        p2: Second point coordinate (x2, y2)

    Returns:
        float: Euclidean distance sqrt((x1 - x2)^2 + (y1 - y2)^2)
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _validate_points(points: Any) -> None:
    """
    Validate that points is a valid sequence of at least 2 2D points.

    Args:
        points: Input collection to validate

    Raises:
        ValueError: If points is None, has length < 2, or contains invalid coordinates.
    """
    if points is None:
        raise ValueError("Points collection cannot be None. At least 2 points are required.")
    try:
        n = len(points)
    except TypeError:
        raise ValueError("Points input must be a sizable sequence (e.g., list or tuple).")

    if n < 2:
        raise ValueError(f"At least 2 points are required, got {n}.")

    for idx, p in enumerate(points):
        if not (isinstance(p, (tuple, list)) and len(p) >= 2):
            raise ValueError(
                f"Invalid point at index {idx}: expected 2D coordinate (tuple or list of length >= 2), got {p}"
            )


def closest_pair_brute_force(
    points: Sequence[Sequence[float]],
) -> Tuple[float, Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Find closest pair using brute-force O(N^2) approach.

    Compares every pair (i, j) where j > i, tracks the minimum distance,
    and returns the first closest pair found if multiple pairs share the
    minimum distance. Handles duplicates (distance = 0) and floating-point coordinates.

    Args:
        points: List of tuples/lists [(x1, y1), (x2, y2), ...]

    Returns:
        tuple: (min_distance, (point1, point2))
               where point1 and point2 are tuples representing the closest pair of points.

    Raises:
        ValueError: if N < 2 or invalid point data is provided.
    """
    _validate_points(points)

    n = len(points)
    min_distance = float("inf")
    closest_pair = None

    for i in range(n - 1):
        p1 = (float(points[i][0]), float(points[i][1]))
        for j in range(i + 1, n):
            p2 = (float(points[j][0]), float(points[j][1]))
            d = euclidean_distance(p1, p2)
            # Strictly less than preserves the first pair found
            if d < min_distance:
                min_distance = d
                closest_pair = (p1, p2)

    return (min_distance, closest_pair)


def find_all_closest_pairs(
    points: Sequence[Sequence[float]], tolerance: float = 1e-9
) -> Tuple[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
    """
    Find ALL pairs of points that share the minimum Euclidean distance.

    Args:
        points: List of tuples/lists [(x1, y1), (x2, y2), ...]
        tolerance: Floating-point comparison tolerance (default: 1e-9)

    Returns:
        tuple: (min_distance, list_of_pairs)
               where list_of_pairs contains all pairs ((x1, y1), (x2, y2))
               achieving the minimum distance within the specified tolerance.

    Raises:
        ValueError: if N < 2.
    """
    _validate_points(points)

    n = len(points)
    min_distance = float("inf")
    all_pairs: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []

    for i in range(n - 1):
        p1 = (float(points[i][0]), float(points[i][1]))
        for j in range(i + 1, n):
            p2 = (float(points[j][0]), float(points[j][1]))
            d = euclidean_distance(p1, p2)

            if d < min_distance - tolerance:
                # New strict minimum found
                min_distance = d
                all_pairs = [(p1, p2)]
            elif abs(d - min_distance) <= tolerance:
                # Distance ties with current minimum within tolerance
                all_pairs.append((p1, p2))

    return (min_distance, all_pairs)


if __name__ == "__main__":
    print("Testing brute_force.py module...")
    sample = [(0, 0), (3, 4), (1, 1), (5, 5), (1, 1)]
    dist, pair = closest_pair_brute_force(sample)
    print(f"Closest pair: {pair} with distance {dist}")

    all_dist, all_pairs = find_all_closest_pairs(sample)
    print(f"All closest pairs (dist {all_dist}): {all_pairs}")
