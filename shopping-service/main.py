from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app import api, models, database

# 创建上传目录
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

# 挂载静态文件服务，用于访问上传的图片
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api.router)


@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    try:
        if db.query(models.Product).count() == 0:
            sample_products = [
                models.Product(name="iPhone 15", description="苹果最新手机", price=7999.0, image="https://picsum.photos/200/200?1", stock=100),
                models.Product(name="MacBook Pro", description="苹果笔记本电脑", price=14999.0, image="https://picsum.photos/200/200?2", stock=50),
                models.Product(name="AirPods Pro", description="无线降噪耳机", price=1899.0, image="https://picsum.photos/200/200?3", stock=200),
                models.Product(name="iPad Air", description="苹果平板电脑", price=4799.0, image="https://picsum.photos/200/200?4", stock=80),
                models.Product(name="Apple Watch", description="苹果智能手表", price=2999.0, image="https://picsum.photos/200/200?5", stock=120),
            ]
            for product in sample_products:
                db.add(product)
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Shopping Service is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
