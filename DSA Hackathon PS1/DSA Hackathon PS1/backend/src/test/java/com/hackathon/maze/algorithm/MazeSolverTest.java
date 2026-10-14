package com.hackathon.maze.algorithm;

import static org.junit.jupiter.api.Assertions.*;
import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.Position;
import com.hackathon.maze.model.SolverResult;
import com.hackathon.maze.validation.MazeValidator;
import java.util.List;
import org.junit.jupiter.api.Test;

class MazeSolverTest {
    private final MazeSolver solver = new MazeSolver();

    @Test void startAdjacentToExitHasOneMove() {
        SolverResult result = solve("SE", "##", 1);
        assertTrue(result.solvable()); assertEquals(1, result.shortestPathLength()); assertEquals(2, result.path().size()); verifyPath(maze("SE", "##", 1), result);
    }

    @Test void unreachableAndSurroundedExitReturnNoPath() {
        SolverResult result = solve("S#E", "###", "###", 1);
        assertFalse(result.solvable()); assertEquals(-1, result.shortestPathLength()); assertTrue(result.path().isEmpty());
    }

    @Test void collectsKeyBeforeOpeningDoor() {
        Maze maze = maze("#####", "#SaA#", "###.#", "###E#", "#####", 1);
        SolverResult result = solver.solve(maze);
        assertTrue(result.solvable()); assertEquals(List.of("a"), result.keysCollected()); assertEquals(List.of("A"), result.doorsOpened());
        assertEquals("a", result.pathSteps().stream().filter(step -> step.keyPickedUp() != null).findFirst().orElseThrow().keyPickedUp());
        verifyPath(maze, result);
    }

    @Test void doorAheadOfKeyRequiresBacktrackingAndSamePositionDifferentMask() {
        Maze maze = maze("#######", "#S.A.E#", "#a#####", "#######", "#######", "#######", "#######", 1);
        SolverResult result = solver.solve(maze);
        assertTrue(result.solvable()); assertEquals(6, result.shortestPathLength());
        assertTrue(result.path().stream().filter(p -> p.equals(new Position(1, 1))).count() >= 2);
        assertEquals(1, result.pathSteps().get(2).keyMask());
        verifyPath(maze, result);
    }

    @Test void multipleDoorsOfOneTypeAndGeometricallyShorterLockedRoute() {
        Maze maze = maze("#######", "#S.aAAE", "#######", "#######", "#######", "#######", "#######", 1);
        SolverResult result = solver.solve(maze);
        assertTrue(result.solvable()); assertEquals(2, result.doorsOpened().size()); verifyPath(maze, result);
    }

    @Test void unnecessaryKeyDoesNotAppearInSolutionInventory() {
        Maze maze = maze("S.E", "a##", "###", 1);
        SolverResult result = solver.solve(maze);
        assertTrue(result.solvable()); assertEquals(2, result.shortestPathLength()); assertTrue(result.keysCollected().isEmpty()); verifyPath(maze, result);
    }

    @Test void multipleShortestPathsHaveDeterministicTieBreaking() {
        Maze maze = maze("S..", "...", "..E", 1);
        SolverResult first = solver.solve(maze), second = solver.solve(maze);
        assertEquals(4, first.shortestPathLength());
        assertEquals(first.path(), second.path());
        assertEquals(List.of(new Position(0, 0), new Position(0, 1), new Position(0, 2), new Position(1, 2), new Position(2, 2)), first.path());
        verifyPath(maze, first);
    }

    @Test void doorWithoutMatchingKeyIsUnsolvable() {
        SolverResult result = solve("#####", "#S.AE", "#####", "#####", "#####", 1);
        assertFalse(result.solvable());
    }

    @Test void invalidSymbolsAndEndpointCountsAreRejected() {
        MazeValidator validator = new MazeValidator();
        assertFalse(validator.validate(maze("S?E", "###", "###", 1)).isEmpty());
        assertTrue(validator.validate(maze("..E", "...", "...", 1)).stream().anyMatch(e -> e.contains("start")));
        assertTrue(validator.validate(maze("SSE", "...", "...", 1)).stream().anyMatch(e -> e.contains("start")));
        assertTrue(validator.validate(maze("S..", "...", "...", 1)).stream().anyMatch(e -> e.contains("exit")));
        assertTrue(validator.validate(maze("SEE", "...", "...", 1)).stream().anyMatch(e -> e.contains("Door 'E'")));
    }

    @Test void invalidKeyCountAndSymbolsOutsideConfiguredTypesAreRejected() {
        assertThrows(IllegalArgumentException.class, () -> solver.solve(maze("S.E", "...", "...", 0)));
        assertThrows(IllegalArgumentException.class, () -> solver.solve(maze("S.b", "...", "..E", 1)));
    }

    @Test void allSixKeyTypesCanBeCollectedAndOpened() {
        String[] rows = new String[16];
        java.util.Arrays.fill(rows, "################");
        // All six keys and doors sit in sequence on the only route.
        rows[1] = "#S.aAbBcCdDeEfFE";
        Maze maze = maze(rows, 6);
        SolverResult result = solver.solve(maze);
        assertTrue(result.solvable()); assertEquals(6, result.keysCollected().size()); assertEquals(6, result.doorsOpened().size()); verifyPath(maze, result);
    }

    private SolverResult solve(String row1, String row2, int types) { return solver.solve(maze(row1, row2, types)); }
    private SolverResult solve(String r1, String r2, String r3, int types) { return solver.solve(maze(r1, r2, r3, types)); }
    private SolverResult solve(String r1, String r2, String r3, String r4, String r5, int types) { return solver.solve(maze(r1, r2, r3, r4, r5, types)); }
    private Maze maze(String r1, String r2, int types) { return new Maze(List.of(r1, r2), types); }
    private Maze maze(String r1, String r2, String r3, int types) { return new Maze(List.of(r1, r2, r3), types); }
    private Maze maze(String r1, String r2, String r3, String r4, String r5, int types) { return new Maze(List.of(r1, r2, r3, r4, r5), types); }
    private Maze maze(String[] rows, int types) { return new Maze(List.of(rows), types); }
    private Maze maze(String r1, String r2, String r3, String r4, String r5, String r6, String r7, int types) { return new Maze(List.of(r1, r2, r3, r4, r5, r6, r7), types); }

    private void verifyPath(Maze maze, SolverResult result) {
        assertEquals(result.shortestPathLength(), result.path().size() - 1);
        assertEquals(new MazeValidator().find(maze, 'S'), result.path().get(0));
        assertEquals(new MazeValidator().find(maze, 'E'), result.path().get(result.path().size() - 1));
        int mask = 0;
        for (int i = 0; i < result.path().size(); i++) {
            Position p = result.path().get(i); char cell = maze.cell(p.row(), p.col());
            assertNotEquals('#', cell);
            if (i > 0) {
                Position previous = result.path().get(i - 1);
                assertEquals(1, Math.abs(p.row() - previous.row()) + Math.abs(p.col() - previous.col()));
                if (maze.isDoor(p.row(), p.col())) assertTrue((mask & (1 << (cell - 'A'))) != 0);
            }
            if (cell >= 'a' && cell <= 'f') mask |= 1 << (cell - 'a');
        }
    }
}
