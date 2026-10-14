package com.hackathon.maze.algorithm;

import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.PathStep;
import com.hackathon.maze.model.Position;
import com.hackathon.maze.model.SolverResult;
import com.hackathon.maze.validation.MazeValidator;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** BFS over (row, column, keyMask); neighbor order is up, right, down, left. */
public final class MazeSolver {
    private static final int[] DR = {-1, 0, 1, 0};
    private static final int[] DC = {0, 1, 0, -1};
    private final MazeValidator validator;

    public MazeSolver() { this(new MazeValidator()); }
    public MazeSolver(MazeValidator validator) { this.validator = validator; }

    public SolverResult solve(Maze maze) {
        validator.requireValid(maze);
        long started = System.nanoTime();
        int rows = maze.height(), cols = maze.width(), masks = 1 << maze.keyTypes();
        int totalStates = rows * cols * masks;
        int[] distance = new int[totalStates];
        int[] parent = new int[totalStates];
        java.util.Arrays.fill(distance, -1);
        java.util.Arrays.fill(parent, -1);
        Position start = validator.find(maze, 'S');
        Position exit = validator.find(maze, 'E');
        int startId = encode(start.row(), start.col(), 0, cols, masks);
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        queue.add(startId);
        distance[startId] = 0;
        int goalId = -1;
        long explored = 0, visited = 1;
        while (!queue.isEmpty()) {
            int current = queue.removeFirst();
            explored++;
            int mask = current % masks;
            int cellIndex = current / masks;
            int row = cellIndex / cols, col = cellIndex % cols;
            if (maze.isExit(row, col)) { goalId = current; break; }
            for (int direction = 0; direction < 4; direction++) {
                int nr = row + DR[direction], nc = col + DC[direction];
                if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
                char cell = maze.cell(nr, nc);
                if (cell == '#') continue;
                if (maze.isDoor(nr, nc) && (mask & (1 << (cell - 'A'))) == 0) continue;
                int nextMask = mask;
                if (cell >= 'a' && cell <= 'f') nextMask |= 1 << (cell - 'a');
                int next = encode(nr, nc, nextMask, cols, masks);
                if (distance[next] >= 0) continue;
                distance[next] = distance[current] + 1;
                parent[next] = current;
                queue.addLast(next);
                visited++;
            }
        }
        if (goalId < 0) return new SolverResult(false, -1, List.of(), List.of(), List.of(), List.of(), explored, visited, System.nanoTime() - started);
        List<Integer> ids = new ArrayList<>();
        for (int at = goalId; at >= 0; at = parent[at]) { ids.add(at); if (at == startId) break; }
        Collections.reverse(ids);
        List<Position> path = new ArrayList<>();
        List<PathStep> steps = new ArrayList<>();
        List<String> keys = new ArrayList<>(), doors = new ArrayList<>();
        int previousMask = 0;
        for (int id : ids) {
            int mask = id % masks, cellIndex = id / masks;
            int row = cellIndex / cols, col = cellIndex % cols;
            char cell = maze.cell(row, col);
            String picked = cell >= 'a' && cell <= 'f' && (previousMask & (1 << (cell - 'a'))) == 0 ? String.valueOf(cell) : null;
            String opened = maze.isDoor(row, col) ? String.valueOf(cell) : null;
            if (picked != null && !keys.contains(picked)) keys.add(picked);
            if (opened != null) doors.add(opened);
            List<String> inventory = new ArrayList<>();
            for (int k = 0; k < maze.keyTypes(); k++) if ((mask & (1 << k)) != 0) inventory.add(String.valueOf((char) ('a' + k)));
            Position position = new Position(row, col);
            path.add(position);
            steps.add(new PathStep(position, opened == null ? String.valueOf(cell) : "door:" + cell, mask, inventory, picked, opened));
            previousMask = mask;
        }
        return new SolverResult(true, distance[goalId], path, steps, keys, doors, explored, visited, System.nanoTime() - started);
    }

    private int encode(int row, int col, int mask, int cols, int masks) { return ((row * cols + col) * masks) + mask; }
}
