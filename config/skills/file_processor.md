# 文件处理技能规范

## 技能名称
file_processor

## 描述
处理各种文件的操作，包括数据清洗、汇总、分析、格式转换、内容提取等。支持 Excel、Word、PPT、PDF、CSV、JSON、TXT、图片等多种格式。

## 适用场景
- **Excel 处理**: 数据清洗、汇总、分析、格式转换
- **Word 处理**: 内容提取、格式转换、批量修改
- **PPT 处理**: 幻灯片提取、内容替换、格式转换
- **PDF 处理**: 文本提取、内容分析
- **数据文件**: CSV/JSON/XML 解析、转换、合并
- **文本文件**: 内容分析、格式化、编码转换
- **图片处理**: 格式转换、尺寸调整、信息提取

## 支持的文件格式

| 类型 | 扩展名 | 处理库 |
|------|--------|--------|
| Excel | .xlsx, .xls | pandas, openpyxl |
| Word | .docx, .doc | python-docx |
| PPT | .pptx, .ppt | python-pptx |
| PDF | .pdf | PyPDF2, pdfplumber |
| 数据 | .csv, .json, .xml | pandas, json, xml |
| 文本 | .txt | 标准库 |
| 图片 | .png, .jpg, .gif, .webp | Pillow |

## 技术规范

### 库使用优先级
1. **pandas** - 首选，用于表格数据处理
2. **openpyxl** - 用于 Excel 样式操作
3. **python-docx** - 用于 Word 文档
4. **python-pptx** - 用于 PPT 演示文稿
5. **PyPDF2/pdfplumber** - 用于 PDF 处理
6. **Pillow** - 用于图片处理

### Excel 处理示例

```python
import pandas as pd
from datetime import datetime

# 读取 Excel
df = pd.read_excel('input.xlsx')

# 处理数据
# ... 业务逻辑 ...

# 输出文件
df.to_excel('result.xlsx', index=False)
```

### Word 处理示例

```python
from docx import Document

# 读取 Word
doc = Document('input.docx')

# 提取文本
text = '\n'.join([para.text for para in doc.paragraphs])

# 输出
with open('result.txt', 'w') as f:
    f.write(text)
```

### PDF 处理示例

```python
import pdfplumber

# 读取 PDF
with pdfplumber.open('input.pdf') as pdf:
    text = ''
    for page in pdf.pages:
        text += page.extract_text() or ''

# 输出
with open('result.txt', 'w') as f:
    f.write(text)
```

### CSV/JSON 处理示例

```python
import pandas as pd
import json

# CSV 处理
df = pd.read_csv('input.csv')
df.to_json('result.json', orient='records')

# JSON 处理
with open('input.json') as f:
    data = json.load(f)
```

### 输出格式选择

根据任务需求选择合适的输出格式：
- 表格数据 → Excel (.xlsx) 或 CSV (.csv)
- 结构化数据 → JSON (.json)
- 文本内容 → TXT (.txt)
- 报告文档 → Word (.docx) 或 PDF (.pdf)

### 格式规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 日期格式 | YYYY-MM-DD | 2026-05-14 |
| 时间格式 | HH:MM:SS | 14:30:00 |
| 数值精度 | 保留2位小数 | 1234.56 |
| 百分比 | 保留1位小数 | 85.5% |
| 金额 | 千分位分隔 | 1,234,567.89 |

## 错误处理

1. **文件不存在**: 返回明确错误信息
2. **格式不支持**: 提示支持的格式
3. **数据异常**: 记录异常行，继续处理
4. **内存不足**: 分块处理大文件
5. **编码问题**: 尝试多种编码（UTF-8, GBK, GB2312）

## 示例指令

```
# Excel 数据清洗
处理 file_xxx 清洗数据，去除重复行，填充空值为0

# Excel 数据汇总
处理 file_xxx 按部门汇总销售额

# Word 内容提取
处理 file_xxx 提取所有标题和段落内容

# PDF 文本提取
处理 file_xxx 提取所有文本内容并保存为 txt

# CSV 转换
处理 file_xxx 将 CSV 转换为 Excel 格式

# JSON 分析
处理 file_xxx 分析 JSON 数据结构，生成统计报告

# 图片信息
处理 file_xxx 获取图片的尺寸、格式信息
```

## 安全要求

- 禁止执行任何文件系统操作（删除、移动系统文件）
- 禁止网络请求
- 仅处理传入的文件
- 输出文件仅保存到指定目录

## 版本
v2.0.0 - 扩展为通用文件处理器
