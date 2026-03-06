-- 自动建表脚本：项目启动时由 Spring Boot 执行
-- 数据库会在启动时自动创建（如果不存在）

CREATE TABLE IF NOT EXISTS users (
    userId INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，自增主键',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    telephone BIGINT DEFAULT NULL COMMENT '手机号',
    token VARCHAR(255) DEFAULT NULL COMMENT '登录 token',
    updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE IF NOT EXISTS restaurant(
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '饭店ID',
    rname VARCHAR(50) NOT NULL COMMENT '饭店名',
    address VARCHAR(200) NOT NULL COMMENT '饭店地址',
    floor TINYINT NOT NULL COMMENT '饭店所在楼层',
    windows INT NOT NULL COMMENT '具体窗口',
    openTime VARCHAR(50) COMMENT '营业时间',
    rate DECIMAL(2,1) DEFAULT 0.0 COMMENT '饭店综合评分',
    updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_restaurant_rname (rname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='饭店表';

CREATE TABLE IF NOT EXISTS dish(
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '菜品ID',
    dname VARCHAR(50) NOT NULL COMMENT '菜品名',
    restaurantId  INT NOT NULL COMMENT '菜品所属饭店ID',
    price DECIMAL(3,1) DEFAULT 0.0 NOT NULL COMMENT '菜品价格',
    tags VARCHAR(100) COMMENT '菜品标签',
    photo VARCHAR(50) COMMENT '菜品图片地址',
    status TINYINT DEFAULT 1 COMMENT '菜品状态，1-在售,0-售罄',
    rate DECIMAL(2,1) DEFAULT 0.0 COMMENT '菜品综合评分',
    updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY(restaurantId) REFERENCES restaurant(id) ON DELETE CASCADE,
    INDEX idx_dish_restaurant (restaurantId),
    INDEX idx_dish_tags (tags),
    INDEX idx_dish_rate (rate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品表';

CREATE TABLE IF NOT EXISTS comment(
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评论ID',
    targetType TINYINT NOT NULL COMMENT '评论对象类型,1-饭店,2-菜品',
    targetId INT NOT NULL COMMENT '评论对象ID',
    content TEXT NOT NULL COMMENT '评论内容',
    rate TINYINT NOT NULL COMMENT '评分',
    userId INT NOT NULL COMMENT '评论者ID',
    userName VARCHAR(50) NOT NULL COMMENT '评论者昵称',
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
    INDEX idx_comment_target (targetType,targetId)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

CREATE TABLE IF NOT EXISTS dishTag(
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    tagName VARCHAR(50) NOT NULL UNIQUE COMMENT '标签关键词',
    INDEX idx_tag_name (tagName)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品标签统计表';

CREATE TABLE IF NOT EXISTS dishTagRelation (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '关联ID',
    dishId INT NOT NULL COMMENT '菜品ID，关联dish表id',
    tagId INT NOT NULL COMMENT '标签ID，关联dishTag表id',
    -- 外键约束
    FOREIGN KEY (dishId) REFERENCES dish(id) ON DELETE CASCADE,
    FOREIGN KEY (tagId) REFERENCES dishTag(id) ON DELETE CASCADE,
    -- 联合唯一索引，避免同一菜品重复绑定同一标签
    UNIQUE KEY uk_dish_tag_uni (dishId, tagId)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品-标签关联表';