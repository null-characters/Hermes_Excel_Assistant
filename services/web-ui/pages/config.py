"""
配置页面
========

LLM 配置管理页面。
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

st.set_page_config(
    page_title="配置 - Hermes Work Assistant",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ LLM 配置")

st.markdown("""
配置 LLM API 参数。配置将保存到 `.env` 文件中。
""")

st.divider()

# 加载现有配置
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# 配置表单
with st.form("llm_config"):
    st.subheader("API 配置")
    
    api_key = st.text_input(
        "API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="LLM API 密钥"
    )
    
    base_url = st.text_input(
        "API Base URL",
        value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        help="API 基础 URL"
    )
    
    model = st.text_input(
        "Model",
        value=os.getenv("HERMES_MODEL", "gpt-4"),
        help="模型名称"
    )
    
    st.divider()
    
    st.subheader("安全配置")
    
    network_disabled = st.checkbox(
        "禁用网络访问",
        value=os.getenv("TERMINAL_NETWORK_DISABLED", "true").lower() == "true",
        help="禁止 Agent 访问网络"
    )
    
    timeout = st.number_input(
        "执行超时 (秒)",
        min_value=60,
        max_value=600,
        value=int(os.getenv("TERMINAL_TIMEOUT", "300")),
        help="任务执行超时时间"
    )
    
    submitted = st.form_submit_button("保存配置", type="primary")

if submitted:
    # 保存到 .env 文件
    if not env_path.exists():
        env_path.touch()
    
    set_key(str(env_path), "OPENAI_API_KEY", api_key)
    set_key(str(env_path), "OPENAI_BASE_URL", base_url)
    set_key(str(env_path), "HERMES_MODEL", model)
    set_key(str(env_path), "TERMINAL_NETWORK_DISABLED", str(network_disabled).lower())
    set_key(str(env_path), "TERMINAL_TIMEOUT", str(timeout))
    
    st.success("✅ 配置已保存到 .env 文件")
    st.info("⚠️ 需要重启服务才能生效")

# 显示当前配置
st.divider()
st.subheader("当前配置文件")

if env_path.exists():
    with open(env_path, "r") as f:
        content = f.read()
    
    # 隐藏敏感信息
    lines = content.split("\n")
    safe_lines = []
    for line in lines:
        if "API_KEY" in line and "=" in line:
            key, value = line.split("=", 1)
            safe_lines.append(f"{key}=***HIDDEN***")
        else:
            safe_lines.append(line)
    
    st.code("\n".join(safe_lines), language="bash")
else:
    st.warning(".env 文件不存在")
