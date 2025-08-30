from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from ..models.score import Score
from ..models.participant import Participant
from ..models.judge import Judge

class ScoreService:
    """评分服务类"""
    
    @staticmethod
    def submit_score(db: Session, participant_id: int, judge_id: int, 
                    score: float, round_number: int = 1) -> Dict[str, Any]:
        """
        提交评分
        
        Args:
            db: 数据库会话
            participant_id: 参赛者ID
            judge_id: 评委ID
            score: 评分(0-10)
            round_number: 轮次
        
        Returns:
            提交结果
        """
        # 验证评分范围
        if not (0 <= score <= 10):
            return {
                "success": False,
                "message": "评分必须在0-10之间",
                "error_code": "INVALID_SCORE_RANGE"
            }
        
        # 验证参赛者是否存在
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant:
            return {
                "success": False,
                "message": "参赛者不存在",
                "error_code": "PARTICIPANT_NOT_FOUND"
            }
        
        # 验证评委是否存在且激活
        judge = db.query(Judge).filter(Judge.id == judge_id).first()
        if not judge or not judge.is_active:
            return {
                "success": False,
                "message": "评委不存在或已停用",
                "error_code": "JUDGE_NOT_FOUND"
            }
        
        # 检查是否已经评过分
        existing_score = db.query(Score).filter(
            and_(
                Score.participant_id == participant_id,
                Score.judge_id == judge_id,
                Score.round_number == round_number
            )
        ).first()
        
        if existing_score:
            # 更新现有评分
            existing_score.score = score
            db.commit()
            db.refresh(existing_score)
            
            return {
                "success": True,
                "message": "评分更新成功",
                "score": existing_score.to_dict(),
                "action": "updated"
            }
        else:
            # 创建新评分
            new_score = Score(
                participant_id=participant_id,
                judge_id=judge_id,
                score=score,
                round_number=round_number
            )
            
            db.add(new_score)
            db.commit()
            db.refresh(new_score)
            
            return {
                "success": True,
                "message": "评分提交成功",
                "score": new_score.to_dict(),
                "action": "created"
            }
    
    @staticmethod
    def get_participant_scores(db: Session, participant_id: int, 
                              round_number: int = 1) -> List[Score]:
        """获取参赛者的所有评分"""
        return db.query(Score).filter(
            and_(
                Score.participant_id == participant_id,
                Score.round_number == round_number
            )
        ).all()
    
    @staticmethod
    def get_judge_scores(db: Session, judge_id: int, 
                        round_number: int = 1) -> List[Score]:
        """获取评委的所有评分"""
        return db.query(Score).filter(
            and_(
                Score.judge_id == judge_id,
                Score.round_number == round_number
            )
        ).all()
    
    @staticmethod
    def calculate_participant_average(db: Session, participant_id: int, 
                                    round_number: int = 1) -> Optional[float]:
        """计算参赛者平均分"""
        scores = ScoreService.get_participant_scores(db, participant_id, round_number)
        
        if not scores:
            return None
        
        total_score = sum(score.score for score in scores)
        return round(total_score / len(scores), 2)
    
    @staticmethod
    def get_ranking(db: Session, round_number: int = 1) -> List[Dict[str, Any]]:
        """
        获取排行榜
        
        Args:
            db: 数据库会话
            round_number: 轮次
        
        Returns:
            排行榜列表
        """
        # 查询所有参赛者的平均分
        subquery = db.query(
            Score.participant_id,
            func.avg(Score.score).label('avg_score'),
            func.count(Score.id).label('score_count')
        ).filter(
            Score.round_number == round_number
        ).group_by(Score.participant_id).subquery()
        
        # 连接参赛者信息
        results = db.query(
            Participant,
            subquery.c.avg_score,
            subquery.c.score_count
        ).join(
            subquery, Participant.id == subquery.c.participant_id
        ).order_by(subquery.c.avg_score.desc()).all()
        
        ranking = []
        for rank, (participant, avg_score, score_count) in enumerate(results, 1):
            ranking.append({
                "rank": rank,
                "participant": participant.to_dict(),
                "average_score": round(float(avg_score), 2),
                "score_count": score_count,
                "total_judges": db.query(Judge).filter(Judge.is_active == True).count()
            })
        
        return ranking
    
    @staticmethod
    def get_scoring_progress(db: Session, round_number: int = 1) -> Dict[str, Any]:
        """获取评分进度"""
        total_participants = db.query(Participant).count()
        total_judges = db.query(Judge).filter(Judge.is_active == True).count()
        total_expected_scores = total_participants * total_judges
        
        actual_scores = db.query(Score).filter(Score.round_number == round_number).count()
        
        # 按参赛者统计评分完成情况
        participant_progress = db.query(
            Participant.id,
            Participant.name,
            func.count(Score.id).label('received_scores')
        ).outerjoin(
            Score, and_(
                Participant.id == Score.participant_id,
                Score.round_number == round_number
            )
        ).group_by(Participant.id, Participant.name).all()
        
        # 按评委统计评分完成情况
        judge_progress = db.query(
            Judge.id,
            Judge.name,
            func.count(Score.id).label('given_scores')
        ).outerjoin(
            Score, and_(
                Judge.id == Score.judge_id,
                Score.round_number == round_number
            )
        ).filter(Judge.is_active == True).group_by(Judge.id, Judge.name).all()
        
        return {
            "total_participants": total_participants,
            "total_judges": total_judges,
            "total_expected_scores": total_expected_scores,
            "actual_scores": actual_scores,
            "completion_rate": round(actual_scores / total_expected_scores * 100, 2) if total_expected_scores > 0 else 0,
            "participant_progress": [
                {
                    "participant_id": p_id,
                    "participant_name": p_name,
                    "received_scores": received,
                    "completion_rate": round(received / total_judges * 100, 2) if total_judges > 0 else 0
                }
                for p_id, p_name, received in participant_progress
            ],
            "judge_progress": [
                {
                    "judge_id": j_id,
                    "judge_name": j_name,
                    "given_scores": given,
                    "completion_rate": round(given / total_participants * 100, 2) if total_participants > 0 else 0
                }
                for j_id, j_name, given in judge_progress
            ]
        }
    
    @staticmethod
    def delete_score(db: Session, score_id: int) -> bool:
        """删除评分"""
        score = db.query(Score).filter(Score.id == score_id).first()
        if not score:
            return False
        
        db.delete(score)
        db.commit()
        return True
    
    @staticmethod
    def get_participant_detailed_scores(db: Session, participant_id: int, 
                                       round_number: int = 1) -> Dict[str, Any]:
        """获取参赛者详细评分信息"""
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant:
            return None
        
        scores = ScoreService.get_participant_scores(db, participant_id, round_number)
        
        score_details = []
        for score in scores:
            score_details.append({
                "judge_name": score.judge.name,
                "judge_organization": score.judge.organization,
                "score": score.score,
                "created_at": score.created_at.isoformat() if score.created_at else None
            })
        
        average_score = ScoreService.calculate_participant_average(db, participant_id, round_number)
        
        return {
            "participant": participant.to_dict(),
            "scores": score_details,
            "average_score": average_score,
            "score_count": len(scores),
            "total_judges": db.query(Judge).filter(Judge.is_active == True).count()
        }
    
    @staticmethod
    def export_scores(db: Session, round_number: int = 1) -> Dict[str, Any]:
        """导出评分数据"""
        ranking = ScoreService.get_ranking(db, round_number)
        
        export_data = []
        for item in ranking:
            participant = item["participant"]
            
            # 获取详细评分
            scores = ScoreService.get_participant_scores(db, participant["id"], round_number)
            score_details = {}
            
            for score in scores:
                judge_name = score.judge.name
                score_details[f"评委_{judge_name}"] = score.score
            
            export_data.append({
                "排名": item["rank"],
                "姓名": participant["name"],
                "单位": participant["organization"],
                "组别": participant["group_name"] or "未分组",
                "平均分": item["average_score"],
                "评分数量": item["score_count"],
                **score_details
            })
        
        return {
            "round_number": round_number,
            "export_time": func.now(),
            "total_participants": len(export_data),
            "data": export_data
        }
    
    @staticmethod
    def get_score_statistics(db: Session, round_number: int = 1) -> Dict[str, Any]:
        """获取评分统计信息"""
        scores = db.query(Score).filter(Score.round_number == round_number).all()
        
        if not scores:
            return {
                "total_scores": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "score_distribution": {}
            }
        
        score_values = [score.score for score in scores]
        
        # 分数分布统计
        score_distribution = {}
        for i in range(11):  # 0-10分
            count = len([s for s in score_values if int(s) == i])
            if count > 0:
                score_distribution[str(i)] = count
        
        return {
            "total_scores": len(scores),
            "average_score": round(sum(score_values) / len(score_values), 2),
            "highest_score": max(score_values),
            "lowest_score": min(score_values),
            "score_distribution": score_distribution
        }