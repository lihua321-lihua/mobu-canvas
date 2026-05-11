import json
import os
import random
from typing import Dict, Any

# 假设你的工作流 JSON 文件存放在项目根目录下的 workflows 文件夹中
WORKFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflows")


class WorkflowBuilder:
    def __init__(self, workflow_dir: str = WORKFLOW_DIR):
        """初始化 Builder，绑定工作流目录"""
        self.workflow_dir = workflow_dir

    def _load_workflow(self, mode: str) -> Dict[str, Any]:
        """从本地磁盘读取对应模式的 JSON 工作流文件"""
        file_path = os.path.join(self.workflow_dir, f"workflow_{mode}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到对应的工作流文件: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_payload(self, mode: str, req: Any, image_meta: dict) -> Dict[str, Any]:
        """
        核心构建方法：读取并篡改工作流 JSON，生成最终的 ComfyUI Payload

        :param mode: 工作流模式 ('sketch', 'color', 'inpaint')
        :param req: 前端发来的 GenerateRequest 对象
        :param image_meta: 包含真实宽高和落盘物理路径的字典，例如：
                           {"width": 512, "height": 512, "base_path": "...", "lineart_path": "...", "color_path": "..."}
        """
        workflow = self._load_workflow(mode)

        # ---------------------------------------------------------
        # 1. 通用契约注入 (所有模式生效)
        # ---------------------------------------------------------

        # ["6"] 正向提示词
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = req.prompt

        # ["7"] 负面提示词 (可以从 req 获取，或使用系统预设)
        if "7" in workflow:
            # 假设 req 中没有提供负面提示词，提供一个高质量的兜底预设
            workflow["7"]["inputs"]["text"] = getattr(req, "negative_prompt",
                                                      "monochrome, greyscale, watermark, bad anatomy")

        # ["3"] 随机种子
        if "3" in workflow:
            workflow["3"]["inputs"]["seed"] = random.randint(1, 10 ** 15)

        # ---------------------------------------------------------
        # 2. 尺寸控制 (Sketch 和 Color 模式生效)
        # ---------------------------------------------------------
        if mode in ["sketch", "color"] and "5" in workflow:
            workflow["5"]["inputs"]["width"] = image_meta.get("width", 512)
            workflow["5"]["inputs"]["height"] = image_meta.get("height", 512)

        # ---------------------------------------------------------
        # 3. 差异化模式处理
        # ---------------------------------------------------------

        # 【铺色模式 Color】的智能降级与路径捕获
        if mode == "color":
            lineart_path = image_meta.get("lineart_path")
            color_path = image_meta.get("color_path")

            # 处理通道 A：线稿 (Node 10 & 11)
            if lineart_path and "10" in workflow:
                workflow["10"]["inputs"]["image"] = lineart_path
                if "11" in workflow:
                    workflow["11"]["inputs"]["strength"] = 1.0
            else:
                if "11" in workflow:
                    workflow["11"]["inputs"]["strength"] = 0.0  # 无线稿，权重归零降级

            # 处理通道 B：色块 (Node 13 & 14)
            if color_path and "13" in workflow:
                workflow["13"]["inputs"]["image"] = color_path
                if "14" in workflow:
                    workflow["14"]["inputs"]["strength"] = 0.85
            else:
                if "14" in workflow:
                    workflow["14"]["inputs"]["strength"] = 0.0  # 无色块，权重归零降级

        # 【草图模式 Sketch】的底层映射
        elif mode == "sketch":
            base_path = image_meta.get("base_path")
            if base_path and "10" in workflow:
                workflow["10"]["inputs"]["image"] = base_path

        # 【局部精修 Inpaint】的底层映射
        elif mode == "inpaint":
            base_path = image_meta.get("base_path")
            mask_path = image_meta.get("mask_path")
            if base_path and "10" in workflow:
                workflow["10"]["inputs"]["image"] = base_path
            if mask_path and "11" in workflow:
                workflow["11"]["inputs"]["image"] = mask_path

        return workflow