package com.hackathon.maze.generator;

import com.hackathon.maze.algorithm.MazeSolver;
import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.SolverResult;
import com.hackathon.maze.validation.MazeValidator;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

/** Builds a guaranteed route first, then grows connected dead-end branches off it. */
public final class MazeGenerator {
    private static final int MAX_RETRIES = 8;
    private final MazeValidator validator;
    private final MazeSolver solver;

    public MazeGenerator() { this(new MazeValidator(), new MazeSolver()); }
    public MazeGenerator(MazeValidator validator, MazeSolver solver) { this.validator = validator; this.solver = solver; }

    public GenerationResult generate(int size, int keyTypes, Long requestedSeed) {
        if (size < 5 || size > MazeValidator.MAX_SIZE) throw new IllegalArgumentException("Grid size must be between 5 and " + MazeValidator.MAX_SIZE + ".");
        if (keyTypes < 1 || keyTypes > 6) throw new IllegalArgumentException("keyTypes (T) must be between 1 and 6.");
        if (size < keyTypes + 4) throw new IllegalArgumentException("Grid size " + size + " is too small for T=" + keyTypes + "; use at least " + (keyTypes + 4) + " cells per side.");
        long seed = requestedSeed == null ? new Random().nextLong() : requestedSeed;
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            Random random = new Random(seed + attempt);
            char[][] grid = new char[size][size];
            for (char[] row : grid) java.util.Arrays.fill(row, '#');
            List<int[]> route = new ArrayList<>();
            for (int c = 1; c < size - 1; c++) route.add(new int[]{1, c});
            for (int r = 2; r < size - 1; r++) route.add(new int[]{r, size - 2});
            Set<Integer> routeSet = new HashSet<>();
            for (int[] point : route) { grid[point[0]][point[1]] = '.'; routeSet.add(point[0] * size + point[1]); }
            grid[route.get(0)[0]][route.get(0)[1]] = 'S';
            grid[route.get(route.size() - 1)[0]][route.get(route.size() - 1)[1]] = 'E';
            int routeIndex = 1;
            for (int key = 0; key < keyTypes; key++) {
                grid[route.get(routeIndex)[0]][route.get(routeIndex)[1]] = (char) ('a' + key);
                routeIndex++;
                grid[route.get(routeIndex)[0]][route.get(routeIndex)[1]] = (char) ('A' + key);
                routeIndex++;
            }
            // Add randomized, connected dead-end pockets without ever removing the protected route.
            List<int[]> candidates = new ArrayList<>();
            for (int r = 1; r < size - 1; r++) for (int c = 1; c < size - 1; c++)
                if (!routeSet.contains(r * size + c)) candidates.add(new int[]{r, c});
            Collections.shuffle(candidates, random);
            int branchBudget = Math.max(1, size * size / 8);
            for (int[] point : candidates) {
                if (branchBudget == 0 || random.nextDouble() > 0.72) continue;
                int neighbors = 0;
                if (grid[point[0] - 1][point[1]] != '#') neighbors++;
                if (grid[point[0] + 1][point[1]] != '#') neighbors++;
                if (grid[point[0]][point[1] - 1] != '#') neighbors++;
                if (grid[point[0]][point[1] + 1] != '#') neighbors++;
                if (neighbors == 1) { grid[point[0]][point[1]] = '.'; branchBudget--; }
            }
            List<String> rows = new ArrayList<>();
            for (char[] row : grid) rows.add(new String(row));
            Maze maze = new Maze(rows, keyTypes);
            try {
                validator.requireValid(maze);
                SolverResult result = solver.solve(maze);
                if (result.solvable()) return new GenerationResult(maze, seed + attempt);
            } catch (IllegalArgumentException ignored) { /* bounded retry */ }
        }
        throw new IllegalStateException("Could not generate a valid solvable maze after " + MAX_RETRIES + " attempts.");
    }
}
