# Rayshopping 购物平台

## 项目概述

基于微服务架构的简易购物系统，包含用户服务和购物服务两个独立运行的微服务，通过 HTTP 接口交互。

## 功能特性

- 用户注册/登录（JWT 认证）
- 角色权限管理（普通用户/管理员）
- 商品浏览与管理（支持分类、搜索、热门商品）
- 购物车功能
- 收货地址管理
- **订单状态流转**（待付款→待发货→待收货→已完成/已取消）
- **模拟支付流程**
- **物流信息管理**（物流单号、物流公司）
- **商品评价系统**（1-5星评分、文字评价）
- 商品收藏功能
- 消息/客服功能
- 图片上传功能
- 管理员后台（用户管理、商品管理、订单管理、消息管理）

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                             │
│                 http://localhost:5173                         │
│                                                               │
│  页面：首页 / 登录/注册 / 购物车 / 地址 / 收藏 / 订单 / 消息 / 管理 │
└──────────┬──────────────────────┬────────────────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────────────────┐
│   用户服务 (user)    │  │       购物服务 (shopping)         │
│  :8081               │  │      :8082                       │
│                      │  │                                  │
│  - 用户注册/登录     │  │  - 商品管理（分类/搜索/热门）      │
│  - 用户 CRUD (管理)  │  │  - 购物车                         │
│  - JWT 认证          │  │  - 订单管理（状态流转/物流）      │
│  - 地址管理          │  │  - 商品评价                         │
│  SQLite: user.db     │  │  - 收藏夹                         │
└──────────────────────┘  │  - 消息系统                       │
           ▲              │  - 图片上传                         │
           │              │  SQLite: shopping.db               │
           │              └──────────┬───────────────────────┘
           │                         │
           └───── HTTP 调用 ─────────┘
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
│       ├── App.vue
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
│       │   ├── Addresses.vue  # 收货地址管理
│       │   ├── Orders.vue     # 订单管理（含评价）
│       │   ├── Favorites.vue  # 我的收藏
│       │   ├── Messages.vue   # 消息/客服（管理员）
│       │   ├── Users.vue      # 用户管理（管理员）
│       │   └── Products.vue   # 商品管理（管理员）
│       └── components/
│           ├── ProductCard.vue
│           ├── ProductDetail.vue  # 商品详情+评价
│           └── CustomerService.vue
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
    ├── uploads/               # 图片上传目录
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

Address (addresses表 - 收货地址)
├── id          Integer
├── user_id     Integer
├── name        String
├── phone       String
├── province    String
├── city        String
├── district    String
├── detail      String
├── is_default  Integer (0-否 1-是)
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
├── category    String   (商品分类，默认"其他")
├── is_hot      Integer  (是否热门 0-否 1-是)
├── sales       Integer  (销量)
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
├── id              Integer
├── user_id         Integer
├── total_price     Float
├── status          String  (pending/paid/shipped/completed/cancelled)
├── address_name    String  (收货人姓名-快照)
├── address_phone   String  (收货人电话-快照)
├── address_province String (省份-快照)
├── address_city    String  (城市-快照)
├── address_district String (区县-快照)
├── address_detail  String  (详细地址-快照)
├── tracking_number String  (物流单号)
├── tracking_company String (物流公司)
├── paid_at         DateTime (付款时间)
├── shipped_at      DateTime (发货时间)
├── completed_at    DateTime (完成时间)
├── cancelled_at    DateTime (取消时间)
├── created_at      DateTime
└── updated_at      DateTime

OrderItem (order_items表 - 订单明细)
├── id          Integer
├── order_id    Integer (外键)
├── product_id  Integer
├── quantity    Integer
├── price       Float
└── created_at  DateTime

Favorite (favorites表 - 收藏)
├── id          Integer
├── user_id     Integer
├── product_id  Integer
└── created_at  DateTime

Message (messages表 - 消息)
├── id              Integer
├── from_user_id    Integer  (发送者ID)
├── to_user_id      Integer  (接收者ID)
├── content         String   (消息内容)
├── is_read         Integer  (0-未读 1-已读)
└── created_at      DateTime

