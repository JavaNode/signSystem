.PHONY: build up down logs clean rebuild config-check

# 检查配置
config-check:
	@echo "检查配置文件..."
	@if [ ! -f backend/.env ]; then \
		echo "警告: backend/.env 文件不存在，将使用默认配置"; \
		echo "建议复制 backend/.env.example 到 backend/.env 并修改配置"; \
	fi
	@echo "当前配置:"
	@echo "- 环境: $$(grep ENVIRONMENT backend/.env 2>/dev/null || echo 'ENVIRONMENT=development')"
	@echo "- 前端URL: $$(grep FRONTEND_URL backend/.env 2>/dev/null || echo 'FRONTEND_URL=http://localhost:5173')"
	@echo "- 移动端URL: $$(grep MOBILE_BASE_URL backend/.env 2>/dev/null || echo 'MOBILE_BASE_URL=http://localhost:3000')"

# 构建服务（使用缓存）
build: config-check
	docker-compose build --parallel

# 启动服务
up: config-check
	docker-compose up -d

# 停止服务
down:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f

# 查看后端日志
logs-backend:
	docker-compose logs -f backend

# 重新构建（不使用缓存）
rebuild:
	docker-compose build --no-cache --parallel

# 清理未使用的镜像和容器
clean:
	docker system prune -f
	docker image prune -f

# 完全重启
restart: down up

# 进入后端容器
shell:
	docker-compose exec backend /bin/bash

# 查看服务状态
status:
	docker-compose ps

# 初始化配置文件
init-config:
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "已创建 backend/.env 配置文件，请根据需要修改配置"; \
	else \
		echo "backend/.env 已存在"; \
	fi

# 生产环境部署
deploy-prod: init-config
	@echo "部署到生产环境..."
	@echo "请确保已正确配置 backend/.env 文件中的域名和安全设置"
	docker-compose build --no-cache
	docker-compose up -d
	@echo "部署完成！"
	@echo "API地址: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"