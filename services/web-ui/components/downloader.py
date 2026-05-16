"""
Downloader Component
====================

文件下载和上传列表显示组件。
支持结果预览功能 (T03-17~T03-19)。
"""

import streamlit as st
from pathlib import Path
import logging
import pandas as pd
import io

logger = logging.getLogger(__name__)


def preview_file(file_path: Path):
    """T03-17~T03-19: 结果预览组件
    
    根据文件类型提供不同的预览方式：
    - Excel/CSV: 表格预览
    - 图片: 直接显示
    - PDF: 提示下载查看
    - 其他文本: 内容预览
    """
    suffix = file_path.suffix.lower()
    
    # T03-18: Excel/CSV 预览
    if suffix in [".xlsx", ".xls", ".csv"]:
        try:
            if suffix == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # 显示表格预览（限制行数）
            preview_rows = min(len(df), 100)
            st.dataframe(df.head(preview_rows), use_container_width=True)
            
            if len(df) > preview_rows:
                st.caption(f"预览前 {preview_rows} 行，共 {len(df)} 行")
            
            # 显示统计信息
            st.caption(f"📊 行数: {len(df)} | 列数: {len(df.columns)}")
            return True
        except Exception as e:
            st.warning(f"无法预览: {e}")
            return False
    
    # T03-19: 图片预览
    elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        try:
            st.image(file_path, use_container_width=True)
            return True
        except Exception as e:
            st.warning(f"无法预览图片: {e}")
            return False
    
    # PDF 预览提示
    elif suffix == ".pdf":
        st.info("📄 PDF 文件请下载后查看")
        return False
    
    # 文本文件预览
    elif suffix in [".txt", ".md", ".json", ".xml", ".html"]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 限制显示长度
            if len(content) > 5000:
                st.text(content[:5000])
                st.caption(f"预览前 5000 字符，共 {len(content)} 字符")
            else:
                st.text(content)
            return True
        except Exception as e:
            st.warning(f"无法预览: {e}")
            return False
    
    # 其他文件类型
    else:
        st.caption(f"文件类型: {suffix}")
        return False


def show_downloads(session_id: str, data_path: Path):
    """显示会话的输出文件列表和下载按钮
    
    T03-17: 添加预览功能
    """
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
        # 文件信息行
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.text(file_path.name)
        
        with col2:
            size_kb = file_path.stat().st_size / 1024
            st.caption(f"{size_kb:.1f} KB")
        
        with col3:
            # T03-17: 预览按钮
            preview_key = f"preview_{file_path.name}"
            if st.button("👁️", key=preview_key):
                st.session_state[f"show_preview_{file_path.name}"] = True
        
        with col4:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥",
                    data=f,
                    file_name=file_path.name,
                    mime="application/octet-stream",
                    key=f"dl_{file_path.name}"
                )
        
        # T03-17~T03-19: 显示预览内容
        if st.session_state.get(f"show_preview_{file_path.name}"):
            with st.expander(f"📄 预览: {file_path.name}", expanded=True):
                preview_file(file_path)


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
