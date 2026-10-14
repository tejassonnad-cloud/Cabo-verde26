package com.hackathon.maze.dto;

import java.util.List;
import com.hackathon.maze.model.Position;

public record MazeResponse(List<String> grid, int size, int keyTypes, Long seed, Position start, Position exit) { }
