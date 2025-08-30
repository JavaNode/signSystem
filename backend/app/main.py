from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .database import init_database
from .api import api_router

# 创建FastAPI应用
app = FastAPI(
    title="联盟杯内训师大赛管理系统",
    description="支持签到、分组、抽签、评分、照片展示等功能的完整比赛管理系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务
if os.path.exists("data"):
    app.mount("/static", StaticFiles(directory="data"), name="static")

# 注册API路由
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_database()
    print("数据库初始化完成")
    print("应用启动成功！")
    print("API文档地址: http://localhost:8000/docs")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "联盟杯内训师大赛管理系统",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "系统运行正常"}

# 文件下载接口
@app.get("/download/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """下载文件"""
    # 定义允许的文件类型和对应的目录
    allowed_types = {
        "photos": "data/photos",
        "exports": "data/exports",
        "qrcodes": "data/qrcodes"
    }
    
    if file_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    file_path = os.path.join(allowed_types[file_type], filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "资源不存在", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "服务器内部错误", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )