# Rayshopping 购物平台

## 项目概述

基于微服务架构的简易购物系统，包含用户服务和购物服务两个独立运行的微服务，通过 HTTP 接口交互。

## 功能特性

### 用户系统
- 用户注册/登录（JWT 认证）
- 角色权限管理（普通用户/管理员）
- 收货地址管理

### 商品系统
- 商品浏览与管理（支持分类、搜索、热门商品）
- **商品规格/SKU 管理**（多规格、多库存）
- 图片上传功能
- 低库存预警、售罄提醒
- 库存流水记录

### 购物系统
- 购物车功能
- **订单状态流转**（待付款→待发货→待收货→已完成/已取消）
- **模拟支付流程**
- **物流信息管理**（物流单号、物流公司）
- **商品评价系统**（1-5星评分、文字评价）
- 商品收藏功能

### 营销系统
- **限时秒杀**（指定商品秒杀价）
- **满减活动**（订单满额自动减）
- **拼团活动**（折扣率优惠）
- **新人专享**（新用户特价）
- 活动配置向导（可视化配置，无需手写 JSON）

### 统计系统
- **数据统计面板**（销售额、订单量、商品数、转化率）
- 销售趋势（日/周/月统计）
- 商品销售排行
- 低库存预警、售罄商品监控

### 客服系统
- 消息/客服功能

### 管理后台
- 用户管理
- 商品管理（含规格/SKU）
- 订单管理
- 营销活动管理
- 数据统计
- 消息管理（客服）

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                               │
│                 http://localhost:5173                           │
│                                                                 │
│  页面：首页 / 登录/注册 / 购物车 / 地址 / 收藏 / 订单 / 消息   │
│        / 商品详情 / 管理后台(商品/用户/订单/营销/统计)        │
└──────────┬──────────────────────┬────────────────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────────────────┐
│   用户服务 (user)    │  │       购物服务 (shopping)         │
│  :8081               │  │      :8082                       │
│                      │  │                                  │
│  - 用户注册/登录     │  │  - 商品管理（分类/搜索/热门）      │
│  - 用户 CRUD (管理)  │  │  - 商品规格/SKU                  │
│  - JWT 认证          │  │  - 购物车                         │
│  - 地址管理          │  │  - 订单管理（状态流转/物流）      │
│  SQLite: user.db     │  │  - 商品评价                         │
└──────────────────────┘  │  - 收藏夹                         │
           ▲              │  - 消息系统                       │
           │              │  - 图片上传                         │
           │              │  - 营销活动（秒杀/满减/拼团/新人）│
           │              │  - 数据统计                         │
           │              │  - 库存预警                         │
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
├── README.md
├── 营销活动配置指南.md
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
│       │   ├── Mall.vue       # 商城首页（商品列表+营销活动）
│       │   ├── Login.vue      # 登录
│       │   ├── Register.vue   # 注册
│       │   ├── Cart.vue       # 购物车
│       │   ├── Addresses.vue  # 收货地址管理
│       │   ├── Orders.vue     # 订单管理（含评价+满减计算）
│       │   ├── Favorites.vue  # 我的收藏
│       │   ├── Messages.vue   # 消息/客服（管理员）
│       │   ├── Users.vue      # 用户管理（管理员）
│       │   ├── Products.vue   # 商品管理（管理员，含规格/SKU）
│       │   ├── ProductDetail.vue  # 商品详情+评价
│       │   ├── Dashboard.vue  # 数据统计（管理员）
│       │   └── Promotions.vue # 营销活动管理（管理员）
│       └── components/
│           ├── ProductCard.vue # 商品卡片（支持活动价格显示）
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
├── id                  Integer
├── name                String
├── description         String
├── price               Float
├── image               String
├── images              String (JSON数组)
├── stock               Integer
├── low_stock_threshold Integer (低库存预警线，默认10)
├── category            String (商品分类，默认"其他")
├── is_hot              Integer (是否热门 0-否 1-是)
├── is_active           Integer (是否上架 0-下架 1-是)
├── has_sku             Integer (是否有规格 0-否 1-是)
├── tags                String (JSON数组)
├── sales               Integer (销量)
├── created_at          DateTime
└── updated_at          DateTime

ProductSpec (product_specs表 - 商品规格)
├── id          Integer
├── product_id  Integer (外键)
├── spec_name   String (规格名称，如"颜色"、"尺寸")
├── spec_values String (JSON数组，规格值如["红色","蓝色"])
└── created_at  DateTime

