# 墨步-AI画布

**—— 源代码与本地部署运行指南**

尊敬的评委老师，您好！感谢您评审本项目。

为了保障极高的运行稳定性和渲染性能，墨步采用了完全解耦的**前后端分离微服务架构**。系统由三个独立运行的节点组成：**前端渲染层 (Vue 3)**、**业务调度网关 (FastAPI)** 以及 **纯计算引擎 (ComfyUI)**。

根据竞赛规则，本源码包仅包含团队**100% 自主研发**的前端源码与后端网关源码。底层开源生图引擎及模型资产，请按照本文档引导配置。

------

## 1. 基础环境与硬件要求

为保障“构思 -> 铺色 -> 精修”全工作流顺畅运行，请确保测试设备满足以下要求：

- **硬件要求**：推荐配备 NVIDIA 独立显卡，**最低显存要求 8GB (VRAM)**。
- **前端环境**：Node.js 大于等于 20.19.0 或 大于等于 22.12.0。
- **后端环境**：Python 3.10 或更高版本。
- **浏览器**：推荐使用最新版 Chrome 或 Edge 以获得最佳的 Canvas 硬件加速渲染性能。

------

## 2. 部署节点一：开源生图计算引擎 (ComfyUI)

本项目底层核心算力依赖开源计算节点 ComfyUI，请务必先启动此节点。

### 2.1 获取源码与配置 Python 虚拟环境

请在本地新建一个目录，将 ComfyUI 拉取到本地并隔离环境：

```bash
# 1. 克隆开源仓库
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 2. 创建并激活 Python 虚拟环境
python -m venv venv
# Windows 激活命令：
.\venv\Scripts\activate
# (Mac/Linux 激活命令：source venv/bin/activate)

# 3. 安装核心依赖包
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 2.2 下载并配置开源模型资产

请通过下方官方 HuggingFace 链接下载对应的开源模型权重，并严格放入 ComfyUI 的对应文件夹中：

**A. 大模型 (Checkpoints)** -> 放入 `ComfyUI/models/checkpoints/` 目录：

1. **Counterfeit-V3.0** (提供二次元精细画风基底)
   - 下载地址: [HuggingFace - Counterfeit-V3.0.safetensors](https://www.google.com/search?q=https://huggingface.co/gsdf/Counterfeit-V3.0/resolve/main/Counterfeit-V3.0_fp16.safetensors)
2. **Counterfeit-V3.0-inpainting** (特化重绘模型)
   - 下载地址: [HuggingFace - Counterfeit-V3.0-inpainting.safetensors](https://www.google.com/search?q=https://huggingface.co/gsdf/Counterfeit-V3.0/resolve/main/Counterfeit-V3.0-inpainting.safetensors)

**B. 控制网模型 (ControlNet)** -> 放入 `ComfyUI/models/controlnet/` 目录：

1. **Lineart** (线稿提取与骨架锁死)
   - 下载地址: [HuggingFace - control_v11p_sd15_lineart.pth](https://www.google.com/search?q=https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_lineart.pth)
2. **T2I-Adapter Color** (色彩引导与色块融合)
   - 下载地址: [HuggingFace - t2i-adapter-color.pth](https://www.google.com/search?q=https://huggingface.co/TencentARC/T2I-Adapter/resolve/main/models/t2i-adapter-color-sd14v1.pth)

### 2.3 跨域启动引擎

确保处于 `venv` 虚拟环境中，执行以下命令启动 ComfyUI。

⚠️ **极其重要**：由于本项目为严格的前后端分离架构，**必须携带跨域参数**启动，否则前端画布将无法与引擎建立通信：

```bash
python main.py --enable-cors-header "*"
```

- **验证**：请确保控制台输出引擎成功运行在 `http://127.0.0.1:8188`。

------

##  3. 部署节点二：业务调度网关 (FastAPI - 自研)

此服务为团队自主研发的核心调度网关，负责多态任务分发、长连接维持与大语言模型 (LLM) 代理。

1. 进入后端源码目录 `mobu-backend`。

2. 同样建议您在此目录下创建独立的虚拟环境，并安装依赖：

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **🔑 API 密钥配置 (免配置特权)**：

   为方便评委测试，我们在项目根目录的 `.env` 文件中，**已经为您预置了具有充足测试额度的 `ZHIPU_API_KEY`**。您无需自行注册申请，可直接开箱体验“智能提示词润色”等功能。

4. 启动后端网关服务：

   ```bash
   # 请直接执行团队编写的批处理启动脚本：
   .\run.bat
   ```

- **验证**：请确保后端网关服务成功运行在 `http://127.0.0.1:8000`。

------

## 4. 部署节点三：前端交互画板 (Vue 3 - 自研)

此服务为团队自主研发的客户端界面，承载所有的非破坏性画布交互、图层流转与状态管理。

1. 进入前端源码目录 `mobu-frontend`。

2. 安装 Node 依赖：

   ```bash
   npm install
   ```

3. 启动本地开发服务器：

   ```bash
   npm run dev
   ```

4. 终端将输出本地访问地址（通常为 `http://localhost:5173` 或 `http://localhost:5174`）。在浏览器中打开该地址，即可开始体验墨步 (MoBu) 艺术画布！

5. 测试账号和密码：
   测试账号：19000000000

   测试密码：123456


------

## 5. 架构说明与未来演进计划 (关于“伴生智能体”)

您在体验过程中，会注意到右侧控制台中设计了创新的**“伴生智能”交互面板**。

- **当前成果**：前端“双态协同右脑引擎”的 UI/UX、云水行文排版、以及核心的跨组件状态调度（Pinia Dispatcher 拦截机制）已 **100% 自主开发完毕**，您可以完美体验其人机交互的视觉与业务逻辑。
- **未来演进**：底层的 `openclaw` 智能体框架，目前规划为作为一个**独立的第三方微服务**运行，用于实现真正的“意图识别与参数自动代填”。由于其涉及复杂的意图对齐算法，目前尚处于实验室调优阶段，本次提交包暂不包含该独立第三方服务的逻辑代码。这亦是本项目未来的核心商业演进方向。