package com.example.whateat.mapper;

import com.example.whateat.entity.Users;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * users 表的 Mapper 接口
 *
 * 功能：
 *  - 插入用户（userId 自增）
 *  - 根据 userId 修改用户信息
 *  - 根据 userId 删除用户
 *  - 根据 userId 查询用户全部信息
 *
 * 说明：这里假设数据库表名为 users，字段名与实体类一致：
 *  userId, username, password, email, telephone, token
 * 如果你的实际表名或字段名不同，请根据实际情况修改 SQL。
 */
@Mapper
public interface UsersMapper {

    /**
     * 插入用户，userId 使用数据库自增
     */
    @Insert("INSERT INTO users(username, password, email, telephone, token) " +
            "VALUES(#{username}, #{password}, #{email}, #{telephone}, #{token})")
    @Options(useGeneratedKeys = true, keyProperty = "userId")
    int insertUser(Users user);

    /**
     * 根据 userId 修改用户所有信息
     */
    @Update("UPDATE users SET " +
            "username = #{username}, " +
            "password = #{password}, " +
            "email = #{email}, " +
            "telephone = #{telephone}, " +
            "token = #{token} " +
            "WHERE userId = #{userId}")
    int updateUserById(Users user);

    /**
     * 根据 userId 删除用户
     */
    @Delete("DELETE FROM users WHERE userId = #{userId}")
    int deleteUserById(@Param("userId") int userId);

    /**
     * 根据 userId 查询用户全部信息
     */
    @Select("SELECT userId, username, password, email, telephone, token " +
            "FROM users WHERE userId = #{userId}")
    Users selectUserById(@Param("userId") int userId);

    /**
     * 根据用户名查询用户（登录用）
     */
    @Select("SELECT userId, username, password, email, telephone, token " +
            "FROM users WHERE username = #{username} LIMIT 1")
    Users selectUserByUsername(@Param("username") String username);

    /**
     * 根据 token 清空用户 token（退出登录）
     */
    @Update("UPDATE users SET token = NULL WHERE token = #{token}")
    int clearTokenByToken(@Param("token") String token);

    /**
     * 更新指定用户的 token（登录成功后保存）
     */
    @Update("UPDATE users SET token = #{token} WHERE userId = #{userId}")
    int updateTokenByUserId(@Param("userId") int userId, @Param("token") String token);
}
