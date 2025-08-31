#!/bin/bash

echo "开始构建签名系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 构建前端dist包
echo "正在构建前端..."
cd frontend
npm install
npm run build
cd ..

# 构建Docker镜像
echo "正在构建Docker镜像..."
docker-compose build

echo "构建完成！"
echo "运行以下命令启动服务:"
echo "docker-compose up -d"