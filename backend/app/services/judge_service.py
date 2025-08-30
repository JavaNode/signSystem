from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..models.judge import Judge
from ..utils.auth import hash_password, verify_password, create_judge_token

class JudgeService:
    """评委服务类"""
    
    @staticmethod
    def create_judge(db: Session, name: str, username: str, 
                    password: str, organization: str = None) -> Judge:
        """
        创建评委
        
        Args:
            db: 数据库会话
            name: 评委姓名
            username: 登录用户名
            password: 登录密码
            organization: 所属单位
        
        Returns:
            创建的评委对象
        """
        # 检查用户名是否已存在
        existing_judge = db.query(Judge).filter(Judge.username == username).first()
        if existing_judge:
            raise ValueError(f"用户名 '{username}' 已存在")
        
        # 创建评委
        judge = Judge(
            name=name,
            username=username,
            password=hash_password(password),
            organization=organization
        )
        
        db.add(judge)
        db.commit()
        db.refresh(judge)
        
        return judge
    
    @staticmethod
    def get_judge_by_id(db: Session, judge_id: int) -> Optional[Judge]:
        """根据ID获取评委"""
        return db.query(Judge).filter(Judge.id == judge_id).first()
    
    @staticmethod
    def get_judge_by_username(db: Session, username: str) -> Optional[Judge]:
        """根据用户名获取评委"""
        return db.query(Judge).filter(Judge.username == username).first()
    
    @staticmethod
    def get_all_judges(db: Session, include_inactive: bool = False) -> List[Judge]:
        """获取所有评委"""
        query = db.query(Judge)
        if not include_inactive:
            query = query.filter(Judge.is_active == True)
        return query.all()
    
    @staticmethod
    def authenticate_judge(db: Session, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        评委登录验证
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
        
        Returns:
            验证成功返回评委信息和token，否则返回None
        """
        judge = JudgeService.get_judge_by_username(db, username)
        
        if not judge:
            return None
        
        if not judge.is_active:
            return None
        
        if not verify_password(password, judge.password):
            return None
        
        # 生成访问令牌
        token = create_judge_token(judge.id, judge.username)
        
        return {
            "judge": judge.to_dict(),
            "token": token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def update_judge(db: Session, judge_id: int, 
                    update_data: Dict[str, Any]) -> Optional[Judge]:
        """更新评委信息"""
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        if not judge:
            return None
        
        # 如果更新密码，需要加密
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])
        
        # 如果更新用户名，检查是否重复
        if "username" in update_data:
            existing_judge = db.query(Judge).filter(
                Judge.username == update_data["username"],
                Judge.id != judge_id
            ).first()
            if existing_judge:
                raise ValueError(f"用户名 '{update_data['username']}' 已存在")
        
        for key, value in update_data.items():
            if hasattr(judge, key):
                setattr(judge, key, value)
        
        db.commit()
        db.refresh(judge)
        return judge
    
    @staticmethod
    def delete_judge(db: Session, judge_id: int) -> bool:
        """删除评委"""
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        if not judge:
            return False
        
        db.delete(judge)
        db.commit()
        return True
    
    @staticmethod
    def deactivate_judge(db: Session, judge_id: int) -> bool:
        """停用评委"""
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        if not judge:
            return False
        
        judge.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def activate_judge(db: Session, judge_id: int) -> bool:
        """激活评委"""
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        if not judge:
            return False
        
        judge.is_active = True
        db.commit()
        return True
    
    @staticmethod
    def reset_judge_password(db: Session, judge_id: int, new_password: str) -> bool:
        """重置评委密码"""
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        if not judge:
            return False
        
        judge.password = hash_password(new_password)
        db.commit()
        return True
    
    @staticmethod
    def batch_create_judges(db: Session, judges_data: List[Dict[str, Any]]) -> List[Judge]:
        """批量创建评委"""
        judges = []
        
        for data in judges_data:
            # 检查用户名是否已存在
            existing_judge = db.query(Judge).filter(Judge.username == data["username"]).first()
            if existing_judge:
                continue  # 跳过已存在的用户名
            
            judge = Judge(
                name=data["name"],
                username=data["username"],
                password=hash_password(data["password"]),
                organization=data.get("organization")
            )
            
            judges.append(judge)
        
        if judges:
            db.add_all(judges)
            db.commit()
            
            # 刷新所有对象
            for judge in judges:
                db.refresh(judge)
        
        return judges
    
    @staticmethod
    def get_judge_statistics(db: Session) -> Dict[str, Any]:
        """获取评委统计信息"""
        total_judges = db.query(Judge).count()
        active_judges = db.query(Judge).filter(Judge.is_active == True).count()
        inactive_judges = total_judges - active_judges
        
        # 按单位统计
        judges = db.query(Judge).all()
        org_stats = {}
        
        for judge in judges:
            org = judge.organization or "未指定单位"
            if org not in org_stats:
                org_stats[org] = {"total": 0, "active": 0}
            
            org_stats[org]["total"] += 1
            if judge.is_active:
                org_stats[org]["active"] += 1
        
        org_list = [
            {
                "organization": org,
                "total": stats["total"],
                "active": stats["active"]
            }
            for org, stats in org_stats.items()
        ]
        
        return {
            "total_judges": total_judges,
            "active_judges": active_judges,
            "inactive_judges": inactive_judges,
            "organization_stats": org_list
        }
    
    @staticmethod
    def change_judge_password(db: Session, judge_id: int, 
                             old_password: str, new_password: str) -> Dict[str, Any]:
        """
        评委修改密码
        
        Args:
            db: 数据库会话
            judge_id: 评委ID
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            操作结果
        """
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        
        if not judge:
            return {"success": False, "message": "评委不存在"}
        
        if not verify_password(old_password, judge.password):
            return {"success": False, "message": "原密码错误"}
        
        judge.password = hash_password(new_password)
        db.commit()
        
        return {"success": True, "message": "密码修改成功"}
    
    @staticmethod
    def get_judge_profile(db: Session, judge_id: int) -> Optional[Dict[str, Any]]:
        """获取评委个人信息"""
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        
        if not judge:
            return None
        
        return {
            "id": judge.id,
            "name": judge.name,
            "username": judge.username,
            "organization": judge.organization,
            "is_active": judge.is_active,
            "score_count": judge.score_count,
            "created_at": judge.created_at.isoformat() if judge.created_at else None
        }