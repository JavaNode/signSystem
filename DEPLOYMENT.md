# 联盟杯内训师大赛管理系统 - 部署指南

## 配置化改进说明

系统已经完成配置化改造，解决了原有的硬编码问题，现在支持通过环境变量进行灵活配置。

## 主要改进

### 1. 配置管理
- 新增 `backend/config.py` 配置管理模块
- 支持通过 `.env` 文件和环境变量配置
- 区分开发环境和生产环境配置

### 2. 解决的硬编码问题
- ✅ API服务地址配置化
- ✅ 前端和移动端URL配置化
- ✅ CORS域名配置化
- ✅ 比赛信息配置化
- ✅ 评分范围配置化
- ✅ 二维码生成URL配置化

## 快速部署

### 1. 初始化配置
```bash
# 创建配置文件
make init-config

# 编辑配置文件
nano backend/.env
```

### 2. 修改关键配置
编辑 `backend/.env` 文件，修改以下配置：

```env
# 环境配置
ENVIRONMENT=production
DEBUG=false

# 前端配置 - 修改为实际的域名
FRONTEND_URL=http://your-domain.com:5173
MOBILE_BASE_URL=http://your-domain.com:3000

# CORS配置 - 添加实际域名
CORS_ORIGINS=http://your-domain.com:3000,http://your-domain.com:5173

# 安全配置 - 修改为强密码
SECRET_KEY=your-very-secure-secret-key-here
DEFAULT_ADMIN_PASSWORD=your-secure-admin-password
```

### 3. 部署服务
```bash
# 生产环境部署
make deploy-prod

# 或者手动部署
make build
make up
```

### 4. 验证部署
```bash
# 查看服务状态
make status

# 查看日志
make logs

# 检查配置
make config-check
```

## 配置说明

### 环境变量列表

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ENVIRONMENT` | `development` | 运行环境 (development/production) |
| `DEBUG` | `true` | 调试模式 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `FRONTEND_URL` | `http://localhost:5173` | 前端访问地址 |
| `MOBILE_BASE_URL` | `http://localhost:3000` | 移动端基础地址 |
| `CORS_ORIGINS` | `http://localhost:3000,...` | 允许的跨域地址 |
| `COMPETITION_NAME` | `联盟杯内训师大赛` | 比赛名称 |
| `COMPETITION_DATE` | `2024年9月24日` | 比赛日期 |
| `COMPETITION_LOCATION` | `比赛现场` | 比赛地点 |

### Docker Compose 环境变量

在 `docker-compose.yml` 中也可以直接配置环境变量：

```yaml
environment:
  - ENVIRONMENT=production
  - FRONTEND_URL=http://your-domain.com:5173
  - MOBILE_BASE_URL=http://your-domain.com:3000
  # ... 其他配置
```

## 常用命令

```bash
# 检查配置
make config-check

# 构建并启动
make build && make up

# 查看日志
make logs-backend

# 重启服务
make restart

# 进入容器调试
make shell

# 清理资源
make clean
```

## 故障排除

### 1. 导入模块错误
如果遇到 `Error loading ASGI app. Could not import module "app.main"` 错误：
- 确认 Dockerfile 中的启动命令是 `app_fixed:app`
- 检查文件结构是否正确

### 2. 跨域问题
如果前端无法访问API：
- 检查 `CORS_ORIGINS` 配置是否包含前端域名
- 确认前端请求的API地址是否正确

### 3. 二维码链接错误
如果二维码扫描后链接不正确：
- 检查 `MOBILE_BASE_URL` 配置
- 确认移动端服务是否正常运行

## 安全建议

1. **修改默认密码**：更改 `DEFAULT_ADMIN_PASSWORD`
2. **设置强密钥**：修改 `SECRET_KEY` 为复杂字符串
3. **限制CORS**：生产环境中不要使用 `*` 作为CORS配置
4. **使用HTTPS**：生产环境建议配置SSL证书

## 监控和日志

```bash
# 实时查看日志
docker-compose logs -f backend

# 查看容器状态
docker-compose ps

# 查看资源使用情况
docker stats signSystem