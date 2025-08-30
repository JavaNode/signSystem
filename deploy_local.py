#!/usr/bin/env python3
"""
本地部署脚本 - 联盟杯内训师大赛管理系统
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def run_command(command, cwd=None):
    """执行命令"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"执行命令失败: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("检查系统依赖...")
    
    # 检查Python
    try:
        import sys
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("错误: 需要Python 3.8或更高版本")
            return False
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except:
        print("错误: 未找到Python")
        return False
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js {result.stdout.strip()}")
        else:
            print("警告: 未找到Node.js，前端将无法启动")
    except:
        print("警告: 未找到Node.js，前端将无法启动")
    
    return True

def install_backend_deps():
    """安装后端依赖"""
    print("\n安装后端依赖...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("错误: backend目录不存在")
        return False
    
    # 安装Python依赖
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print("安装Python包...")
        if not run_command("pip install -r requirements.txt", cwd=backend_dir):
            print("尝试使用pip3...")
            if not run_command("pip3 install -r requirements.txt", cwd=backend_dir):
                print("错误: 无法安装Python依赖")
                return False
        print("✓ 后端依赖安装完成")
    else:
        print("警告: 未找到requirements.txt")
    
    return True

def install_frontend_deps():
    """安装前端依赖"""
    print("\n安装前端依赖...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("错误: frontend目录不存在")
        return False
    
    package_json = frontend_dir / "package.json"
    if package_json.exists():
        print("安装Node.js包...")
        if not run_command("npm install", cwd=frontend_dir):
            print("尝试使用yarn...")
            if not run_command("yarn install", cwd=frontend_dir):
                print("错误: 无法安装前端依赖")
                return False
        print("✓ 前端依赖安装完成")
    else:
        print("警告: 未找到package.json")
    
    return True

def start_backend():
    """启动后端服务"""
    print("\n启动后端服务...")
    backend_dir = Path("backend")
    
    # 使用修复版应用
    app_file = backend_dir / "app_fixed.py"
    if app_file.exists():
        print("使用修复版后端应用...")
        subprocess.Popen([sys.executable, "app_fixed.py"], cwd=backend_dir)
    else:
        # 使用简化版应用
        simple_app = backend_dir / "simple_app.py"
        if simple_app.exists():
            print("使用简化版后端应用...")
            subprocess.Popen([sys.executable, "simple_app.py"], cwd=backend_dir)
        else:
            print("错误: 未找到后端应用文件")
            return False
    
    print("✓ 后端服务启动中...")
    return True

def start_frontend():
    """启动前端服务"""
    print("\n启动前端服务...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("警告: frontend目录不存在，跳过前端启动")
        return True
    
    package_json = frontend_dir / "package.json"
    if package_json.exists():
        print("启动前端开发服务器...")
        subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)
        print("✓ 前端服务启动中...")
    else:
        print("警告: 未找到package.json，跳过前端启动")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("联盟杯内训师大赛管理系统 - 本地部署")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请安装必要的依赖后重试")
        return
    
    # 安装依赖
    if not install_backend_deps():
        print("后端依赖安装失败")
        return
    
    install_frontend_deps()  # 前端依赖安装失败不影响后端运行
    
    # 启动服务
    if not start_backend():
        print("后端启动失败")
        return
    
    start_frontend()  # 前端启动失败不影响后端运行
    
    # 等待服务启动
    print("\n等待服务启动...")
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("部署完成！")
    print("=" * 60)
    print("后端API: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("前端应用: http://localhost:5173")
    print("=" * 60)
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 自动打开浏览器
    try:
        time.sleep(2)
        webbrowser.open("http://localhost:8000/docs")
    except:
        pass
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")

if __name__ == "__main__":
    main()