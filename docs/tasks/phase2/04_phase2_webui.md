# Phase 2: Streamlit Web UI 开发

> **阶段**: Phase 2 - 产品化线 (Day 3-5)
> **目标**: 开发 Web 界面，让非技术用户可用
> **依赖**: T02-13 ~ T02-19 (本地文件存储)
> **并行**: 与安全修复线并行推进

---

## 功能需求

### 用户交互流程

```
用户访问 Web UI
    ↓
选择/上传 Excel 文件
    ↓
输入自然语言指令
    ↓
点击"执行"按钮
    ↓
等待处理（显示进度）
    ↓
下载结果文件
```

### 界面组件

| 组件 | 功能 | 说明 |
|------|------|------|
| 文件上传 | 上传 Excel 文件 | 支持 .xlsx/.xls |
| 指令输入 | 自然语言输入框 | 多行文本 |
| 执行按钮 | 触发任务 | 显示 loading 状态 |
| 进度显示 | 任务进度 | 状态文本 + 进度条 |
| 结果下载 | 下载处理结果 | 文件列表 + 下载按钮 |
| LLM 配置 | 设置 API Key | 侧边栏配置页面 |

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T02-20 | 创建 Streamlit 项目 | 在 `services/web-ui/` 创建项目结构 | `streamlit run app.py` 启动 | | 30min |
| T02-21 | 实现文件上传组件 | st.file_uploader 上传 Excel | 文件保存到会话目录 | | 30min |
| T02-22 | 实现指令输入组件 | st.text_area 输入自然语言 | 支持 Enter 提交 | | 15min |
| T02-23 | 实现任务执行逻辑 | 调用 Bridge API 提交任务 | 任务提交成功 | | 30min |
| T02-24 | 实现进度显示 | 显示任务状态和进度 | 状态实时更新 | | 30min |
| T02-25 | 实现结果下载 | st.download_button 下载文件 | 文件正确下载 | | 30min |
| T02-26 | 实现 LLM 配置页面 | 侧边栏配置 API Key | 配置保存到 .env | | 30min |
| T02-27 | 实现会话管理 | 自动创建/恢复会话 | 会话 ID 显示在界面 | | 30min |
| T02-28 | 添加 Dockerfile | 创建 web-ui 容器镜像 | 容器可启动 | | 30min |
| T02-29 | 更新 docker-compose.yml | 添加 web-ui 服务 | 服务正确启动 | | 15min |
| T02-30 | 用户界面测试 | 非技术用户完成 Excel 处理 | 用户无需 CLI | P0 | 1h |

---

## 验收清单

- [ ] `streamlit run app.py` 成功启动
- [ ] 文件上传组件可上传 Excel
- [ ] 指令输入框可输入自然语言
- [ ] 点击执行按钮后任务提交成功
- [ ] 进度显示实时更新
- [ ] 结果文件可下载
- [ ] 侧边栏可配置 LLM API Key
- [ ] 非技术用户可完成完整流程

---

## 关键文件

```
Hermes-WeCom-Assistant/
├── docker-compose.yml           # T02-29
├── services/
│   └── web-ui/
│       ├── Dockerfile           # T02-28
│       ├── requirements.txt
│       ├── app.py               # T02-20 (主入口)
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── upload.py        # T02-21
│       │   ├── config.py        # T02-26
│       │   └── history.py       # T02-27
│       └── components/
│           ├── __init__.py
│           ├── task_runner.py   # T02-23, T02-24
│           └── downloader.py    # T02-25
```

---

## Streamlit 主界面代码

```python
# app.py
import streamlit as st
from session_manager import create_session, get_session_path
from components.task_runner import run_task
from components.downloader import show_downloads

st.set_page_config(
    page_title="Excel Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Excel 智能助手")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ LLM 配置")
    api_key = st.text_input("API Key", type="password")
    base_url = st.text_input("API Base URL", value="https://api.openai.com/v1")
    model = st.text_input("Model", value="gpt-4")
    
    if st.button("保存配置"):
        # 保存到 .env 或配置文件
        st.success("配置已保存")

# 主界面
session_id = st.session_state.get("session_id")
if not session_id:
    session_id = create_session()
    st.session_state["session_id"] = session_id

st.caption(f"会话 ID: {session_id}")

# 文件上传
uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx", "xls"])

# 指令输入
instruction = st.text_area(
    "输入处理指令",
    placeholder="例如：将第一列数据按升序排序，并添加汇总行",
    height=100
)

# 执行按钮
if st.button("执行", type="primary"):
    if uploaded_file and instruction:
        with st.spinner("处理中..."):
            result = run_task(session_id, uploaded_file, instruction)
            st.success("处理完成!")
    else:
        st.warning("请上传文件并输入指令")

# 结果下载
show_downloads(session_id)
```

---

## Dockerfile

```dockerfile
# services/web-ui/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## docker-compose.yml 更新

```yaml
# 添加 web-ui 服务
web-ui:
  build: ./services/web-ui
  container_name: excel-web-ui
  ports:
    - "8501:8501"
  volumes:
    - ./data:/app/data
  environment:
    - BRIDGE_API_URL=http://hermes-bridge:8646
  depends_on:
    - hermes-bridge
  restart: unless-stopped
```

---

## AI Prompt 模板

**T02-20**: "请创建 Streamlit 项目结构，包含 app.py 主入口、pages 目录、components 目录"

**T02-23**: "请实现 task_runner.py，调用 Hermes Bridge API 提交任务，返回任务状态"

**T02-26**: "请实现侧边栏 LLM 配置页面，用户可以输入 API Key、Base URL、Model，配置保存到 .env 文件"

**T02-28**: "请创建 web-ui 的 Dockerfile，基于 python:3.11-slim，安装 Streamlit，启动 app.py"

---

## ⏱️ 检查点触发

> **本任务线完成后触发 CP3 检查点 + Phase 2 结项**

**触发条件**: T02-20 ~ T02-30 全部完成

**Review 流程**:
```
1. 完成所有任务 → 勾选验收清单
2. 运行验收测试:
   - docker-compose up → 服务全部启动
   - 打开 http://localhost:8501 → 界面正常显示
   - 执行完整用户流程 → 上传 → 处理 → 下载
3. 邀请 3+ 名文职人员测试 → 收集反馈
4. 提交 Review Request → 等待 Reviewer + PM + 用户代表确认
5. CP3 通过 → Phase 2 结项 → 决定是否进入 Phase 3
```

**详见**: [00_phase2_overview.md - CP3 检查点](./00_phase2_overview.md#cp3-web-ui-验收--phase-2-结项-day-5-结束)