#!/usr/bin/env python3
"""
系统快速测试脚本
用于验证后端API和前端页面是否正常工作
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_backend_api():
    """测试后端API"""
    print("=" * 50)
    print("测试后端API服务")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 测试根路径
        print("1. 测试根路径...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
            return False
            
        # 测试参赛者列表
        print("\n2. 测试参赛者列表...")
        response = requests.get(f"{base_url}/api/participants", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 参赛者列表获取成功，共 {data.get('total', 0)} 人")
        else:
            print(f"❌ 参赛者列表获取失败: {response.status_code}")
            
        # 测试分组列表
        print("\n3. 测试分组列表...")
        response = requests.get(f"{base_url}/api/groups", timeout=5)
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ 分组列表获取成功，共 {len(groups)} 个组")
        else:
            print(f"❌ 分组列表获取失败: {response.status_code}")
            
        # 测试统计数据
        print("\n4. 测试统计数据...")
        response = requests.get(f"{base_url}/api/statistics/overview", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ 统计数据获取成功")
            print(f"   总参赛者: {stats.get('total_participants', 0)}")
            print(f"   已签到: {stats.get('checked_in_count', 0)}")
            print(f"   签到率: {stats.get('checkin_rate', 0):.1f}%")
        else:
            print(f"❌ 统计数据获取失败: {response.status_code}")
            
        # 测试签到验证
        print("\n5. 测试签到验证...")
        test_data = {
            "qr_code_id": "QR001",
            "phone_last4": "5678",
            "name": "张三"
        }
        response = requests.post(f"{base_url}/api/checkin/verify", 
                               json=test_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 签到验证成功")
                print(f"   参赛者: {result['participant']['name']}")
            else:
                print(f"⚠️  签到验证返回: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 签到验证失败: {response.status_code}")
            
        print("\n✅ 后端API测试完成")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务已启动")
        print("   启动命令: cd backend && python simple_app.py")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def test_frontend_access():
    """测试前端访问"""
    print("\n" + "=" * 50)
    print("测试前端服务")
    print("=" * 50)
    
    frontend_url = "http://localhost:3000"
    
    try:
        print("1. 测试前端页面访问...")
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ 前端页面访问成功")
            return True
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到前端服务，请确保前端服务已启动")
        print("   启动命令: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def show_test_accounts():
    """显示测试账号信息"""
    print("\n" + "=" * 50)
    print("测试账号信息")
    print("=" * 50)
    
    print("管理员账号:")
    print("  用户名: admin")
    print("  密码: admin123")
    print("  访问地址: http://localhost:3000/admin")
    
    print("\n评委账号:")
    print("  用户名: judge01")
    print("  密码: 123456")
    print("  访问地址: http://localhost:3000/judge/score")
    
    print("\n测试参赛者 (用于签到测试):")
    participants = [
        {"name": "张三", "qr": "QR001", "phone": "5678"},
        {"name": "李四", "qr": "QR002", "phone": "4321"},
        {"name": "王五", "qr": "QR003", "phone": "1111"},
        {"name": "赵六", "qr": "QR004", "phone": "2222"},
        {"name": "孙七", "qr": "QR005", "phone": "3333"},
    ]
    
    for p in participants:
        print(f"  姓名: {p['name']}, 二维码: {p['qr']}, 手机后四位: {p['phone']}")
        print(f"  签到地址: http://localhost:3000/mobile/checkin/{p['qr']}")

def show_system_urls():
    """显示系统访问地址"""
    print("\n" + "=" * 50)
    print("系统访问地址")
    print("=" * 50)
    
    urls = [
        ("后端API服务", "http://localhost:8000"),
        ("API接口文档", "http://localhost:8000/docs"),
        ("前端管理界面", "http://localhost:3000"),
        ("管理员仪表板", "http://localhost:3000/admin"),
        ("参赛者管理", "http://localhost:3000/admin/participants"),
        ("评委打分页面", "http://localhost:3000/judge/score"),
        ("移动端签到", "http://localhost:3000/mobile/checkin"),
    ]
    
    for name, url in urls:
        print(f"  {name}: {url}")

def main():
    """主函数"""
    print("联盟杯内训师大赛管理系统 - 系统测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试后端API
    backend_ok = test_backend_api()
    
    # 测试前端访问
    frontend_ok = test_frontend_access()
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    if backend_ok:
        print("✅ 后端服务: 正常")
    else:
        print("❌ 后端服务: 异常")
        
    if frontend_ok:
        print("✅ 前端服务: 正常")
    else:
        print("❌ 前端服务: 异常")
    
    if backend_ok and frontend_ok:
        print("\n🎉 系统测试通过！所有服务运行正常")
    else:
        print("\n⚠️  部分服务异常，请检查服务启动状态")
    
    # 显示系统信息
    show_system_urls()
    show_test_accounts()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()