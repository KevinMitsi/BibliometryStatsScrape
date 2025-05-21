package com.kevin.msvc_texts;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class MsvcTextsApplication {

	public static void main(String[] args) {
		SpringApplication.run(MsvcTextsApplication.class, args);
	}

}
