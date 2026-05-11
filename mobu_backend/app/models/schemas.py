from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class GenerateMode(str, Enum):
    SKETCH = "sketch"
    COLOR = "color"
    INPAINT = "inpaint"

class GenerateRequest(BaseModel):
    mode: GenerateMode = Field(..., description="生成模式：sketch (草图), color (上色), inpaint (局部重绘)")
    prompt: str = Field(..., description="正向提示词")
    base_image: Optional[str] = Field(default="", description="基础图像的 Base64 编码")
    lineart_image: Optional[str] = Field(default="", description="线稿图像的 Base64 编码")
    color_image: Optional[str] = Field(default="", description="参考色图像的 Base64 编码")
    mask_image: Optional[str] = Field(default="", description="遮罩图像的 Base64 编码")
    mock_image_urls: Optional[List[str]] = Field(default=None, description="【调试专用】直接返回指定的本地图片 URL 列表")