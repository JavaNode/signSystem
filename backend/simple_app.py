#!/usr/bin/env python3
"""
简化版后端应用 - 用于快速启动和测试
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
import qrcode
from io import BytesIO
import base64

# 创建FastAPI应用
app = FastAPI(
    title="联盟杯内训师大赛管理系统",
    description="简化版API用于快速测试",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

class Group(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    draw_order: Optional[int] = None
    member_count: int = 0
    organizations: List[str] = []
    created_at: str

class Judge(BaseModel):
    id: int
    name: str
    username: str
    organization: str
    is_active: bool = True
    created_at: str

class Score(BaseModel):
    id: int
    participant_id: int
    participant_name: str
    judge_id: int
    judge_name: str
    score: float
    created_at: str

class CheckinRequest(BaseModel):
    qr_code_id: str
    phone_last4: str
    name: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ScoreRequest(BaseModel):
    participant_id: int
    score: float

# 内存数据存储
data_store = {
    "participants": [],
    "groups": [],
    "judges": [],
    "scores": [],
    "checkin_logs": []
}

# 数据文件路径
DATA_FILE = "data/simple_data.json"

def load_data():
    """加载数据"""
    global data_store
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data_store = json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")
            init_sample_data()
    else:
        init_sample_data()

def save_data():
    """保存数据"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_store, f, ensure_ascii=False, indent=2)

def init_sample_data():
    """初始化示例数据"""
    global data_store
    
    # 创建示例分组
    groups = [
        {"id": 1, "name": "第1组", "description": "XX银行", "member_count": 0, "organizations": ["XX银行"], "created_at": datetime.now().isoformat()},
        {"id": 2, "name": "第2组", "description": "YY银行", "member_count": 0, "organizations": ["YY银行"], "created_at": datetime.now().isoformat()},
        {"id": 3, "name": "第3组", "description": "ZZ银行", "member_count": 0, "organizations": ["ZZ银行"], "created_at": datetime.now().isoformat()},
    ]
    
    # 创建示例参赛者
    participants = [
        {"id": 1, "name": "张三", "organization": "XX银行", "phone": "13812345678", "phone_last4": "5678", "group_id": 1, "group_name": "第1组", "qr_code_id": "QR001", "is_checked_in": False, "created_at": datetime.now().isoformat()},
        {"id": 2, "name": "李四", "organization": "XX银行", "phone": "13887654321", "phone_last4": "4321", "group_id": 1, "group_name": "第1组", "qr_code_id": "QR002", "is_checked_in": False, "created_at": datetime.now().isoformat()},
        {"id": 3, "name": "王五", "organization": "YY银行", "phone": "13911111111", "phone_last4": "1111", "group_id": 2, "group_name": "第2组", "qr_code_id": "QR003", "is_checked_in": False, "created_at": datetime.now().isoformat()},
        {"id": 4, "name": "赵六", "organization": "YY银行", "phone": "13922222222", "phone_last4": "2222", "group_id": 2, "group_name": "第2组", "qr_code_id": "QR004", "is_checked_in": False, "created_at": datetime.now().isoformat()},
        {"id": 5, "name": "孙七", "organization": "ZZ银行", "phone": "13933333333", "phone_last4": "3333", "group_id": 3, "group_name": "第3组", "qr_code_id": "QR005", "is_checked_in": False, "created_at": datetime.now().isoformat()},
    ]
    
    # 创建示例评委
    judges = [
        {"id": 1, "name": "系统管理员", "username": "admin", "organization": "管理组", "is_active": True, "created_at": datetime.now().isoformat()},
        {"id": 2, "name": "张评委", "username": "judge01", "organization": "评委组", "is_active": True, "created_at": datetime.now().isoformat()},
        {"id": 3, "name": "李评委", "username": "judge02", "organization": "评委组", "is_active": True, "created_at": datetime.now().isoformat()},
    ]
    
    # 更新分组成员数量
    for group in groups:
        group["member_count"] = len([p for p in participants if p["group_id"] == group["id"]])
    
    data_store = {
        "participants": participants,
        "groups": groups,
        "judges": judges,
        "scores": [],
        "checkin_logs": []
    }
    
    save_data()

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

# API路由
@app.get("/")
async def root():
    return {"message": "联盟杯内训师大赛管理系统 - 简化版", "version": "1.0.0"}

@app.get("/api/participants")
async def get_participants():
    return {
        "items": data_store["participants"],
        "total": len(data_store["participants"]),
        "page": 1,
        "size": 100,
        "pages": 1
    }

