# 🚀 MoBu (墨步) Backend Gateway

**墨步 (MoBu)** 后端服务是一个基于 `FastAPI` 构建的高性能、高可用**网关分离式微服务**。它作为 Vue 3 前端画板与底层深度学习计算引擎（ComfyUI）之间的“智能调度枢纽”，彻底剥离了核心业务逻辑与重度 GPU 计算任务。

## ✨ 核心特性 (Core Features)

- ⚡ **网关分离架构**：前端请求不直接触达 GPU 节点，由 FastAPI 进行多态任务分发与防抖拦截。
- 🌊 **SSE 实时流通信**：基于 `sse-starlette` 与 `websockets` 桥接底层引擎，实现生图进度、状态、多图层的长连接实时下发。
- 🧠 **LLM 智能代理**：集成 GLM-4-Flash (智谱AI)，原生提供用户提示词的清洗、专业化翻译与扩写润色。
- 🛡️ **企业级防御工程**：
  - **幽灵连接熔断**：前端异常断开自动回收 WebSocket 连接。
  - **缓存命中假死防御**：智能识别 ComfyUI `execution_cached` 状态，主动轮询“捞图”，防止前端进度条死锁。
  - **磁盘 GC 自动回收**：基于 FastAPI `BackgroundTasks` 异步清理 Base64 物理落盘缓冲区，防止 I/O 爆炸。
  - **跨域安全护盾**：极宽泛 CORS 策略设计，彻底杜绝前端 Tainted Canvas 污染。

## 🏗️ 架构与工作流模型 (Workflows)

系统底层挂载三大特化 ComfyUI 工作流，支持多态降维渲染：

1. **构思线稿 (Sketch Mode)**：依托 `Counterfeit-V3.0` 与 Lineart ControlNet，将涂鸦转化为高阶单色线稿，并在服务端自动镇压“实体画板”等 AI 幻觉。
2. **氛围铺色 (Color Mode)**：双通道混合渲染。通道 A (Lineart) 锁死人物骨架，通道 B (T2I-Adapter-Color) 提取前端色块引导填色与光影融合。
3. **局部精修 (Inpaint Mode)**：掩码重绘与无缝融合。后端锁死 `denoise=0.75`，基于特化 inpainting 模型实现局部像素重构。

## 📂 工程目录结构

Plaintext

```
mobu-fastapi/
├── app/
│   ├── main.py             # 全局应用实例、CORS 中间件与路由总线
│   ├── models/
│   │   └── schemas.py      # 全局 Pydantic 数据契约 (请求/响应模型)
│   ├── utils/
│   │   ├── image_utils.py  # Base64 编解码、真实宽高测算与磁盘 GC 回收
│   │   └── builder.py      # 工作流 JSON 篡改与多态参数组装器
│   └── api/
│       └── v1/
│           ├── llm.py      # LLM 提示词翻译与润色接口
│           ├── generate.py # 核心多态生图网关
│           └── stream.py   # SSE 状态流与 WebSocket 桥接
├── workflows/              # 标准化 ComfyUI API 工作流卷轴
│   ├── workflow_sketch.json
│   ├── workflow_color.json
│   └── workflow_inpaint.json
├── temp_inputs/            # 前端入参 Base64 物理落盘缓冲区 (Git 忽略)
├── .env.example            # 环境变量配置模板
├── run.bat                 # Windows 快速启动脚本
└── requirements.txt        # 生产依赖锁定清单
```

## 🚀 快速上手 (Quick Start)

### 1. 环境准备

- 确保已安装 Python 3.10 或更高版本。
- 确保本地或远程已启动 ComfyUI 实例，并安装了项目所需的 Checkpoints 与 ControlNet 权重。

### 2. 依赖安装

Bash

```
cd mobu-fastapi

# 推荐使用虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 用户使用: .\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动服务

你可以通过快捷脚本启动：

Bash

```
# Windows
.\run.bat
```

或者使用 uvicorn 手动启动：

Bash

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，可访问 `http://127.0.0.1:8000/docs` 查看自动生成的 Swagger UI 接口文档。

## 📡 核心 API 契约 (API Reference)

所有业务路由均挂载于 `/api/v1` 命名空间下：

| **接口路径**                                | **方法** | **核心入参 (Payload)**             | **职责说明**                                                 |
| ------------------------------------------- | -------- | ---------------------------------- | ------------------------------------------------------------ |
| `/api/v1/llm/polish-prompt`                 | `POST`   | `prompt` (原始自然语言)            | 代理请求 GLM-4，15s 断路防御，清洗 Markdown，返回纯净英文咒语。 |
| `/api/v1/sd/generate`                       | `POST`   | `mode`, `prompt`, `base_image`, 等 | 多态分发器。执行 Base64 洗缩、节点篡改，向引擎投递任务，触发异步 GC。 |
| `/api/v1/sd/stream/{client_id}/{prompt_id}` | `GET`    | 路径参数                           | 建立 SSE 长连接。桥接底层引擎 WS，推送 `progress`, `completed`, `error` 流。 |