"""
Hermes Bridge Service
=====================

本地桥接服务，将任务请求转发给 Hermes Agent 处理。

功能：
- REST API 接收任务请求
- 通过 Docker 与 Hermes Agent 通信
- 返回处理结果
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routers import task
from app.services.hermes_client import HermesClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局 Hermes 客户端
hermes_client: HermesClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global hermes_client
    
    # 启动时初始化
    logger.info("初始化 Hermes Bridge Service...")
    hermes_client = HermesClient()
    app.state.hermes_client = hermes_client
    
    yield
    
    # 关闭时清理
    logger.info("关闭 Hermes Bridge Service...")


app = FastAPI(
    title="Hermes Bridge Service",
    description="本地桥接服务，将任务请求转发给 Hermes Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(task.router, prefix="/api", tags=["task"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "hermes-bridge",
        "hermes_available": hermes_client.is_available() if hermes_client else False
    }