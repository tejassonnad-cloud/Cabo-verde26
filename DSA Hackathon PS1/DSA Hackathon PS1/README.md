# Maze with Keys and Doors

An interactive shortest-path visualizer for mazes with keys and locked doors. The Spring Boot backend owns validation, generation, CSV handling, and the solver. The React frontend renders and animates only the path returned by that Java backend.

## Requirements

- Java 17 or later
- Maven Wrapper (included; Maven 3.9.11 is downloaded on first use)
- Node.js 20.19 or later (or 22.12 or later) and npm

## Run locally

In one terminal, start the API:

```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

In another terminal, install and start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). Vite proxies `/api` to Spring Boot on port 8080. The backend allows browser requests from `localhost:5173` and `127.0.0.1:5173` only.

Run backend tests and build artifacts:

```powershell
cd backend
.\mvnw.cmd test
.\mvnw.cmd package
```

Build the production frontend:

```powershell
cd frontend
npm run build
```

The frontend output is in `frontend/dist`. For production, serve that directory and proxy `/api` to the Spring Boot service on the same origin (or configure a specific allowed origin in `WebConfig`).

## Project layout

```text
backend/src/main/java/com/hackathon/maze/
  model/       Immutable maze, positions, path steps, solver result
  validation/  Grid and symbol validation
  algorithm/   Augmented-state breadth-first search
  generator/   Seeded solvable maze generation
  io/          CSV parser, path verification, and marked export
  service/     Application orchestration
  controller/  REST endpoints, CORS, and API error handling
  dto/         Request and response types
backend/src/test/java/  JUnit 5 tests for the solver, generator, and CSV layer
frontend/src/
  services/    Calls to the Java API
  components/  UI elements are composed in App.tsx
  types/       API response types
  styles.css   Responsive dashboard and maze presentation
examples/      Solvable and unsolvable CSV inputs
```

## Maze format

Each grid is square. A CSV cell contains one symbol: `.` open, `#` wall, `S` start, `E` exit, `a`–`f` keys, and `A`–`F` doors. `T` (`keyTypes`) is between 1 and 6. Symbols outside the configured first `T` key/door types are rejected. A door without a key is valid input but may make the maze unsolvable. The export marker `x` is accepted as an open cell when a marked CSV is uploaded again.

The prompt assigns `E` both to the exit and to the door paired with key `e`. When both are present, the API resolves that ambiguity by treating the final `E` in row-major order as the exit and any earlier `E` cells as doors for key `e`. With only one `E`, it is the exit. This rule supports all six pairs and is used consistently by validation, solving, and CSV export.

CSV uploads use UTF-8 (with or without BOM), comma-separated cells, optional quoted fields, and trimmed cell whitespace. Upload with the selected `keyTypes` configuration. The sample files are under `examples/` and use `T=1`.

## REST API

Requests and responses use JSON unless noted. Invalid request data returns HTTP 400 with `{ "timestamp", "status", "error", "message" }`. A valid but unsolvable maze returns HTTP 200 with `solvable: false` and `shortestPathLength: -1`.

### `POST /api/mazes/generate`

Request:

```json
{ "size": 15, "keyTypes": 3, "seed": 2026 }
```

`seed` is optional. Response contains the grid rows, size, key type count, actual seed, and start/exit coordinates. The generator builds a connected protected route, puts each key before its door, grows optional connected branches, then validates the result with the solver.

### `POST /api/mazes/solve`

Request:

```json
{ "grid": ["#####", "#SaA#", "###.#", "###E#", "#####"], "keyTypes": 1 }
```

Response fields include `solvable`, `shortestPathLength`, `path`, `pathSteps`, `keysCollected`, `doorsOpened`, `statesExplored`, `uniqueStatesVisited`, and `executionTimeNanos`. Each path step reports its coordinate, cell type, key mask, inventory, and key/door event.

### `POST /api/mazes/validate`

Uses the same maze request and returns `{ "valid": true|false, "errors": [] }`.

### `POST /api/mazes/upload?keyTypes=1`

Multipart form with a `file` CSV field and required `keyTypes` query parameter. Returns the parsed, validated maze.

### `POST /api/mazes/export`

Accepts the maze request and returns `maze-solution.csv` as a downloadable `text/csv` response. The backend computes its own solution, validates the path, marks ordinary intermediate path cells with `x`, and preserves start, exit, keys, doors, walls, and off-path cells. The original maze object is not changed.

### `GET /api/algorithm/info`

Returns the algorithm name, augmented state, key limit, complexity, and a brief explanation.

## Algorithm and correctness

The solver searches `(row, column, keyMask)`, not just grid coordinates. Key `a` maps to bit 0 through key `f` at bit 5. Entering a key updates the mask with OR; a door transition is legal only when its corresponding bit is already present. Walls are skipped. The FIFO queue is an `ArrayDeque`; each augmented state is enqueued once, its distance is recorded, and a parent state ID is stored for reconstruction. The neighbor order is up, right, down, left, so equal-length solutions are deterministic.

Every move has unit cost. BFS removes states in nondecreasing distance order. The position and key mask contain all information needed to determine future legal moves, and state-aware visited tracking keeps the same coordinate with different inventories separate. Thus the first exit state removed from the queue has minimum distance. Each parent pointer represents one legal transition, so following those pointers reconstructs a valid shortest route.

For an `N × N` maze and `T` key types, there are at most `N² × 2^T` states. Every state has at most four outgoing transitions, giving `O(N² × 2^T)` time and space. Since `T ≤ 6`, the inventory multiplier is at most 64. Ordinary grid BFS loses inventory distinctions; DFS does not guarantee the shortest route; Dijkstra adds no value when all moves cost one; A* can be useful with a strong heuristic but must still include the key mask and preserve optimality conditions.

## Animation and results

The visualization animates `pathSteps` returned by the API. Play, pause, previous/next, reset, speed, and scrubbing all operate on that response. The inventory panel updates from the exact backend step, with pickup and door events shown as they happen. No BFS exploration animation is shown because the API returns no exploration trace. Search counts, solution length, key/door counts, and runtime come from the solver response.
