# Rayshopping 购物平台

基于微服务架构的现代化购物系统，包含完整的电商功能和管理后台。

## 功能特性

### 用户端
- 用户注册/登录（JWT 认证）
- 商品浏览（分类、搜索、热门推荐）
- 购物车管理
- 收货地址管理
- 订单管理（创建、支付、确认收货、评价）
- 商品收藏
- 消息/客服

### 营销功能
- **限时秒杀** - 指定商品特价
- **满减活动** - 订单满额自动减
- **拼团活动** - 多人团购折扣
- **新人专享** - 新用户特价

### 管理后台
- 商品管理（含规格/SKU）
- 用户管理
- 订单管理
- 营销活动管理
- 数据统计（销售额、订单量、转化率等）
- 库存预警

## 技术栈

- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Python + FastAPI（双微服务）
- **数据库**: SQLite
- **认证**: JWT
- **密码加密**: bcrypt

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+

### 启动服务

```bash
# 1. 启动用户服务
cd user-service
pip install -r requirements.txt
python main.py
# 监听 :8081

# 2. 启动购物服务（新终端）
cd shopping-service
pip install -r requirements.txt
python main.py
# 监听 :8082

# 3. 启动前端（新终端）
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 测试账号

- 管理员: `admin` / `admin123`
- 普通用户: `test1` / `123456`

## 项目文档

详细文档请查看 [CLAUDE.md](./CLAUDE.md)

营销活动配置请查看 [营销活动配置指南.md](./营销活动配置指南.md)

## 项目结构

```
shopping/
├── frontend/              # 前端项目
├── user-service/          # 用户微服务 (:8081)
├── shopping-service/      # 购物微服务 (:8082)
├── CLAUDE.md             # 详细技术文档
├── README.md             # 本文件
└── 营销活动配置指南.md    # 营销活动配置说明
```

## 许可证

MIT License
