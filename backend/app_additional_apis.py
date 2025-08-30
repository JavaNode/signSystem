# 额外的API接口
from fastapi import FastAPI, HTTPException
from typing import List

def add_additional_apis(app: FastAPI, participants_data, groups_data, scores_data, judges_data):
    """添加额外的API接口"""
    
    # 获取分组统计
    @app.get("/api/statistics/groups")
    async def get_group_statistics():
        """获取分组统计信息"""
        group_stats = []
        for group in groups_data:
            group_participants = [p for p in participants_data if p["group_id"] == group["id"]]
            checked_in_count = len([p for p in group_participants if p["is_checked_in"]])
            
            group_stats.append({
                "group_name": group["name"],
                "total": len(group_participants),
                "checked_in": checked_in_count
            })
        
        return group_stats

    # 获取最近签到记录
    @app.get("/api/checkins/recent")
    async def get_recent_checkins(limit: int = 10):
        """获取最近的签到记录"""
        # 获取已签到的参赛者，按签到时间倒序
        checked_in_participants = [p for p in participants_data if p["is_checked_in"] and p.get("checkin_time")]
        checked_in_participants.sort(key=lambda x: x["checkin_time"], reverse=True)
        
        recent_checkins = []
        for participant in checked_in_participants[:limit]:
            recent_checkins.append({
                "id": participant["id"],
                "name": participant["name"],
                "organization": participant["organization"],
                "checkin_time": participant["checkin_time"]
            })
        
        return recent_checkins

    # 获取签到时间分布统计
    @app.get("/api/statistics/checkin-timeline")
    async def get_checkin_timeline():
        """获取签到时间分布"""
        from datetime import datetime
        
        # 统计每小时的签到数量
        hourly_counts = {}
        for i in range(24):
            hourly_counts[f"{i:02d}"] = 0
        
        # 统计实际签到数据
        for participant in participants_data:
            if participant["is_checked_in"] and participant.get("checkin_time"):
                try:
                    checkin_dt = datetime.fromisoformat(participant["checkin_time"].replace('Z', '+00:00'))
                    hour = f"{checkin_dt.hour:02d}"
                    hourly_counts[hour] += 1
                except:
                    continue
        
        return {
            "hours": list(hourly_counts.keys()),
            "counts": list(hourly_counts.values())
        }

    # 获取参赛者详细信息
    @app.get("/api/participants/{participant_id}/detail")
    async def get_participant_detail(participant_id: int):
        """获取参赛者详细信息"""
        participant = next((p for p in participants_data if p["id"] == participant_id), None)
        if not participant:
            raise HTTPException(status_code=404, detail="参赛者不存在")
        
        # 获取分组信息
        group = next((g for g in groups_data if g["id"] == participant["group_id"]), None)
        group_name = group["name"] if group else "未分组"
        
        # 获取评分信息
        participant_scores = [s for s in scores_data if s["participant_id"] == participant_id]
        
        # 计算平均分
        avg_score = 0
        if participant_scores:
            avg_score = sum(s["score"] for s in participant_scores) / len(participant_scores)
        
        # 获取评委信息
        detailed_scores = []
        for score in participant_scores:
            judge = next((j for j in judges_data if j["id"] == score["judge_id"]), None)
            detailed_scores.append({
                "score": score["score"],
                "created_at": score["created_at"],
                "judge_name": judge["name"] if judge else "未知评委"
            })
        
        participant_detail = {
            **participant,
            "group_name": group_name,
            "score_count": len(participant_scores),
            "avg_score": round(avg_score, 2),
            "scores": detailed_scores
        }
        
        return participant_detail