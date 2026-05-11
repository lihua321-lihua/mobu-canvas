import os
import base64
import uuid
import logging
from io import BytesIO
from typing import Dict, List, Any
from PIL import Image

# 配置基础日志
logger = logging.getLogger(__name__)


def process_base64_image(b64_str: str, output_dir: str) -> Dict[str, Any]:
    """
    处理 Base64 图像数据：切除前缀、解码、保存为物理 PNG 文件，并返回元数据。

    :param b64_str: 前端传来的 base64 图像字符串
    :param output_dir: 临时图像保存目录 (如 temp_inputs/)
    :return: 包含 filepath, width, height 的字典
    """
    if not b64_str:
        raise ValueError("接收到的 Base64 字符串为空")

    try:
        # 1. 防御性切除前缀 (例如 data:image/png;base64,)
        if "," in b64_str:
            b64_data = b64_str.split(",", 1)[1]
        else:
            b64_data = b64_str

        # 2. 解码 Base64
        image_bytes = base64.b64decode(b64_data)

        # 3. 使用 PIL 验证图像并获取真实宽高
        with Image.open(BytesIO(image_bytes)) as img:
            width, height = img.size

            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)

            # 生成唯一临时文件名
            filename = f"mobu_temp_{uuid.uuid4().hex}.png"
            filepath = os.path.join(output_dir, filename)

            # 统一转为 PNG 格式保存，处理 RGBA 确保透明通道正确保留
            img.save(filepath, format="PNG")

        return {
            "filepath": filepath,
            "width": width,
            "height": height
        }

    except Exception as e:
        logger.error(f"Base64 图像解析失败: {e}")
        raise ValueError(f"无效的图像数据，解析失败: {str(e)}")


def cleanup_temp_files(file_paths: List[str]) -> None:
    """
    垃圾回收工具：安全地删除临时文件。

    :param file_paths: 需要删除的文件路径列表
    """
    for file_path in file_paths:
        if not file_path:
            continue

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"成功清理临时文件: {file_path}")
            else:
                logger.warning(f"尝试清理的文件不存在，可能已被删除: {file_path}")
        except PermissionError:
            logger.error(f"权限不足，无法删除文件: {file_path}")
        except Exception as e:
            logger.error(f"清理临时文件 {file_path} 时发生未知异常: {e}")