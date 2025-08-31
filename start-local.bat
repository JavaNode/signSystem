@echo off
echo ========================================
echo 签名系统本地启动脚本
echo ========================================

echo 1. 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo 2. 启动后端服务...
cd backend
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境并安装依赖...
call venv\Scripts\activate
pip install -r requirements.txt

echo 启动后端API服务...
start "后端API服务" cmd /k "venv\Scripts\activate && python run.py"

cd ..

echo 3. 启动前端服务...
timeout /t 3 /nobreak >nul
cd frontend
start "前端开发服务器" cmd /k "npm run dev"

cd ..

echo.
echo ========================================
echo 本地开发环境启动完成！
echo ========================================
echo 前端地址: http://localhost:3000
echo 后端API: http://localhost:8000
echo 管理后台: http://localhost:3000/admin
echo ========================================
echo 按任意键关闭此窗口...
pause >nul