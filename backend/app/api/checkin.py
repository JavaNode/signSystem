from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..services.checkin_service import CheckinService

router = APIRouter()

class CheckinVerifyRequest(BaseModel):
    qr_code_id: str
    phone_last4: str
    name: str

class CheckinInfoResponse(BaseModel):
    qr_code_id: str
    participant_exists: bool
    is_checked_in: bool
    checkin_time: Optional[str] = None

@router.get("/info/{qr_code_id}", response_model=CheckinInfoResponse)
async def get_checkin_info(qr_code_id: str, db: Session = Depends(get_db)):
    """根据二维码ID获取签到信息"""
    info = CheckinService.get_checkin_info(db, qr_code_id)
    
    if not info:
        raise HTTPException(status_code=404, detail="二维码无效")
    
    return CheckinInfoResponse(**info)

@router.post("/verify")
async def verify_checkin(
    request: CheckinVerifyRequest, 
    client_request: Request,
    db: Session = Depends(get_db)
):
    """验证身份并完成签到"""
    # 获取客户端信息
    ip_address = client_request.client.host if client_request.client else None
    user_agent = client_request.headers.get("user-agent", "")
    
    result = CheckinService.process_checkin(
        db=db,
        qr_code_id=request.qr_code_id,
        phone_last4=request.phone_last4,
        name=request.name,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/status/{participant_id}")
async def get_participant_checkin_status(participant_id: int, db: Session = Depends(get_db)):
    """获取参赛者签到状态"""
    status = CheckinService.get_participant_checkin_status(db, participant_id)
    
    if not status["exists"]:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    return status

@router.get("/statistics")
async def get_checkin_statistics(db: Session = Depends(get_db)):
    """获取签到统计信息"""
    return CheckinService.get_checkin_statistics(db)

@router.get("/recent")
async def get_recent_checkins(limit: int = 50, db: Session = Depends(get_db)):
    """获取最近的签到记录"""
    return CheckinService.get_recent_checkins(db, limit)

@router.get("/export")
async def export_checkin_data(db: Session = Depends(get_db)):
    """导出签到数据"""
    return CheckinService.export_checkin_data(db)

# 管理员功能
@router.post("/manual/{participant_id}")
async def manual_checkin(
    participant_id: int, 
    admin_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """管理员手动签到"""
    result = CheckinService.manual_checkin(db, participant_id, admin_note)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/cancel/{participant_id}")
async def cancel_checkin(
    participant_id: int,
    admin_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """取消签到"""
    result = CheckinService.cancel_checkin(db, participant_id, admin_note)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result