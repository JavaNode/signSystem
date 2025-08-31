@echo off
echo 开始构建签名系统...

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未运行，请先启动Docker
    pause
    exit /b 1
)

REM 构建前端dist包
echo 正在构建前端...
cd frontend
call npm install
call npm run build
cd ..

REM 构建Docker镜像
echo 正在构建Docker镜像...
docker-compose build

echo 构建完成！
echo 运行以下命令启动服务:
echo docker-compose up -d
pause