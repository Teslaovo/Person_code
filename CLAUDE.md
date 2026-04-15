# Rayshopping 购物平台

## 项目概述

基于微服务架构的简易购物系统，包含用户服务和购物服务两个独立运行的微服务，通过 HTTP 接口交互。

## 功能特性

- 用户注册/登录（JWT 认证）
- 角色权限管理（普通用户/管理员）
- 商品浏览与管理
- 购物车功能
- 订单创建与查询
- 管理员后台（用户管理、商品管理、订单管理）

## 架构设计

```
┌─────────────────────────────────────────────────┐
│                   前端 (Vue 3)                    │
│              http://localhost:5173                │
│                                                   │
│  页面：首页 / 登录/注册 / 购物车 / 订单 / 管理    │
└──────────┬──────────────────────┬────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────────┐
│   用户服务 (user)    │  │   购物服务 (shopping)     │
│  :8081               │  │  :8082                   │
│                      │  │                          │
│  - 用户注册/登录     │  │  - 商品管理               │
│  - 用户 CRUD (管理)  │  │  - 购物车                 │
│  - JWT 认证          │  │  - 订单管理               │
│  SQLite: user.db     │  │  - 结算                   │
└──────────────────────┘  │                          │
           ▲              │  SQLite: shopping.db      │
           │              └─────────┬─────────────────┘
           │                        │
           └── HTTP 调用 ───────────┘
           (购物服务调用用户服务校验用户)
```

## 技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite + Element Plus | SPA，组合式 API |
| 后端 | Python + FastAPI | 两个独立的 FastAPI 服务 |
| 数据库 | SQLite | 零配置，本地文件存储，无需安装 |
| ORM | SQLAlchemy | Python 主流 ORM |
| 数据验证 | Pydantic | 数据序列化和验证 |
| 认证 | JWT (python-jose) | 无状态认证 |
| 密码加密 | passlib[bcrypt] | 密码哈希存储 |
| 服务通信 | HTTP/REST + httpx | 购物服务通过 HTTP 调用用户服务 |
| 包管理 | pip / npm | 各自独立管理依赖 |

## 目录结构

```
shopping/
├── CLAUDE.md
├── frontend/                  # 前端项目
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── router/
│       │   └── index.js
│       ├── api/               # 接口封装
│       │   ├── user.js
│       │   └── shopping.js
│       ├── views/
│       │   ├── Mall.vue       # 商城首页（商品列表）
│       │   ├── Login.vue      # 登录
│       │   ├── Register.vue   # 注册
│       │   ├── Cart.vue       # 购物车
│       │   ├── Orders.vue     # 订单管理
│       │   ├── Users.vue      # 用户管理（管理员）
│       │   └── Products.vue   # 商品管理（管理员）
│       └── components/
│           └── ProductCard.vue
├── user-service/              # 用户微服务
│   ├── requirements.txt
│   ├── main.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py        # 数据库连接配置
│   │   ├── models.py          # SQLAlchemy 模型
│   │   ├── schemas.py         # Pydantic 模式
│   │   ├── crud.py            # 数据库操作
│   │   ├── auth.py            # JWT 认证工具
│   │   └── api.py             # API 路由
│   └── user.db                # SQLite 数据文件（运行时生成）
└── shopping-service/          # 购物微服务
    ├── requirements.txt
    ├── main.py
    ├── app/
    │   ├── __init__.py
    │   ├── database.py        # 数据库连接配置
    │   ├── models.py          # SQLAlchemy 模型
    │   ├── schemas.py         # Pydantic 模式
    │   ├── crud.py            # 数据库操作
    │   ├── api.py             # API 路由
    │   └── user_client.py     # 调用用户服务的 HTTP 客户端
    └── shopping.db            # SQLite 数据文件（运行时生成）
```

## 数据模型

### 用户服务

```
User (users表)
├── id          Integer (主键，自增)
├── username    String  (唯一)
├── password    String  (bcrypt 加密)
├── nickname    String
├── phone       String
├── role        String  (user/admin)
├── created_at  DateTime
└── updated_at  DateTime
```

### 购物服务

