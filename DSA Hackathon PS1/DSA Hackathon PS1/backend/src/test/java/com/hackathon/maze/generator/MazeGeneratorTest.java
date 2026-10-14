package com.hackathon.maze.generator;

import static org.junit.jupiter.api.Assertions.*;
import com.hackathon.maze.algorithm.MazeSolver;
import com.hackathon.maze.model.Maze;
import org.junit.jupiter.api.Test;

class MazeGeneratorTest {
    private final MazeGenerator generator = new MazeGenerator();
    private final MazeSolver solver = new MazeSolver();

    @Test void seededGenerationIsRepeatableAndSolvableAcrossSeeds() {
        var a = generator.generate(13, 4, 872L);
        var b = generator.generate(13, 4, 872L);
        assertEquals(a.maze().rows(), b.maze().rows()); assertEquals(a.seed(), b.seed());
        for (long seed = 0; seed < 12; seed++) {
            Maze maze = generator.generate(10, 6, seed).maze();
            var result = solver.solve(maze);
            assertTrue(result.solvable());
            assertEquals(1, maze.rows().stream().mapToLong(row -> row.chars().filter(ch -> ch == 'S').count()).sum());
            assertEquals(maze.exitPosition(), result.path().get(result.path().size() - 1));
            for (int key = 0; key < 6; key++) {
                final char keyCell = (char) ('a' + key), doorCell = (char) ('A' + key);
                assertTrue(maze.rows().stream().anyMatch(row -> row.indexOf(keyCell) >= 0));
                assertTrue(maze.rows().stream().anyMatch(row -> row.indexOf(doorCell) >= 0));
            }
        }
    }

    @Test void rejectsTooSmallOrInvalidConfigurations() {
        assertThrows(IllegalArgumentException.class, () -> generator.generate(9, 6, 1L));
        assertThrows(IllegalArgumentException.class, () -> generator.generate(12, 0, 1L));
    }

    @Test void smallestSupportedConfigurationIsSolvable() {
        Maze maze = generator.generate(5, 1, 5L).maze();
        assertEquals(5, maze.height());
        assertTrue(solver.solve(maze).solvable());
    }
}
