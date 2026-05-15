"""
File Upload Service - 主应用
Hermes WeCom Assistant
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .routers.upload import router as upload_router

# 配置日志
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="File Upload Service",
    description="Hermes WeCom Assistant - 文件上传服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置 - 生产环境应限制具体域名
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://localhost,https://127.0.0.1").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload_router)

# 静态文件（H5 上传页面）
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "file-upload"}


@app.get("/")
async def root():
    """根路径 - 重定向到上传页面"""
    return {"message": "File Upload Service", "upload_url": "/static/upload.html", "api_docs": "/docs"}


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("File Upload Service starting...")
    logger.info(f"MINIO_ENDPOINT: {os.getenv('MINIO_ENDPOINT', 'minio:9000')}")
    logger.info(f"MINIO_BUCKET: {os.getenv('MINIO_BUCKET', 'user-files')}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("File Upload Service shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)