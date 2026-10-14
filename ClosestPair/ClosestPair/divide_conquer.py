"""
Closest Pair of Points — Divide-and-Conquer Implementation
===========================================================
Complexity:
    Time:  O(N log N)
    Space: O(N)

This module implements the genuine O(N log N) divide-and-conquer algorithm
for finding the closest pair of points on a 2D Euclidean plane.

Key Algorithmic Properties:
1. Sort points by X-coordinate ONCE at the start: O(N log N).
2. Maintain Y-sorted points throughout recursion via linear splitting: O(N).
3. Recurrence relation: T(N) = 2*T(N/2) + O(N) = O(N log N) by Master Theorem.
4. Base case: If N <= 3, compute pairwise distance directly on those points.
5. Strip processing: For points within delta of the dividing line, sort by Y
   and compare each point to at most 7 following points (geometric packing argument).
6. Records comprehensive recursive steps for step-by-step visualization.
"""

import math
from typing import List, Tuple, Sequence, Dict, Any


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


def _closest_pair_rec(
    px: List[Tuple[float, float, int]],
    py: List[Tuple[float, float, int]],
    level: int,
    steps: List[Dict[str, Any]],
) -> Tuple[float, Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Internal recursive divide-and-conquer function.

    Args:
        px: Points sorted by x-coordinate, each point is (x, y, original_id)
        py: Points sorted by y-coordinate, each point is (x, y, original_id)
        level: Current recursion depth (starts at 0)
        steps: List to accumulate step metadata dictionaries for visualization

    Returns:
        (min_distance, (point1, point2))
    """
    n = len(px)

    # Base case: if N <= 3, solve using brute force on those points only
    if n <= 3:
        min_dist = float("inf")
        best_pair = None
        for i in range(n - 1):
            p1 = (float(px[i][0]), float(px[i][1]))
            for j in range(i + 1, n):
                p2 = (float(px[j][0]), float(px[j][1]))
                d = euclidean_distance(p1, p2)
                if d < min_dist:
                    min_dist = d
                    best_pair = (p1, p2)

        mid_idx = n // 2
        mid_x = float(px[mid_idx][0])
        step: Dict[str, Any] = {
            "level": level,
            "points": [(float(p[0]), float(p[1])) for p in px],
            "mid_x": mid_x,
            "left_points": [(float(p[0]), float(p[1])) for p in px[:mid_idx]],
            "right_points": [(float(p[0]), float(p[1])) for p in px[mid_idx:]],
            "strip": [],
            "delta": float(min_dist),
            "closest_pair": best_pair,
            "min_dist": float(min_dist),
        }
        steps.append(step)
        return (min_dist, best_pair)  # type: ignore[return-value]

    # Recursive case: N > 3
    mid = n // 2
    mid_point = px[mid]
    mid_x = float(mid_point[0])

    left_x = px[:mid]
    right_x = px[mid:]

    # Linear O(N) partitioning of y-sorted list into left and right halves
    left_id_set = {p[2] for p in left_x}
    left_y = [p for p in py if p[2] in left_id_set]
    right_y = [p for p in py if p[2] not in left_id_set]

    # Register step in pre-order so that the root level step sits at steps[0]
    step = {
        "level": level,
        "points": [(float(p[0]), float(p[1])) for p in px],
        "mid_x": mid_x,
        "left_points": [(float(p[0]), float(p[1])) for p in left_x],
        "right_points": [(float(p[0]), float(p[1])) for p in right_x],
        "strip": [],
        "delta": float("inf"),
        "closest_pair": None,
        "min_dist": float("inf"),
    }
    steps.append(step)

    # Recurse on left and right subproblems
    d_left, pair_left = _closest_pair_rec(left_x, left_y, level + 1, steps)
    d_right, pair_right = _closest_pair_rec(right_x, right_y, level + 1, steps)

    if d_left <= d_right:
        delta = d_left
        best_pair = pair_left
    else:
        delta = d_right
        best_pair = pair_right

    min_dist = delta

    # Build strip: points with |x - mid_x| < delta
    # Since py is already sorted by y-coordinate, filtering py maintains y-sort in O(N)
    strip = [p for p in py if abs(p[0] - mid_x) < delta]
    # Explicitly ensure sorted by y-coordinate (Timsort runs in O(K) on sorted data)
    strip.sort(key=lambda p: (p[1], p[0]))

    strip_len = len(strip)

    # For each point in strip, compare to next points where y-difference < delta (at most 7)
    for i in range(strip_len):
        p1 = (float(strip[i][0]), float(strip[i][1]))
        # Compare to at most 7 subsequent points
        for j in range(i + 1, min(i + 8, strip_len)):
            p2 = (float(strip[j][0]), float(strip[j][1]))
            # If vertical distance exceeds min_dist, no subsequent point can be closer
            if (p2[1] - p1[1]) >= min_dist:
                break
            d = euclidean_distance(p1, p2)
            if d < min_dist:
                min_dist = d
                best_pair = (p1, p2)

    # Update the step dictionary with final combine results
    step["strip"] = [(float(p[0]), float(p[1])) for p in strip]
    step["delta"] = float(delta)
    step["closest_pair"] = best_pair
    step["min_dist"] = float(min_dist)

    return (min_dist, best_pair)


def closest_pair_dnc(
    points: Sequence[Sequence[float]],
) -> Tuple[float, Tuple[Tuple[float, float], Tuple[float, float]], List[Dict[str, Any]]]:
    """
    Find closest pair using Divide-and-Conquer genuine O(N log N) approach.

    Args:
        points: List of tuples/lists [(x1,y1), (x2,y2), ...]

    Returns:
        (min_distance, (point1, point2), steps)
        where:
            min_distance: float representing minimum Euclidean distance found
            (point1, point2): tuple of two closest points
            steps: list of dicts recording the recursive process for visualization

    Raises:
        ValueError: if N < 2 or invalid point data is provided.
    """
    _validate_points(points)

    # Tag each point with its original index to handle identical duplicate coordinates cleanly
    indexed_pts: List[Tuple[float, float, int]] = [
        (float(p[0]), float(p[1]), idx) for idx, p in enumerate(points)
    ]

    # Pre-sort once by X-coordinate and once by Y-coordinate: O(N log N)
    px = sorted(indexed_pts, key=lambda p: (p[0], p[1], p[2]))
    py = sorted(indexed_pts, key=lambda p: (p[1], p[0], p[2]))

    steps: List[Dict[str, Any]] = []
    min_dist, best_pair = _closest_pair_rec(px, py, level=0, steps=steps)

    return (min_dist, best_pair, steps)


if __name__ == "__main__":
    print("Testing divide_conquer.py module...")
    sample = [(0, 0), (3, 4), (1, 1), (5, 5), (1, 1)]
    dist, pair, steps_record = closest_pair_dnc(sample)
    print(f"D&C Closest pair: {pair} with distance {dist}")
    print(f"Total steps recorded: {len(steps_record)}")
    print(f"Top-level step mid_x: {steps_record[0]['mid_x']}, delta: {steps_record[0]['delta']}")
