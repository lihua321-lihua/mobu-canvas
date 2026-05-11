import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 导入我们在 app/api/v1 下编写的核心路由
from app.api.v1 import llm, generate, stream

# 初始化 FastAPI 应用
app = FastAPI(
    title="墨步 (MoBu) 核心后端 API",
    description="AI 辅助绘图 Web 应用后端，基于 FastAPI + ComfyUI + GLM-4-Flash",
    version="1.0.0"
)

# ==========================================
# 🛡️ 极度宽松的跨域配置 (CORS) - 根除 Tainted Canvas
# ==========================================
app.add_middleware(
    CORSMiddleware,
    # 使用 allow_origin_regex=".*" 替代 allow_origins=["*"]
    # 这样可以完美兼容 allow_credentials=True 的严格检查机制
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # 核心：必须明确暴露 Headers，否则前端 Canvas 的 crossOrigin="anonymous" 可能会被浏览器拦截
    expose_headers=["*"]
)

# ==========================================
# 🗂️ 静态资源挂载：明确暴露图像资源
# ==========================================
# 确保临时目录存在，将其挂载为静态服务。
# 这样如果前端需要读取后端生成的临时线稿/占位图，可以直接通过 /temp_inputs/... 访问，并且受上述 CORS 保护。
TEMP_DIR = os.path.join(os.getcwd(), "temp_inputs")
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/temp_inputs", StaticFiles(directory=TEMP_DIR), name="temp_inputs")

# ==========================================
# 🚀 核心路由挂载 (全部收束在 /api/v1 下)
# ==========================================
app.include_router(llm.router)
app.include_router(generate.router)
app.include_router(stream.router)

# ==========================================
# 🩺 存活探针
# ==========================================
@app.get("/", tags=["System"])
async def root():
    return {"message": "Welcome to MoBu (墨步) API"}

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "MoBu Backend is running safely."}