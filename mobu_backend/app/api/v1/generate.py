import os
import json
import uuid
import base64
import json
import httpx
import random
from typing import Tuple, Dict, Any, List
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from PIL import Image
import traceback

# 导入我们在 Step 1 和 Step 2 定义的模型和工具
from app.models.schemas import GenerateRequest, GenerateMode
from app.utils.image_utils import process_base64_image, cleanup_temp_files

load_dotenv()

router = APIRouter(prefix="/api/v1/sd", tags=["Stable Diffusion Generation"])

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")  # 防御双斜杠
TEMP_DIR = os.path.join(os.getcwd(), "temp_inputs")
WORKFLOW_DIR = os.path.join(os.getcwd(), "workflows")


# ==========================================
# 响应模型定义
# ==========================================
class GenerateResponse(BaseModel):
    status: str
    prompt_id: str
    client_id: str


# ==========================================
# 辅助函数：提权三段式 Prompt (🎨 AI 炼丹师终极优化版)
# ==========================================
def build_prompts(mode: GenerateMode, user_prompt: str) -> Tuple[str, str]:
    # 🌟 核心法则：将 user_prompt 前置，保证用户意图拥有最高 Token 权重！
    # 仅使用最稳定、模型认知度最高的 Danbooru 标准标签或通用高质量修饰词

    if mode == GenerateMode.SKETCH:
        # 正面：极简线稿映射。摒弃所有色彩暗示，专注“干净的数字线条”
        pos = f"{user_prompt}, (masterpiece, best quality, highres:1.1), pure digital lineart, monochrome, sketch, clean outlines, white background"

        # 负面：克制的权重。用模型听得懂的标准词汇剔除颜色和背景
        neg = "(color, colorful, flat color:1.2), shading, gradient, depth of field, screentones, complex background, traditional media, paper texture, bad anatomy, worst quality, messy lines, missing fingers"

    elif mode == GenerateMode.COLOR:
        # 正面：强调丰富的细节、清晰的边缘和专业的数字艺术上色
        pos = f"{user_prompt}, (masterpiece, best quality, highres:1.2), highly detailed, intricate details, vibrant colors, expressive digital painting, cinematic lighting, sharp focus"

        # 负面：剔除未完成感和粗糙感
        neg = "monochrome, grayscale, lineart, sketch, flat, dull colors, bad anatomy, worst quality, lowres, blurry, jpeg artifacts"

    elif mode == GenerateMode.INPAINT:
        # 正面：Inpaint 模式必须极度克制，只强化用户意图和基础质量，防止画风跑偏
        pos = f"{user_prompt}, (masterpiece, best quality, highres:1.1), highly detailed"

        # 负面：基础防崩坏
        neg = "bad anatomy, worst quality, lowres, mutated, extra limbs, ugly, messy"

    else:
        pos = user_prompt
        neg = "worst quality, lowres"

    return pos, neg

