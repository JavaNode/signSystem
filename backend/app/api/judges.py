from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from ..database import get_db
from ..services.judge_service import JudgeService

router = APIRouter()

class JudgeCreate(BaseModel):
    name: str
    username: str
    password: str
    organization: Optional[str] = None

class JudgeUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    organization: Optional[str] = None
    is_active: Optional[bool] = None

class JudgeLogin(BaseModel):
    username: str
    password: str

class JudgeResponse(BaseModel):
    id: int
    name: str
    username: str
    organization: Optional[str] = None
    is_active: bool
    score_count: int
    created_at: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/", response_model=JudgeResponse)
async def create_judge(judge: JudgeCreate, db: Session = Depends(get_db)):
    """创建评委"""
    try:
        new_judge = JudgeService.create_judge(
            db, judge.name, judge.username, judge.password, judge.organization
        )
        return JudgeResponse(**new_judge.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login_judge(login_data: JudgeLogin, db: Session = Depends(get_db)):
    """评委登录"""
    result = JudgeService.authenticate_judge(db, login_data.username, login_data.password)
    
    if not result:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    return result

@router.get("/", response_model=List[JudgeResponse])
async def get_judges(include_inactive: bool = False, db: Session = Depends(get_db)):
    """获取评委列表"""
    judges = JudgeService.get_all_judges(db, include_inactive)
    return [JudgeResponse(**judge.to_dict()) for judge in judges]

@router.get("/{judge_id}", response_model=JudgeResponse)
async def get_judge(judge_id: int, db: Session = Depends(get_db)):
    """获取单个评委信息"""
    judge = JudgeService.get_judge_by_id(db, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    return JudgeResponse(**judge.to_dict())

@router.put("/{judge_id}", response_model=JudgeResponse)
async def update_judge(
    judge_id: int, 
    judge_update: JudgeUpdate, 
    db: Session = Depends(get_db)
):
    """更新评委信息"""
    # 过滤掉None值
    update_data = {k: v for k, v in judge_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    try:
        updated_judge = JudgeService.update_judge(db, judge_id, update_data)
        if not updated_judge:
            raise HTTPException(status_code=404, detail="评委不存在")
        
        return JudgeResponse(**updated_judge.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{judge_id}")
async def delete_judge(judge_id: int, db: Session = Depends(get_db)):
    """删除评委"""
    success = JudgeService.delete_judge(db, judge_id)
    if not success:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    return {"message": "评委删除成功"}

@router.post("/{judge_id}/deactivate")
async def deactivate_judge(judge_id: int, db: Session = Depends(get_db)):
    """停用评委"""
    success = JudgeService.deactivate_judge(db, judge_id)
    if not success:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    return {"message": "评委已停用"}

@router.post("/{judge_id}/activate")
async def activate_judge(judge_id: int, db: Session = Depends(get_db)):
    """激活评委"""
    success = JudgeService.activate_judge(db, judge_id)
    if not success:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    return {"message": "评委已激活"}

@router.post("/{judge_id}/reset-password")
async def reset_judge_password(
    judge_id: int, 
    new_password: str, 
    db: Session = Depends(get_db)
):
    """重置评委密码（管理员功能）"""
    success = JudgeService.reset_judge_password(db, judge_id, new_password)
    if not success:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    return {"message": "密码重置成功"}

@router.post("/{judge_id}/change-password")
async def change_judge_password(
    judge_id: int,
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db)
):
    """评委修改密码"""
    result = JudgeService.change_judge_password(
        db, judge_id, password_data.old_password, password_data.new_password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/{judge_id}/profile")
async def get_judge_profile(judge_id: int, db: Session = Depends(get_db)):
    """获取评委个人信息"""
    profile = JudgeService.get_judge_profile(db, judge_id)
    if not profile:
        raise HTTPException(status_code=404, detail="评委不存在")
    
    return profile

@router.post("/batch")
async def batch_create_judges(judges_data: List[JudgeCreate], db: Session = Depends(get_db)):
    """批量创建评委"""
    try:
        judges_dict = [j.dict() for j in judges_data]
        created_judges = JudgeService.batch_create_judges(db, judges_dict)
        
        return {
            "message": f"成功创建 {len(created_judges)} 个评委",
            "judges": [JudgeResponse(**j.to_dict()) for j in created_judges]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/statistics/overview")
async def get_judges_statistics(db: Session = Depends(get_db)):
    """获取评委统计信息"""
    return JudgeService.get_judge_statistics(db)