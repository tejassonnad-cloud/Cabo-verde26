package com.hackathon.maze.model;

import java.util.List;

public record SolverResult(boolean solvable, int shortestPathLength, List<Position> path,
                           List<PathStep> pathSteps, List<String> keysCollected,
                           List<String> doorsOpened, long statesExplored,
                           long uniqueStatesVisited, long executionTimeNanos) {
    public SolverResult {
        path = List.copyOf(path);
        pathSteps = List.copyOf(pathSteps);
        keysCollected = List.copyOf(keysCollected);
        doorsOpened = List.copyOf(doorsOpened);
    }
}
