"""
Excel 智能助手 - Web UI
========================

Streamlit 应用主入口。
"""

import streamlit as st
import os
import uuid
from pathlib import Path

from components.task_runner import TaskRunner, get_task_runner
from components.downloader import show_downloads, show_uploads

# 数据目录
DATA_PATH = Path(os.getenv("SESSION_BASE_PATH", "/app/data/sessions"))

# 页面配置
st.set_page_config(
    page_title="Excel 智能助手",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .session-info {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


def create_session() -> str:
    """创建新会话"""
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    session_path = DATA_PATH / session_id
    (session_path / "uploads").mkdir(parents=True, exist_ok=True)
    (session_path / "outputs").mkdir(parents=True, exist_ok=True)
    return session_id


def init_session_state():
    """初始化会话状态"""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = create_session()
        st.session_state["task_history"] = []
        st.session_state["config"] = {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "model": os.getenv("HERMES_MODEL", "gpt-4")
        }


def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.header("⚙️ LLM 配置")
        
        api_key = st.text_input(
            "API Key",
            value=st.session_state.config.get("api_key", ""),
            type="password",
            key="sidebar_api_key"
        )
        
        base_url = st.text_input(
            "API Base URL",
            value=st.session_state.config.get("base_url", "https://api.openai.com/v1"),
            key="sidebar_base_url"
        )
        
        model = st.text_input(
            "Model",
            value=st.session_state.config.get("model", "gpt-4"),
            key="sidebar_model"
        )
        
        if st.button("保存配置", type="primary"):
            st.session_state.config = {
                "api_key": api_key,
                "base_url": base_url,
                "model": model
            }
            st.success("✅ 配置已保存")
        
        st.divider()
        
        st.header("📋 会话信息")
        st.caption(f"会话 ID: `{st.session_state.session_id}`")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 新建会话"):
                st.session_state.session_id = create_session()
                st.session_state.task_history = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ 清空会话"):
                st.session_state.session_id = create_session()
                st.session_state.task_history = []
                st.rerun()
        
        st.divider()
        
        st.header("❓ 使用帮助")
        with st.expander("查看帮助"):
            st.markdown("""
            **使用步骤：**
            1. 上传 Excel 文件 (.xlsx/.xls)
            2. 输入处理指令
            3. 点击"执行"按钮
            4. 等待处理完成
            5. 下载结果文件
            """)


def show_main_content():
    """显示主内容区"""
    st.title("📊 Excel 智能助手")
    st.markdown("使用自然语言处理 Excel 文件，无需编程知识")
    
    st.caption(f"当前会话: `{st.session_state.session_id}`")
    
    st.divider()
    
    # 文件上传区
    st.header("📁 文件上传")
    uploaded_file = st.file_uploader(
        "上传 Excel 文件",
        type=["xlsx", "xls"],
        help="支持 .xlsx 和 .xls 格式"
    )
    
    if uploaded_file:
        st.success(f"✅ 已选择文件: {uploaded_file.name}")
    
    show_uploads(st.session_state.session_id, DATA_PATH)
    
    st.divider()
    
    # 指令输入区
    st.header("💬 处理指令")
    instruction = st.text_area(
        "输入处理指令",
        placeholder="例如：将第一列数据按升序排序，并添加汇总行",
        height=100
    )
    
    with st.expander("📝 查看示例指令"):
        for example in [
            "将第一列数据按升序排序",
            "删除所有空行",
            "在最后一行添加汇总行",
            "合并工作表 Sheet1 和 Sheet2"
        ]:
            st.code(example, language="text")
    
    st.divider()
    
    # 执行按钮
    col1, col2 = st.columns([2, 1])
    with col1:
        execute_button = st.button(
            "🚀 执行",
            type="primary",
            use_container_width=True,
            disabled=not (uploaded_file and instruction)
        )
    
    with col2:
        clear_button = st.button("🗑️ 清空", use_container_width=True)
    
    # 执行任务
    if execute_button and uploaded_file and instruction:
        task_runner = get_task_runner()
        
        with st.spinner("处理中..."):
            result = task_runner.run_task(
                session_id=st.session_state.session_id,
                uploaded_file=uploaded_file,
                instruction=instruction,
                data_path=DATA_PATH
            )
        
        st.session_state.task_history.append({
            "instruction": instruction,
            "result": result,
            "file_name": uploaded_file.name
        })
        
        if result["success"]:
            st.success("✅ 处理完成!")
            if result.get("output"):
                st.text(result["output"])
        else:
            st.error(f"❌ 处理失败: {result.get('error', '未知错误')}")
    
    if clear_button:
        st.rerun()
    
    st.divider()
    
    # 结果下载区
    st.header("📥 结果下载")
    show_downloads(st.session_state.session_id, DATA_PATH)
    
    st.divider()
    
    # 任务历史
    if st.session_state.task_history:
        st.header("📜 任务历史")
        for i, task in enumerate(reversed(st.session_state.task_history[-5:])):
            with st.expander(f"任务 {len(st.session_state.task_history) - i}: {task['instruction'][:50]}..."):
                st.markdown(f"**文件:** {task['file_name']}")
                st.markdown(f"**状态:** {'✅ 成功' if task['result']['success'] else '❌ 失败'}")


def main():
    """主函数"""
    init_session_state()
    show_sidebar()
    show_main_content()


if __name__ == "__main__":
    main()
