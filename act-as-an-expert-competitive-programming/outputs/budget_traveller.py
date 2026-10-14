#!/usr/bin/env python3
"""Minimum-cost flight route with a stop limit and halving coupons.

Stdin format: N M K C, followed by M lines: u v price (1-indexed).
CSV mode: edges CSV with columns from,to,price; provide --n, --k, --coupons.
Outputs the minimum cost (or -1). --csv-out writes the chosen path; coupon_used
and path_mark contain 'x' on the corresponding edge row.
"""
from __future__ import annotations

import argparse
import csv
import heapq
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Edge:
    to: int
    price: int


def solve(n: int, k: int, coupons: int, edges: list[tuple[int, int, int]]):
    if n < 1 or k < 0 or coupons < 0:
        raise ValueError("N must be positive; K and C must be non-negative")
    graph: list[list[Edge]] = [[] for _ in range(n + 1)]
    for u, v, p in edges:
        if not (1 <= u <= n and 1 <= v <= n) or p < 0:
            raise ValueError("edge endpoints must be in 1..N and prices non-negative")
        graph[u].append(Edge(v, p))

    # A route with at most K intermediate cities has at most K+1 flights.
    max_flights = k + 1
    coupons = min(coupons, max_flights)  # extra coupons can never be spent
    # State is (city, flights_used, coupons_used); costs are nonnegative, so
    # Dijkstra is valid. Keeping flights in state enforces the bounded route.
    inf = 10**100
    dist = [[[inf] * (coupons + 1) for _ in range(max_flights + 1)]
            for _ in range(n + 1)]
    parent: dict[tuple[int, int, int], tuple[tuple[int, int, int], int, bool]] = {}
    start = (1, 0, 0)
    dist[1][0][0] = 0
    pq = [(0, 1, 0, 0)]  # cost, city, flights used, coupons used
    goal: Optional[tuple[int, int, int]] = None

    while pq:
        cost, city, flights, used = heapq.heappop(pq)
        if cost != dist[city][flights][used]:
            continue
        if city == n:
            goal = (city, flights, used)
            break
        if flights == max_flights:
            continue
        for edge in graph[city]:
            next_flights = flights + 1
            # Ordinary fare transition.
            candidate = cost + edge.price
            if candidate < dist[edge.to][next_flights][used]:
                dist[edge.to][next_flights][used] = candidate
                state = (edge.to, next_flights, used)
                parent[state] = ((city, flights, used), edge.price, False)
                heapq.heappush(pq, (candidate, *state))
            # Coupon transition; each flight consumes at most one coupon.
            if used < coupons:
                candidate = cost + edge.price // 2
                if candidate < dist[edge.to][next_flights][used + 1]:
                    dist[edge.to][next_flights][used + 1] = candidate
                    state = (edge.to, next_flights, used + 1)
                    parent[state] = ((city, flights, used), edge.price, True)
                    heapq.heappush(pq, (candidate, *state))

    if goal is None:
        return -1, []
    route = []
    state = goal
    while state != start:
        previous, price, coupon = parent[state]
        route.append({"from": previous[0], "to": state[0], "price": price,
                      "coupon_used": "x" if coupon else "",
                      "path_mark": "x"})
        state = previous
    route.reverse()
    return dist[goal[0]][goal[1]][goal[2]], route


def read_stdin():
    data = list(map(int, sys.stdin.buffer.read().split()))
    if len(data) < 4:
        raise ValueError("expected N M K C followed by M edges")
    n, m, k, c = data[:4]
    if len(data) != 4 + 3 * m:
        raise ValueError(f"expected {m} edge triples")
    edges = [tuple(data[i:i + 3]) for i in range(4, len(data), 3)]
    return n, k, c, edges


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)
        required = {"from", "to", "price"}
        if not required.issubset(rows.fieldnames or []):
            raise ValueError("edge CSV must have columns from,to,price")
        return [(int(r["from"]), int(r["to"]), int(r["price"])) for r in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-csv", help="edge CSV (from,to,price); otherwise read stdin")
    ap.add_argument("--n", type=int, help="number of cities (required with CSV)")
    ap.add_argument("--k", type=int, help="maximum intermediate stops")
    ap.add_argument("--coupons", type=int, help="number of available coupons")
    ap.add_argument("--csv-out", help="write selected route rows to this CSV")
    args = ap.parse_args()
    if args.input_csv:
        if None in (args.n, args.k, args.coupons):
            ap.error("--input-csv requires --n, --k, and --coupons")
        n, k, c, edges = args.n, args.k, args.coupons, read_csv(args.input_csv)
    else:
        if any(x is not None for x in (args.n, args.k, args.coupons)):
            ap.error("--n/--k/--coupons are only for --input-csv mode")
        n, k, c, edges = read_stdin()
    cost, route = solve(n, k, c, edges)
    print(cost)
    if args.csv_out:
        with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["from", "to", "price", "coupon_used", "path_mark"])
            writer.writeheader()
            writer.writerows(route)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
