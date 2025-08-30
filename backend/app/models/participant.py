from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="姓名")
    organization = Column(String(200), nullable=False, comment="单位")
    phone = Column(String(20), nullable=False, comment="完整手机号")
    phone_last4 = Column(String(4), nullable=False, comment="手机后四位")
    photo_path = Column(String(500), comment="照片路径")
    group_id = Column(Integer, ForeignKey("groups.id"), comment="组别ID")
    qr_code_id = Column(String(50), unique=True, nullable=False, comment="二维码标识")
    is_checked_in = Column(Boolean, default=False, comment="是否已签到")
    checkin_time = Column(DateTime, comment="签到时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    group = relationship("Group", back_populates="participants")
    scores = relationship("Score", back_populates="participant")
    checkin_logs = relationship("CheckinLog", back_populates="participant")
    
    def __repr__(self):
        return f"<Participant(id={self.id}, name='{self.name}', organization='{self.organization}')>"
    
    @property
    def average_score(self):
        """计算平均分"""
        if not self.scores:
            return 0.0
        return sum(score.score for score in self.scores) / len(self.scores)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "organization": self.organization,
            "phone": self.phone,
            "phone_last4": self.phone_last4,
            "photo_path": self.photo_path,
            "group_id": self.group_id,
            "group_name": self.group.name if self.group else None,
            "qr_code_id": self.qr_code_id,
            "is_checked_in": self.is_checked_in,
            "checkin_time": self.checkin_time.isoformat() if self.checkin_time else None,
            "average_score": self.average_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }