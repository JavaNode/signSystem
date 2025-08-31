#!/usr/bin/env python3
"""
配置管理模块
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本配置
    app_title: str = "联盟杯内训师大赛管理系统"
    app_description: str = "支持签到、分组、抽签、打分等功能的比赛管理系统"
    app_version: str = "1.0.0"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 前端配置
    frontend_url: str = "http://localhost:5173"
    mobile_base_url: str = "http://localhost:3000"
    
    # API配置
    api_docs_url: str = "/docs"
    api_redoc_url: str = "/redoc"
    
    # CORS配置
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8080"
    
    # 数据存储配置
    data_dir: str = "./data"
    photos_dir: str = "./data/photos"
    exports_dir: str = "./data/exports"
    
    # 数据库配置（如果使用数据库）
    database_url: str = "sqlite:///./data/signSystem.db"
    
    # 比赛信息配置
    competition_name: str = "联盟杯内训师大赛"
    competition_date: str = "2024年9月24日"
    competition_location: str = "比赛现场"
    
    # 默认管理员配置
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # 评分配置
    min_score: float = 0.0
    max_score: float = 10.0
    
    # 二维码配置
    qr_code_version: int = 1
    qr_code_box_size: int = 10
    qr_code_border: int = 5
    
    # 环境配置
    environment: str = "development"  # development, production, testing
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()

def get_settings() -> Settings:
    """获取配置实例"""
    return settings

def get_frontend_url() -> str:
    """获取前端URL"""
    return settings.frontend_url

def get_mobile_base_url() -> str:
    """获取移动端基础URL"""
    return settings.mobile_base_url

def get_checkin_url(qr_code_id: str = None) -> str:
    """获取签到URL"""
    base_url = get_mobile_base_url()
    if qr_code_id:
        return f"{base_url}/mobile/checkin/{qr_code_id}"
    return f"{base_url}/mobile/checkin"

def get_api_url() -> str:
    """获取API基础URL"""
    if settings.environment == "production":
        return f"http://{settings.host}:{settings.port}"
    return f"http://localhost:{settings.port}"

def is_production() -> bool:
    """判断是否为生产环境"""
    return settings.environment == "production"

def is_development() -> bool:
    """判断是否为开发环境"""
    return settings.environment == "development"

def get_cors_origins() -> List[str]:
    """获取CORS配置列表"""
    if isinstance(settings.cors_origins, str):
        return [origin.strip() for origin in settings.cors_origins.split(",")]
    return settings.cors_origins