ProductSKU (product_skus表 - 商品SKU)
├── id          Integer
├── product_id  Integer (外键)
├── sku_name    String (SKU名称，如"红色+XL")
├── spec_json   String (JSON存储规格键值对)
├── price       Float (SKU价格)
├── stock       Integer (SKU库存)
├── image       String (SKU图片)
├── sales       Integer (SKU销量)
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
├── status          String (pending/paid/shipped/completed/cancelled)
├── address_name    String (收货人姓名-快照)
├── address_phone   String (收货人电话-快照)
├── address_province String (省份-快照)
├── address_city    String (城市-快照)
├── address_district String (区县-快照)
├── address_detail  String (详细地址-快照)
├── tracking_number String (物流单号)
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
├── from_user_id    Integer (发送者ID)
├── to_user_id      Integer (接收者ID)
├── content         String (消息内容)
├── is_read         Integer (0-未读 1-已读)
└── created_at      DateTime

Review (reviews表 - 商品评价)
├── id          Integer
├── user_id     Integer
├── product_id  Integer
├── order_id    Integer
├── rating      Integer (1-5星)
├── content     String (评价内容)
├── images      String (JSON数组，评价图片)
├── created_at  DateTime
└── updated_at  DateTime

Coupon (coupons表 - 优惠券)
├── id              Integer
├── name            String
├── type            String (fixed-固定金额 discount-折扣)
├── value           Float
├── min_amount      Float (最低使用门槛)
├── total_count     Integer
├── used_count      Integer
├── per_limit       Integer (每人限领)
├── start_time      DateTime
├── end_time        DateTime
├── status          String (active/inactive)
├── category        String (限定分类)
├── product_ids     String (JSON数组，限定商品)
└── created_at      DateTime

UserCoupon (user_coupons表 - 用户优惠券)
├── id          Integer
├── user_id     Integer
├── coupon_id   Integer
├── status      String (unused/used/expired)
├── order_id    Integer
├── received_at DateTime
└── used_at     DateTime

Promotion (promotions表 - 营销活动)
├── id          Integer
├── name        String
├── type        String (flashsale/fullreduce/groupon/newuser)
├── status      String (active/inactive/ended)
├── start_time  DateTime
├── end_time    DateTime
├── config      String (JSON配置)
├── product_ids String (逗号分隔的商品ID)
├── category    String (限定分类)
└── created_at  DateTime

AfterSale (after_sales表 - 售后)
├── id              Integer
├── user_id         Integer
├── order_id        Integer
├── order_item_id   Integer
├── type            String (refund/return/exchange)
├── reason          String
├── description     String
├── images          String (JSON数组)
├── refund_amount   Float
├── status          String (pending/approved/rejected/processing/completed)
├── approved_at     DateTime
├── approved_by     Integer
├── reject_reason   String
├── created_at      DateTime
└── updated_at      DateTime

InventoryLog (inventory_logs表 - 库存流水)
├── id          Integer
├── product_id  Integer
├── sku_id      Integer
├── type        String (in/out/adjust/order/cancel)
├── change      Integer (变动数量)
├── before_stock Integer
├── after_stock  Integer
├── order_id    Integer
├── remark      String
└── created_at  DateTime

SearchHistory (search_histories表 - 搜索历史)
├── id          Integer
├── user_id     Integer
├── keyword     String
└── created_at  DateTime

HotSearch (hot_searches表 - 热门搜索)
├── id             Integer
├── keyword        String (唯一)
├── search_count   Integer
├── is_active      Integer
├── sort_order     Integer
└── created_at     DateTime

StockAlert (stock_alerts表 - 库存预警)
├── id             Integer
├── product_id     Integer
├── sku_id         Integer
├── alert_type     String (low_stock/out_of_stock)
├── stock_before   Integer
├── stock_after    Integer
├── is_resolved    Integer
├── resolved_at    DateTime
└── created_at     DateTime

ProductRecommendation (product_recommendations表 - 商品推荐)
├── id                      Integer
├── product_id              Integer
├── recommended_product_id  Integer
├── type                    String (frequently_bought_together/similar)
├── weight                  Integer
└── created_at              DateTime
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

#### 商品管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/image | 上传商品图片 |
| GET | /api/products | 商品列表（支持 category、search 筛选） |
| GET | /api/products/categories | 获取所有分类 |
| GET | /api/products/hot | 获取热门商品 |
| GET | /api/products/low-stock | 获取低库存商品 |
| GET | /api/products/out-of-stock | 获取售罄商品 |
| GET | /api/products/filter | 商品筛选（价格、销量等） |
| GET | /api/products/{product_id} | 商品详情 |
| POST | /api/products | 添加商品 |
| PUT | /api/products/{product_id} | 更新商品 |
| DELETE | /api/products/{product_id} | 删除商品 |
| PUT | /api/products/batch/status | 批量更新商品状态 |

#### 商品规格/SKU
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/products/{product_id}/specs | 获取商品规格 |
| POST | /api/products/{product_id}/specs | 添加商品规格 |
| PUT | /api/specs/{spec_id} | 更新规格 |
| DELETE | /api/specs/{spec_id} | 删除规格 |
| GET | /api/products/{product_id}/skus | 获取商品SKU |
| GET | /api/products/{product_id}/with-skus | 获取商品详情(含SKU) |
| POST | /api/products/{product_id}/skus | 添加商品SKU |
| PUT | /api/skus/{sku_id} | 更新SKU |
| DELETE | /api/skus/{sku_id} | 删除SKU |

#### 购物车
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/cart/{user_id} | 获取购物车 |
| POST | /api/cart | 加入购物车 |
| PUT | /api/cart/{cart_id} | 更新购物车数量 |
| DELETE | /api/cart/{cart_id} | 移除购物车项 |

#### 订单管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/orders | 创建订单（含收货地址，支持传入优惠后价格） |
| GET | /api/orders | 获取所有订单 |
| GET | /api/orders/{user_id} | 用户订单列表 |
| GET | /api/orders/detail/{order_id} | 订单详情 |
| PUT | /api/orders/{order_id}/status | 更新订单状态 |
| POST | /api/orders/{order_id}/ship | 订单发货（填写物流信息） |

#### 收藏夹
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/favorites/{user_id} | 获取收藏列表 |
| POST | /api/favorites | 添加收藏 |
| DELETE | /api/favorites/item/{favorite_id} | 删除收藏项（by ID） |
| DELETE | /api/favorites/{user_id}/{product_id} | 删除收藏项（by 用户+商品） |

#### 消息系统
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/messages/{user_id} | 获取消息列表 |
| GET | /api/messages/unread/{user_id} | 获取未读消息数 |
| GET | /api/messages/conversations/{user_id} | 获取会话用户列表 |
| POST | /api/messages | 发送消息 |
| PUT | /api/messages/{message_id}/read | 标记单条消息已读 |
| PUT | /api/messages/{user_id}/{other_user_id}/read | 标记会话已读 |

#### 商品评价
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/reviews/product/{product_id} | 获取商品评价列表 |
| GET | /api/reviews/user/{user_id} | 获取用户评价列表 |
| GET | /api/reviews/pending/{user_id}/{order_id} | 获取待评价商品 |
| POST | /api/reviews | 创建评价 |
| PUT | /api/reviews/{review_id} | 更新评价 |
| DELETE | /api/reviews/{review_id} | 删除评价 |

#### 营销活动
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/promotions | 获取活动列表 |
| GET | /api/promotions/active | 获取当前生效活动 |
| GET | /api/promotions/{promotion_id} | 获取活动详情 |
| POST | /api/promotions | 创建活动 |
| PUT | /api/promotions/{promotion_id} | 更新活动 |
| DELETE | /api/promotions/{promotion_id} | 删除活动 |

#### 数据统计
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stats/sales | 销售趋势统计 |
| GET | /api/stats/products/rank | 商品销售排行 |
| GET | /api/stats/users/growth | 用户增长统计 |
| GET | /api/stats/orders/conversion | 订单转化率 |
| GET | /api/stats/summary | 综合统计概览 |

#### 搜索
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/search/history | 添加搜索历史 |
| GET | /api/search/history/{user_id} | 获取搜索历史 |
| GET | /api/search/hot | 获取热门搜索 |
| GET | /api/search/suggestions | 获取搜索建议 |

#### 优惠券
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/coupons | 获取优惠券列表 |
| GET | /api/coupons/{coupon_id} | 获取优惠券详情 |
| POST | /api/coupons | 创建优惠券 |
| PUT | /api/coupons/{coupon_id} | 更新优惠券 |
| DELETE | /api/coupons/{coupon_id} | 删除优惠券 |
| POST | /api/coupons/calculate | 计算优惠金额 |
| GET | /api/user-coupons/{user_id} | 获取用户优惠券 |
| POST | /api/user-coupons/claim | 领取优惠券 |
| PUT | /api/user-coupons/{user_coupon_id}/use | 使用优惠券 |

#### 库存预警
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stock-alerts | 获取库存预警列表 |
| POST | /api/stock-alerts/{alert_id}/resolve | 标记预警已解决 |

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

## 营销活动类型

### 限时秒杀 (flashsale)
- 配置：`{ "flash_price": 1000 }`
- 效果：指定商品直接显示秒杀价
- 范围：可指定商品或分类

### 满减活动 (fullreduce)
- 配置：`{ "min_amount": 300, "discount": 50 }`
- 效果：订单满300减50，结算时自动计算
- 范围：可指定商品或分类

### 拼团活动 (groupon)
- 配置：`{ "group_size": 3, "discount_rate": 0.8 }`
- 效果：3人拼团享8折
- 范围：可指定商品或分类

### 新人专享 (newuser)
- 配置：`{ "new_user_price": 99 }`
- 效果：新用户特价
- 范围：可指定商品或分类

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
| 商品规格/SKU管理 | ✗ | ✓ |
| 营销活动管理 | ✗ | ✓ |
| 数据统计查看 | ✗ | ✓ |
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

- **购物服务**：创建示例商品（支持分类、热门标记、低库存阈值）

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

## 营销活动配置指南

详细的营销活动配置说明请参考 [营销活动配置指南.md](./营销活动配置指南.md)
