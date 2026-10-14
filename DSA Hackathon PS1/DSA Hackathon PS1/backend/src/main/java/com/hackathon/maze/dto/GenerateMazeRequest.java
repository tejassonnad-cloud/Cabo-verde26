package com.hackathon.maze.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public record GenerateMazeRequest(@NotNull @Min(5) @Max(60) Integer size,
                                  @NotNull @Min(1) @Max(6) Integer keyTypes,
                                  Long seed) { }
