package com.hackathon.maze.model;

import java.util.List;

/** Immutable rectangular grid and key-type configuration. */
public final class Maze {
    private final List<String> rows;
    private final int keyTypes;
    private final Position exitPosition;

    public Maze(List<String> rows, int keyTypes) {
        this.rows = List.copyOf(rows);
        this.keyTypes = keyTypes;
        Position exit = null;
        for (int r = this.rows.size() - 1; r >= 0 && exit == null; r--) for (int c = this.rows.get(r).length() - 1; c >= 0; c--)
            if (this.rows.get(r).charAt(c) == 'E') { exit = new Position(r, c); break; }
        this.exitPosition = exit;
    }

    public List<String> rows() { return rows; }
    public int keyTypes() { return keyTypes; }
    public int height() { return rows.size(); }
    public int width() { return rows.isEmpty() ? 0 : rows.get(0).length(); }
    public char cell(int row, int col) { return rows.get(row).charAt(col); }
    public char[][] copyGrid() { return rows.stream().map(String::toCharArray).toArray(char[][]::new); }
    /** E is both the specified exit and the sixth door glyph. If both occur, the last E in row-major order is the exit. */
    public Position exitPosition() {
        if (exitPosition == null) throw new IllegalArgumentException("Maze has no 'E'.");
        return exitPosition;
    }
    public boolean isExit(int row, int col) { return cell(row, col) == 'E' && exitPosition != null && exitPosition.row() == row && exitPosition.col() == col; }
    public boolean isDoor(int row, int col) {
        char cell = cell(row, col);
        return cell >= 'A' && cell <= 'F' && !isExit(row, col);
    }
}
