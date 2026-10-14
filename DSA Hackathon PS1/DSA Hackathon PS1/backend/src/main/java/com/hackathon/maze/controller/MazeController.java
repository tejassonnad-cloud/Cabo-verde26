package com.hackathon.maze.controller;

import com.hackathon.maze.dto.GenerateMazeRequest;
import com.hackathon.maze.dto.MazeRequest;
import com.hackathon.maze.dto.MazeResponse;
import com.hackathon.maze.dto.ValidationResponse;
import com.hackathon.maze.model.Maze;
import com.hackathon.maze.model.SolverResult;
import com.hackathon.maze.service.MazeService;
import com.hackathon.maze.validation.MazeValidator;
import jakarta.validation.Valid;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
public class MazeController {
    private final MazeService service;
    public MazeController(MazeService service) { this.service = service; }

    @PostMapping("/mazes/generate")
    public MazeResponse generate(@Valid @RequestBody GenerateMazeRequest request) {
        var result = service.generate(request.size(), request.keyTypes(), request.seed());
        return response(result.maze(), result.seed());
    }

    @PostMapping("/mazes/solve")
    public SolverResult solve(@Valid @RequestBody MazeRequest request) {
        return service.solve(service.from(request.grid(), request.keyTypes()));
    }

    @PostMapping("/mazes/validate")
    public ValidationResponse validate(@RequestBody MazeRequest request) {
        List<String> errors = service.validate(service.from(request.grid(), request.keyTypes()));
        return new ValidationResponse(errors.isEmpty(), errors);
    }

    @PostMapping(value = "/mazes/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public MazeResponse upload(@RequestPart("file") MultipartFile file, @RequestParam("keyTypes") int keyTypes) {
        if (file.isEmpty()) throw new IllegalArgumentException("CSV file is empty.");
        if (file.getSize() > 1_000_000) throw new IllegalArgumentException("CSV file must be 1 MB or smaller.");
        try {
            String content = new String(file.getBytes(), StandardCharsets.UTF_8);
            return response(service.parseCsv(content, keyTypes), null);
        } catch (java.io.IOException e) { throw new IllegalArgumentException("Unable to read uploaded CSV file."); }
    }

    @PostMapping("/mazes/export")
    public ResponseEntity<byte[]> export(@Valid @RequestBody MazeRequest request) {
        Maze maze = service.from(request.grid(), request.keyTypes());
        byte[] bytes = service.export(maze).getBytes(StandardCharsets.UTF_8);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.parseMediaType("text/csv; charset=UTF-8"));
        headers.setContentDisposition(ContentDisposition.attachment().filename("maze-solution.csv").build());
        return ResponseEntity.ok().headers(headers).body(bytes);
    }

    private MazeResponse response(Maze maze, Long seed) {
        MazeValidator validator = new MazeValidator();
        return new MazeResponse(maze.rows(), maze.height(), maze.keyTypes(), seed, validator.find(maze, 'S'), validator.find(maze, 'E'));
    }
}
