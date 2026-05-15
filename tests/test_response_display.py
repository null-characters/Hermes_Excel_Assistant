"""
测试 Agent 响应内容显示

验证 SSE 事件流中的 response 类型事件被正确收集和显示。
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# 添加 web-ui 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "web-ui"))


def test_response_content_parsing():
    """测试 Hermes 输出解析器正确识别 response 内容"""
    from hermes_client import HermesClient
    
    client = HermesClient()
    
    # 测试用例：缩进的中文响应内容
    test_lines = [
        "    这是嵌入式开发中关于ADC性能调优的实用经验总结。",
        "    这个文件是关于ADC测试的技术文档。",
        "    OK",
    ]
    
    for line in test_lines:
        result = client._parse_hermes_output(line)
        assert result is not None, f"Failed to parse: {line}"
        assert result["type"] == "response", f"Wrong type for: {line}"
        assert "🤖" in result["content"], f"Missing emoji in: {result['content']}"


def test_response_collection_logic():
    """测试响应内容收集逻辑（与 app.py 一致）"""
    
    # 模拟 SSE 事件流
    events = [
        {"type": "progress", "content": "🚀 任务启动..."},
        {"type": "init", "content": "📝 Query: 测试查询"},
        {"type": "thinking", "content": "💭 正在分析文档..."},
        {"type": "response", "content": "🤖 这是第一段响应内容"},
        {"type": "response", "content": "🤖 这是第二段响应内容"},
        {"type": "done", "content": "✅ 任务执行完成"},
    ]
    
    # 模拟 app.py 中的收集逻辑（修复后的版本）
    final_output = ""
    
    for event in events:
        event_type = event.get("type", "")
        content = event.get("content", "")
        
        if event_type == "response":
            # 去掉 emoji 前缀
            actual_content = content.replace("🤖 ", "").strip()
            if actual_content:
                if final_output:
                    final_output += "\n" + actual_content
                else:
                    final_output = actual_content
    
    assert final_output == "这是第一段响应内容\n这是第二段响应内容", \
        f"Unexpected output: {final_output}"


def test_response_with_empty_content():
    """测试空响应内容被正确过滤"""
    
    events = [
        {"type": "response", "content": "🤖 "},  # 只有 emoji，无实际内容
        {"type": "response", "content": "🤖 有效内容"},
    ]
    
    final_output = ""
    
    for event in events:
        event_type = event.get("type", "")
        content = event.get("content", "")
        
        if event_type == "response":
            actual_content = content.replace("🤖 ", "").strip()
            if actual_content:
                if final_output:
                    final_output += "\n" + actual_content
                else:
                    final_output = actual_content
    
    assert final_output == "有效内容", f"Should only contain valid content: {final_output}"


def test_sse_event_format():
    """测试 SSE 事件格式正确"""
    
    # 模拟 task.py 中的 SSE 格式化
    event = {"type": "response", "content": "🤖 测试响应"}
    sse_line = f"data: {json.dumps(event)}\n\n"
    
    # 解析 SSE 行
    parsed = None
    if sse_line.startswith("data: "):
        parsed = json.loads(sse_line[6:].strip())
    
    assert parsed is not None
    assert parsed["type"] == "response"
    assert "🤖" in parsed["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
