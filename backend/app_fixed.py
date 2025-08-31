#!/usr/bin/env python3
"""
联盟杯内训师大赛管理系统 - 修复版后端应用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import json
import os
from datetime import datetime
import qrcode
from io import BytesIO
import base64

# 导入配置
from config import settings, get_checkin_url, get_mobile_base_url, is_development, get_cors_origins

# 数据存储
participants_data = []
groups_data = []
judges_data = []
scores_data = []
checkin_logs = []

def load_data():
    """加载示例数据"""
    global participants_data, groups_data, judges_data
    
    # 示例参赛者数据
    participants_data = [
        {
            "id": 1,
            "name": "张三",
            "organization": "工商银行",
            "phone": "13812345678",
            "phone_last4": "5678",
            "photo_path": "/photos/zhangsan.jpg",
            "group_id": 1,
            "group_name": "第1组",
            "qr_code_id": "QR001",
            "is_checked_in": False,
            "checkin_time": None,
            "created_at": "2024-09-20T10:00:00"
        },
        {
            "id": 2,
            "name": "李四",
            "organization": "建设银行",
            "phone": "13987654321",
            "phone_last4": "4321",
            "photo_path": "/photos/lisi.jpg",
            "group_id": 1,
            "group_name": "第1组",
            "qr_code_id": "QR002",
            "is_checked_in": False,
            "checkin_time": None,
            "created_at": "2024-09-20T10:00:00"
        },
        {
            "id": 3,
            "name": "王五",
            "organization": "农业银行",
            "phone": "13611111111",
            "phone_last4": "1111",
            "photo_path": "/photos/wangwu.jpg",
            "group_id": 2,
            "group_name": "第2组",
            "qr_code_id": "QR003",
            "is_checked_in": False,
            "checkin_time": None,
            "created_at": "2024-09-20T10:00:00"
        }
    ]
    
    # 示例分组数据
    groups_data = [
        {
            "id": 1,
            "name": "第1组",
            "organizations": ["工商银行", "建设银行"],
            "member_count": 2,
            "draw_order": None,
            "created_at": "2024-09-20T10:00:00"
        },
        {
            "id": 2,
            "name": "第2组",
            "organizations": ["农业银行"],
            "member_count": 1,
            "draw_order": None,
            "created_at": "2024-09-20T10:00:00"
        }
    ]
    
    # 示例评委数据
    judges_data = [
        {
            "id": 1,
            "name": "评委一",
            "judge_code": "judge01",
            "password": "123456",
            "is_active": True,
            "created_at": "2024-09-20T10:00:00"
        },
        {
            "id": 2,
            "name": "评委二",
            "judge_code": "judge02",
            "password": "123456",
            "is_active": True,
            "created_at": "2024-09-20T10:00:00"
        }
    ]

def generate_qr_code(data: str) -> str:
    """生成二维码并返回base64编码"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# 使用lifespan替代on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    load_data()
    print("=" * 60)
    print(f"{settings.app_title} - 修复版")
    print("=" * 60)
    print("API服务已启动!")
    print(f"访问地址: http://{settings.host}:{settings.port}")
    print(f"API文档: http://{settings.host}:{settings.port}{settings.api_docs_url}")
    print(f"前端地址: {settings.frontend_url}")
    print(f"移动端地址: {settings.mobile_base_url}")
    print("=" * 60)
    print("默认账号:")
    print(f"- 管理员: {settings.default_admin_username} / {settings.default_admin_password}")
    print("- 评委: judge01 / 123456")
    print("=" * 60)
    print(f"环境: {settings.environment}")
    print(f"调试模式: {settings.debug}")
    print("=" * 60)
    yield
    # 关闭时执行
    print("服务正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    docs_url=settings.api_docs_url,
    redoc_url=settings.api_redoc_url,
    lifespan=lifespan
)

# 定义允许跨域的来源
origins = [
    "http://115.190.42.107",
    "http://115.190.42.107:80", 
    "http://115.190.42.107:3000",
    "http://115.190.42.107:8080",
    "https://115.190.42.107",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有请求头
)

