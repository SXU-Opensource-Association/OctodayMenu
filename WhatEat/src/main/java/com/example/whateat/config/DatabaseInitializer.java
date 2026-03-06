package com.example.whateat.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationEnvironmentPreparedEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.core.env.ConfigurableEnvironment;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

/**
 * 数据库初始化器
 * 在应用启动时自动创建数据库（如果不存在）
 * 使用 ApplicationListener 在环境准备阶段执行，确保在 DataSource 初始化之前创建数据库
 */
public class DatabaseInitializer implements ApplicationListener<ApplicationEnvironmentPreparedEvent> {

    private static final Logger logger = LoggerFactory.getLogger(DatabaseInitializer.class);
    private static boolean initialized = false; // 防止重复初始化

    @Override
    public void onApplicationEvent(ApplicationEnvironmentPreparedEvent event) {
        // 防止重复初始化
        if (initialized) {
            return;
        }
        initialized = true;

        ConfigurableEnvironment environment = event.getEnvironment();
        init(environment);
    }
    
    private void init(ConfigurableEnvironment environment) {
        try {
            // 从配置中读取数据库连接信息
            String jdbcUrl = environment.getProperty("spring.datasource.url", "jdbc:mysql://localhost:3306/sxu_what_eat");
            String username = environment.getProperty("spring.datasource.username", "root");
            String password = environment.getProperty("spring.datasource.password", "");

            // 从完整 URL 中提取数据库名
            // URL 格式：jdbc:mysql://host:port/database?params
            String databaseName = "sxu_what_eat";
            String serverUrl = jdbcUrl;
            
            // 找到端口号后的第一个 /（数据库名的开始位置）
            int portEndIndex = jdbcUrl.indexOf("://");
            if (portEndIndex != -1) {
                portEndIndex = jdbcUrl.indexOf(":", portEndIndex + 3);
                if (portEndIndex != -1) {
                    // 找到端口号后的第一个 /
                    int dbStartIndex = jdbcUrl.indexOf("/", portEndIndex);
                    if (dbStartIndex != -1) {
                        // 找到 ? 或 URL 结束位置
                        int dbEndIndex = jdbcUrl.indexOf("?", dbStartIndex);
                        if (dbEndIndex == -1) {
                            dbEndIndex = jdbcUrl.length();
                        }
                        
                        // 提取数据库名
                        databaseName = jdbcUrl.substring(dbStartIndex + 1, dbEndIndex);
                        
                        // 构建服务器 URL（不包含数据库名，但保留参数）
                        String urlParams = "";
                        if (jdbcUrl.contains("?")) {
                            urlParams = jdbcUrl.substring(jdbcUrl.indexOf("?"));
                        }
                        serverUrl = jdbcUrl.substring(0, dbStartIndex) + urlParams;
                    }
                }
            }

            logger.info("🔍 正在检查数据库: {}", databaseName);
            logger.info("🔗 连接到 MySQL 服务器: {}", serverUrl);

            try (Connection conn = DriverManager.getConnection(serverUrl, username, password);
                 Statement stmt = conn.createStatement()) {

                // 检查数据库是否存在
                String checkDbSql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '" + databaseName + "'";
                boolean dbExists = stmt.executeQuery(checkDbSql).next();

                if (!dbExists) {
                    // 创建数据库
                    String createDbSql = "CREATE DATABASE IF NOT EXISTS " + databaseName + " CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci";
                    stmt.executeUpdate(createDbSql);
                    logger.info("✅ 数据库 '{}' 创建成功", databaseName);
                } else {
                    logger.info("✅ 数据库 '{}' 已存在", databaseName);
                }
            }
        } catch (Exception e) {
            logger.warn("⚠️  数据库初始化失败（可能数据库已存在或 MySQL 未启动）: {}", e.getMessage());
            // 不抛出异常，让应用继续启动
        }
    }
}
