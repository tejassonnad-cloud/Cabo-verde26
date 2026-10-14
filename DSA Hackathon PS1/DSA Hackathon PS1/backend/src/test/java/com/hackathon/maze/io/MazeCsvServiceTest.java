package com.hackathon.maze.io;

import static org.junit.jupiter.api.Assertions.*;
import com.hackathon.maze.algorithm.MazeSolver;
import com.hackathon.maze.model.Maze;
import com.hackathon.maze.validation.MazeValidator;
import java.util.List;
import org.junit.jupiter.api.Test;

class MazeCsvServiceTest {
    private final MazeCsvService csv = new MazeCsvService(new MazeValidator());

    @Test void parsesBomWhitespaceAndQuotedCsvCells() {
        Maze maze = csv.parse("\uFEFF\" S \" , . , #\r\n. , . , .\r\n#,#,E\r\n", 1);
        assertEquals(List.of("S.#", "...", "##E"), maze.rows());
    }

    @Test void rejectsEmptyMalformedAndNonSquareCsv() {
        assertThrows(IllegalArgumentException.class, () -> csv.parse("  \n", 1));
        assertThrows(IllegalArgumentException.class, () -> csv.parse("S,.,E\n#,#,#,#\n", 1));
        assertThrows(IllegalArgumentException.class, () -> csv.parse("\"S,.,E\n", 1));
    }

    @Test void exportMarksOnlyOrdinaryPathCellsAndReimports() {
        Maze original = new Maze(List.of("#####", "#SaA#", "###.#", "###E#", "#####"), 1);
        var solution = new MazeSolver().solve(original);
        String marked = csv.exportMarked(original, solution);
        assertTrue(marked.contains("#,S,a,A,#"));
        assertTrue(marked.contains("#,x,E,#") || marked.contains("#,x,#"));
        Maze parsed = csv.parse(marked, 1);
        assertTrue(parsed.rows().stream().anyMatch(row -> row.contains("x")));
        assertEquals(original.rows().get(1), parsed.rows().get(1));
    }

    @Test void refusesAnInvalidSuppliedPath() {
        Maze maze = new Maze(List.of("S#E", "###", "###"), 1);
        assertThrows(IllegalArgumentException.class, () -> csv.verifyPath(maze, List.of(new com.hackathon.maze.model.Position(0, 0), new com.hackathon.maze.model.Position(0, 1), new com.hackathon.maze.model.Position(0, 2))));
    }
}
