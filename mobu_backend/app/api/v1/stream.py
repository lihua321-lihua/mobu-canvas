import os
import json
import asyncio
import base64
import json
import logging
import httpx
import websockets
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sd", tags=["SSE Stream"])

COMFYUI_HOST = os.getenv("COMFYUI_HOST", "127.0.0.1:8188")
COMFYUI_WS_URL = f"ws://{COMFYUI_HOST}/ws"
COMFYUI_API_URL = f"http://{COMFYUI_HOST}"


# ==========================================
# 辅助函数：从 ComfyUI 历史记录中捞取图像
# ==========================================
async def fetch_image_from_history(prompt_id: str) -> str:
    """
    缓存命中时，主动请求 /history/{prompt_id} 获取最终图像 URL
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{COMFYUI_API_URL}/history/{prompt_id}", timeout=10.0)
        if res.status_code == 200:
            history_data = res.json()
            prompt_result = history_data.get(prompt_id, {})
            outputs = prompt_result.get("outputs", {})

            # 遍历所有节点的输出，寻找包含 images 的节点
            for node_id, node_output in outputs.items():
                if "images" in node_output and len(node_output["images"]) > 0:
                    image_info = node_output["images"][0]
                    filename = image_info.get("filename")
                    subfolder = image_info.get("subfolder", "")
                    img_type = image_info.get("type", "output")
                    # 拼装 ComfyUI 原生获取图像的 URL
                    return f"{COMFYUI_API_URL}/view?filename={filename}&type={img_type}&subfolder={subfolder}"

        raise ValueError(f"无法从历史记录中解析出图像，prompt_id: {prompt_id}")


# ==========================================
# 核心业务：SSE 事件生成器
# ==========================================
async def event_generator(request: Request, client_id: str, prompt_id: str):
    """
    连接 ComfyUI WebSocket 并转换为 SSE 事件流下发
    """
    # 🌟 Mock 拦截逻辑：如果是假任务，伪造进度流并返回指定图片
    if prompt_id.startswith("mock_"):
        logger.info(f"进入 Mock 拦截隧道: prompt_id={prompt_id}")
        for i in range(1, 11):  # 模拟 10 次进度跳动 (10% 到 100%)
            if await request.is_disconnected():
                break
            yield {
                "event": "progress",
                "data": json.dumps({"progress": i * 10, "prompt_id": prompt_id})
            }
            await asyncio.sleep(0.3)  # 每次停顿 0.3 秒，总共模拟约 3 秒的生图耗时

        # 🌟 核心：从 prompt_id 中解密出假图片数组（无状态拦截）
        try:
            import base64 # 确保此处能调用 base64
            encoded_urls = prompt_id.replace("mock_", "")
            # 补齐 base64 编码可能缺失的 '=' padding
            encoded_urls += "=" * ((4 - len(encoded_urls) % 4) % 4)
            urls_json = base64.urlsafe_b64decode(encoded_urls).decode('utf-8')
            mock_urls = json.loads(urls_json)
        except Exception as e:
            logger.error(f"解析 Mock 图片失败: {e}")
            mock_urls = []

        yield {
            "event": "completed",
            "data": json.dumps({"image_urls": mock_urls, "prompt_id": prompt_id})
        }
        return  # 直接返回，彻底不走下面的 ComfyUI WebSocket 逻辑

    ws_url = f"{COMFYUI_WS_URL}?clientId={client_id}"

    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info(f"已连接到 ComfyUI WS: client_id={client_id}")

            while True:
                # 检查前端请求是否已断开，提前退出
                if await request.is_disconnected():
                    logger.info(f"前端主动断开连接，准备清理 WS: {client_id}")
                    break

                try:
                    # 设置极短的超时时间，以便能及时响应 request.is_disconnected()
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue  # 超时说明暂无消息，继续下一轮循环检测断连

                # 忽略 ComfyUI 发送的二进制预览图数据，只处理 JSON 文本字典
                if isinstance(message, bytes):
                    continue

                data = json.loads(message)
                msg_type = data.get("type")
                msg_data = data.get("data", {})

                # 1. 正常进度推送
                if msg_type == "progress":
                    value = msg_data.get("value", 0)
                    max_value = msg_data.get("max", 1)
                    percentage = int((value / max_value) * 100)
                    yield {
                        "event": "progress",
                        "data": json.dumps({"progress": percentage, "prompt_id": prompt_id})
                    }

                # 2. 正常执行完成
                elif msg_type == "executed" and msg_data.get("prompt_id") == prompt_id:
                    output = msg_data.get("output", {})
                    image_urls = []

                    # 现在的 output 直接就是 {"images": [...]}，不需要再遍历节点 ID 了！
                    if "images" in output and len(output["images"]) > 0:
                        for img_info in output["images"]:
                            filename = img_info.get("filename")
                            subfolder = img_info.get("subfolder", "")
                            img_type = img_info.get("type", "output")
                            url = f"{COMFYUI_API_URL}/view?filename={filename}&type={img_type}&subfolder={subfolder}"
                            image_urls.append(url)

                    # 只要提取到了图片（无论是一张还是两张），就立刻下发并结束监听
                    if image_urls:
                        yield {
                            "event": "completed",
                            "data": json.dumps({"image_urls": image_urls, "prompt_id": prompt_id})
                        }
                        break
                # 3. 🛡️ 缓存命中假死防御：ComfyUI 直接复用缓存，不会触发进度和 executed
                elif msg_type == "execution_cached" and msg_data.get("prompt_id") == prompt_id:
                    logger.info(f"部分节点命中内存缓存，继续等待生成: {prompt_id}")
                    continue

                # 4. 执行异常
                elif msg_type == "execution_error":
                    # 确保是当前任务的报错
                    if msg_data.get("prompt_id") == prompt_id or not msg_data.get("prompt_id"):
                        error_msg = msg_data.get("exception_message", "ComfyUI 内部生成错误")
                        yield {
                            "event": "error",
                            "data": json.dumps({"message": error_msg})
                        }
                        break

    except asyncio.CancelledError:
        # 🛡️ 内存泄漏终极防御：捕获 FastAPI 下发的取消信号 (如前端刷新页面)
        logger.warning(f"检测到客户端断开 (CancelledError)，正在强制关闭 WebSocket: {client_id}")
        raise  # 必须往上抛出，让 sse-starlette 正确清理资源

    except websockets.exceptions.ConnectionClosed:
        logger.warning(f"ComfyUI WebSocket 连接意外关闭: {client_id}")
        yield {
            "event": "error",
            "data": json.dumps({"message": "与图像生成引擎断开连接"})
        }

    except Exception as e:
        logger.error(f"SSE 流处理发生未知异常: {e}")
        yield {
            "event": "error",
            "data": json.dumps({"message": "服务器内部流传输异常", "detail": str(e)})
        }


@router.get("/stream/{client_id}/{prompt_id}")
async def stream_generation_status(request: Request, client_id: str, prompt_id: str):
    """
    SSE 接口：前端通过 EventSource 连接此端点以获取生成进度和最终图像
    """
    return EventSourceResponse(
        event_generator(request, client_id, prompt_id),
        ping=15  # 每 15 秒发送一次 ping 保持连接活跃，防止 Nginx 等网关杀掉长连接
    )