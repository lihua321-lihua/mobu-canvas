# 🎨 MoBu (墨步) Frontend Canvas

**墨步 (MoBu)** 前端是基于 `Vue 3` + `Konva` 构建的高性能交互式 AI 艺术共创画板。它不仅是一个前端渲染容器，更是集成了非破坏性图层管理、SSE 流式通信以及创新性“双态协同伴生智能”的复杂单页应用 (SPA)。

系统严格遵循单向数据流原则，实现了 UI 组件与底层渲染逻辑、状态调度的深度解耦。

## ✨ 核心特性 (Core Features)

- 🖌️ **Figma 级高阶画板**：基于 `vue-konva` 驱动。支持图层拖拽重排、混合模式切换、多笔刷（含基于 `perfect-freehand` 的柳叶毛笔算法）以及跨域吸色。
- 🌊 **SSE 实时流通信**：废弃传统的低效短轮询。采用原生 `EventSource`，实现长耗时 AI 生图任务的进度追踪与 4 宫格结果的无缝推送。
- 🧠 **双态协同右脑引擎**：右侧边栏首创“云水行文”交互。**A面 (专业控制台)** 提供极致的参数掌控；**B面 (伴生智能)** 提供无边框对话流与“中式印章授权”，实现意图识别与跨组件状态劫持（幽灵代笔）。
- 🛡️ **极苛刻的防呆与跨域防御**：内置全方位状态机拦截（如精修模式强制锁定图层与画笔）。渲染层采用严格的 `crossOrigin="anonymous"` 预加载机制，彻底杜绝 Tainted Canvas（污染画布）导致的二次导出崩溃。
- 🔐 **安全鉴权闭环**：完整的用户登录、注册与会话状态接管，保障创作者的资产私密性与云端同步能力。

## 🧭 路由与界面拓扑 (Router Topology)

系统由四级递进式漏斗流构成：

1. `/` -> **`HomeView.vue`**：**起始着陆页**。极致简约的居中排版与深邃光影，提供品牌视觉中枢。
2. `/auth` -> **`SignOrRegister.vue`**：**账户鉴权页**。提供流畅的登录与注册表单切换，完成 JWT Token/Session 的获取与 Pinia 状态注入。
3. `/home` -> **`Home.vue`**：**画板尺寸配置页**。提供多比例预设，动态写入全局 Store。
4. `/workspace` -> **`Workspace.vue`**：**核心画板工作区**。由顶部调度器、左侧悬浮工具栏、中央渲染画布与右侧生成调度台构建的绝对核心。

## 🏗️ 核心通信层设计 (Communication Architecture)

前端与后端网关的通信被严格划分为两条职责分明的通道：

- **⚡ Axios (指令投递通道)**：用于“一呼一应”的短耗时任务。例如：向 `/api/v1/llm/polish-prompt` 发送草稿，`await` 等待几秒后回填大模型润色好的纯净英文提示词；或提交包含 Base64 涂层的重量级生图 Payload，换取一个 `task_id`。
- **🌊 SSE (状态监听通道)**：拿到 `task_id` 后，立刻通过 `EventSource` 建立单向长连接。持续接收后端下发的 `{"status": "generating", "progress": "20%"}`，驱动前端 UI 进度条，直到接收 `success` 事件渲染图片并主动断开连接。

## 📂 工程目录结构 (Project Structure)

```Plaintext
mobu-frontend/
├── public/                 # 静态资源 (Icon、全局字体等)
├── src/
│   ├── assets/             # 编译期静态资源 (图片、Logo)
│   ├── components/
│   │   ├── common/         # 全局通用组件 (ImageLightbox, 弹窗等)
│   │   └── workspace/      # 核心工作区组件库
│   │       ├── left/       # 左侧控制流 (画笔/图层/精修面板)
│   │       ├── right/      # 右侧数据流 (包含 A面-生成调度台 与 B面-伴生智能体)
│   │       └── CanvasBoard.vue # 核心 Konva 渲染引擎封装
│   ├── composables/        # Vue 3 组合式函数 (逻辑复用层)
│   ├── router/             # Vue Router 路由表配置
│   ├── services/           # API 接口统一封装与拦截器
│   ├── stores/             # Pinia 状态机 (boardStore.js 核心中枢)
│   ├── views/              # 顶级路由视图
│   │   ├── HomeView.vue         # 落地页
│   │   ├── SignOrRegister.vue   # 🔐 登录注册页
│   │   ├── Home.vue             # 尺寸配置页
│   │   └── Workspace.vue        # 核心画板页
│   ├── App.vue             # 根组件
│   └── main.js             # 实例挂载与全局插件注入
├── .gitignore
├── index.html              # 挂载模板
├── package.json            # 依赖声明
└── vite.config.js          # Vite 构建配置
```

*(注：本源码包已剔除 `node_modules` 及开发工具本地缓存，确保源码纯净度。)*

## 🚀 快速上手 (Quick Start)

### 1. 环境准备

请确保您的计算机上已安装 **Node.js ($\ge$ 20.19.0 或 $\ge$ 22.12.0)**。

### 2. 依赖安装

进入前端根目录，使用 npm 安装项目所需的所有依赖包：

```Bash
npm install
```

### 3. 本地开发服务器启动

启动带有热重载 (HMR) 的 Vite 本地开发服务器：

```Bash
npm run dev
```

### 4. 访问项目

终端将输出可访问的本地地址（通常为 `http://localhost:5173` 或 `http://localhost:5174`）。在浏览器中打开该地址，注册/登录账户后，即可开始体验墨步 (MoBu) 艺术画布！

### 5. 测试账号和密码
测试账号：19000000000

测试密码：123456

