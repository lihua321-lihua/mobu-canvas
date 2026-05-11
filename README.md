# 墨步 (MoBu) - 可控式AI绘画伴侣

> [cite_start]步步随心，画由意动。墨步是一个基于网关分离式微服务架构的智能调度画板系统，彻底剥离了核心业务逻辑与深度学习计算引擎 [cite: 32, 146]。

## 🌟 项目简介

[cite_start]墨步 (MoBu) 提供了一个由前端画板与底层 AI 引擎组成的闭环工作流 [cite: 146][cite_start]。本项目致力于解决传统 AI 生图不可控、等待时间长等痛点。前端采用极致简约的 UI 设计与 Figma 级的双层网格工作区 [cite: 29, 43][cite_start]；后端作为智能调度网关，负责多态任务分发、长连接维持以及系统级稳定性防御 [cite: 147]。

本仓库采用 Monorepo 结构，包含完整的独立前端工作站与后端网关服务。

## 🚀 核心特性

* **⚡ 长短结合的通信架构**
  * [cite_start]**Axios 指令下发**：用于“一呼一应”的短耗时任务，如大模型提示词润色与重量级生图任务的派发 [cite: 4, 5, 8, 11]。
  * [cite_start]**SSE 实时流式追踪**：使用原生 EventSource 建立 Server-Sent Events 单向流长连接，彻底替代低效轮询，实现生图进度的实时反馈与多图层结果接收 [cite: 12, 13, 16, 21]。
* **🎨 递进式多态生图引擎**
  * [cite_start]**构思线稿 (Sketch Mode)**：结合 Counterfeit-V3.0 与 Lineart 控制网，并在提示词中暴力镇压实体画板幻觉，将涂鸦转化为纯粹单色线稿 [cite: 160, 162, 163, 164]。
  * [cite_start]**氛围铺色 (Color Mode)**：采用双通道控制网 (Dual ControlNets)，通道 A 锁死线稿物理边界，通道 B 读取前端涂抹色块精确引导大模型填色 [cite: 165, 168, 169, 170]。
  * [cite_start]**局部精修 (Inpaint Mode)**：支持用户擦除局部，后端锁死重绘幅度 (denoise = 0.75) 实现掩码重绘与无缝融合 [cite: 171, 172, 174]。
* **🛠️ 沉浸式前端画板工作站**
  * [cite_start]包含撤销重做流、物理图层管理、多重混合模式 (如正片叠底、滤色) [cite: 46, 47, 82]。
  * [cite_start]支持柳叶毛笔 (基于 perfect-freehand 算法)、几何拖拽、物理擦薄橡皮擦、跨域吸色等专业级绘图工具 [cite: 60, 63, 68, 72]。
* **🛡️ 生产级后端防御体系**
  * [cite_start]**幽灵连接熔断**：监测前端异常断开，强制闭合底层 WebSocket 避免死循环 [cite: 177, 178]。
  * [cite_start]**缓存命中假死防御**：捕获引擎 `execution_cached` 状态，主动轮询捞图，防止前端进度条永久卡死 [cite: 179, 180]。
  * [cite_start]**磁盘 GC 自动回收**：利用 FastAPI BackgroundTasks 异步删除临时入参 Base64 物理落盘文件，防止 I/O 爆炸 [cite: 181, 182]。
  * [cite_start]**跨域安全护盾**：配置宽松 CORSMiddleware 结合前端 `crossOrigin="anonymous"` 声明，杜绝 Tainted Canvas 污染 [cite: 183, 184]。

## 🛠️ 技术栈 (Tech Stack)

### 前端 (Frontend)
* [cite_start]**核心框架**: Vue 3 + Vite [cite: 3, 143]
* [cite_start]**状态中枢**: Pinia [cite: 3]
* [cite_start]**2D 渲染引擎**: vue-konva [cite: 3]
* [cite_start]**UI 组件库**: Element Plus [cite: 3]
* [cite_start]**通信**: Axios + 原生 EventSource (SSE) [cite: 3]

### 后端 (Backend API Gateway)
* [cite_start]**核心框架**: FastAPI (Python 3.10+) + Pydantic [cite: 147, 151]
* [cite_start]**流式通信**: sse-starlette + websockets [cite: 151]
* [cite_start]**LLM 代理**: ZhipuAI SDK (GLM-4-Flash) [cite: 149, 151]
* [cite_start]**底层计算节点**: ComfyUI (HTTP/WebSocket API) [cite: 148]

## 📂 目录结构

```text
MoBu-AI-Platform/
├── frontend/                 # 前端画板工程目录
│   ├── src/
│   │   ├── components/       # 核心画板与 AI 功能组件
│   │   ├── composables/      # AI 生成与提示词优化逻辑封装
│   │   ├── stores/           # Pinia 全局状态管理
│   │   └── views/            # 路由视图
│   └── package.json
├── backend/                  # 后端调度网关目录
│   ├── app/
│   │   ├── api/v1/           # LLM 提示词润色、生图网关与 SSE 路由
│   │   ├── models/           # Pydantic 数据契约
│   │   └── utils/            # Base64 编解码与工作流篡改器
│   ├── workflows/            # 标准化 ComfyUI API 工作流卷轴
│   └── requirements.txt
└── README.md
## ⚙️ 本地运行指南
1. 启动后端网关
请确保已配置好 Python 3.10+ 环境，并拥有智谱 AI 的 API Key 与本地运行的 ComfyUI 引擎。

Bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 配置环境变量 (在根目录新建 .env 文件并填入 ZHIPU_API_KEY 与 COMFYUI_URL)
# 启动 FastAPI 服务
uvicorn app.main:app --reload
2. 启动前端画板
请确保已安装 Node.js 环境。

Bash
cd frontend
# 安装依赖
npm install
# 启动本地开发服务器
npm run dev
## 🤝 团队协作与版权
本项目作为团队联合开发项目，已规划并支持完整的软著提取规范 。代码核心保留了多端拓展性，未来计划向移动端跨平台演进。
