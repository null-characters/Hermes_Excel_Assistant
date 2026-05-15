# Phase 3: 结果预览

> **阶段**: Phase 3 - 结果预览线 (Day 3 下午)
> **目标**: Web UI 内嵌结果预览，无需下载即可查看处理结果
> **依赖**: T03-05（多文件上传完成）
> **评审来源**: 实现评审分析 B-08（结果预览，P2 提前到 P1）

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T03-16 | 实现结果文件解析 | 支持 xlsx/csv 文件解析为 DataFrame | 解析结果可用于渲染 |  | 30min |
| T03-17 | Web UI 内嵌表格预览 | 使用 st.dataframe 渲染处理结果 | 表格正确显示，支持排序 |  | 45min |
| T03-18 | 预览与下载联动 | 预览区域提供下载按钮 | 点击下载获取原始文件 |  | 15min |
| T03-19 | 预览功能测试 | 编写预览功能测试 | 测试通过 |  | 30min |

---

## 实现方案

### T03-16: 文件解析

```python
# services/session_manager/preview.py (新增)
import pandas as pd

def parse_result_file(filepath: str) -> pd.DataFrame:
    """解析结果文件为 DataFrame"""
    ext = Path(filepath).suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(filepath)
    elif ext == ".csv":
        return pd.read_csv(filepath)
    else:
        raise ValueError(f"Preview not supported for {ext}")
```

### T03-17: 内嵌预览

```python
# web-ui/app.py 修改
# 任务完成后显示预览
if result_path:
    df = parse_result_file(result_path)
    st.subheader("📊 结果预览")
    st.dataframe(df, use_container_width=True, height=300)
```

### T03-18: 预览+下载联动

```python
# 预览区域下方提供下载
col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 下载结果", data, file_name=filename)
with col2:
    st.download_button("📦 下载全部", zip_data, file_name="results.zip")
```

---

## 验收清单

- [ ] xlsx/csv 文件可解析为 DataFrame
- [ ] Web UI 正确渲染表格预览
- [ ] 预览区域提供下载按钮
- [ ] 测试通过

---

## 关键文件

```
services/session_manager/
└── preview.py              # T03-16: 新增

services/web-ui/app.py      # T03-17, T03-18: 预览组件

tests/test_preview.py       # T03-19: 新增
```

---

## 限制说明

| 文件格式 | 预览支持 | 说明 |
|----------|----------|------|
| .xlsx | ✅ | pandas read_excel |
| .xls | ✅ | pandas read_excel |
| .csv | ✅ | pandas read_csv |
| .json | ⚠️ | 仅显示原始文本 |
| 其他 | ❌ | 仅提供下载 |
