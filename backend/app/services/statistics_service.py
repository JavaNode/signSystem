from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..models.participant import Participant
from ..models.group import Group
from ..models.judge import Judge
from ..models.score import Score
from ..models.checkin_log import CheckinLog

class StatisticsService:
    """统计服务类"""
    
    @staticmethod
    def get_dashboard_statistics(db: Session) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        # 基础统计
        total_participants = db.query(Participant).count()
        total_groups = db.query(Group).count()
        total_judges = db.query(Judge).filter(Judge.is_active == True).count()
        
        # 签到统计
        checked_in_count = db.query(Participant).filter(Participant.is_checked_in == True).count()
        checkin_rate = round(checked_in_count / total_participants * 100, 2) if total_participants > 0 else 0
        
        # 评分统计
        total_scores = db.query(Score).count()
        expected_scores = total_participants * total_judges
        scoring_progress = round(total_scores / expected_scores * 100, 2) if expected_scores > 0 else 0
        
        # 最近签到
        recent_checkins = db.query(CheckinLog).order_by(
            CheckinLog.checkin_time.desc()
        ).limit(10).all()
        
        return {
            "basic_stats": {
                "total_participants": total_participants,
                "total_groups": total_groups,
                "total_judges": total_judges,
                "checked_in_participants": checked_in_count,
                "checkin_rate": checkin_rate,
                "total_scores": total_scores,
                "expected_scores": expected_scores,
                "scoring_progress": scoring_progress
            },
            "recent_checkins": [
                {
                    "participant_name": log.participant.name if log.participant else "未知",
                    "organization": log.participant.organization if log.participant else "未知",
                    "checkin_time": log.checkin_time.strftime('%H:%M:%S') if log.checkin_time else ""
                }
                for log in recent_checkins
            ]
        }
    
    @staticmethod
    def get_checkin_timeline(db: Session) -> Dict[str, Any]:
        """获取签到时间线统计"""
        # 按小时统计签到数量
        checkin_logs = db.query(CheckinLog).all()
        
        hourly_stats = {}
        for log in checkin_logs:
            if log.checkin_time:
                hour = log.checkin_time.hour
                hour_key = f"{hour:02d}:00"
                
                if hour_key not in hourly_stats:
                    hourly_stats[hour_key] = 0
                hourly_stats[hour_key] += 1
        
        # 按分钟统计（最近2小时）
        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        
        recent_logs = db.query(CheckinLog).filter(
            CheckinLog.checkin_time >= two_hours_ago
        ).all()
        
        minute_stats = {}
        for log in recent_logs:
            if log.checkin_time:
                minute_key = log.checkin_time.strftime('%H:%M')
                if minute_key not in minute_stats:
                    minute_stats[minute_key] = 0
                minute_stats[minute_key] += 1
        
        return {
            "hourly_checkins": hourly_stats,
            "recent_minute_checkins": minute_stats,
            "peak_hour": max(hourly_stats.items(), key=lambda x: x[1]) if hourly_stats else None
        }
    
    @staticmethod
    def get_organization_statistics(db: Session) -> List[Dict[str, Any]]:
        """获取单位统计信息"""
        # 查询所有单位
        organizations = db.query(Participant.organization).distinct().all()
        
        org_stats = []
        for (org,) in organizations:
            # 该单位总人数
            total_count = db.query(Participant).filter(Participant.organization == org).count()
            
            # 已签到人数
            checked_in_count = db.query(Participant).filter(
                and_(Participant.organization == org, Participant.is_checked_in == True)
            ).count()
            
            # 平均分统计
            avg_score_query = db.query(func.avg(Score.score)).join(
                Participant, Score.participant_id == Participant.id
            ).filter(Participant.organization == org)
            
            avg_score = avg_score_query.scalar()
            avg_score = round(float(avg_score), 2) if avg_score else 0
            
            # 该单位所在的组
            groups = db.query(Group.name).join(
                Participant, Group.id == Participant.group_id
            ).filter(Participant.organization == org).distinct().all()
            
            group_names = [group[0] for group in groups]
            
            org_stats.append({
                "organization": org,
                "total_participants": total_count,
                "checked_in_participants": checked_in_count,
                "checkin_rate": round(checked_in_count / total_count * 100, 2) if total_count > 0 else 0,
                "average_score": avg_score,
                "groups": group_names
            })
        
        # 按签到率排序
        org_stats.sort(key=lambda x: x["checkin_rate"], reverse=True)
        
        return org_stats
    
    @staticmethod
    def get_group_statistics(db: Session) -> List[Dict[str, Any]]:
        """获取分组统计信息"""
        groups = db.query(Group).all()
        
        group_stats = []
        for group in groups:
            # 组内成员
            members = db.query(Participant).filter(Participant.group_id == group.id).all()
            
            # 签到统计
            checked_in_members = [m for m in members if m.is_checked_in]
            
            # 评分统计
            group_scores = []
            for member in members:
                member_scores = db.query(Score).filter(Score.participant_id == member.id).all()
                if member_scores:
                    avg_score = sum(s.score for s in member_scores) / len(member_scores)
                    group_scores.append(avg_score)
            
            group_avg_score = round(sum(group_scores) / len(group_scores), 2) if group_scores else 0
            
            # 单位统计
            organizations = list(set([m.organization for m in members]))
            
            group_stats.append({
                "group_id": group.id,
                "group_name": group.name,
                "draw_order": group.draw_order,
                "total_members": len(members),
                "checked_in_members": len(checked_in_members),
                "checkin_rate": round(len(checked_in_members) / len(members) * 100, 2) if members else 0,
                "average_score": group_avg_score,
                "organizations": organizations,
                "scored_members": len(group_scores)
            })
        
        # 按抽签顺序排序
        group_stats.sort(key=lambda x: x["draw_order"] or 999)
        
        return group_stats
    
    @staticmethod
    def get_scoring_heatmap(db: Session) -> Dict[str, Any]:
        """获取评分热力图数据"""
        # 获取所有评分
        scores = db.query(Score).join(Participant).join(Judge).all()
        
        # 构建评分矩阵
        participants = db.query(Participant).all()
        judges = db.query(Judge).filter(Judge.is_active == True).all()
        
        heatmap_data = []
        for participant in participants:
            participant_scores = {}
            for judge in judges:
                # 查找该评委对该参赛者的评分
                score = db.query(Score).filter(
                    and_(Score.participant_id == participant.id, Score.judge_id == judge.id)
                ).first()
                
                participant_scores[judge.name] = score.score if score else None
            
            heatmap_data.append({
                "participant_name": participant.name,
                "organization": participant.organization,
                "scores": participant_scores
            })
        
        return {
            "participants": [p.name for p in participants],
            "judges": [j.name for j in judges],
            "data": heatmap_data
        }
    
    @staticmethod
    def get_performance_trends(db: Session) -> Dict[str, Any]:
        """获取性能趋势数据"""
        # 按时间统计签到趋势
        checkin_logs = db.query(CheckinLog).order_by(CheckinLog.checkin_time).all()
        
        checkin_trend = []
        cumulative_count = 0
        
        for log in checkin_logs:
            cumulative_count += 1
            checkin_trend.append({
                "time": log.checkin_time.strftime('%H:%M') if log.checkin_time else "",
                "cumulative_checkins": cumulative_count
            })
        
        # 按时间统计评分趋势
        scores = db.query(Score).order_by(Score.created_at).all()
        
        scoring_trend = []
        cumulative_scores = 0
        
        for score in scores:
            cumulative_scores += 1
            scoring_trend.append({
                "time": score.created_at.strftime('%H:%M') if score.created_at else "",
                "cumulative_scores": cumulative_scores
            })
        
        return {
            "checkin_trend": checkin_trend,
            "scoring_trend": scoring_trend
        }
    
    @staticmethod
    def get_competition_summary(db: Session) -> Dict[str, Any]:
        """获取比赛总结统计"""
        # 基础数据
        total_participants = db.query(Participant).count()
        total_organizations = db.query(Participant.organization).distinct().count()
        total_groups = db.query(Group).count()
        
        # 签到完成情况
        checked_in_count = db.query(Participant).filter(Participant.is_checked_in == True).count()
        
        # 评分完成情况
        total_judges = db.query(Judge).filter(Judge.is_active == True).count()
        total_scores = db.query(Score).count()
        expected_scores = total_participants * total_judges
        
        # 获奖统计（前三名）
        ranking = db.query(
            Participant.id,
            Participant.name,
            Participant.organization,
            func.avg(Score.score).label('avg_score')
        ).join(Score).group_by(
            Participant.id, Participant.name, Participant.organization
        ).order_by(func.avg(Score.score).desc()).limit(3).all()
        
        winners = []
        for rank, (p_id, name, org, avg_score) in enumerate(ranking, 1):
            winners.append({
                "rank": rank,
                "name": name,
                "organization": org,
                "average_score": round(float(avg_score), 2)
            })
        
        # 分数分布
        all_avg_scores = db.query(
            func.avg(Score.score).label('avg_score')
        ).join(Participant).group_by(Participant.id).all()
        
        score_ranges = {
            "9-10分": 0,
            "8-9分": 0,
            "7-8分": 0,
            "6-7分": 0,
            "6分以下": 0
        }
        
        for (avg_score,) in all_avg_scores:
            if avg_score >= 9:
                score_ranges["9-10分"] += 1
            elif avg_score >= 8:
                score_ranges["8-9分"] += 1
            elif avg_score >= 7:
                score_ranges["7-8分"] += 1
            elif avg_score >= 6:
                score_ranges["6-7分"] += 1
            else:
                score_ranges["6分以下"] += 1
        
        return {
            "basic_info": {
                "total_participants": total_participants,
                "total_organizations": total_organizations,
                "total_groups": total_groups,
                "total_judges": total_judges
            },
            "completion_status": {
                "checkin_completion": {
                    "completed": checked_in_count,
                    "total": total_participants,
                    "rate": round(checked_in_count / total_participants * 100, 2) if total_participants > 0 else 0
                },
                "scoring_completion": {
                    "completed": total_scores,
                    "expected": expected_scores,
                    "rate": round(total_scores / expected_scores * 100, 2) if expected_scores > 0 else 0
                }
            },
            "winners": winners,
            "score_distribution": score_ranges
        }
    
    @staticmethod
    def export_full_report(db: Session) -> Dict[str, Any]:
        """导出完整报告"""
        return {
            "dashboard": StatisticsService.get_dashboard_statistics(db),
            "organizations": StatisticsService.get_organization_statistics(db),
            "groups": StatisticsService.get_group_statistics(db),
            "summary": StatisticsService.get_competition_summary(db),
            "export_time": datetime.now().isoformat()
        }