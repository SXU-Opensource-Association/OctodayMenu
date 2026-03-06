package com.example.whateat.config;

import com.example.whateat.entity.Users;
import com.example.whateat.mapper.UsersMapper;
import com.example.whateat.util.JwtUtil;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.SignatureException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * 简单的全局 token 校验拦截器
 *  - 放行：/sxu/login、/sxu/register 以及 Swagger 相关接口
 *  - 其他接口：要求 Header 中携带 Authorization: Bearer token
 */
@Component
public class TokenInterceptor implements HandlerInterceptor {

    @Autowired
    private UsersMapper usersMapper;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        String uri = request.getRequestURI();
        String method = request.getMethod();
        
        // 放行 OPTIONS 预检请求（CORS 需要）
        if ("OPTIONS".equalsIgnoreCase(method)) {
            return true;
        }
        
        // 放行登录、注册和 Swagger 相关接口
        // 使用 startsWith 而不是 equals，以防有查询参数
        if (uri.startsWith("/sxu/login") || 
            uri.startsWith("/sxu/register") ||
            uri.startsWith("/v3/api-docs") ||
            uri.startsWith("/swagger-ui")) {
            return true;
        }
        
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("Missing or invalid Authorization header");
            return false;
        }

        String token = authHeader.substring(7);
        try {
            Claims claims = JwtUtil.parseToken(token);
            String username = claims.getSubject();

            // 简单校验：token 必须存在于数据库中
            Users user = usersMapper.selectUserByUsername(username);
            if (user == null || user.getToken() == null || !user.getToken().equals(token)) {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.getWriter().write("Invalid token");
                return false;
            }

            return true;
        } catch (ExpiredJwtException e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("Token expired");
            return false;
        } catch (SignatureException e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("Token signature error");
            return false;
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("Token parse error");
            return false;
        }
    }
}

