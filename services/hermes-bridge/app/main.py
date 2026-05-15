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


@app.get("/api/smoke-test")
async def smoke_test():
    """
    冒烟测试 - 验证 LLM API 是否可用

    发送简单提示词测试 LLM 连接是否正常
    """
    import os

    # 检查环境变量是否配置
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("HERMES_MODEL", "")

    if not api_key or api_key == "your-api-key-here":
        return {
            "success": False,
            "error": "API Key 未配置",
            "detail": "请在 .env 文件中设置 OPENAI_API_KEY"
        }

    if not model:
        return {
            "success": False,
            "error": "模型未配置",
            "detail": "请在 .env 文件中设置 HERMES_MODEL"
        }

    # 检查 Hermes Agent 是否可用
    if not hermes_client or not hermes_client.is_available():
        return {
            "success": False,
            "error": "Hermes Agent 不可用",
            "detail": "请确保 hermes-agent 容器正在运行"
        }

    # 执行简单测试
    try:
        response = await hermes_client.execute_task(
            prompt="请回复'OK'两个字符，不要输出其他内容。",
            timeout=30
        )

        if response.success:
            # 提取实际响应内容（过滤 Hermes 日志）
            output = response.output or ""
            # 查找实际响应内容（通常是最后一行非空内容）
            lines = [l.strip() for l in output.split('\n') if l.strip()]
            actual_response = "OK"
            for line in reversed(lines):
                # 跳过 Hermes 日志行
                if any(skip in line for skip in ['Query:', 'Initializing', 'API call', 'Token', 'Conversation', 'Hermes', '─', '╭', '╰', '┊', '│']):
                    continue
                if line and not line.startswith(('┊', '│', '╭', '╰', '─')):
                    actual_response = line[:50]
                    break

            return {
                "success": True,
                "model": model,
                "response": actual_response
            }
        else:
            return {
                "success": False,
                "error": "LLM 调用失败",
                "detail": response.error or response.message
            }
    except Exception as e:
        return {
            "success": False,
            "error": "测试异常",
            "detail": str(e)
        }