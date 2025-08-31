@echo off
echo ========================================
echo 签名系统静态服务启动
echo ========================================

echo 1. 启动后端API服务...
cd backend
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

start "后端API" cmd /k "python run.py"
cd ..

echo 2. 启动前端静态服务...
timeout /t 3 /nobreak >nul

REM 检查是否安装了http-server
npm list -g http-server >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装http-server...
    npm install -g http-server
)

cd frontend
start "前端静态服务" cmd /k "http-server dist -p 3000 -c-1 --proxy http://localhost:8000?"

cd ..

echo.
echo ========================================
echo 生产环境启动完成！
echo ========================================
echo 前端地址: http://localhost:3000
echo 后端API: http://localhost:8000
echo ========================================
pause