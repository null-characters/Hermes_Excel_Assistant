"""
配置页面
========

环境配置说明与冒烟测试页面。
"""

import streamlit as st
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

st.set_page_config(
    page_title="配置 - Hermes Work Assistant",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ 环境配置")

st.divider()

# 检查 .env 配置
env_path = Path("/app/.env") if Path("/app/.env").exists() else Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY", "")
model = os.getenv("HERMES_MODEL", "")
base_url = os.getenv("OPENAI_BASE_URL", "")

is_configured = bool(api_key and api_key != "your-api-key-here")

# 配置状态 + 冒烟测试
col1, col2 = st.columns([3, 1])

with col1:
    if is_configured:
        st.success("✅ 配置文件已就绪")
        st.markdown(f"- 模型: `{model or '未设置'}`  \n- API URL: `{base_url or '默认'}`")
    else:
        st.error("⚠️ API Key 未配置，请在 `.env` 文件中设置 `OPENAI_API_KEY`")

with col2:
    if st.button("🔍 冒烟测试", type="primary", disabled=not is_configured, use_container_width=True):
        bridge_url = os.getenv("BRIDGE_API_URL", "http://localhost:8646")

        with st.spinner("正在测试 LLM 连接..."):
            try:
                resp = requests.get(f"{bridge_url}/api/smoke-test", timeout=60)
                result = resp.json()

                if result.get("success"):
                    st.session_state.smoke_result = ("success", f"✅ 测试通过 - 模型: {result.get('model', '')}")
                else:
                    st.session_state.smoke_result = ("error", f"❌ {result.get('error', '测试失败')}: {result.get('detail', '')}")
            except requests.exceptions.ConnectionError:
                st.session_state.smoke_result = ("error", "❌ 无法连接到 Bridge 服务，请确保服务已启动")
            except Exception as e:
                st.session_state.smoke_result = ("error", f"❌ 测试异常: {e}")

# 显示测试结果
if "smoke_result" in st.session_state:
    status, msg = st.session_state.smoke_result
    if status == "success":
        st.success(msg)
    else:
        st.error(msg)

st.divider()

st.markdown("""
### 配置说明

所有配置通过项目根目录的 `.env` 文件管理，**请勿在页面上修改配置**。

#### 必填项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | LLM API 密钥 | `sk-xxxxx` |
| `HERMES_MODEL` | 模型名称 | `glm-5` |

#### 可选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.openai.com/v1` |
| `TERMINAL_NETWORK_DISABLED` | 禁用 Agent 网络访问 | `true` |
| `TERMINAL_TIMEOUT` | 任务执行超时（秒） | `300` |

#### 配置步骤

1. 在项目根目录创建或编辑 `.env` 文件
2. 填写 `OPENAI_API_KEY=你的API密钥`
3. 填写 `HERMES_MODEL=模型名称`
4. 重启服务：`docker compose restart`
5. 点击上方"冒烟测试"按钮验证配置
""")
