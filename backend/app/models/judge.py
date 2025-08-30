from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Judge(Base):
    __tablename__ = "judges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="评委姓名")
    username = Column(String(50), unique=True, nullable=False, comment="登录用户名")
    password = Column(String(255), nullable=False, comment="登录密码")
    organization = Column(String(200), comment="所属单位")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    scores = relationship("Score", back_populates="judge")
    
    def __repr__(self):
        return f"<Judge(id={self.id}, name='{self.name}', username='{self.username}')>"
    
    @property
    def score_count(self):
        """评分数量"""
        return len(self.scores)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "organization": self.organization,
            "is_active": self.is_active,
            "score_count": self.score_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }