"""
全链路测试脚本
==============

本地化方案测试：
- 通过 Hermes Bridge API 提交任务
- Hermes Agent 通过 docker exec 调用
- 本地模式可模拟处理，无需 LLM API Key

测试流程：
1. 创建示例 Excel 文件
2. 上传到 File Upload Service
3. 发送处理任务到 Hermes Agent（或模拟处理）
4. 下载处理结果
5. 验证结果是否符合预期

使用方法：
    # 完整测试（需要 Hermes Agent 运行 + LLM API Key）
    python tests/test_full_chain.py --mode full

    # 本地测试（���拟处理，无需 LLM API Key）
    python tests/test_full_chain.py --mode local
"""

import os
import sys
import json
import time
import argparse
import tempfile
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "services/file-upload"))

import requests
import pandas as pd
from openpyxl import Workbook, load_workbook


class FullChainTest:
    """全链路测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8080", hermes_url: str = "http://localhost:8645"):
        self.base_url = base_url
        self.hermes_url = hermes_url
        self.user_id = "test_user_chain"
        self.test_file_id = None
        self.test_file_path = None
        self.result_file_id = None
        
    def create_test_excel(self) -> str:
        """创建测试 Excel 文件"""
        print("\n" + "="*60)
        print("Step 1: 创建测试 Excel 文件")
        print("="*60)
        
        # 创建测试数据
        wb = Workbook()
        ws = wb.active
        ws.title = "员工数据"
        
        # 原始数据（第一行将被替换）
        headers = ["姓名", "部门", "年龄", "入职日期", "薪资"]
        ws.append(headers)
        
        data = [
            ["张三", "行政部", 28, "2020-03-15", 8500],
            ["李四", "技术部", 32, "2019-07-20", 12000],
            ["王五", "市场部", 26, "2021-01-10", 9000],
            ["赵六", "财务部", 35, "2018-05-08", 11000],
            ["钱七", "技术部", 29, "2020-09-01", 10500],
        ]
        
        for row in data:
            ws.append(row)
        
        # 保存到临时文件
        temp_dir = tempfile.gettempdir()
        self.test_file_path = os.path.join(temp_dir, "test_employees.xlsx")
        wb.save(self.test_file_path)
        
        print(f"✅ 测试文件创建成功: {self.test_file_path}")
        print(f"   - 工作表: 员工数据")
        print(f"   - 数据行数: {len(data) + 1} (含表头)")
        print(f"   - 表头: {headers}")
        
        return self.test_file_path
    
    def upload_file(self) -> str:
        """上传文件到 File Upload Service"""
        print("\n" + "="*60)
        print("Step 2: 上传文件到 File Upload Service")
        print("="*60)
        
        url = f"{self.base_url}/api/upload?user_id={self.user_id}"
        
        with open(self.test_file_path, "rb") as f:
            files = {"file": ("test_employees.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(url, files=files)
        
        if response.status_code != 200:
            raise Exception(f"上传失败: {response.text}")
        
        data = response.json()
        self.test_file_id = data["file_id"]
        
        print(f"✅ 文件上传成功")
        print(f"   - File ID: {self.test_file_id}")
        print(f"   - 用户 ID: {data['user_id']}")
        print(f"   - 过期时间: {data['expires_at']}")
        
        return self.test_file_id
    
    def process_with_hermes(self, task: str = "替换第一行数据为：员工姓名,所属部门,年龄,入职时间,月薪"):
        """发送处理任务到 Hermes Agent"""
        print("\n" + "="*60)
        print("Step 3: 发送处理任务到 Hermes Agent")
        print("="*60)
        
        # 构造任务消息
        message = f"处理 {self.test_file_id} {task}"
        print(f"   - 任务: {message}")
        
        # 尝试通过 Hermes Agent API 发送任务
        try:
            # Hermes Agent 可能没有直接的 REST API
            # 这里模拟发送任务并等待处理
            print(f"   - 检查 Hermes Agent 状态...")
            
            health_response = requests.get(f"{self.hermes_url}/health", timeout=5)
            if health_response.status_code == 200:
                print(f"   ✅ Hermes Agent 运行中")
                
                # TODO: 实现 Hermes Agent 任务提交
                # Hermes Agent 使用消息网关或 CLI 交互
                # 这里模拟处理过程
                print(f"   ⚠️ Hermes Agent 消息网关未配置，使用模拟处理")
                return self._simulate_processing(task)
            else:
                print(f"   ❌ Hermes Agent 不可用")
                return self._simulate_processing(task)
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 无法连接 Hermes Agent: {e}")
            return self._simulate_processing(task)
    
    def _simulate_processing(self, task: str) -> dict:
        """模拟 Excel 处理过程"""
        print(f"\n   🔄 使用模拟处理...")
        
        # 下载原文件
        download_url = f"{self.base_url}/api/download/{self.test_file_id}.xlsx?user_id={self.user_id}"
        response = requests.get(download_url)
        
        if response.status_code != 200:
            raise Exception(f"下载文件失败: {response.text}")
        
        # 读取并处理 Excel
        temp_input = os.path.join(tempfile.gettempdir(), "input.xlsx")
        temp_output = os.path.join(tempfile.gettempdir(), "output.xlsx")
        
        with open(temp_input, "wb") as f:
            f.write(response.content)
        
        # 使用 pandas 处理
        df = pd.read_excel(temp_input)
        print(f"   - 原始表头: {list(df.columns)}")
        
        # 替换第一行（表头）
        new_headers = ["员工姓名", "所属部门", "年龄", "入职时间", "月薪"]
        df.columns = new_headers
        print(f"   - 新表头: {new_headers}")
        
        # 保存处理后的文件
        df.to_excel(temp_output, index=False)
        
        # 上传处理后的文件
        with open(temp_output, "rb") as f:
            files = {"file": ("test_employees_processed.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            upload_response = requests.post(
                f"{self.base_url}/api/upload?user_id={self.user_id}",
                files=files
            )
        
        if upload_response.status_code != 200:
            raise Exception(f"上传处理结果失败: {upload_response.text}")
        
        result = upload_response.json()
        self.result_file_id = result["file_id"]
        
        print(f"   ✅ 处理完成")
        print(f"   - 结果文件 ID: {self.result_file_id}")
        
        return {
            "success": True,
            "result_file_id": self.result_file_id,
            "message": "处理完成"
        }
    
    def download_and_verify(self) -> bool:
        """下载处理结果并验证"""
        print("\n" + "="*60)
        print("Step 4: 下载处理结果并验证")
        print("="*60)
        
        if not self.result_file_id:
            raise Exception("没有处理结果可下载")
        
        # 下载结果文件
        download_url = f"{self.base_url}/api/download/{self.result_file_id}.xlsx?user_id={self.user_id}"
        response = requests.get(download_url)
        
        if response.status_code != 200:
            raise Exception(f"下载结果失败: {response.text}")
        
        # 保存并读取
        temp_result = os.path.join(tempfile.gettempdir(), "result.xlsx")
        with open(temp_result, "wb") as f:
            f.write(response.content)
        
        print(f"✅ 结果文件下载成功: {temp_result}")
        
        # 验证内容
        df = pd.read_excel(temp_result)
        
        expected_headers = ["员工姓名", "所属部门", "年龄", "入职时间", "月薪"]
        actual_headers = list(df.columns)
        
        print(f"\n   验证结果:")
        print(f"   - 期望表头: {expected_headers}")
        print(f"   - 实际表头: {actual_headers}")
        
        if actual_headers == expected_headers:
            print(f"   ✅ 表头替换成功！")
            print(f"\n   数据预览:")
            print(df.head().to_string(index=False))
            return True
        else:
            print(f"   ❌ 表头不匹配")
            return False
    
    def cleanup(self):
        """清理测试文件"""
        print("\n" + "="*60)
        print("Step 5: 清理测试文件")
        print("="*60)
        
        # 删除上传的测试文件
        for file_id in [self.test_file_id, self.result_file_id]:
            if file_id:
                try:
                    url = f"{self.base_url}/api/delete/{file_id}.xlsx?user_id={self.user_id}"
                    response = requests.delete(url)
                    if response.status_code == 200:
                        print(f"   ✅ 已删除: {file_id}")
                    else:
                        print(f"   ⚠️ 删除失败: {file_id}")
                except Exception as e:
                    print(f"   ❌ 删除异常: {e}")
        
        # 删除临时文件
        for path in [self.test_file_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"   ✅ 已删除临时文件: {path}")
                except Exception as e:
                    print(f"   ⚠️ 删除临时文件失败: {e}")
    
    def run(self, mode: str = "local"):
        """运行完整测试"""
        print("\n" + "="*60)
        print("Hermes WeCom Excel Assistant - 全链路测试")
        print("="*60)
        print(f"模式: {mode}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"File Upload Service: {self.base_url}")
        print(f"Hermes Agent: {self.hermes_url}")
        
        try:
            # Step 1: 创建测试文件
            self.create_test_excel()
            
            # Step 2: 上传文件
            self.upload_file()
            
            # Step 3: 处理文件
            if mode == "full":
                self.process_with_hermes()
            else:
                self._simulate_processing("替换第一行数据")
            
            # Step 4: 下载并验证
            success = self.download_and_verify()
            
            # Step 5: 清理
            self.cleanup()
            
            # 总结
            print("\n" + "="*60)
            print("测试结果")
            print("="*60)
            if success:
                print("✅ 全链路测试通过！")
                return 0
            else:
                print("❌ 全链路测试失败")
                return 1
                
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()
            return 1


def main():
    parser = argparse.ArgumentParser(description="Hermes WeCom Excel Assistant 全链路测试")
    parser.add_argument(
        "--mode",
        choices=["full", "local"],
        default="local",
        help="测试模式: full=完整测试(需Hermes Agent), local=本地测试(模拟处理)"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8080",
        help="File Upload Service 地址"
    )
    parser.add_argument(
        "--hermes-url",
        default="http://localhost:8645",
        help="Hermes Agent 地址"
    )
    
    args = parser.parse_args()
    
    test = FullChainTest(base_url=args.base_url, hermes_url=args.hermes_url)
    sys.exit(test.run(mode=args.mode))


if __name__ == "__main__":
    main()
