#!/usr/bin/env python3
"""
应用启动脚本
"""

import sys
import os
import uvicorn

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("=" * 60)
    print("联盟杯内训师大赛管理系统")
    print("=" * 60)
    print("正在启动服务器...")
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("管理界面: http://localhost:3000 (需要启动前端)")
    print("=" * 60)
    
    try:
        # 检查数据库是否存在
        if not os.path.exists("data/database.db"):
            print("警告: 数据库文件不存在，请先运行 python init_db.py 初始化数据库")
            return
        
        # 启动服务器
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()