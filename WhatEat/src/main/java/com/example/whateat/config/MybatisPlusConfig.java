package com.example.whateat.config;

import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.extension.spring.MybatisSqlSessionFactoryBean;
import org.apache.ibatis.logging.stdout.StdOutImpl;
import org.springframework.context.annotation.Bean;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import javax.sql.DataSource;

/**
 * 显式创建 MyBatis-Plus 的 SqlSessionFactory。
 *
 * 说明：
 * - Spring Boot 4 / Spring Framework 7 下，部分组合会导致 MyBatis-Plus 自动配置未能创建 sqlSessionFactory，
 *   进而出现 "Property 'sqlSessionFactory' or 'sqlSessionTemplate' are required"。
 * - 该配置同时避免 classpath 下不存在 mapper 目录时的资源解析异常。
 */
@org.springframework.context.annotation.Configuration
public class MybatisPlusConfig {

    @Bean("sqlSessionFactory")
    public MybatisSqlSessionFactoryBean sqlSessionFactory(DataSource dataSource) throws Exception {
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);

        try {
            var mapperResources =
                    new PathMatchingResourcePatternResolver().getResources("classpath*:mapper/*.xml");
            if (mapperResources.length > 0) {
                factory.setMapperLocations(mapperResources);
            }
        } catch (Exception ignored) {
            // 无 mapper 目录或无 XML 时跳过
        }

        factory.setTypeAliasesPackage("com.example.whateat.entity");

        MybatisConfiguration configuration = new MybatisConfiguration();
        configuration.setLogImpl(StdOutImpl.class);
        factory.setConfiguration(configuration);

        return factory;
    }
}

