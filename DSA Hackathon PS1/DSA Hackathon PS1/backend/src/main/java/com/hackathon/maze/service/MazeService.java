package com.hackathon.maze.service;

import com.hackathon.maze.algorithm.MazeSolver;
import com.hackathon.maze.generator.GenerationResult;
import com.hackathon.maze.generator.MazeGenerator;
import com.hackathon.maze.io.MazeCsvService;
import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.SolverResult;
import com.hackathon.maze.validation.MazeValidator;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class MazeService {
    private final MazeValidator validator = new MazeValidator();
    private final MazeSolver solver = new MazeSolver(validator);
    private final MazeGenerator generator = new MazeGenerator(validator, solver);
    private final MazeCsvService csv = new MazeCsvService(validator);

    public Maze from(List<String> grid, Integer keyTypes) {
        if (grid == null || keyTypes == null) throw new IllegalArgumentException("Both grid and keyTypes are required.");
        return new Maze(grid, keyTypes);
    }
    public List<String> validate(Maze maze) { return validator.validate(maze); }
    public SolverResult solve(Maze maze) { return solver.solve(maze); }
    public GenerationResult generate(int size, int keyTypes, Long seed) { return generator.generate(size, keyTypes, seed); }
    public Maze parseCsv(String content, int keyTypes) { return csv.parse(content, keyTypes); }
    public String export(Maze maze) { return csv.exportMarked(maze, solver.solve(maze)); }
}
