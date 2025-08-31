@echo off
echo ========================================
echo 签名系统 Docker 部署脚本
echo ========================================

echo 1. 检查Docker环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未安装或未启动
    echo 请先安装Docker Desktop并启动
    pause
    exit /b 1
)

echo Docker已安装 ✓

echo.
echo 2. 检查前端构建...
if not exist "frontend\dist" (
    echo 前端dist目录不存在，开始构建...
    cd frontend
    call npm install --legacy-peer-deps
    call npm run build
    cd ..
) else (
    echo 前端已构建 ✓
)

echo.
echo 3. 构建Docker镜像...
REM 尝试使用新版本的docker compose命令
docker compose build >nul 2>&1
if %errorlevel% neq 0 (
    echo 尝试使用docker-compose...
    docker-compose build
    if %errorlevel% neq 0 (
        echo 错误: Docker构建失败
        pause
        exit /b 1
    )
)

echo Docker镜像构建完成 ✓

echo.
echo 4. 启动服务...
docker compose up -d >nul 2>&1
if %errorlevel% neq 0 (
    docker-compose up -d
    if %errorlevel% neq 0 (
        echo 错误: 服务启动失败
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo 前端访问地址: http://localhost
echo 后端API地址: http://localhost:8000
echo.
echo 常用命令:
echo   查看状态: docker compose ps
echo   查看日志: docker compose logs -f
echo   停止服务: docker compose down
echo ========================================
pause