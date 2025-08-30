from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.participant import Participant
from ..models.checkin_log import CheckinLog
from .participant_service import ParticipantService

class CheckinService:
    """签到服务类"""
    
    @staticmethod
    def process_checkin(db: Session, qr_code_id: str, phone_last4: str, 
                       name: str, ip_address: str = None, 
                       user_agent: str = None) -> Dict[str, Any]:
        """
        处理签到流程
        
        Args:
            db: 数据库会话
            qr_code_id: 二维码ID
            phone_last4: 手机后四位
            name: 姓名
            ip_address: IP地址
            user_agent: 用户代理
        
        Returns:
            签到结果
        """
        # 验证参赛者身份
        participant = ParticipantService.verify_participant_identity(
            db, qr_code_id, phone_last4, name
        )
        
        if not participant:
            return {
                "success": False,
                "message": "身份验证失败，请检查输入信息是否正确",
                "error_code": "IDENTITY_VERIFICATION_FAILED"
            }
        
        # 检查是否已经签到
        if participant.is_checked_in:
            return {
                "success": False,
                "message": f"您已于 {participant.checkin_time.strftime('%H:%M:%S')} 完成签到",
                "error_code": "ALREADY_CHECKED_IN",
                "participant": participant.to_dict()
            }
        
        # 执行签到
        checkin_time = datetime.now()
        
        # 更新参赛者签到状态
        participant.is_checked_in = True
        participant.checkin_time = checkin_time
        
        # 创建签到日志
        checkin_log = CheckinLog(
            participant_id=participant.id,
            checkin_time=checkin_time,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(checkin_log)
        db.commit()
        db.refresh(participant)
        
        return {
            "success": True,
            "message": "签到成功！",
            "participant": participant.to_dict(),
            "checkin_time": checkin_time.isoformat()
        }
    
    @staticmethod
    def get_checkin_info(db: Session, qr_code_id: str) -> Optional[Dict[str, Any]]:
        """
        根据二维码ID获取签到信息
        
        Args:
            db: 数据库会话
            qr_code_id: 二维码ID
        
        Returns:
            参赛者基本信息（用于验证页面显示）
        """
        participant = ParticipantService.get_participant_by_qr_code(db, qr_code_id)
        
        if not participant:
            return None
        
        return {
            "qr_code_id": qr_code_id,
            "participant_exists": True,
            "is_checked_in": participant.is_checked_in,
            "checkin_time": participant.checkin_time.isoformat() if participant.checkin_time else None
        }
    
    @staticmethod
    def get_participant_checkin_status(db: Session, participant_id: int) -> Dict[str, Any]:
        """获取参赛者签到状态"""
        participant = ParticipantService.get_participant_by_id(db, participant_id)
        
        if not participant:
            return {"exists": False}
        
        # 获取签到日志
        checkin_logs = db.query(CheckinLog).filter(
            CheckinLog.participant_id == participant_id
        ).order_by(CheckinLog.checkin_time.desc()).all()
        
        return {
            "exists": True,
            "participant": participant.to_dict(),
            "is_checked_in": participant.is_checked_in,
            "checkin_time": participant.checkin_time.isoformat() if participant.checkin_time else None,
            "checkin_logs": [log.to_dict() for log in checkin_logs]
        }
    
    @staticmethod
    def manual_checkin(db: Session, participant_id: int, 
                      admin_note: str = None) -> Dict[str, Any]:
        """
        管理员手动签到
        
        Args:
            db: 数据库会话
            participant_id: 参赛者ID
            admin_note: 管理员备注
        
        Returns:
            签到结果
        """
        participant = ParticipantService.get_participant_by_id(db, participant_id)
        
        if not participant:
            return {
                "success": False,
                "message": "参赛者不存在",
                "error_code": "PARTICIPANT_NOT_FOUND"
            }
        
        if participant.is_checked_in:
            return {
                "success": False,
                "message": "该参赛者已经签到",
                "error_code": "ALREADY_CHECKED_IN"
            }
        
        # 执行签到
        checkin_time = datetime.now()
        participant.is_checked_in = True
        participant.checkin_time = checkin_time
        
        # 创建签到日志
        user_agent = f"MANUAL_CHECKIN: {admin_note}" if admin_note else "MANUAL_CHECKIN"
        checkin_log = CheckinLog(
            participant_id=participant.id,
            checkin_time=checkin_time,
            ip_address="ADMIN",
            user_agent=user_agent
        )
        
        db.add(checkin_log)
        db.commit()
        db.refresh(participant)
        
        return {
            "success": True,
            "message": "手动签到成功",
            "participant": participant.to_dict()
        }
    
    @staticmethod
    def cancel_checkin(db: Session, participant_id: int, 
                      admin_note: str = None) -> Dict[str, Any]:
        """
        取消签到（管理员功能）
        
        Args:
            db: 数据库会话
            participant_id: 参赛者ID
            admin_note: 管理员备注
        
        Returns:
            操作结果
        """
        participant = ParticipantService.get_participant_by_id(db, participant_id)
        
        if not participant:
            return {
                "success": False,
                "message": "参赛者不存在",
                "error_code": "PARTICIPANT_NOT_FOUND"
            }
        
        if not participant.is_checked_in:
            return {
                "success": False,
                "message": "该参赛者尚未签到",
                "error_code": "NOT_CHECKED_IN"
            }
        
        # 取消签到
        participant.is_checked_in = False
        participant.checkin_time = None
        
        # 创建取消签到日志
        user_agent = f"CANCEL_CHECKIN: {admin_note}" if admin_note else "CANCEL_CHECKIN"
        checkin_log = CheckinLog(
            participant_id=participant.id,
            checkin_time=datetime.now(),
            ip_address="ADMIN",
            user_agent=user_agent
        )
        
        db.add(checkin_log)
        db.commit()
        db.refresh(participant)
        
        return {
            "success": True,
            "message": "取消签到成功",
            "participant": participant.to_dict()
        }
    
    @staticmethod
    def get_checkin_statistics(db: Session) -> Dict[str, Any]:
        """获取签到统计信息"""
        return ParticipantService.get_participants_statistics(db)
    
    @staticmethod
    def get_recent_checkins(db: Session, limit: int = 50) -> list:
        """获取最近的签到记录"""
        recent_logs = db.query(CheckinLog).order_by(
            CheckinLog.checkin_time.desc()
        ).limit(limit).all()
        
        return [log.to_dict() for log in recent_logs]
    
    @staticmethod
    def export_checkin_data(db: Session) -> Dict[str, Any]:
        """导出签到数据"""
        participants = ParticipantService.get_all_participants(db)
        
        checkin_data = []
        for participant in participants:
            checkin_data.append({
                "id": participant.id,
                "name": participant.name,
                "organization": participant.organization,
                "phone": participant.phone,
                "group_name": participant.group.name if participant.group else "未分组",
                "is_checked_in": participant.is_checked_in,
                "checkin_time": participant.checkin_time.strftime('%Y-%m-%d %H:%M:%S') if participant.checkin_time else "",
                "qr_code_id": participant.qr_code_id
            })
        
        return {
            "total_count": len(participants),
            "checked_in_count": len([p for p in participants if p.is_checked_in]),
            "data": checkin_data
        }