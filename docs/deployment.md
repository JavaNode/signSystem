# 签名系统部署指南

## 前置要求

- Docker 和 Docker Compose
- Node.js 18+ (用于前端构建)

## 快速部署

### 方法一：使用构建脚本

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

**Windows:**
```cmd
build.bat
```

### 方法二：手动构建

1. **构建前端dist包:**
```bash
cd frontend
npm install
npm run build
cd ..
```

2. **构建并启动Docker容器:**
```bash
docker-compose build
docker-compose up -d
```

## 访问应用

- 前端: http://localhost
- 后端API: http://localhost:8000

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up --build -d

# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

## 生产环境配置

1. 修改 `docker-compose.yml` 中的环境变量
2. 配置域名和SSL证书
3. 设置数据库连接
4. 配置文件存储路径

## 故障排除

1. **端口冲突**: 修改 `docker-compose.yml` 中的端口映射
2. **构建失败**: 检查Docker和Node.js版本
3. **权限问题**: 确保数据目录有正确的读写权限