package com.hackathon.maze.controller;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AlgorithmController {
    @GetMapping("/api/algorithm/info")
    public Map<String, Object> info() {
        return Map.of("name", "Breadth-first search with augmented state", "maximumKeyTypes", 6,
                "state", "(row, column, keyMask)", "maximumStates", "N² × 2^T",
                "timeComplexity", "O(N² × 2^T)", "spaceComplexity", "O(N² × 2^T)",
                "explanation", "The Java solver runs BFS over position and collected-key bitmask. Each transition checks walls and door access, updates the mask on key pickup, and stores a parent pointer. The first exit state removed from the FIFO queue is a shortest valid route.");
    }
}
