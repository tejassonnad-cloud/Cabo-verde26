# API reference

Base URL for local development: `http://localhost:8080`.

## Maze request schema

```json
{
  "grid": ["#####", "#SaA#", "###.#", "###E#", "#####"],
  "keyTypes": 1
}
```

`grid` is a list of equal-width row strings and must form a square, at most 60×60. Valid cells are `.`, `#`, `S`, `E`, `a`–`f`, `A`–`F`, and the export/re-import marker `x`. Exactly one `S` is required. The last row-major `E` is the exit; earlier `E` cells are doors for key `e` when `keyTypes` is at least five.

## Endpoints

| Method | Endpoint | Input | Output |
|---|---|---|---|
| POST | `/api/mazes/generate` | `{ "size": 15, "keyTypes": 3, "seed": 7 }` | Maze rows, configuration, seed, start, exit |
| POST | `/api/mazes/solve` | Maze request | `SolverResult` with path, path steps, inventory events, and measured search statistics |
| POST | `/api/mazes/validate` | Maze request | `{ "valid": boolean, "errors": string[] }` |
| POST | `/api/mazes/upload?keyTypes=1` | Multipart `file` CSV | Parsed maze response |
| POST | `/api/mazes/export` | Maze request | Downloadable path-marked CSV, computed and checked in Java |
| GET | `/api/algorithm/info` | None | Algorithm, augmented-state, and complexity metadata |

Validation failures return HTTP 400:

```json
{
  "timestamp": "2026-01-01T00:00:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Maze must contain exactly one start 'S'; found 0."
}
```

An unreachable but valid maze returns HTTP 200, `solvable: false`, `shortestPathLength: -1`, and empty path arrays.
