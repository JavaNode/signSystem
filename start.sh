#!/bin/bash

echo "========================================"
echo "联盟杯内训师大赛管理系统 - 快速启动"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

echo "正在启动后端服务..."
cd backend

# 检查并安装Python依赖
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 启动后端服务
echo "启动后端API服务..."
python simple_app.py &
BACKEND_PID=$!

cd ..

echo "等待后端服务启动..."
sleep 3

echo "正在启动前端服务..."
cd frontend

# 检查并安装Node.js依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端服务
echo "启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo
echo "========================================"
echo "服务启动完成！"
echo "========================================"
echo "后端服务: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "前端服务: http://localhost:3000"
echo "========================================"
echo
echo "默认测试账号:"
echo "管理员: admin / admin123"
echo "评委: judge01 / 123456"
echo "========================================"
echo
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
wait