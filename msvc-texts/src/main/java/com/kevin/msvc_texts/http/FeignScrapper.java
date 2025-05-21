package com.kevin.msvc_texts.http;


import com.kevin.msvc_texts.DTO.RefItemResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;


@FeignClient(name = "scrapper", url = "host.docker.internal:8000")
public interface FeignScrapper {

    @GetMapping("/convert")
    RefItemResponse getAllItems();


}
