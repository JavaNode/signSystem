from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, comment="参赛者ID")
    judge_id = Column(Integer, ForeignKey("judges.id"), nullable=False, comment="评委ID")
    score = Column(Float, nullable=False, comment="评分(0-10)")
    round_number = Column(Integer, default=1, comment="轮次")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    participant = relationship("Participant", back_populates="scores")
    judge = relationship("Judge", back_populates="scores")
    
    # 唯一约束：每个评委对每个参赛者在每轮只能评分一次
    __table_args__ = (
        UniqueConstraint('participant_id', 'judge_id', 'round_number', name='unique_score_per_round'),
    )
    
    def __repr__(self):
        return f"<Score(id={self.id}, participant_id={self.participant_id}, judge_id={self.judge_id}, score={self.score})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "participant_name": self.participant.name if self.participant else None,
            "judge_id": self.judge_id,
            "judge_name": self.judge.name if self.judge else None,
            "score": self.score,
            "round_number": self.round_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }