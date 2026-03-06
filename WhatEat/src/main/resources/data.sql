-- 初始样例数据
-- 注意：只有当表为空时才会插入（避免重复插入）

-- 插入测试用户（如果不存在）
INSERT INTO users (username, password, email, telephone, token)
SELECT 'admin', 'admin123', 'admin@example.com', 13800000001, NULL
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

INSERT INTO users (username, password, email, telephone, token)
SELECT 'test', 'test123', 'test@example.com', 13800000002, NULL
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'test');

INSERT INTO users (username, password, email, telephone, token)
SELECT 'user1', 'user123', 'user1@example.com', 13800000003, NULL
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'user1');


-- 1. 真实用户（至少保留1个管理员账号）
INSERT INTO users (username, password, email, telephone,token)
SELECT 'zhangxujia','Xj987456','zhangxujia@sxu.edu.cn',15235827263,NULL
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'zhangxujia');

-- 2. 真实饭店（窗口）信息
INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '临汾呼氏混炒米线', '令德食堂', 2,11,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '临汾呼氏混炒米线');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '南北馄饨/掉渣饼/晋运胡子大盘鸡/颜宝宝土豆泥拌粉/面', '令德食堂', 2,10,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '南北馄饨/掉渣饼/晋运胡子大盘鸡/颜宝宝土豆泥拌粉/面');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '玖号干锅/骨汤鸭血粉丝/淮南牛肉汤', '令德食堂', 2,9,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '玖号干锅/骨汤鸭血粉丝/淮南牛肉汤');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '精美快餐', '令德食堂', 2,8,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '精美快餐');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '精美快餐', '令德食堂', 2,7,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '精美快餐');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '好味道面馆', '令德食堂', 2,6,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '好味道面馆');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '本地菜/晋菜味道', '令德食堂', 2,5,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '本地菜/晋菜味道');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '莫小朵小锅焖面', '令德食堂', 2,4,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '莫小朵小锅焖面');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '韭菜菇小锅猪肚鸡', '令德食堂', 2,3,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '韭菜菇小锅猪肚鸡');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '付广宇大碗鸡肉饭/五谷鱼粉', '令德食堂', 2,2,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '付广宇大碗鸡肉饭/五谷鱼粉');

INSERT INTO restaurant (rname, address, floor, windows, openTime, rate)
SELECT '丑娘舅螺狮粉', '令德食堂', 2,1,NULL,NULL
WHERE NOT EXISTS (SELECT 1 FROM restaurant WHERE rname = '丑娘舅螺狮粉');

-- 3. 【必填】真实菜品信息
INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '砂锅鸡肉米线', 1,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '砂锅鸡肉米线');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '砂锅鸡肉面', 1,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '砂锅鸡肉面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '砂锅鸡方便面', 1,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '砂锅鸡方便面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '砂锅猫耳朵', 1,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '砂锅猫耳朵');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加肉', 1,3.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加香肠', 1,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加香肠');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加麻花', 1,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加麻花');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加卤鸡蛋', 1,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加卤鸡蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加豆腐串', 1,1.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加豆腐串');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '馍夹肉', 1,7.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '馍夹肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '馍夹蛋', 1,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '馍夹蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '馍夹串', 1,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '馍夹串');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鲜肉馄饨（小份）', 2,7.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鲜肉馄饨（小份）');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鲜肉馄饨（大份）', 2,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鲜肉馄饨（大份）');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸辣馄饨（小份）', 2,7.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸辣馄饨（小份）');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸辣馄饨（大份）', 2,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸辣馄饨（大份）');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '青菜鲜肉馄饨', 2,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '青菜鲜肉馄饨');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '咸蛋黄鲜肉馄饨', 2,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '咸蛋黄鲜肉馄饨');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '麻酱干拌馄饨', 2,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '麻酱干拌馄饨');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '剁椒干拌馄饨', 2,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '剁椒干拌馄饨');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '掉渣饼', 2,3.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '掉渣饼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '土豆', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '土豆');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '包菜', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '包菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '海带', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '海带');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '尖椒', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '尖椒');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '生菜', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '生菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '金针菇', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '金针菇');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '烤肠', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '烤肠');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '豆皮', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '豆皮');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '蟹棒', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '蟹棒');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '千叶豆腐', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '千叶豆腐');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鸡蛋', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鸡蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鱼豆腐', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鱼豆腐');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '培根', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '培根');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '脆皮', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '脆皮');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鸡柳', 2,2.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鸡柳');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '里脊肉串', 2,2.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '里脊肉串');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鸡排', 2,3.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鸡排');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '腿排', 2,4.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '腿排');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '晋运大盘鸡', 2,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '晋运大盘鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '晋乡猪肉面', 2,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '晋乡猪肉面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '麻酱鲜椒面', 2,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '麻酱鲜椒面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '风味杂酱面', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '风味杂酱面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '麻酱肉沫面', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '麻酱肉沫面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '豌杂面', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '豌杂面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '热干面', 2,8.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '热干面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '葱油汤面', 2,7.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '葱油汤面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '风味杂酱面', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '风味杂酱面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌肉酱土豆泥拌面/粉', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌肉酱土豆泥拌面/粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '剁椒肉酱土豆泥拌面/粉', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '剁椒肉酱土豆泥拌面/粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '孜然肉酱土豆泥拌面/粉', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '孜然肉酱土豆泥拌面/粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '香辣肉酱土豆泥拌面/粉', 2,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '香辣肉酱土豆泥拌面/粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '经典土豆泥拌面/粉', 2,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '经典土豆泥拌面/粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加鸡蛋', 2,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加鸡蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加宽粉', 2,5.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加宽粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干锅有机花菜（香辣/蒜香）',3,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干锅有机花菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干锅土豆片（香辣/蒜香）',3,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干锅土豆片');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干锅千叶豆腐（香辣/蒜香）',3,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干锅千叶豆腐');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干锅腐竹（香辣/蒜香）',3,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干锅腐竹');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干锅娃娃菜（香辣/蒜香）',3,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干锅娃娃菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干锅包菜（香辣/蒜香）',3,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干锅包菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '米饭（可续加）',3,1.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '米饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '骨汤鸭血粉丝+饼1个',3,10.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '骨汤鸭血粉丝+饼1个');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '淮南牛肉汤+饼1个',3,10.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '淮南牛肉汤+饼1个');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '煎蛋',3,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '煎蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '油酥烧饼',3,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '油酥烧饼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '三杯鸡',4,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '三杯鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酱香鸭腿',4,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酱香鸭腿');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '辣椒炒肉',4,5.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '辣椒炒肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '土豆炒奥尔良',4,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '土豆炒奥尔良');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '火腿炒蛋',4,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '火腿炒蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '青椒肉丝',4,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '青椒肉丝');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '荷塘月色',4,3.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '荷塘月色');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '韭叶千层',4,3.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '韭叶千层');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '西红柿炒鸡蛋',4,3.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '西红柿炒鸡蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '煎鸡蛋',4,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '煎鸡蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '蒜蓉生菜',4,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '蒜蓉生菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸辣白菜',4,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸辣白菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '香辣鱼块',5,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '香辣鱼块');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干炸小酥肉',5,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干炸小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '糖醋锅包肉',5,5.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '糖醋锅包肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '土豆鱼块',5,5.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '土豆鱼块');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '五香鸡腿',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '五香鸡腿');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '过油肉',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '过油肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干炸蘑菇',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干炸蘑菇');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '花菜炒肉',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '花菜炒肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '红烧茄子',5,3.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '红烧茄子');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '过油土豆片',5,2.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '过油土豆片');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '水蒸蛋',5,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '水蒸蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸辣土豆丝',5,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸辣土豆丝');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '红烧肉',5,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '红烧肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '无锡排骨',5,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '无锡排骨');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '木耳肉片',5,5.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '木耳肉片');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '香菇炖鸡',5,5.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '香菇炖鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '蒜苔炒肉',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '蒜苔炒肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '宫保鸡丁',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '宫保鸡丁');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '韭菜炒蛋',5,4.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '韭菜炒蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '家乡豆腐',5,3.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '家乡豆腐');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '土豆焖茄子',5,3.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '土豆焖茄子');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '粉丝包菜',5,2.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '粉丝包菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '麻婆豆腐',5,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '麻婆豆腐');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '蒜蓉油菜',5,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '蒜蓉油菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '清汤面',6,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '清汤面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '浇头酸菜面',6,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '浇头酸菜面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '肉末炸酱面',6,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '肉末炸酱面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '剁椒肉酱面',6,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '剁椒肉酱面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '红烧大肉面',6,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '红烧大肉面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '油泼面',6,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '油泼面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸菜油泼面',6,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸菜油泼面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '剁椒油泼面',6,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '剁椒油泼面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '肉酱油泼面',6,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '肉酱油泼面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '尖椒肉丝面',6,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '尖椒肉丝面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸菜肉丝面',6,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸菜肉丝面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '虎皮尖椒',6,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '虎皮尖椒');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '煎蛋',6,1.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '煎蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '续面',6,0.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '续面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '一荤两素',7,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '一荤两素');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '两荤两素',7,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '两荤两素');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '两荤一素',7,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '两荤一素');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '一荤三素',7,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '一荤三素');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '三素+鸡腿',7,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '三素+鸡腿');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '一荤两素+鸡腿',7,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '一荤两素+鸡腿');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '糖醋里脊饭',7,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '糖醋里脊饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鸡排饭',7,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鸡排饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '小酥肉饭',7,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '小酥肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '花椒鸡饭',7,8.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '花椒鸡饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '双拼',7,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '双拼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '玉米火腿焖面',8,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '玉米火腿焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '豇豆肉沫焖面',8,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '豇豆肉沫焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鱼香肉丝焖面',8,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鱼香肉丝焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '小酥肉薯条/茄条焖面',8,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '小酥肉薯条/茄条焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '奥尔良鸡块面',8,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '奥尔良鸡块面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '锅包肉焖面',8,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '锅包肉焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '韩式五花肉焖面',8,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '韩式五花肉焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '东北大丰收焖面',8,16.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '东北大丰收焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '时蔬焖面',8,9.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '时蔬焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '薯条豆角焖面',8,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '薯条豆角焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '地三鲜焖面',8,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '地三鲜焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '番茄煎蛋焖面',8,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '番茄煎蛋焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '培根金针菇焖面',8,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '培根金针菇焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '肉沫薯条/茄条焖面',8,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '肉沫薯条/茄条焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '台式香肠焖面',8,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '台式香肠焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '大块排骨焖面',8,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '大块排骨焖面');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加薯条/茄条/豆角/煎蛋/台式香肠/玉米',8,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加薯条/茄条/豆角/煎蛋/台式香肠/玉米');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加培根/肉丝/小酥肉/锅包肉/五花肉/鸡块',8,3.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加培根/肉丝/小酥肉/锅包肉/五花肉/鸡块');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加排骨',8,6.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加排骨');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '川湘麻辣猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '川湘麻辣猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '清香柠檬猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '清香柠檬猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '爽口藤椒猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '爽口藤椒猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '爆款酸辣猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '爆款酸辣猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '老坛酸菜猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '老坛酸菜猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '苗家金汤猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '苗家金汤猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '韩式泡菜猪肚鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '韩式泡菜猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '可爱番茄猪肚鸡',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '可爱番茄猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌原味猪肚鸡',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌原味猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鲜香香辣猪肚鸡',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鲜香香辣猪肚鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '麻辣猪肚小酥肉',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '麻辣猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸辣猪肚小酥肉',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸辣猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸菜猪肚小酥肉',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸菜猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '金汤猪肚小酥肉',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '金汤猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '泡菜猪肚小酥肉',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '泡菜猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '柠檬猪肚小酥肉',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '柠檬猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '番茄猪肚小酥肉',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '番茄猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '藤椒猪肚小酥肉',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '藤椒猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '原味猪肚小酥肉',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '原味猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '香辣猪肚小酥肉',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '香辣猪肚小酥肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '米饭',9,0.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '米饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '泡菜钵钵鸡',9,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '泡菜钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '麻辣钵钵鸡',9,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '麻辣钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸菜钵钵鸡',9,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸菜钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '酸辣钵钵鸡',9,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '酸辣钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '金汤钵钵鸡',9,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '金汤钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '藤椒钵钵鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '藤椒钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '原味钵钵鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '原味钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '香辣钵钵鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '香辣钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '番茄钵钵鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '番茄钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '柠檬钵钵鸡',9,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '柠檬钵钵鸡');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '清香柠檬鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '清香柠檬鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '爆款酸辣鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '爆款酸辣鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '老坛酸菜鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '老坛酸菜鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '韩式泡菜鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '韩式泡菜鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '川湘麻辣鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '川湘麻辣鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '苗家金汤鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '苗家金汤鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '爽口藤椒鱼',9,14.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '爽口藤椒鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌清炖鱼',9,15.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌清炖鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '鲜香香辣鱼',9,15.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '鲜香香辣鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '可爱番茄鱼',9,15.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '可爱番茄鱼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加蔬菜',9,1.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加蔬菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加海鲜菇/牛肉丸',9,2.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加海鲜菇/牛肉丸');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加小酥肉/鸡肉/猪肚/鱼肉',9,15.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加小酥肉/鸡肉/猪肚/鱼肉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '大碗龙虾鸡肉饭',10,14.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '大碗龙虾鸡肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌大碗鸡肉饭',10,11.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌大碗鸡肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '孜然剁椒鸡肉饭',10,12.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '孜然剁椒鸡肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '照烧大碗鸡肉饭',10,12.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '照烧大碗鸡肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '可乐鸡翅根饭',10,13.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '可乐鸡翅根饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '叉烧菠萝鸡肉饭',10,13.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '叉烧菠萝鸡肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '肉沫茄子饭',10,9.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '肉沫茄子饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '港式红烧肉饭',10,14.9,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '港式红烧肉饭');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '米饭/自助汤',10,0.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '米饭/自助汤');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '原味渔粉',10,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '原味渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '番茄渔粉',10,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '番茄渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '菌汤渔粉',10,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '菌汤渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '三鲜渔粉',10,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '三鲜渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '藤椒渔粉',10,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '藤椒渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '椒麻渔粉',10,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '椒麻渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '黄金酸汤渔粉',10,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '黄金酸汤渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '猪肚鸡渔粉',10,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '猪肚鸡渔粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加鱼豆腐/墨鱼丸/亲亲肠/生菜',10,1.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加鱼豆腐/墨鱼丸/亲亲肠/生菜');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加卤蛋/金针菇/豆腐皮',10,1.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加卤蛋/金针菇/豆腐皮');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加炸蛋',10,3.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加炸蛋');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌原味螺狮粉',11,9.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌原味螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '五香豆干螺狮粉',11,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '五香豆干螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '极品卤蛋螺狮粉',11,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '极品卤蛋螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '撒尿肉丸螺狮粉',11,11.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '撒尿肉丸螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '特色鱼丸螺狮粉',11,11.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '特色鱼丸螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '广式香肠螺狮粉',11,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '广式香肠螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '炸鸡蛋螺狮粉',11,12.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '炸鸡蛋螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '干捞螺狮粉',11,13.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '干捞螺狮粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌酱拌粉',11,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌酱拌粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '茄汁酱拌粉',11,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '茄汁酱拌粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '椒麻鸡酱拌粉',11,10.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '椒麻鸡酱拌粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '黑鸭酱拌粉',11,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '黑鸭酱拌粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '蟹黄酱拌粉',11,11.0,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '蟹黄酱拌粉');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '招牌螺狮粉+葱花饼',11,11.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '招牌螺狮粉+葱花饼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '炸蛋螺狮粉+葱花饼',11,14.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '炸蛋螺狮粉+葱花饼');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加豆干/卤蛋/腐竹',11,1,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加豆干/卤蛋/腐竹');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加鱼丸/肉丸',11,2.5,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加鱼丸/肉丸');

INSERT INTO dish (dname, restaurantId, price, tags, photo, status, rate)
SELECT '加腊肠/炸鸡蛋/响铃卷',11,3,NULL,NULL,1, NULL
WHERE NOT EXISTS (SELECT 1 FROM dish WHERE dname = '加腊肠/炸鸡蛋/响铃卷');
