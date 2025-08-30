@echo off
echo ========================================
echo 联盟杯内训师大赛管理系统 - 快速启动
echo ========================================
echo.

echo 正在启动后端服务...
cd backend
start "后端服务" cmd /k "python simple_app.py"
cd ..

echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo 正在启动前端服务...
cd frontend
start "前端服务" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo 后端服务: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 前端服务: http://localhost:3000
echo ========================================
echo.
echo 默认测试账号:
echo 管理员: admin / admin123
echo 评委: judge01 / 123456
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul