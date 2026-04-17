from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app import api, models, database

os.makedirs("uploads", exist_ok=True)

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Shopping Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api.router)


@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    try:
        if db.query(models.Product).count() == 0:
            sample_products = [
                models.Product(name="iPhone 15 Pro", description="苹果最新旗舰手机，A17芯片，钛金属边框", price=8999.0, image="https://picsum.photos/400/400?1", stock=100, low_stock_threshold=20, category="手机", is_hot=1, sales=256),
                models.Product(name="MacBook Pro 14", description="M3 Pro芯片，专业性能笔记本", price=16999.0, image="https://picsum.photos/400/400?2", stock=50, low_stock_threshold=10, category="电脑", is_hot=1, sales=128),
                models.Product(name="AirPods Pro 2", description="无线降噪耳机，自适应通透模式", price=1899.0, image="https://picsum.photos/400/400?3", stock=200, low_stock_threshold=30, category="耳机", is_hot=1, sales=512),
                models.Product(name="iPad Air 5", description="M1芯片，轻薄平板电脑", price=4799.0, image="https://picsum.photos/400/400?4", stock=80, low_stock_threshold=15, category="平板", is_hot=0, sales=189),
                models.Product(name="Apple Watch S9", description="健康监测，运动追踪", price=2999.0, image="https://picsum.photos/400/400?5", stock=120, low_stock_threshold=20, category="手表", is_hot=1, sales=345),
                models.Product(name="小米14 Ultra", description="徕卡影像，骁龙8 Gen3", price=6499.0, image="https://picsum.photos/400/400?6", stock=150, low_stock_threshold=25, category="手机", is_hot=0, sales=234),
                models.Product(name="华为Mate 60 Pro", description="卫星通话，麒麟芯片", price=6999.0, image="https://picsum.photos/400/400?7", stock=90, low_stock_threshold=20, category="手机", is_hot=1, sales=456),
                models.Product(name="Sony WH-1000XM5", description="行业标杆降噪耳机", price=2499.0, image="https://picsum.photos/400/400?8", stock=110, low_stock_threshold=15, category="耳机", is_hot=0, sales=167),
                models.Product(name="Dell XPS 15", description="4K OLED屏，轻薄高性能", price=12999.0, image="https://picsum.photos/400/400?9", stock=60, low_stock_threshold=10, category="电脑", is_hot=0, sales=78),
                models.Product(name="Samsung Galaxy S24", description="Dynamic AMOLED 2X", price=7999.0, image="https://picsum.photos/400/400?10", stock=130, low_stock_threshold=20, category="手机", is_hot=0, sales=234),
                models.Product(name="Switch OLED", description="任天堂游戏机，7英寸屏", price=2499.0, image="https://picsum.photos/400/400?11", stock=180, low_stock_threshold=25, category="游戏", is_hot=1, sales=678),
                models.Product(name="PS5 光驱版", description="索尼次世代游戏机", price=3899.0, image="https://picsum.photos/400/400?12", stock=75, low_stock_threshold=10, category="游戏", is_hot=1, sales=445),
            ]
            for product in sample_products:
                db.add(product)
            db.commit()
        else:
            products = db.query(models.Product).all()
            for product in products:
                if product.low_stock_threshold is None or product.low_stock_threshold == 0:
                    product.low_stock_threshold = 10
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Shopping Service is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
