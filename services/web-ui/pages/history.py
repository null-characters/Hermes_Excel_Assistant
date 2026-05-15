"""
历史记录页面
============

会话历史和任务记录。
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="历史记录 - Hermes Work Assistant",
    page_icon="📜",
    layout="wide"
)

st.title("📜 历史记录")

st.markdown("查看所有会话和任务执行历史")

st.divider()

from session_manager import get_session_manager

session_manager = get_session_manager()
sessions = session_manager.list_sessions()

if not sessions:
    st.info("暂无会话记录")
else:
    st.markdown(f"**共 {len(sessions)} 个会话**")
    
    for session_id in sessions:
        info = session_manager.get_session_info(session_id)
        if info is None:
            continue
        
        with st.expander(f"📋 {session_id}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("上传文件", info.get("upload_count", 0))
            with col2:
                st.metric("输出文件", info.get("output_count", 0))
            with col3:
                st.metric("任务数", info.get("task_count", 0))
            
            # 列出输出文件
            outputs_path = session_manager.get_outputs_path(session_id)
            if outputs_path.exists():
                output_files = list(outputs_path.iterdir())
                if output_files:
                    st.markdown("**输出文件：**")
                    for f in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True):
                        st.text(f"  {f.name} ({f.stat().st_size / 1024:.1f} KB)")
