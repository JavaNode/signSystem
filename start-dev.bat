@echo off
echo 启动开发环境...

echo 1. 启动后端服务...
start "后端服务" cmd /k "cd backend && python run.py"

timeout /t 3 /nobreak >nul

echo 2. 启动前端服务...
start "前端服务" cmd /k "cd frontend && npm run dev"

echo 开发环境启动完成！
echo 前端: http://localhost:3000
echo 后端: http://localhost:8000
pause