package com.hackathon.maze.model;

import java.util.List;

public record PathStep(Position position, String cellType, int keyMask, List<String> inventory,
                       String keyPickedUp, String doorOpened) {
    public PathStep { inventory = List.copyOf(inventory); }
}
