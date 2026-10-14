# Budget Traveller with Coupons

Find the cheapest directed route from city `1` to city `N`, using no more than
`K` intermediate cities and up to `C` coupons. A coupon changes a flight fare
`p` to `floor(p/2)`. Each flight can use at most one coupon.

## Algorithms and correctness

Both solvers use Dijkstra on an expanded state graph. A state is
`(city, flights_used, coupons_used)` (equivalently, the requested
`(cost, city, stops_used, coupons_remaining)` tuple, with remaining coupons
derived from `C - coupons_used`). There can be at most `K+1` flights. Every
original flight produces a regular transition and, if a coupon remains, a
coupon transition costing `p//2`. All transition costs are nonnegative, so
Dijkstra finalizes states in nondecreasing cost order. The first destination
state removed from the priority queue is therefore the cheapest feasible
route. Predecessor records reconstruct the selected flights and coupon marks.

The state graph has `O(N (K+1) (min(C,K+1)+1))` states. With adjacency lists
and a binary heap, runtime is `O((N+M)(K+1)(min(C,K+1)+1) log(N(K+1)(min(C,K+1)+1)))`;
space is `O((N+M)(K+1)(min(C,K+1)+1))`. Here `C` is capped at `K+1`, since no
route can use more coupons than flights. Python uses arbitrary-precision
integers; Java uses `long` for route costs.

Corner cases: `K=0` permits only a direct flight; `C=0` disables coupon
transitions; a disconnected destination prints `-1`; parallel edges are kept
as distinct transitions; zero-price edges are valid; `N=1` returns zero.

## Python

Stdin:

```text
N M K C
u1 v1 price1
...
uM vM priceM
```

```sh
python budget_traveller.py < input.txt
python budget_traveller.py < input.txt --csv-out route.csv
python budget_traveller.py --input-csv flights.csv --n 8 --k 3 --coupons 2 --csv-out route.csv
```

## Java

```sh
javac BudgetTraveller.java
java BudgetTraveller < input.txt
java BudgetTraveller < input.txt --csv-out route.csv
java BudgetTraveller --input-csv flights.csv --n 8 --k 3 --coupons 2 --csv-out route.csv
```

For CSV input, `flights.csv` must have a header with `from,to,price` columns.
The path output has columns `from,to,price,coupon_used,path_mark`; each selected
edge has `x` in `path_mark`, and coupon-discounted edges also have `x` in
`coupon_used`. Standard output contains only the minimum cost, or `-1`.

## Interactive visualization

Install `matplotlib` and `networkx`, then run:

```sh
python visualize_route.py --edges flights.csv --path route.csv
```

It draws all flights, then animates the selected route one flight at a time,
showing accumulated cost and stops. Coupon flights are gold; other chosen
flights are blue. This is a lightweight desktop plot, rather than a browser
canvas. As with any graph drawing, parallel directed flights share a visual
connection; their fares are still handled separately by the solvers.