```
Product (products表 - 商品)
├── id          Integer
├── name        String
├── description String
├── price       Float
├── image       String   (图片 URL)
├── stock       Integer
├── created_at  DateTime
└── updated_at  DateTime

CartItem (cart_items表 - 购物车项)
├── id          Integer
├── user_id     Integer
├── product_id  Integer
├── quantity    Integer
├── created_at  DateTime
└── updated_at  DateTime

Order (orders表 - 订单)
├── id          Integer
├── user_id     Integer
├── total_price Float
├── status      String  (pending/paid/cancelled)
├── created_at  DateTime
└── updated_at  DateTime

OrderItem (order_items表 - 订单明细)
├── id          Integer
├── order_id    Integer (外键)
├── product_id  Integer
├── quantity    Integer
├── price       Float
└── created_at  DateTime
```

## API 设计

### 用户服务 (:8081)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/register | 用户注册 | 否 |
| POST | /api/login | 用户登录 | 否 |
| GET | /api/users/verify/{user_id} | 验证用户是否存在 | 否 |
| GET | /api/users/me | 获取当前用户信息 | 是 |
| GET | /api/users | 用户列表 | 仅管理员 |
| GET | /api/users/{user_id} | 用户详情 | 仅管理员 |
| POST | /api/users | 创建用户 | 仅管理员 |
| PUT | /api/users/{user_id} | 更新用户 | 仅管理员 |
| DELETE | /api/users/{user_id} | 删除用户 | 仅管理员 |

### 购物服务 (:8082)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/products | 商品列表 |
| GET | /api/products/{product_id} | 商品详情 |
| POST | /api/products | 添加商品 |
| PUT | /api/products/{product_id} | 更新商品 |
| DELETE | /api/products/{product_id} | 删除商品 |
| GET | /api/cart/{user_id} | 获取购物车 |
| POST | /api/cart | 加入购物车 |
| PUT | /api/cart/{cart_id} | 更新购物车数量 |
| DELETE | /api/cart/{cart_id} | 移除购物车项 |
| POST | /api/orders | 创建订单 |
| GET | /api/orders | 获取所有订单 |
| GET | /api/orders/{user_id} | 用户订单列表 |
| GET | /api/orders/detail/{order_id} | 订单详情 |

### 统一返回格式

```json
{
  "code": 200,
  "message": "ok",
  "data": {}
}
```

### 认证方式

使用 Bearer Token，在请求头中添加：
```
Authorization: Bearer <access_token>
```

## 角色权限

| 功能 | 普通用户 | 管理员 |
|------|---------|--------|
| 浏览商品 | ✓ | ✓ |
| 注册/登录 | ✓ | ✓ |
| 购物车操作 | ✓ | ✓ |
| 创建订单 | ✓ | ✓ |
| 查看自己订单 | ✓ | ✓ |
| 查看所有订单 | ✗ | ✓ |
| 商品管理（上架/编辑/删除） | ✗ | ✓ |
| 用户管理（创建/编辑/删除） | ✗ | ✓ |

## 微服务交互

购物服务在创建订单时通过 HTTP 调用用户服务验证用户是否存在：

```
购物服务 --GET http://localhost:8081/api/users/verify/{id}--> 用户服务
```

使用 httpx 异步客户端进行调用，超时时间 5 秒。

## 本地开发与运行

### 环境要求

- Python 3.8+
- Node.js 18+
- Git（可选）

### 启动步骤

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

### 初始化数据

两个服务在启动时会自动检查并初始化示例数据：

- **用户服务**：
  - 管理员: `admin` / `admin123`
  - 普通用户: `test1` / `123456`, `test2` / `123456`

- **购物服务**：创建 5 个示例商品（iPhone 15, MacBook Pro, AirPods Pro, iPad Air, Apple Watch）

### 前端代理配置

Vite 开发服务器配置反向代理：

- `/api/user/*` → `http://localhost:8081/*`
- `/api/shop/*` → `http://localhost:8082/*`

避免跨域问题。

## 编码规范

- Python 代码遵循 PEP 8
- 前端使用 ESLint + Prettier
- API 统一返回格式：`{ "code": 200, "message": "ok", "data": {} }`
- 错误码：200 成功，400 参数错误，401 未授权，403 禁止，404 未找到，500 服务器错误
