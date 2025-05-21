package com.kevin.msvc_texts.controller;

import com.kevin.msvc_texts.service.AbstractReader;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


import java.util.List;
import java.util.Map;

@CrossOrigin(origins = { "http://bibliometry-view","http://bibliometry-view:4200","http://localhost:4200" ,"docker.host.internal:4200"})
@RestController
@RequestMapping("/texts")
public class AbstractReaderController {
    private final AbstractReader abstractReaderService;

    public AbstractReaderController(AbstractReader abstractReaderService) {
        this.abstractReaderService = abstractReaderService;
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Running");
    }

    @GetMapping("/read")
    public ResponseEntity<List<String>> read() {
            return ResponseEntity.ok(abstractReaderService.read());
    }


    @GetMapping("/findSimilar")
    public ResponseEntity<Map<List<String>,List<String>>>findSimilar() {
        return ResponseEntity.ok(abstractReaderService.getAbstractsSimilar());
    }


}
