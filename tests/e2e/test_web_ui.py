"""
Web UI E2E 测试
===============

测试 Excel 智能助手 Web UI 的完整用户流程。
"""

import asyncio
from playwright.async_api import async_playwright
import time


async def test_web_ui_flow():
    """测试 Web UI 完整流程"""
    
    print("🚀 启动 Web UI E2E 测试...")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. 访问 Web UI
            print("\n📍 Step 1: 访问 Web UI")
            await page.goto("http://localhost:8501", wait_until="networkidle")
            await page.wait_for_timeout(3000)  # Streamlit 初始化需要时间
            
            # 检查页面标题
            title = await page.title()
            print(f"   页面标题: {title}")
            
            # 检查主标题
            h1 = await page.locator("h1").first.text_content()
            print(f"   主标题: {h1}")
            assert "Excel" in h1, "页面标题应包含 Excel"
            print("   ✅ 页面加载成功")
            
            # 2. 检查会话 ID 显示
            print("\n📍 Step 2: 检查会话 ID")
            session_caption = await page.locator("p.caption").first.text_content()
            print(f"   {session_caption}")
            assert "sess_" in session_caption, "应显示会话 ID"
            print("   ✅ 会话已创建")
            
            # 3. 检查文件上传组件
            print("\n📍 Step 3: 检查文件上传组件")
            file_uploader = page.locator("input[type='file']")
            await file_uploader.wait_for(state="visible", timeout=10000)
            print("   ✅ 文件上传组件可见")
            
            # 4. 检查指令输入框
            print("\n📍 Step 4: 检查指令输入框")
            textarea = page.locator("textarea").first
            await textarea.wait_for(state="visible", timeout=5000)
            placeholder = await textarea.get_attribute("placeholder")
            print(f"   Placeholder: {placeholder}")
            print("   ✅ 指令输入框可见")
            
            # 5. 检查执行按钮
            print("\n📍 Step 5: 检查执行按钮")
            execute_btn = page.locator("button").filter(has_text="执行")
            await execute_btn.wait_for(state="visible", timeout=5000)
            # 检查按钮是否禁用（因为没有上传文件）
            is_disabled = await execute_btn.is_disabled()
            print(f"   执行按钮禁用状态: {is_disabled}")
            assert is_disabled, "无文件时执行按钮应禁用"
            print("   ✅ 执行按钮状态正确")
            
            # 6. 检查侧边栏
            print("\n📍 Step 6: 检查侧边栏")
            sidebar = page.locator("[data-testid='stSidebar']")
            await sidebar.wait_for(state="visible", timeout=5000)
            
            # 检查 LLM 配置
            api_key_input = sidebar.locator("input[type='password']").first
            await api_key_input.wait_for(state="visible", timeout=5000)
            print("   ✅ API Key 输入框可见")
            
            # 检查新建会话按钮
            new_session_btn = sidebar.locator("button").filter(has_text="新建会话")
            await new_session_btn.wait_for(state="visible", timeout=5000)
            print("   ✅ 新建会话按钮可见")
            
            # 7. 检查帮助信息
            print("\n📍 Step 7: 检查帮助信息")
            help_expander = sidebar.locator("[data-testid='stExpander']").first
            await help_expander.click()
            await page.wait_for_timeout(500)
            help_content = await help_expander.locator(".element-container").first.text_content()
            print(f"   帮助内容: {help_content[:50]}...")
            print("   ✅ 帮助信息可展开")
            
            # 8. 检查示例指令
            print("\n📍 Step 8: 检查示例指令")
            example_expander = page.locator("[data-testid='stExpander']").filter(has_text="示例指令")
            await example_expander.click()
            await page.wait_for_timeout(500)
            examples = await example_expander.locator("code").all_text_contents()
            print(f"   示例数量: {len(examples)}")
            for ex in examples[:3]:
                print(f"   - {ex}")
            print("   ✅ 示例指令可展开")
            
            print("\n" + "="*50)
            print("🎉 所有 UI 组件检查通过！")
            print("="*50)
            
            # 汇总结果
            results = {
                "页面加载": "✅",
                "会话创建": "✅",
                "文件上传组件": "✅",
                "指令输入框": "✅",
                "执行按钮状态": "✅",
                "侧边栏配置": "✅",
                "帮助信息": "✅",
                "示例指令": "✅"
            }
            
            print("\n📊 测试结果汇总:")
            for test, status in results.items():
                print(f"   {status} {test}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            # 截图保存
            await page.screenshot(path="/tmp/web_ui_error.png")
            print("   截图已保存: /tmp/web_ui_error.png")
            raise
            
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_web_ui_flow())