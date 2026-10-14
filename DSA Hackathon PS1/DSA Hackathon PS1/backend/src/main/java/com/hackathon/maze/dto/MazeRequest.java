package com.hackathon.maze.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public record MazeRequest(@NotNull @NotEmpty List<String> grid,
                          @NotNull @Min(1) @Max(6) Integer keyTypes) { }
