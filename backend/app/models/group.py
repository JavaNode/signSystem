from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="组名")
    description = Column(Text, comment="组描述")
    draw_order = Column(Integer, comment="抽签顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    participants = relationship("Participant", back_populates="group")
    
    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"
    
    @property
    def member_count(self):
        """组内成员数量"""
        return len(self.participants)
    
    @property
    def checkin_count(self):
        """已签到成员数量"""
        return len([p for p in self.participants if p.is_checked_in])
    
    @property
    def checkin_rate(self):
        """签到率"""
        if self.member_count == 0:
            return 0.0
        return self.checkin_count / self.member_count * 100
    
    @property
    def organizations(self):
        """组内单位列表"""
        return list(set([p.organization for p in self.participants]))
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "draw_order": self.draw_order,
            "member_count": self.member_count,
            "checkin_count": self.checkin_count,
            "checkin_rate": round(self.checkin_rate, 2),
            "organizations": self.organizations,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }