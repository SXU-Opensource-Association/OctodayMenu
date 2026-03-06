package com.example.whateat;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan(basePackages = "com.example.whateat.mapper", sqlSessionFactoryRef = "sqlSessionFactory")
public class WhatEatApplication {

    public static void main(String[] args) {
        SpringApplication.run(WhatEatApplication.class, args);
    }

}
