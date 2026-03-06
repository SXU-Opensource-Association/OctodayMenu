package com.example.whateat.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

public class JwtUtil {
    // 7 天token 过期
    private static final long EXPIRATION_TIME = 604800;
    // deepseek生成的 32 位密钥
    private static final String SECRET = "k8x!Pq3@Z9s$RvY5^WjFn7*KtLmCwE4B";
    private static final SecretKey SECRET_KEY = Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));

    //生成 token
    public static String generateToken(String username) {
        Date now = new Date();
        Date exp = new Date(now.getTime() + 1000 * EXPIRATION_TIME);
        return Jwts.builder()
                .setHeaderParam("projectName", "SXU_WhatEat")
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(exp)
                .signWith(SECRET_KEY)
                .compact();
    }
    
    //token 解析
    public static Claims parseToken(String token) {
        return Jwts.parser()
                .setSigningKey(SECRET_KEY)
                .parseClaimsJws(token)
                .getBody();
    }
}
