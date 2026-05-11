import os
import re
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, APITimeoutError
from dotenv import load_dotenv

# 加载环境变量，确保 .env 文件被正确读取
load_dotenv()

# 初始化路由
router = APIRouter(prefix="/api/v1/llm", tags=["LLM Text Polish"])

# ==========================================
# 智谱大模型配置 (OpenAI 兼容模式)与安全校验
# ==========================================
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
if not ZHIPU_API_KEY:
    raise ValueError("严重错误：未在环境变量或 .env 文件中找到 ZHIPU_API_KEY 配置！")

zhipu_client = AsyncOpenAI(
    api_key=ZHIPU_API_KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

SYSTEM_PROMPT = """你是一个顶级的 AI 绘画 Prompt 工程师。你的任务是优化用户输入的画面描述，将其转化为 Stable Diffusion (Danbooru 标签体系) 的英文 Prompt。
规则：
1. 提取用户描述的核心主体、动作、服装、表情等。
2. 自动补充高质量的起手式标签（如 masterpiece, best quality）。
3. ⚠️ 极其重要：如果用户的描述中包含“线稿、草图、黑白、素描、lineart、sketch”等词汇，你【绝对不能】添加任何关于光影、体积、写实的标签（严禁使用 cinematic lighting, photorealistic, depth of field 等词），必须保持画面的扁平纯粹。
4. 必须全部转化为英文半角逗号分隔的标签序列。
5. 你的输出只能包含润色后的 Prompt 纯文本，绝对不能包含任何解释性文字。"""
# ==========================================
# 数据模型定义
# ==========================================
class PolishRequest(BaseModel):
    prompt: str = Field(..., max_length=1000, description="用户输入的原始提示词")


class PolishResponseData(BaseModel):
    polishedPrompt: str


class PolishResponse(BaseModel):
    code: int
    data: PolishResponseData
    message: str


# ==========================================
# 核心业务逻辑
# ==========================================
async def polish_prompt_service(user_prompt: str) -> str:
    if not user_prompt or not user_prompt.strip():
        return ""

    # 调用大模型，严格限制 15 秒超时
    response = await zhipu_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        timeout=15.0,
        temperature=0.6,
    )

    raw_result = response.choices[0].message.content

    # 数据深度清洗
    cleaned_result = raw_result.strip()

    # 1. 移除首尾引号 (处理大模型偶尔包裹的 " 或 ')
    cleaned_result = re.sub(r'^["\']|["\']$', '', cleaned_result)

    # 2. 彻底移除 Markdown 代码块标识及其附带的语言名称 (如 ```json, ```text, 以及结尾的 ```)
    cleaned_result = re.sub(r'```[a-zA-Z]*', '', cleaned_result)

    # 3. 将所有换行符和回车符替换为空格，确保输出为单行
    cleaned_result = cleaned_result.replace('\n', ' ').replace('\r', ' ')

    # 4. 移除由于替换产生的连续多余空格
    cleaned_result = re.sub(r'\s+', ' ', cleaned_result).strip()

    return cleaned_result


# ==========================================
# 路由接口
# ==========================================
@router.post("/polish-prompt", response_model=PolishResponse)
async def polish_prompt(req: PolishRequest, response: Response) -> PolishResponse:
    """
    提示词润色接口：将用户简短描述扩写为高质量 ComfyUI 英文标签
    """
    try:
        polished_text = await polish_prompt_service(req.prompt)
        # 默认 200 状态码由 FastAPI 自动处理
        return PolishResponse(
            code=200,
            data=PolishResponseData(polishedPrompt=polished_text),
            message="success"
        )

    except APITimeoutError:
        # 捕获超时异常，强制修改真实 HTTP 状态码为 408
        response.status_code = status.HTTP_408_REQUEST_TIMEOUT
        return PolishResponse(
            code=408,
            data=PolishResponseData(polishedPrompt=""),
            message="大模型响应超时，请稍后重试"
        )

    except Exception as e:
        # 捕获其他未知异常，强制修改真实 HTTP 状态码为 500
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return PolishResponse(
            code=500,
            data=PolishResponseData(polishedPrompt=""),
            message=f"服务内部处理异常: {str(e)}"
        )