# 数据模型
class Participant(BaseModel):
    id: int
    name: str
    organization: str
    phone: str
    phone_last4: str
    photo_path: Optional[str] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    qr_code_id: str
    is_checked_in: bool = False
    checkin_time: Optional[str] = None
    created_at: str

class CheckinRequest(BaseModel):
    qr_code_id: str
    phone_last4: str
    name: str
    phone_last4: str
    name: str

class JudgeLogin(BaseModel):
    judge_code: str
    password: str

class ScoreSubmit(BaseModel):
    participant_id: int
    judge_id: int
    score: float

# API路由
@app.get("/")
async def root():
    return {
        "message": f"{settings.app_title}API", 
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": settings.api_docs_url
    }

@app.get("/api/participants", response_model=List[Participant])
async def get_participants():
    """获取所有参赛者"""
    return participants_data

@app.get("/api/participants/{participant_id}")
async def get_participant(participant_id: int):
    """获取单个参赛者信息"""
    participant = next((p for p in participants_data if p["id"] == participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    return participant

@app.post("/api/checkin/verify")
async def verify_checkin(request: CheckinRequest):
    """验证签到信息"""
    # 查找参赛者
    participant = next((p for p in participants_data if p["qr_code_id"] == request.qr_code_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="无效的二维码")
    
    # 验证信息
    if participant["phone_last4"] != request.phone_last4 or participant["name"] != request.name:
        raise HTTPException(status_code=400, detail="验证信息不匹配")
    
    # 检查是否已签到
    if participant["is_checked_in"]:
        return {"success": False, "message": "您已经签到过了", "participant": participant}
    
    # 完成签到
    participant["is_checked_in"] = True
    participant["checkin_time"] = datetime.now().isoformat()
    
    # 记录签到日志
    checkin_logs.append({
        "participant_id": participant["id"],
        "checkin_time": participant["checkin_time"],
        "ip_address": "127.0.0.1"
    })
    
    return {"success": True, "message": "签到成功!", "participant": participant}

@app.get("/api/groups")
async def get_groups():
    """获取所有分组"""
    return groups_data

@app.get("/api/groups/{group_id}/members")
async def get_group_members(group_id: int):
    """获取分组成员"""
    group = next((g for g in groups_data if g["id"] == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    members = [p for p in participants_data if p["group_id"] == group_id]
    return {"group": group, "members": members}

@app.post("/api/judges/login")
async def judge_login(request: JudgeLogin):
    """评委登录"""
    judge = next((j for j in judges_data if j["judge_code"] == request.judge_code), None)
    if not judge or judge["password"] != request.password:
        raise HTTPException(status_code=401, detail="评委编号或密码错误")
    
    return {"success": True, "judge": judge, "token": f"judge_token_{judge['id']}"}

@app.post("/api/scores/submit")
async def submit_score(request: ScoreSubmit):
    """提交评分"""
    # 验证参赛者存在
    participant = next((p for p in participants_data if p["id"] == request.participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    # 验证评委存在
    judge = next((j for j in judges_data if j["id"] == request.judge_id), None)
    if not judge:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    # 验证分数范围
    if not (settings.min_score <= request.score <= settings.max_score):
        raise HTTPException(status_code=400, detail=f"分数必须在{settings.min_score}-{settings.max_score}之间")
    
    # 检查是否已评分
    existing_score = next((s for s in scores_data if s["participant_id"] == request.participant_id and s["judge_id"] == request.judge_id), None)
    if existing_score:
        existing_score["score"] = request.score
        existing_score["updated_at"] = datetime.now().isoformat()
    else:
        scores_data.append({
            "id": len(scores_data) + 1,
            "participant_id": request.participant_id,
            "judge_id": request.judge_id,
            "score": request.score,
            "created_at": datetime.now().isoformat()
        })
    
    return {"success": True, "message": "评分提交成功"}

@app.get("/api/statistics/checkin")
async def get_checkin_statistics():
    """获取签到统计"""
    total_participants = len(participants_data)
    checked_in = len([p for p in participants_data if p["is_checked_in"]])
    checkin_rate = (checked_in / total_participants * 100) if total_participants > 0 else 0
    
    return {
        "total_participants": total_participants,
        "checked_in": checked_in,
        "not_checked_in": total_participants - checked_in,
        "checkin_rate": round(checkin_rate, 2)
    }

@app.get("/api/statistics/scores")
async def get_score_statistics():
    """获取评分统计"""
    # 计算每个参赛者的平均分
    participant_scores = {}
    for score in scores_data:
        pid = score["participant_id"]
        if pid not in participant_scores:
            participant_scores[pid] = []
        participant_scores[pid].append(score["score"])
    
    # 计算平均分并排序
    rankings = []
    for pid, scores in participant_scores.items():
        participant = next((p for p in participants_data if p["id"] == pid), None)
        if participant:
            avg_score = sum(scores) / len(scores)
            rankings.append({
                "participant": participant,
                "average_score": round(avg_score, 2),
                "score_count": len(scores)
            })
    
    rankings.sort(key=lambda x: x["average_score"], reverse=True)
    
    return {
        "total_scores": len(scores_data),
        "participants_scored": len(participant_scores),
        "rankings": rankings
    }

@app.get("/api/participants/{participant_id}/qrcode")
async def get_participant_qrcode(participant_id: int):
    """获取参赛者二维码"""
    participant = next((p for p in participants_data if p["id"] == participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    # 生成签到链接
    checkin_url = get_checkin_url(participant['qr_code_id'])
    qr_code_data = generate_qr_code(checkin_url)
    
    return {"qr_code_data": qr_code_data, "checkin_url": checkin_url}

# 生成公共签到二维码
@app.get("/api/qrcode/public")
async def get_public_qrcode():
    """获取公共签到二维码"""
    checkin_url = get_checkin_url()
    qr_code_data = generate_qr_code(checkin_url)
    
    return {
        "qr_code_data": qr_code_data,
        "checkin_url": checkin_url,
        "description": "参赛者扫描此二维码进行签到"
    }

# 移动端签到验证
@app.post("/api/mobile/checkin")
async def mobile_checkin(request: CheckinRequest):
    """移动端签到验证"""
    # 根据手机后四位和姓名查找参赛者
    participant = None
    for p in participants_data:
        if p["phone_last4"] == request.phone_last4 and p["name"] == request.name:
            participant = p
            break
    
    if not participant:
        raise HTTPException(status_code=404, detail="未找到匹配的参赛者信息，请检查手机号后四位和姓名")
    
    if participant["is_checked_in"]:
        return {
            "success": False, 
            "message": "您已经签到过了", 
            "participant": participant,
            "checkin_time": participant["checkin_time"]
        }
    
    # 执行签到
    participant["is_checked_in"] = True
    participant["checkin_time"] = datetime.now().isoformat()
    
    # 记录签到日志
    checkin_log = {
        "id": len(checkin_logs) + 1,
        "participant_id": participant["id"],
        "participant_name": participant["name"],
        "organization": participant["organization"],
        "checkin_time": participant["checkin_time"],
        "checkin_method": "mobile_qr"
    }
    checkin_logs.append(checkin_log)
    
    return {
        "success": True, 
        "message": "签到成功！", 
        "participant": participant,
        "group_info": {
            "group_id": participant["group_id"],
            "group_name": participant["group_name"]
        },
        "competition_info": {
            "name": settings.competition_name,
            "date": settings.competition_date,
            "location": settings.competition_location
        }
    }

# 评委端登录
@app.post("/api/mobile/judge/login")
async def mobile_judge_login(request: JudgeLogin):
    """评委端登录"""
    judge = None
    for j in judges_data:
        if j["judge_code"] == request.judge_code and j["password"] == request.password:
            judge = j
            break
    
    if not judge:
        raise HTTPException(status_code=401, detail="评委编号或密码错误")
    
    return {
        "success": True, 
        "judge": judge, 
        "token": f"judge_token_{judge['id']}",
        "message": "登录成功"
    }

# 获取评委的打分列表
@app.get("/api/mobile/judge/{judge_id}/participants")
async def get_judge_participants(judge_id: int):
    """获取评委需要打分的参赛者列表"""
    # 获取已签到的参赛者
    checked_in_participants = [p.copy() for p in participants_data if p["is_checked_in"]]
    
    # 获取该评委已打分的记录
    judge_scores = [s for s in scores_data if s["judge_id"] == judge_id]
    scored_participant_ids = [s["participant_id"] for s in judge_scores]
    
    # 为每个参赛者添加打分状态
    for participant in checked_in_participants:
        participant["scored"] = participant["id"] in scored_participant_ids
        if participant["scored"]:
            score_record = next(s for s in judge_scores if s["participant_id"] == participant["id"])
            participant["score"] = score_record["score"]
        else:
            participant["score"] = None
    
    return {
        "participants": checked_in_participants,
        "total_participants": len(checked_in_participants),
        "scored_count": len([p for p in checked_in_participants if p["scored"]]),
        "pending_count": len([p for p in checked_in_participants if not p["scored"]])
    }

# 移动端提交分数
@app.post("/api/mobile/scores/submit")
async def mobile_submit_score(request: ScoreSubmit):
    """移动端提交分数"""
    if not (settings.min_score <= request.score <= settings.max_score):
        raise HTTPException(status_code=400, detail=f"分数必须在{settings.min_score}-{settings.max_score}之间")
    
    # 检查参赛者是否存在且已签到
    participant = next((p for p in participants_data if p["id"] == request.participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    if not participant["is_checked_in"]:
        raise HTTPException(status_code=400, detail="该参赛者尚未签到，无法打分")
    
    # 检查是否已经打过分
    existing_score = next((s for s in scores_data if s["participant_id"] == request.participant_id and s["judge_id"] == request.judge_id), None)
    
    if existing_score:
        # 更新分数
        existing_score["score"] = request.score
        existing_score["updated_at"] = datetime.now().isoformat()
        message = "分数更新成功"
    else:
        # 新增分数
        new_score = {
            "id": len(scores_data) + 1,
            "participant_id": request.participant_id,
            "judge_id": request.judge_id,
            "score": request.score,
            "created_at": datetime.now().isoformat()
        }
        scores_data.append(new_score)
        message = "评分提交成功"
    
    return {
        "success": True, 
        "message": message,
        "score": request.score,
        "participant_name": participant["name"]
    }

# 生成公共签到二维码（重复接口，已在上面定义）
# @app.get("/api/qrcode/public")
# async def get_public_qrcode():
#     """获取公共签到二维码"""
#     checkin_url = get_checkin_url()
#     qr_code_data = generate_qr_code(checkin_url)
#     
#     return {
#         "qr_code_data": qr_code_data,
#         "checkin_url": checkin_url,
#         "description": "参赛者扫描此二维码进行签到"
#     }

# 移动端签到验证
@app.post("/api/mobile/checkin")
async def mobile_checkin(request: CheckinRequest):
    """移动端签到验证"""
    # 根据手机后四位和姓名查找参赛者
    participant = None
    for p in participants_data:
        if p["phone_last4"] == request.phone_last4 and p["name"] == request.name:
            participant = p
            break
    
    if not participant:
        raise HTTPException(status_code=404, detail="未找到匹配的参赛者信息，请检查手机号后四位和姓名")
    
    if participant["is_checked_in"]:
        return {
            "success": False, 
            "message": "您已经签到过了", 
            "participant": participant,
            "checkin_time": participant["checkin_time"]
        }
    
    # 执行签到
    participant["is_checked_in"] = True
    participant["checkin_time"] = datetime.now().isoformat()
    
    # 记录签到日志
    checkin_log = {
        "id": len(checkin_logs) + 1,
        "participant_id": participant["id"],
        "participant_name": participant["name"],
        "organization": participant["organization"],
        "checkin_time": participant["checkin_time"],
        "checkin_method": "mobile_qr"
    }
    checkin_logs.append(checkin_log)
    
    return {
        "success": True, 
        "message": "签到成功！", 
        "participant": participant,
        "group_info": {
            "group_id": participant["group_id"],
            "group_name": participant["group_name"]
        },
        "competition_info": {
            "name": "联盟杯内训师大赛",
            "date": "2024年9月24日",
            "location": "比赛现场"
        }
    }

# 评委端登录
@app.post("/api/mobile/judge/login")
async def mobile_judge_login(request: JudgeLogin):
    """评委端登录"""
    judge = None
    for j in judges_data:
        if j["judge_code"] == request.judge_code and j["password"] == request.password:
            judge = j
            break
    
    if not judge:
        raise HTTPException(status_code=401, detail="评委编号或密码错误")
    
    return {
        "success": True, 
        "judge": judge, 
        "token": f"judge_token_{judge['id']}",
        "message": "登录成功"
    }

# 获取评委的打分列表
@app.get("/api/mobile/judge/{judge_id}/participants")
async def get_judge_participants(judge_id: int):
    """获取评委需要打分的参赛者列表"""
    # 获取已签到的参赛者
    checked_in_participants = [p.copy() for p in participants_data if p["is_checked_in"]]
    
    # 获取该评委已打分的记录
    judge_scores = [s for s in scores_data if s["judge_id"] == judge_id]
    scored_participant_ids = [s["participant_id"] for s in judge_scores]
    
    # 为每个参赛者添加打分状态
    for participant in checked_in_participants:
        participant["scored"] = participant["id"] in scored_participant_ids
        if participant["scored"]:
            score_record = next(s for s in judge_scores if s["participant_id"] == participant["id"])
            participant["score"] = score_record["score"]
        else:
            participant["score"] = None
    
    return {
        "participants": checked_in_participants,
        "total_participants": len(checked_in_participants),
        "scored_count": len([p for p in checked_in_participants if p["scored"]]),
        "pending_count": len([p for p in checked_in_participants if not p["scored"]])
    }

# 移动端提交分数
@app.post("/api/mobile/scores/submit")
async def mobile_submit_score(request: ScoreSubmit):
    """移动端提交分数"""
    if not (0 <= request.score <= 10):
        raise HTTPException(status_code=400, detail="分数必须在0-10之间")
    
    # 检查参赛者是否存在且已签到
    participant = next((p for p in participants_data if p["id"] == request.participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    if not participant["is_checked_in"]:
        raise HTTPException(status_code=400, detail="该参赛者尚未签到，无法打分")
    
    # 检查是否已经打过分
    existing_score = next((s for s in scores_data if s["participant_id"] == request.participant_id and s["judge_id"] == request.judge_id), None)
    
    if existing_score:
        # 更新分数
        existing_score["score"] = request.score
        existing_score["updated_at"] = datetime.now().isoformat()
        message = "分数更新成功"
    else:
        # 新增分数
        new_score = {
            "id": len(scores_data) + 1,
            "participant_id": request.participant_id,
            "judge_id": request.judge_id,
            "score": request.score,
            "created_at": datetime.now().isoformat()
        }
        scores_data.append(new_score)
        message = "评分提交成功"
    
    return {
        "success": True, 
        "message": message,
        "score": request.score,
        "participant_name": participant["name"]
    }

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

# 添加额外的API接口（如果存在）
try:
    try:
        from .app_additional_apis import add_additional_apis
    except ImportError:
        from app_additional_apis import add_additional_apis
    add_additional_apis(app, participants_data, groups_data, scores_data, judges_data)
except ImportError:
    print("app_additional_apis 模块不存在，跳过额外API加载")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        reload=settings.debug and is_development()
    )