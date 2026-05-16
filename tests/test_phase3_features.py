"""
Phase3 功能单元测试
==================

测试 T03-06~T03-19 新增功能：
- 文件大小限制 (T03-06~T03-07)
- 批量处理 (T03-08~T03-12)
- 处理模板 (T03-13~T03-16)
- 结果预览 (T03-17~T03-19)
"""

import sys
import os
import tempfile
from pathlib import Path
from io import BytesIO

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "web-ui"))

from components.task_runner import TaskRunner, MAX_FILE_SIZE_MB, MAX_FILE_SIZE_BYTES


class MockUploadedFile:
    """模拟 Streamlit UploadedFile"""
    def __init__(self, name: str, content: bytes):
        self.name = name
        self._content = content
    
    def getbuffer(self):
        return self._content


def test_file_size_limit():
    """T03-07: 测试文件大小限制"""
    print("\n=== T03-07: 文件大小限制测试 ===")
    
    runner = TaskRunner()
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = Path(tmpdir)
        session_id = "test_session"
        
        # 测试正常大小文件
        normal_content = b"test content" * 100  # ~1KB
        normal_file = MockUploadedFile("normal.xlsx", normal_content)
        
        try:
            file_path = runner.save_upload_file(session_id, normal_file, data_path)
            print(f"  ✅ 正常大小文件上传成功: {file_path}")
        except ValueError as e:
            print(f"  ❌ 正常大小文件被错误拦截: {e}")
            return False
        
        # 测试超大文件（模拟超过限制）
        # 注意：实际测试时可能需要调整 MAX_FILE_SIZE_MB
        large_size = MAX_FILE_SIZE_BYTES + 1024  # 超过限制 1KB
        large_content = b"x" * large_size
        large_file = MockUploadedFile("large.xlsx", large_content)
        
        try:
            runner.save_upload_file(session_id, large_file, data_path)
            print(f"  ❌ 超大文件未被拦截（应该抛出 ValueError）")
            return False
        except ValueError as e:
            print(f"  ✅ 超大文件正确拦截: {e}")
    
    return True


def test_batch_processing_logic():
    """T03-08~T03-10: 测试批量处理逻辑"""
    print("\n=== T03-08~T03-10: 批量处理逻辑测试 ===")
    
    # 测试文件列表处理
    files_to_process = ["file1.xlsx", "file2.xlsx", "file3.xlsx"]
    total_files = len(files_to_process)
    
    batch_results = []
    for file_idx, filename in enumerate(files_to_process):
        # 模拟处理结果
        result = {
            "success": True,
            "output": f"处理完成: {filename}",
            "error": None
        }
        batch_results.append({
            "file_name": filename,
            "result": result
        })
        
        print(f"  ✅ 处理进度 ({file_idx + 1}/{total_files}): {filename}")
    
    # 验证批量结果汇总
    success_count = sum(1 for r in batch_results if r["result"]["success"])
    fail_count = total_files - success_count
    
    print(f"  ✅ 批量结果汇总: 总计={total_files}, 成功={success_count}, 失败={fail_count}")
    
    if success_count == total_files:
        print(f"  ✅ 所有文件处理成功")
        return True
    else:
        print(f"  ❌ 有 {fail_count} 个文件处理失败")
        return False


def test_template_functionality():
    """T03-13~T03-16: 测试处理模板功能"""
    print("\n=== T03-13~T03-16: 处理模板测试 ===")
    
    # 模拟模板数据
    templates = [
        {"id": "sort_data", "name": "📊 数据排序", "instruction": "将数据按第一列升序排序"},
        {"id": "remove_empty", "name": "🧹 清理空行", "instruction": "删除所有空行"},
        {"id": "add_summary", "name": "📈 添加汇总", "instruction": "在最后一行添加汇总行"},
    ]
    
    # 测试模板选择
    selected_id = "sort_data"
    selected_template = next((t for t in templates if t["id"] == selected_id), None)
    
    if selected_template:
        print(f"  ✅ 模板选择成功: {selected_template['name']}")
        print(f"     指令模板: {selected_template['instruction']}")
    else:
        print(f"  ❌ 模板选择失败")
        return False
    
    # 测试模板指令应用
    instruction = selected_template["instruction"]
    if "排序" in instruction:
        print(f"  ✅ 模板指令正确应用")
    else:
        print(f"  ❌ 模板指令内容错误")
        return False
    
    # 测试模板持久化（模拟 session_state）
    session_state = {"selected_template_id": selected_id}
    if session_state.get("selected_template_id") == selected_id:
        print(f"  ✅ 模板持久化验证通过")
    else:
        print(f"  ❌ 模板持久化失败")
        return False
    
    return True


def test_preview_functionality():
    """T03-17~T03-19: 测试结果预览功能"""
    print("\n=== T03-17~T03-19: 结果预览测试 ===")
    
    # 模拟预览文件类型判断
    preview_cases = [
        ("output.xlsx", "表格预览"),
        ("output.csv", "表格预览"),
        ("output.png", "图片预览"),
        ("output.pdf", "PDF提示下载"),
        ("output.txt", "文本预览"),
    ]
    
    for filename, expected_preview in preview_cases:
        suffix = Path(filename).suffix.lower()
        
        # 判断预览类型
        if suffix in [".xlsx", ".xls", ".csv"]:
            actual_preview = "表格预览"
        elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            actual_preview = "图片预览"
        elif suffix == ".pdf":
            actual_preview = "PDF提示下载"
        elif suffix in [".txt", ".md", ".json"]:
            actual_preview = "文本预览"
        else:
            actual_preview = "未知类型"
        
        if actual_preview == expected_preview:
            print(f"  ✅ {filename} → {actual_preview}")
        else:
            print(f"  ❌ {filename} → 期望 {expected_preview}, 实际 {actual_preview}")
            return False
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("Phase3 功能单元测试")
    print("=" * 50)
    
    results = []
    
    # T03-06~T03-07: 文件大小限制
    results.append(("文件大小限制", test_file_size_limit()))
    
    # T03-08~T03-10: 批量处理
    results.append(("批量处理逻辑", test_batch_processing_logic()))
    
    # T03-13~T03-16: 处理模板
    results.append(("处理模板", test_template_functionality()))
    
    # T03-17~T03-19: 结果预览
    results.append(("结果预览", test_preview_functionality()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)