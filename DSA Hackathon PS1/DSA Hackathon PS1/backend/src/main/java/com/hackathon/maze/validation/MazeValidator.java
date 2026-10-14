package com.hackathon.maze.validation;

import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.Position;
import java.util.ArrayList;
import java.util.List;

public final class MazeValidator {
    public static final int MAX_SIZE = 60;

    public List<String> validate(Maze maze) {
        List<String> errors = new ArrayList<>();
        if (maze.keyTypes() < 1 || maze.keyTypes() > 6) errors.add("keyTypes (T) must be between 1 and 6.");
        if (maze.height() < 2) errors.add("Maze must contain at least 2 rows.");
        if (maze.height() > MAX_SIZE) errors.add("Maze cannot exceed " + MAX_SIZE + " rows.");
        if (maze.rows().isEmpty()) return errors;
        int width = maze.width();
        if (width < 2) errors.add("Maze must contain at least 2 columns.");
        if (width > MAX_SIZE) errors.add("Maze cannot exceed " + MAX_SIZE + " columns.");
        if (maze.height() != width) errors.add("Maze must be a square grid; found " + maze.height() + " rows and " + width + " columns.");
        for (int r = 0; r < maze.height(); r++) {
            String row = maze.rows().get(r);
            if (row.length() != width) errors.add("Maze must be rectangular: row " + (r + 1) + " has " + row.length() + " cells; expected " + width + ".");
        }
        int starts = 0, exits = 0;
        Position exit = null;
        for (int r = maze.height() - 1; r >= 0 && exit == null; r--) for (int c = maze.rows().get(r).length() - 1; c >= 0; c--)
            if (maze.rows().get(r).charAt(c) == 'E') { exit = new Position(r, c); break; }
        for (int r = 0; r < maze.height(); r++) {
            String row = maze.rows().get(r);
            for (int c = 0; c < row.length(); c++) {
                char ch = row.charAt(c);
                if (ch == 'S') starts++;
                else if (ch == 'E') {
                    if (exit != null && exit.row() == r && exit.col() == c) exits++;
                    else if (maze.keyTypes() <= 4) errors.add("Door 'E' at row " + (r + 1) + ", column " + (c + 1) + " is outside the configured T=" + maze.keyTypes() + " types.");
                }
                else if (ch == '.' || ch == '#' || ch == 'x') { /* allowed */ }
                else if (ch >= 'a' && ch <= 'f') {
                    if (ch - 'a' >= maze.keyTypes()) errors.add("Key '" + ch + "' at row " + (r + 1) + ", column " + (c + 1) + " is outside the configured T=" + maze.keyTypes() + " types.");
        } else if (ch >= 'A' && ch <= 'F' && ch != 'E') {
                    if (ch - 'A' >= maze.keyTypes()) errors.add("Door '" + ch + "' at row " + (r + 1) + ", column " + (c + 1) + " is outside the configured T=" + maze.keyTypes() + " types.");
                } else errors.add("Invalid symbol '" + ch + "' at row " + (r + 1) + ", column " + (c + 1) + ". Allowed: . # S E a-f A-F x.");
            }
        }
        if (starts != 1) errors.add("Maze must contain exactly one start 'S'; found " + starts + ".");
        if (exits != 1) errors.add("Maze must contain exactly one exit 'E'; found " + exits + ".");
        return errors;
    }

    public void requireValid(Maze maze) {
        List<String> errors = validate(maze);
        if (!errors.isEmpty()) throw new IllegalArgumentException(String.join(" ", errors));
    }

    public Position find(Maze maze, char symbol) {
        if (symbol == 'E') return maze.exitPosition();
        for (int r = 0; r < maze.height(); r++) for (int c = 0; c < maze.width(); c++)
            if (maze.cell(r, c) == symbol) return new Position(r, c);
        throw new IllegalArgumentException("Maze has no '" + symbol + "'.");
    }
}
