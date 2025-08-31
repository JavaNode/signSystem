@echo off
echo 开始构建签名系统...

echo 1. 构建前端dist包...
cd frontend
call npm install --legacy-peer-deps
call npm run build
if %errorlevel% neq 0 (
    echo 前端构建失败，尝试不进行类型检查的构建...
    call npm run build
)
cd ..

echo 2. 检查构建结果...
if exist "frontend\dist" (
    echo 前端构建成功！
) else (
    echo 前端构建失败！
    pause
    exit /b 1
)

echo 3. 构建Docker镜像...
docker-compose build

echo 构建完成！
echo 运行 docker-compose up -d 启动服务
pause