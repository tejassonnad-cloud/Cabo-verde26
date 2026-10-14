package com.hackathon.maze.generator;

import com.hackathon.maze.model.Maze;

public record GenerationResult(Maze maze, long seed) { }
