"""
Downloader Component
====================

文件下载和上传列表显示组件。
"""

import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def show_downloads(session_id: str, data_path: Path):
    """显示会话的输出文件列表和下载按钮"""
    outputs_path = data_path / session_id / "outputs"
    
    if not outputs_path.exists():
        st.info("暂无输出文件")
        return
    
    output_files = list(outputs_path.iterdir())
    
    if not output_files:
        st.info("暂无输出文件")
        return
    
    st.markdown(f"**输出文件 ({len(output_files)} 个):**")
    
    for file_path in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.text(file_path.name)
        
        with col2:
            size_kb = file_path.stat().st_size / 1024
            st.caption(f"{size_kb:.1f} KB")
        
        with col3:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥",
                    data=f,
                    file_name=file_path.name,
                    mime="application/octet-stream",
                    key=f"dl_{file_path.name}"
                )


def show_uploads(session_id: str, data_path: Path):
    """显示会话的上传文件列表"""
    uploads_path = data_path / session_id / "uploads"
    
    if not uploads_path.exists():
        return
    
    upload_files = list(uploads_path.iterdir())
    
    if not upload_files:
        return
    
    st.markdown(f"**已上传文件 ({len(upload_files)} 个):**")
    
    for file_path in sorted(upload_files, key=lambda x: x.stat().st_mtime, reverse=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.text(file_path.name)
        
        with col2:
            size_kb = file_path.stat().st_size / 1024
            st.caption(f"{size_kb:.1f} KB")
