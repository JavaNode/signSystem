from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from ..database import get_db
from ..services.participant_service import ParticipantService
from ..utils.file_handler import save_participant_photo

router = APIRouter()

class ParticipantCreate(BaseModel):
    name: str
    organization: str
    phone: str
    group_id: Optional[int] = None

class ParticipantUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None
    group_id: Optional[int] = None

class ParticipantResponse(BaseModel):
    id: int
    name: str
    organization: str
    phone: str
    phone_last4: str
    photo_path: Optional[str] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    qr_code_id: str
    is_checked_in: bool
    checkin_time: Optional[str] = None
    average_score: float
    created_at: Optional[str] = None

@router.post("/", response_model=ParticipantResponse)
async def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    """创建参赛者"""
    try:
        new_participant = ParticipantService.create_participant(db, participant.dict())
        return ParticipantResponse(**new_participant.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ParticipantResponse])
async def get_participants(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """获取参赛者列表"""
    participants = ParticipantService.get_all_participants(db, skip, limit)
    return [ParticipantResponse(**p.to_dict()) for p in participants]

@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(participant_id: int, db: Session = Depends(get_db)):
    """获取单个参赛者信息"""
    participant = ParticipantService.get_participant_by_id(db, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    return ParticipantResponse(**participant.to_dict())

@router.put("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: int, 
    participant_update: ParticipantUpdate, 
    db: Session = Depends(get_db)
):
    """更新参赛者信息"""
    # 过滤掉None值
    update_data = {k: v for k, v in participant_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    try:
        updated_participant = ParticipantService.update_participant(db, participant_id, update_data)
        if not updated_participant:
            raise HTTPException(status_code=404, detail="参赛者不存在")
        
        return ParticipantResponse(**updated_participant.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{participant_id}")
async def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    """删除参赛者"""
    success = ParticipantService.delete_participant(db, participant_id)
    if not success:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    return {"message": "参赛者删除成功"}

@router.get("/search/{keyword}", response_model=List[ParticipantResponse])
async def search_participants(keyword: str, db: Session = Depends(get_db)):
    """搜索参赛者"""
    participants = ParticipantService.search_participants(db, keyword)
    return [ParticipantResponse(**p.to_dict()) for p in participants]

@router.get("/organization/{organization}", response_model=List[ParticipantResponse])
async def get_participants_by_organization(organization: str, db: Session = Depends(get_db)):
    """根据单位获取参赛者"""
    participants = ParticipantService.get_participants_by_organization(db, organization)
    return [ParticipantResponse(**p.to_dict()) for p in participants]

@router.get("/group/{group_id}", response_model=List[ParticipantResponse])
async def get_participants_by_group(group_id: int, db: Session = Depends(get_db)):
    """根据组别获取参赛者"""
    participants = ParticipantService.get_participants_by_group(db, group_id)
    return [ParticipantResponse(**p.to_dict()) for p in participants]

@router.get("/status/checked-in", response_model=List[ParticipantResponse])
async def get_checked_in_participants(db: Session = Depends(get_db)):
    """获取已签到的参赛者"""
    participants = ParticipantService.get_checked_in_participants(db)
    return [ParticipantResponse(**p.to_dict()) for p in participants]

@router.get("/status/not-checked-in", response_model=List[ParticipantResponse])
async def get_not_checked_in_participants(db: Session = Depends(get_db)):
    """获取未签到的参赛者"""
    participants = ParticipantService.get_not_checked_in_participants(db)
    return [ParticipantResponse(**p.to_dict()) for p in participants]

@router.post("/{participant_id}/photo")
async def upload_participant_photo(
    participant_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传参赛者照片"""
    # 检查参赛者是否存在
    participant = ParticipantService.get_participant_by_id(db, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    try:
        # 保存照片
        photo_path = save_participant_photo(file, participant_id)
        
        # 更新参赛者照片路径
        ParticipantService.update_participant(db, participant_id, {"photo_path": photo_path})
        
        return {"message": "照片上传成功", "photo_path": photo_path}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"照片上传失败: {str(e)}")

@router.post("/batch")
async def batch_create_participants(participants_data: List[ParticipantCreate], db: Session = Depends(get_db)):
    """批量创建参赛者"""
    try:
        participants_dict = [p.dict() for p in participants_data]
        created_participants = ParticipantService.batch_create_participants(db, participants_dict)
        
        return {
            "message": f"成功创建 {len(created_participants)} 个参赛者",
            "participants": [ParticipantResponse(**p.to_dict()) for p in created_participants]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-qr-codes")
async def generate_qr_codes(db: Session = Depends(get_db)):
    """为所有参赛者生成二维码"""
    try:
        file_paths = ParticipantService.generate_qr_codes_for_all(db)
        return {
            "message": f"成功生成 {len(file_paths)} 个二维码",
            "file_paths": file_paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成二维码失败: {str(e)}")

@router.get("/statistics/overview")
async def get_participants_statistics(db: Session = Depends(get_db)):
    """获取参赛者统计信息"""
    return ParticipantService.get_participants_statistics(db)