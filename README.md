<div align="center">
  <h1>🚀 墨步 (MoBu) Canvas</h1>
  <p><strong>步步随心 画由意动 —— 你的可控式 AI 绘画伴侣</strong></p>

  <img src="https://img.shields.io/badge/Frontend-Vue%203%20%7C%20Pinia-4FC08D.svg?logo=vuedotjs" alt="Vue3"/>
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Engine-ComfyUI-FF6F00.svg" alt="ComfyUI"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"/>
</div>

<br/>

## 📖 项目简介 (Overview)

墨步 (MoBu) 是一个面向现代 AIGC 创作者的智能调度画板系统。项目由学生开发团队主导，且已完全跑通了无外部资金依赖的前后端 Web 全链路闭环。项目代码规范严格，可无缝用于软件著作权（软著）申请，并具备极强的双创竞赛落地价值。

核心架构采用**网关分离式微服务架构**，将前端画板的 UI 交互、业务网关的智能调度与底层深度学习引擎（ComfyUI）进行了彻底的物理剥离。

## ✨ 核心特性 (Features)

* 🚪 **丝滑的用户着陆体验**：登录验证体系严密，用户成功登录后，系统会自动且无缝地将其重定向至画板主页，确保极佳的用户操作流。
* ⚡ **长短结合的通信架构**：
  * **Axios 指令下发**：负责“一呼一应”的短耗时任务，如调用 GLM 模型进行提示词润色与生图任务的指令派发。
  * **SSE 实时流式追踪**：采用原生 EventSource 建立 Server-Sent Events 单向流长连接，彻底替代低效的轮询机制，实时推送生图进度并无缝接收多图层结果。
* 🎨 **递进式多态生图引擎**：
  * **构思线稿**：结合 Counterfeit-V3.0 与 Lineart 控制网，在后端强制注入提示词防线，暴力镇压“实体画板”等 AI 幻觉，将涂鸦直接降维为纯净单色线稿。
  * **氛围铺色**：采用双通道控制网策略 (Dual ControlNets)，通道 A 锁死线稿物理边界，通道 B 读取前端涂抹色块，精确引导 AI 进行体素填色。
  * **局部精修**：支持套索掩码涂抹，后端锁死重绘幅度 (`denoise = 0.75`)，实现对图像局部的无缝修补与重绘。
* 🛡️ **企业级网关防御 (Defensive Engineering)**：
  * **幽灵连接熔断**：实时监测前端长连接状态，异常断开时强制闭合底层 WebSocket 引擎连接，防止服务器陷入死循环。
  * **缓存假死防御**：捕获引擎底层的 `execution_cached` 状态，主动触发轮询捞图，强行组装事件下发，防止前端进度条永久卡死。
  * **跨域安全护盾**：配置严谨的 CORSMiddleware 结合前端 `crossOrigin="anonymous"` 声明，彻底杜绝跨域图片引发的 Tainted Canvas 画布污染崩溃。

## 🏗️ 架构与技术栈 (Architecture & Tech Stack)

### 前端工作站 (Frontend)
前端技术基座采用 Vue 3 + Pinia + vue-konva + Element Plus 构建，严格遵循单向数据流原则。
* **核心画板**：提供 Figma 级别的双层网格，深度支持撤销/重做流、图层管理及多种混合模式（如提取线稿必用的正片叠底）。
* **专业工具**：内置基于 perfect-freehand 算法的柳叶毛笔、支持 `destination-out` 的物理擦薄橡皮擦、以及调用原生 API 的屏幕级跨域吸色工具。

### 后端网关 (Backend)
采用 Python 3.10+、FastAPI 与 Pydantic 构建高度模块化的业务网关。
* **LLM 代理**：基于 GLM-4-Flash API 构建大模型代理，专职负责用户提示词的清洗、扩写与专业润色。
* **计算节点**：使用 ComfyUI 作为无状态纯计算节点，仅通过预设的标准 JSON 工作流接口提供计算支持。

## 📁 项目目录 (Project Structure)

本项目采用 Monorepo 规范管理前后端独立服务：

```text
MoBu/
├── frontend/               # 前端工程目录
│   ├── src/
│   │   ├── components/     # 画板与核心组件面板
│   │   ├── composables/    # AI 生成与提示词封装钩子
│   │   ├── stores/         # Pinia 全局状态与图层管理
│   │   └── views/          # 核心路由级页面
│   └── package.json
├── backend/                # 后端调度网关目录
│   ├── app/
│   │   ├── api/v1/         # llm, generate, stream 核心路由分发
│   │   ├── models/         # 全局 Pydantic 数据契约
│   │   └── utils/          # Base64 编解码与磁盘 GC 回收工具
│   ├── workflows/          # ComfyUI 标准化 JSON 工作流卷轴
│   └── requirements.txt
└── README.md               # 项目主说明文档
```
## 🚀 快速开始 (Getting Started)
1. 启动后端智能网关
请确保服务器已配置 Python 3.10+，并持有智谱 AI API Key 与可用的 ComfyUI 引擎地址。

```Bash
cd backend
pip install -r requirements.txt

# 在 backend 目录下创建 .env 文件，填入秘钥：
# ZHIPU_API_KEY=your_key_here
# COMFYUI_URL=http://your_comfyui_address

uvicorn app.main:app --reload
```
2. 启动前端绘图工作站
请确保本地环境已安装 Node.js。

```Bash
cd frontend
npm install
npm run dev
```
## 🤝 参与贡献 (Contributing)
我们欢迎开发者提交 Pull Request 共同完善 MoBu。提交代码前，请确保 UI 层与业务逻辑层已进行深度解耦。有关功能拓展或底层图层逻辑的修改建议，请提前通过 Issue 与团队发起讨论。