Review (reviews表 - 商品评价)
├── id          Integer
├── user_id     Integer
├── product_id  Integer
├── order_id    Integer
├── rating      Integer  (1-5星)
├── content     String   (评价内容)
├── images      String   (JSON数组，评价图片)
├── created_at  DateTime
└── updated_at  DateTime
```

## API 设计

### 用户服务 (:8081)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/register | 用户注册 | 否 |
| POST | /api/login | 用户登录 | 否 |
| GET | /api/users/verify/{user_id} | 验证用户是否存在 | 否 |
| GET | /api/users/info/{user_id} | 获取用户基本信息 | 否 |
| GET | /api/users/me | 获取当前用户信息 | 是 |
| GET | /api/users | 用户列表 | 仅管理员 |
| GET | /api/users/{user_id} | 用户详情 | 仅管理员 |
| POST | /api/users | 创建用户 | 仅管理员 |
| PUT | /api/users/{user_id} | 更新用户 | 仅管理员 |
| DELETE | /api/users/{user_id} | 删除用户 | 仅管理员 |
| GET | /api/addresses | 获取地址列表 | 是 |
| GET | /api/addresses/{id} | 获取地址详情 | 是 |
| POST | /api/addresses | 创建地址 | 是 |
| PUT | /api/addresses/{id} | 更新地址 | 是 |
| DELETE | /api/addresses/{id} | 删除地址 | 是 |

### 购物服务 (:8082)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/image | 上传商品图片 |
| GET | /api/products | 商品列表（支持 category、search 筛选） |
| GET | /api/products/categories | 获取所有分类 |
| GET | /api/products/hot | 获取热门商品 |
| GET | /api/products/{product_id} | 商品详情 |
| POST | /api/products | 添加商品 |
| PUT | /api/products/{product_id} | 更新商品 |
| DELETE | /api/products/{product_id} | 删除商品 |
| GET | /api/cart/{user_id} | 获取购物车 |
| POST | /api/cart | 加入购物车 |
| PUT | /api/cart/{cart_id} | 更新购物车数量 |
| DELETE | /api/cart/{cart_id} | 移除购物车项 |
| POST | /api/orders | 创建订单（含收货地址） |
| GET | /api/orders | 获取所有订单 |
| GET | /api/orders/{user_id} | 用户订单列表 |
| GET | /api/orders/detail/{order_id} | 订单详情 |
| PUT | /api/orders/{order_id}/status | 更新订单状态 |
| POST | /api/orders/{order_id}/ship | 订单发货（填写物流信息） |
| GET | /api/favorites/{user_id} | 获取收藏列表 |
| POST | /api/favorites | 添加收藏 |
| DELETE | /api/favorites/item/{favorite_id} | 删除收藏项（by ID） |
| DELETE | /api/favorites/{user_id}/{product_id} | 删除收藏项（by 用户+商品） |
| GET | /api/messages/{user_id} | 获取消息列表 |
| GET | /api/messages/unread/{user_id} | 获取未读消息数 |
| GET | /api/messages/conversations/{user_id} | 获取会话用户列表 |
| POST | /api/messages | 发送消息 |
| PUT | /api/messages/{message_id}/read | 标记单条消息已读 |
| PUT | /api/messages/{user_id}/{other_user_id}/read | 标记会话已读 |
| GET | /api/reviews/product/{product_id} | 获取商品评价列表 |
| GET | /api/reviews/user/{user_id} | 获取用户评价列表 |
| GET | /api/reviews/pending/{user_id}/{order_id} | 获取待评价商品 |
| POST | /api/reviews | 创建评价 |
| PUT | /api/reviews/{review_id} | 更新评价 |
| DELETE | /api/reviews/{review_id} | 删除评价 |

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

## 订单状态流转

```
待付款 (pending)
    ↓ [用户付款/管理员标记已付款]
待发货 (paid)
    ↓ [管理员发货，填写物流信息]
待收货 (shipped)
    ↓ [用户确认收货/管理员标记完成]
已完成 (completed)

[取消订单] → 已取消 (cancelled)
    (待付款/待发货状态可取消，取消时回滚库存和销量)
```

## 角色权限

| 功能 | 普通用户 | 管理员 |
|------|---------|--------|
| 浏览商品 | ✓ | ✓ |
| 注册/登录 | ✓ | ✓ |
| 购物车操作 | ✓ | ✓ |
| 收货地址管理 | ✓ | ✓ |
| 创建订单 | ✓ | ✓ |
| 订单付款 | ✓ | ✓ |
| 确认收货 | ✓ | ✗ |
| 评价商品 | ✓ | ✗ |
| 查看自己订单 | ✓ | ✓ |
| 商品收藏 | ✓ | ✓ |
| 发送/接收消息 | ✓ | ✓ |
| 查看所有订单 | ✗ | ✓ |
| 标记订单已付款 | ✗ | ✓ |
| 订单发货 | ✗ | ✓ |
| 标记订单完成 | ✗ | ✓ |
| 取消订单 | ✓ | ✓ |
| 商品管理（上架/编辑/删除） | ✗ | ✓ |
| 用户管理（创建/编辑/删除） | ✗ | ✓ |
| 消息管理（客服） | ✗ | ✓ |

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

- **购物服务**：创建示例商品（支持分类、热门标记）

### 前端代理配置

Vite 开发服务器配置反向代理：

- `/api/user/*` → `http://localhost:8081/*`
- `/api/shop/*` → `http://localhost:8082/*`
- `/uploads/*` → `http://localhost:8082/uploads/*`

避免跨域问题。

## 编码规范

- Python 代码遵循 PEP 8
- 前端使用 ESLint + Prettier
- API 统一返回格式：`{ "code": 200, "message": "ok", "data": {} }`
- 错误码：200 成功，400 参数错误，401 未授权，403 禁止，404 未找到，500 服务器错误
