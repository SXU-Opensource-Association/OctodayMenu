package com.example.whateat.controller;

import com.example.whateat.entity.Users;
import com.example.whateat.mapper.UsersMapper;
import com.example.whateat.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/sxu")
public class LoginController {

    @Autowired
    private UsersMapper usersMapper;

    /**
     * 登录接口
     * 请求体：{"username":"xxx","password":"yyy"}
     * 返回：包含 token 的简单 JSON
     */
    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody Users loginUser) {
        Map<String, Object> result = new HashMap<>();

        if (loginUser == null || loginUser.getUsername() == null || loginUser.getPassword() == null) {
            result.put("code", 400);
            result.put("message", "用户名或密码不能为空");
            return result;
        }

        Users dbUser = usersMapper.selectUserByUsername(loginUser.getUsername());
        if (dbUser == null) {
            result.put("code", 401);
            result.put("message", "用户不存在");
            return result;
        }

        if (!dbUser.getPassword().equals(loginUser.getPassword())) {
            result.put("code", 401);
            result.put("message", "密码错误");
            return result;
        }

        // 生成 token
        String token = JwtUtil.generateToken(dbUser.getUsername());
        // 保存 token 到数据库
        usersMapper.updateTokenByUserId(dbUser.getUserId(), token);

        result.put("code", 200);
        result.put("message", "登录成功");
        result.put("token", token);
        return result;
    }

    /**
     * 注册接口
     * 简单实现：直接插入一条用户记录，不自动登录
     */
    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody Users newUser) {
        Map<String, Object> result = new HashMap<>();

        if (newUser == null || newUser.getUsername() == null || newUser.getPassword() == null) {
            result.put("code", 400);
            result.put("message", "用户名或密码不能为空");
            return result;
        }

        Users existed = usersMapper.selectUserByUsername(newUser.getUsername());
        if (existed != null) {
            result.put("code", 409);
            result.put("message", "用户名已存在");
            return result;
        }

        // 初始没有 token
        newUser.setToken(null);
        usersMapper.insertUser(newUser);

        result.put("code", 200);
        result.put("message", "注册成功");
        return result;
    }

    /**
     * 退出登录接口
     * 前端需在 Header 中携带 token：Authorization: Bearer xxx
     */
    @PostMapping("/logout")
    public Map<String, Object> logout(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        Map<String, Object> result = new HashMap<>();

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            result.put("code", 400);
            result.put("message", "未提供有效的 token");
            return result;
        }

        String token = authHeader.substring(7);
        // 数据库中清空 token
        usersMapper.clearTokenByToken(token);

        result.put("code", 200);
        result.put("message", "已退出登录");
        return result;
    }
}