@app.get("/api/participants/{participant_id}")
async def get_participant(participant_id: int):
    participant = next((p for p in data_store["participants"] if p["id"] == participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    return participant

@app.get("/api/participants/qr/{qr_id}")
async def get_participant_by_qr(qr_id: str):
    participant = next((p for p in data_store["participants"] if p["qr_code_id"] == qr_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="二维码无效")
    return participant

@app.post("/api/checkin/verify")
async def verify_checkin(request: CheckinRequest):
    # 查找参赛者
    participant = next((p for p in data_store["participants"] if p["qr_code_id"] == request.qr_code_id), None)
    if not participant:
        return {"success": False, "message": "二维码无效"}
    
    # 验证信息
    if participant["phone_last4"] != request.phone_last4 or participant["name"] != request.name:
        return {"success": False, "message": "验证信息不匹配"}
    
    # 检查是否已签到
    if participant["is_checked_in"]:
        return {"success": False, "message": "已经签到过了"}
    
    # 完成签到
    participant["is_checked_in"] = True
    participant["checkin_time"] = datetime.now().isoformat()
    
    # 记录签到日志
    checkin_log = {
        "id": len(data_store["checkin_logs"]) + 1,
        "participant_id": participant["id"],
        "participant_name": participant["name"],
        "organization": participant["organization"],
        "checkin_time": participant["checkin_time"]
    }
    data_store["checkin_logs"].append(checkin_log)
    
    save_data()
    
    return {"success": True, "participant": participant}

@app.get("/api/groups")
async def get_groups():
    return data_store["groups"]

@app.get("/api/groups/{group_id}")
async def get_group(group_id: int):
    group = next((g for g in data_store["groups"] if g["id"] == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    members = [p for p in data_store["participants"] if p["group_id"] == group_id]
    return {**group, "members": members}

@app.get("/api/judges")
async def get_judges():
    return {
        "items": data_store["judges"],
        "total": len(data_store["judges"]),
        "page": 1,
        "size": 100,
        "pages": 1
    }

@app.post("/api/judges/login")
async def judge_login(request: LoginRequest):
    # 简单的登录验证
    judge = next((j for j in data_store["judges"] if j["username"] == request.username), None)
    if not judge:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 简化密码验证（实际应用中应该使用哈希验证）
    valid_passwords = {"admin": "admin123", "judge01": "123456", "judge02": "123456"}
    if request.password != valid_passwords.get(request.username):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    return {
        "success": True,
        "judge": judge,
        "token": f"token_{judge['id']}_{datetime.now().timestamp()}",
        "expires_in": 86400
    }

@app.get("/api/scores")
async def get_scores():
    return {
        "items": data_store["scores"],
        "total": len(data_store["scores"]),
        "page": 1,
        "size": 100,
        "pages": 1
    }

@app.post("/api/scores")
async def submit_score(request: ScoreRequest):
    # 查找参赛者
    participant = next((p for p in data_store["participants"] if p["id"] == request.participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    # 创建评分记录（简化版，不验证评委）
    score = {
        "id": len(data_store["scores"]) + 1,
        "participant_id": request.participant_id,
        "participant_name": participant["name"],
        "judge_id": 1,  # 简化为默认评委
        "judge_name": "系统评委",
        "score": request.score,
        "created_at": datetime.now().isoformat()
    }
    
    data_store["scores"].append(score)
    save_data()
    
    # 计算平均分
    participant_scores = [s for s in data_store["scores"] if s["participant_id"] == request.participant_id]
    avg_score = sum(s["score"] for s in participant_scores) / len(participant_scores)
    
    return {
        "success": True,
        "score": score,
        "participant_avg_score": avg_score,
        "total_scores": len(participant_scores)
    }

@app.get("/api/statistics/overview")
async def get_statistics():
    participants = data_store["participants"]
    checked_in = [p for p in participants if p["is_checked_in"]]
    scores = data_store["scores"]
    
    # 按单位统计签到情况
    org_stats = {}
    for p in participants:
        org = p["organization"]
        if org not in org_stats:
            org_stats[org] = {"total": 0, "checked_in": 0}
        org_stats[org]["total"] += 1
        if p["is_checked_in"]:
            org_stats[org]["checked_in"] += 1
    
    checkin_by_organization = [
        {
            "organization": org,
            "total": stats["total"],
            "checked_in": stats["checked_in"],
            "rate": (stats["checked_in"] / stats["total"] * 100) if stats["total"] > 0 else 0
        }
        for org, stats in org_stats.items()
    ]
    
    # 签到时间线
    checkin_timeline = []
    for log in data_store["checkin_logs"]:
        time_str = log["checkin_time"][:16]  # 精确到分钟
        existing = next((item for item in checkin_timeline if item["time"] == time_str), None)
        if existing:
            existing["count"] += 1
        else:
            checkin_timeline.append({"time": time_str, "count": 1})
    
    # 评分分布
    score_distribution = [
        {"range": "0-2", "count": len([s for s in scores if 0 <= s["score"] < 2])},
        {"range": "2-4", "count": len([s for s in scores if 2 <= s["score"] < 4])},
        {"range": "4-6", "count": len([s for s in scores if 4 <= s["score"] < 6])},
        {"range": "6-8", "count": len([s for s in scores if 6 <= s["score"] < 8])},
        {"range": "8-10", "count": len([s for s in scores if 8 <= s["score"] <= 10])},
    ]
    
    return {
        "total_participants": len(participants),
        "checked_in_count": len(checked_in),
        "checkin_rate": (len(checked_in) / len(participants) * 100) if participants else 0,
        "total_groups": len(data_store["groups"]),
        "total_judges": len(data_store["judges"]),
        "total_scores": len(scores),
        "avg_score": (sum(s["score"] for s in scores) / len(scores)) if scores else 0,
        "checkin_by_organization": checkin_by_organization,
        "checkin_timeline": checkin_timeline,
        "score_distribution": score_distribution
    }

@app.get("/api/participants/{participant_id}/qrcode")
async def get_participant_qrcode(participant_id: int):
    participant = next((p for p in data_store["participants"] if p["id"] == participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    # 生成签到链接
    checkin_url = f"http://localhost:3000/mobile/checkin/{participant['qr_code_id']}"
    qr_code_data = generate_qr_code(checkin_url)
    
    return {"qr_code_data": qr_code_data, "checkin_url": checkin_url}

# 启动时加载数据
@app.on_event("startup")
async def startup_event():
    load_data()
    print("=" * 60)
    print("联盟杯内训师大赛管理系统 - 简化版")
    print("=" * 60)
    print("API服务已启动!")
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("前端地址: http://localhost:3000")
    print("=" * 60)
    print("默认账号:")
    print("- 管理员: admin / admin123")
    print("- 评委: judge01 / 123456")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)