@echo off
chcp 65001 >nul
echo ===================================================
echo   墨步 (MoBu) 核心后端 API 启动程序
echo ===================================================

:: 1. 检查虚拟环境是否存在
if not exist ".venv\Scripts\activate.bat" (
    echo [错误] 未在当前目录检测到 .venv 虚拟环境！
    echo 请确认您是否在正确的目录，或者虚拟环境名称是否为 .venv
    pause
    exit /b 1
)

:: 2. 激活虚拟环境
echo [INFO] 正在激活虚拟环境...
call .venv\Scripts\activate.bat

:: 3. 检查 .env 文件
if not exist ".env" (
    echo [警告] 根目录下未找到 .env 文件，请确保环境变量已配置！
)

:: 4. 启动 FastAPI 服务
echo [INFO] 正在启动 Uvicorn 服务器...
echo [INFO] API 文档地址: http://127.0.0.1:8000/docs
echo ===================================================

:: 使用热重载模式启动，监听 8000 端口
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause