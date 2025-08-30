from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class CheckinLog(Base):
    __tablename__ = "checkin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, comment="参赛者ID")
    checkin_time = Column(DateTime, nullable=False, comment="签到时间")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    participant = relationship("Participant", back_populates="checkin_logs")
    
    def __repr__(self):
        return f"<CheckinLog(id={self.id}, participant_id={self.participant_id}, checkin_time={self.checkin_time})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "participant_name": self.participant.name if self.participant else None,
            "checkin_time": self.checkin_time.isoformat() if self.checkin_time else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }