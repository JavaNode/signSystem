from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from ..models.participant import Participant
from ..models.group import Group
from ..utils.qr_generator import generate_participant_qr
import uuid
import os

class ParticipantService:
    """参赛者服务类"""
    
    @staticmethod
    def create_participant(db: Session, participant_data: Dict[str, Any]) -> Participant:
        """
        创建参赛者
        
        Args:
            db: 数据库会话
            participant_data: 参赛者数据
        
        Returns:
            创建的参赛者对象
        """
        # 生成唯一的二维码ID
        qr_code_id = str(uuid.uuid4())[:8].upper()
        
        # 确保二维码ID唯一
        while db.query(Participant).filter(Participant.qr_code_id == qr_code_id).first():
            qr_code_id = str(uuid.uuid4())[:8].upper()
        
        participant = Participant(
            name=participant_data["name"],
            organization=participant_data["organization"],
            phone=participant_data["phone"],
            phone_last4=participant_data["phone"][-4:],  # 自动提取后四位
            photo_path=participant_data.get("photo_path"),
            group_id=participant_data.get("group_id"),
            qr_code_id=qr_code_id
        )
        
        db.add(participant)
        db.commit()
        db.refresh(participant)
        
        return participant
    
    @staticmethod
    def get_participant_by_id(db: Session, participant_id: int) -> Optional[Participant]:
        """根据ID获取参赛者"""
        return db.query(Participant).filter(Participant.id == participant_id).first()
    
    @staticmethod
    def get_participant_by_qr_code(db: Session, qr_code_id: str) -> Optional[Participant]:
        """根据二维码ID获取参赛者"""
        return db.query(Participant).filter(Participant.qr_code_id == qr_code_id).first()
    
    @staticmethod
    def get_participants_by_group(db: Session, group_id: int) -> List[Participant]:
        """获取指定组的参赛者"""
        return db.query(Participant).filter(Participant.group_id == group_id).all()
    
    @staticmethod
    def get_all_participants(db: Session, skip: int = 0, limit: int = 1000) -> List[Participant]:
        """获取所有参赛者"""
        return db.query(Participant).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_participants(db: Session, keyword: str) -> List[Participant]:
        """搜索参赛者"""
        return db.query(Participant).filter(
            or_(
                Participant.name.contains(keyword),
                Participant.organization.contains(keyword),
                Participant.phone.contains(keyword)
            )
        ).all()
    
    @staticmethod
    def update_participant(db: Session, participant_id: int, 
                          update_data: Dict[str, Any]) -> Optional[Participant]:
        """更新参赛者信息"""
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant:
            return None
        
        for key, value in update_data.items():
            if hasattr(participant, key):
                setattr(participant, key, value)
        
        # 如果更新了手机号，同时更新后四位
        if "phone" in update_data:
            participant.phone_last4 = update_data["phone"][-4:]
        
        db.commit()
        db.refresh(participant)
        return participant
    
    @staticmethod
    def delete_participant(db: Session, participant_id: int) -> bool:
        """删除参赛者"""
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant:
            return False
        
        db.delete(participant)
        db.commit()
        return True
    
    @staticmethod
    def verify_participant_identity(db: Session, qr_code_id: str, 
                                  phone_last4: str, name: str) -> Optional[Participant]:
        """
        验证参赛者身份
        
        Args:
            db: 数据库会话
            qr_code_id: 二维码ID
            phone_last4: 手机后四位
            name: 姓名
        
        Returns:
            验证成功返回参赛者对象，否则返回None
        """
        participant = db.query(Participant).filter(
            and_(
                Participant.qr_code_id == qr_code_id,
                Participant.phone_last4 == phone_last4,
                Participant.name == name
            )
        ).first()
        
        return participant
    
    @staticmethod
    def batch_create_participants(db: Session, participants_data: List[Dict[str, Any]]) -> List[Participant]:
        """批量创建参赛者"""
        participants = []
        
        for data in participants_data:
            # 生成唯一的二维码ID
            qr_code_id = str(uuid.uuid4())[:8].upper()
            
            # 确保二维码ID唯一
            while db.query(Participant).filter(Participant.qr_code_id == qr_code_id).first():
                qr_code_id = str(uuid.uuid4())[:8].upper()
            
            participant = Participant(
                name=data["name"],
                organization=data["organization"],
                phone=data["phone"],
                phone_last4=data["phone"][-4:],
                photo_path=data.get("photo_path"),
                group_id=data.get("group_id"),
                qr_code_id=qr_code_id
            )
            
            participants.append(participant)
        
        db.add_all(participants)
        db.commit()
        
        # 刷新所有对象
        for participant in participants:
            db.refresh(participant)
        
        return participants
    
    @staticmethod
    def generate_qr_codes_for_all(db: Session) -> List[str]:
        """为所有参赛者生成二维码"""
        participants = db.query(Participant).all()
        file_paths = []
        
        for participant in participants:
            try:
                file_path = generate_participant_qr(
                    participant_id=participant.id,
                    qr_code_id=participant.qr_code_id,
                    participant_name=participant.name
                )
                file_paths.append(file_path)
            except Exception as e:
                print(f"生成二维码失败 - 参赛者ID: {participant.id}, 错误: {e}")
        
        return file_paths
    
    @staticmethod
    def get_participants_by_organization(db: Session, organization: str) -> List[Participant]:
        """根据单位获取参赛者"""
        return db.query(Participant).filter(Participant.organization == organization).all()
    
    @staticmethod
    def get_checked_in_participants(db: Session) -> List[Participant]:
        """获取已签到的参赛者"""
        return db.query(Participant).filter(Participant.is_checked_in == True).all()
    
    @staticmethod
    def get_not_checked_in_participants(db: Session) -> List[Participant]:
        """获取未签到的参赛者"""
        return db.query(Participant).filter(Participant.is_checked_in == False).all()
    
    @staticmethod
    def get_participants_statistics(db: Session) -> Dict[str, Any]:
        """获取参赛者统计信息"""
        total_count = db.query(Participant).count()
        checked_in_count = db.query(Participant).filter(Participant.is_checked_in == True).count()
        
        # 按单位统计
        organizations = db.query(Participant.organization).distinct().all()
        org_stats = []
        
        for (org,) in organizations:
            org_total = db.query(Participant).filter(Participant.organization == org).count()
            org_checked_in = db.query(Participant).filter(
                and_(Participant.organization == org, Participant.is_checked_in == True)
            ).count()
            
            org_stats.append({
                "organization": org,
                "total": org_total,
                "checked_in": org_checked_in,
                "checkin_rate": round(org_checked_in / org_total * 100, 2) if org_total > 0 else 0
            })
        
        return {
            "total_participants": total_count,
            "checked_in_participants": checked_in_count,
            "checkin_rate": round(checked_in_count / total_count * 100, 2) if total_count > 0 else 0,
            "organization_stats": org_stats
        }