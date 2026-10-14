package com.hackathon.maze.io;

import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.Position;
import com.hackathon.maze.model.SolverResult;
import com.hackathon.maze.validation.MazeValidator;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class MazeCsvService {
    private final MazeValidator validator;
    public MazeCsvService(MazeValidator validator) { this.validator = validator; }

    public Maze parse(String csv, int keyTypes) {
        if (csv == null || csv.isBlank()) throw new IllegalArgumentException("CSV file is empty.");
        if (csv.charAt(0) == '\uFEFF') csv = csv.substring(1);
        List<List<String>> records = parseRecords(csv);
        List<String> rows = new ArrayList<>();
        for (int r = 0; r < records.size(); r++) {
            List<String> cells = records.get(r);
            if (cells.isEmpty()) continue;
            StringBuilder row = new StringBuilder();
            for (int c = 0; c < cells.size(); c++) {
                String value = cells.get(c).trim();
                if (value.length() != 1) throw new IllegalArgumentException("CSV cell at row " + (r + 1) + ", column " + (c + 1) + " must contain exactly one maze symbol.");
                row.append(value);
            }
            rows.add(row.toString());
        }
        Maze maze = new Maze(rows, keyTypes);
        validator.requireValid(maze);
        if (maze.height() != maze.width()) throw new IllegalArgumentException("Maze CSV must be a square grid; found " + maze.height() + " rows and " + maze.width() + " columns.");
        return maze;
    }

    public String exportMarked(Maze maze, SolverResult solution) {
        validator.requireValid(maze);
        if (solution == null || !solution.solvable()) throw new IllegalArgumentException("A verified solvable solution is required for CSV export.");
        verifyPath(maze, solution.path());
        char[][] grid = maze.copyGrid();
        List<Position> path = solution.path();
        for (int i = 1; i < path.size() - 1; i++) {
            Position p = path.get(i);
            if (grid[p.row()][p.col()] == '.') grid[p.row()][p.col()] = 'x';
        }
        StringBuilder csv = new StringBuilder();
        for (char[] row : grid) {
            for (int c = 0; c < row.length; c++) {
                if (c > 0) csv.append(',');
                csv.append(row[c]);
            }
            csv.append("\r\n");
        }
        return csv.toString();
    }

    public void verifyPath(Maze maze, List<Position> path) {
        if (path == null || path.size() < 2) throw new IllegalArgumentException("Solution path must include a start and exit.");
        Position expectedStart = validator.find(maze, 'S'), expectedExit = validator.find(maze, 'E');
        if (!path.get(0).equals(expectedStart) || !path.get(path.size() - 1).equals(expectedExit)) throw new IllegalArgumentException("Solution path must start at S and end at E.");
        int mask = 0;
        for (int i = 0; i < path.size(); i++) {
            Position p = path.get(i);
            if (p.row() < 0 || p.row() >= maze.height() || p.col() < 0 || p.col() >= maze.width()) throw new IllegalArgumentException("Solution path leaves the maze bounds.");
            char cell = maze.cell(p.row(), p.col());
            if (cell == '#') throw new IllegalArgumentException("Solution path crosses a wall.");
            if (i > 0) {
                Position previous = path.get(i - 1);
                if (Math.abs(previous.row() - p.row()) + Math.abs(previous.col() - p.col()) != 1) throw new IllegalArgumentException("Solution path contains a non-orthogonal move.");
                if (maze.isDoor(p.row(), p.col()) && (mask & (1 << (cell - 'A'))) == 0) throw new IllegalArgumentException("Solution path enters door '" + cell + "' before collecting its key.");
            }
            if (cell >= 'a' && cell <= 'f') mask |= 1 << (cell - 'a');
        }
    }

    private List<List<String>> parseRecords(String csv) {
        List<List<String>> records = new ArrayList<>();
        List<String> record = new ArrayList<>();
        StringBuilder field = new StringBuilder();
        boolean quoted = false, fieldWasQuoted = false, touched = false, lastWasNewline = false;
        for (int i = 0; i < csv.length(); i++) {
            char ch = csv.charAt(i);
            if (quoted) {
                if (ch == '"') {
                    if (i + 1 < csv.length() && csv.charAt(i + 1) == '"') { field.append('"'); i++; }
                    else quoted = false;
                } else field.append(ch);
                touched = true;
                lastWasNewline = false;
            } else if (ch == '"') {
                if (!field.toString().trim().isEmpty() || fieldWasQuoted) throw new IllegalArgumentException("Malformed CSV: quote must begin at the start of a field.");
                field.setLength(0); quoted = true; fieldWasQuoted = true; touched = true; lastWasNewline = false;
            } else if (ch == ',') {
                record.add(field.toString().trim()); field.setLength(0); fieldWasQuoted = false; touched = true; lastWasNewline = false;
            } else if (ch == '\r' || ch == '\n') {
                if (ch == '\r' && i + 1 < csv.length() && csv.charAt(i + 1) == '\n') i++;
                record.add(field.toString().trim()); records.add(record);
                record = new ArrayList<>(); field.setLength(0); fieldWasQuoted = false; touched = false; lastWasNewline = true;
            } else {
                if (fieldWasQuoted && !Character.isWhitespace(ch)) throw new IllegalArgumentException("Malformed CSV: unexpected content after a quoted field.");
                field.append(ch); if (!Character.isWhitespace(ch)) touched = true; lastWasNewline = false;
            }
        }
        if (quoted) throw new IllegalArgumentException("Malformed CSV: unterminated quoted field.");
        if (touched || !record.isEmpty() || !lastWasNewline) { record.add(field.toString().trim()); records.add(record); }
        if (records.isEmpty()) throw new IllegalArgumentException("CSV file is empty.");
        return records;
    }
}
