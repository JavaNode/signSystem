#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始化基础数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_database, SessionLocal
from app.models import Participant, Group, Judge, Score, CheckinLog
from app.services.judge_service import JudgeService
from app.services.group_service import GroupService
from app.utils.auth import hash_password

def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()
    
    try:
        print("正在创建示例数据...")
        
        # 创建示例分组
        print("创建示例分组...")
        groups_data = [
            {"name": "第1组", "description": "XX银行 + YY银行"},
            {"name": "第2组", "description": "ZZ银行"},
            {"name": "第3组", "description": "AA银行 + BB银行"},
        ]
        
        created_groups = []
        for group_data in groups_data:
            group = GroupService.create_group(db, group_data["name"], group_data["description"])
            created_groups.append(group)
            print(f"  - 创建分组: {group.name}")
        
        # 创建示例评委
        print("创建示例评委...")
        judges_data = [
            {"name": "张评委", "username": "judge01", "password": "123456", "organization": "评委组"},
            {"name": "李评委", "username": "judge02", "password": "123456", "organization": "评委组"},
            {"name": "王评委", "username": "judge03", "password": "123456", "organization": "评委组"},
            {"name": "赵评委", "username": "judge04", "password": "123456", "organization": "评委组"},
            {"name": "孙评委", "username": "judge05", "password": "123456", "organization": "评委组"},
        ]
        
        for judge_data in judges_data:
            try:
                judge = JudgeService.create_judge(
                    db, 
                    judge_data["name"], 
                    judge_data["username"], 
                    judge_data["password"], 
                    judge_data["organization"]
                )
                print(f"  - 创建评委: {judge.name} (用户名: {judge.username})")
            except ValueError as e:
                print(f"  - 跳过评委 {judge_data['name']}: {e}")
        
        # 创建管理员账号
        print("创建管理员账号...")
        try:
            admin_judge = JudgeService.create_judge(
                db, "系统管理员", "admin", "admin123", "管理组"
            )
            print(f"  - 创建管理员: {admin_judge.name} (用户名: {admin_judge.username})")
        except ValueError as e:
            print(f"  - 跳过管理员: {e}")
        
        print("示例数据创建完成！")
        
    except Exception as e:
        print(f"创建示例数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 50)
    print("联盟杯内训师大赛管理系统 - 数据库初始化")
    print("=" * 50)
    
    try:
        # 初始化数据库
        print("正在初始化数据库...")
        init_database()
        print("数据库初始化完成！")
        
        # 询问是否创建示例数据
        create_sample = input("\n是否创建示例数据？(y/N): ").lower().strip()
        if create_sample in ['y', 'yes']:
            create_sample_data()
        
        print("\n" + "=" * 50)
        print("初始化完成！")
        print("=" * 50)
        print("系统信息:")
        print("- 数据库文件: data/database.db")
        print("- 照片目录: data/photos/")
        print("- 导出目录: data/exports/")
        print("- 二维码目录: data/qrcodes/")
        print("\n默认账号:")
        print("- 管理员: admin / admin123")
        print("- 评委示例: judge01 / 123456")
        print("\n启动命令:")
        print("- cd backend && python run.py")
        print("- 访问地址: http://localhost:8000")
        print("- API文档: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()