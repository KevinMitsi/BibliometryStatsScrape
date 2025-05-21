package com.kevin.msvc_texts.service;

import java.util.List;
import java.util.Map;

public interface AbstractReader {
    List<String> read();
    Map<List<String>, List<String>> getAbstractsSimilar();
}