# ==========================================
# 辅助函数：生成纯白占位图
# ==========================================
def create_white_placeholder(width: int, height: int, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    img = Image.new("RGB", (width, height), "white")
    filename = f"mobu_placeholder_{uuid.uuid4().hex}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, format="PNG")
    return filepath


# ==========================================
# 🌟 核心业务类：WorkflowBuilder (解耦 JSON 组装)
# ==========================================
class WorkflowBuilder:
    def __init__(self, workflow_dir: str = WORKFLOW_DIR):
        self.workflow_dir = workflow_dir

    def _load_workflow(self, mode: str) -> Dict[str, Any]:
        file_path = os.path.join(self.workflow_dir, f"workflow_{mode}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到对应的工作流文件: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_payload(self, mode: str, pos_prompt: str, neg_prompt: str, image_meta: dict) -> Dict[str, Any]:
        workflow = self._load_workflow(mode)

        # 1. 注入文本与随机种子 (契约映射)
        if "6" in workflow: workflow["6"]["inputs"]["text"] = pos_prompt
        if "7" in workflow: workflow["7"]["inputs"]["text"] = neg_prompt
        if "3" in workflow: workflow["3"]["inputs"]["seed"] = random.randint(1, 10 ** 15)

        # 2. 注入真实宽高与双黄蛋设定
        if mode in ["sketch", "color"] and "5" in workflow:
            workflow["5"]["inputs"]["width"] = image_meta.get("width", 512)
            workflow["5"]["inputs"]["height"] = image_meta.get("height", 512)
            workflow["5"]["inputs"]["batch_size"] = 2

        # 3. 差异化模式的节点组装与降级逻辑
        if mode == "color":
            # 通道 A: 线稿 (10号加载, 11号CN)
            if "10" in workflow: workflow["10"]["inputs"]["image"] = image_meta.get("lineart_path")
            if "11" in workflow: workflow["11"]["inputs"]["strength"] = 1.0 if image_meta.get("use_lineart") else 0.0

            # 通道 B: 色块 (13号加载, 14号CN)
            if "13" in workflow: workflow["13"]["inputs"]["image"] = image_meta.get("color_path")
            if "14" in workflow: workflow["14"]["inputs"]["strength"] = 0.85 if image_meta.get("use_color") else 0.0

        elif mode == "sketch":
            # 🟢 注入底图，并根据 use_sketch 动态调节节点 13 的权重
            if "10" in workflow:
                workflow["10"]["inputs"]["image"] = image_meta.get("base_path")
            if "13" in workflow:
                workflow["13"]["inputs"]["strength"] = 1.0 if image_meta.get("use_sketch") else 0.0

        elif mode == "inpaint":
            if "10" in workflow: workflow["10"]["inputs"]["image"] = image_meta.get("base_path")
            if "11" in workflow: workflow["11"]["inputs"]["image"] = image_meta.get("mask_path")
            if "3" in workflow: workflow["3"]["inputs"]["denoise"] = 0.75  # 锁定重绘幅度

        return workflow


# ==========================================
# 路由接口：提交生成任务 (完全成为流水线调度员)
# ==========================================
@router.post("/generate", response_model=GenerateResponse)
async def generate_image(req: GenerateRequest, background_tasks: BackgroundTasks):
    # 🌟 拦截器核心：如果前端传了 mock_image_urls，直接短路！
    if req.mock_image_urls:
        client_id = str(uuid.uuid4())
        urls_json = json.dumps(req.mock_image_urls)
        encoded_urls = base64.urlsafe_b64encode(urls_json.encode('utf-8')).decode('utf-8')
        prompt_id = "mock_" + encoded_urls # 把图片藏在 ID 里
        return GenerateResponse(status="success", prompt_id=prompt_id, client_id=client_id)

    temp_files = []
    try:
        # 🟢 极其严格的前置业务拦截：移除了 sketch 模式必须传图的拦截！
        if req.mode == GenerateMode.INPAINT and not req.mask_image:
            raise HTTPException(status_code=422, detail="局部精修 (Inpaint) 模式下，必须提供 mask_image 遮罩图参数")

        # 2. 脏活累活：物理文件 I/O 与 image_meta 组装
        image_meta = {"width": 512, "height": 768, "use_sketch": False, "use_lineart": False, "use_color": False}

        # 只有真正传了图才会去解析 Base64 尺寸并落盘
        if req.base_image:
            info = process_base64_image(req.base_image, TEMP_DIR)
            temp_files.append(info["filepath"])
            image_meta.update({"width": info["width"], "height": info["height"], "base_path": info["filepath"]})

        # --- 针对不同模式的特殊降级落盘逻辑 ---
        if req.mode == GenerateMode.SKETCH:
            if req.base_image:
                image_meta["use_sketch"] = True
            else:
                # 🟢 核心降级逻辑：没传草图，造一张纯白图片顶上，并标记 use_sketch=False
                p_path = create_white_placeholder(image_meta["width"], image_meta["height"], TEMP_DIR)
                temp_files.append(p_path)
                image_meta["base_path"] = p_path
                image_meta["use_sketch"] = False

        elif req.mode == GenerateMode.COLOR:
            if req.lineart_image:
                info = process_base64_image(req.lineart_image, TEMP_DIR)
                temp_files.append(info["filepath"])
                image_meta.update({"lineart_path": info["filepath"], "use_lineart": True})
            else:
                p_path = create_white_placeholder(image_meta["width"], image_meta["height"], TEMP_DIR)
                temp_files.append(p_path)
                image_meta["lineart_path"] = p_path

            if req.color_image:
                info = process_base64_image(req.color_image, TEMP_DIR)
                temp_files.append(info["filepath"])
                image_meta.update({"color_path": info["filepath"], "use_color": True})
            else:
                p_path = create_white_placeholder(image_meta["width"], image_meta["height"], TEMP_DIR)
                temp_files.append(p_path)
                image_meta["color_path"] = p_path

        elif req.mode == GenerateMode.INPAINT:
            mask_info = process_base64_image(req.mask_image, TEMP_DIR)
            temp_files.append(mask_info["filepath"])
            image_meta["mask_path"] = mask_info["filepath"]

        # 3. 脑力活：调用 Builder 组装 JSON
        pos_prompt, neg_prompt = build_prompts(req.mode, req.prompt)
        builder = WorkflowBuilder(WORKFLOW_DIR)
        workflow_json = builder.build_payload(req.mode.value, pos_prompt, neg_prompt, image_meta)

        # 4. 注册垃圾回收并构建投递包裹
        # ⚠️ 绝对不要解开下面这行的注释，防止 ComfyUI 报错找不到图片
        # background_tasks.add_task(cleanup_temp_files, temp_files)

        client_id = str(uuid.uuid4())
        payload = {"prompt": workflow_json, "client_id": client_id}

        # 5. 网络 I/O：桥接 ComfyUI 引擎
        async with httpx.AsyncClient(proxy=None, trust_env=False) as client:
            comfy_res = await client.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=10.0)

            if comfy_res.status_code != 200:
                raise HTTPException(status_code=502,
                                    detail=f"ComfyUI 服务异常 ({comfy_res.status_code}): {comfy_res.text}")

            prompt_id = comfy_res.json().get("prompt_id")
            if not prompt_id:
                raise HTTPException(status_code=500, detail="ComfyUI 响应中缺少 prompt_id")

        return GenerateResponse(status="success", prompt_id=prompt_id, client_id=client_id)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # 🟢 恢复了异常处理骨架，但去掉了导致误删图片的 cleanup_temp_files()
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))