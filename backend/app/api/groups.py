from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from ..database import get_db
from ..services.group_service import GroupService

router = APIRouter()

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    draw_order: Optional[int] = None

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    draw_order: Optional[int] = None
    member_count: int
    checkin_count: int
    checkin_rate: float
    organizations: List[str]
    created_at: Optional[str] = None

class AutoGroupRequest(BaseModel):
    max_group_size: int = 20

class MergeGroupRequest(BaseModel):
    min_group_size: int = 8
    max_group_size: int = 20

@router.post("/", response_model=GroupResponse)
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """创建分组"""
    try:
        new_group = GroupService.create_group(db, group.name, group.description)
        return GroupResponse(**new_group.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[GroupResponse])
async def get_groups(db: Session = Depends(get_db)):
    """获取所有分组"""
    groups = GroupService.get_all_groups(db)
    return [GroupResponse(**group.to_dict()) for group in groups]

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    """获取单个分组信息"""
    group = GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    return GroupResponse(**group.to_dict())

@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int, 
    group_update: GroupUpdate, 
    db: Session = Depends(get_db)
):
    """更新分组信息"""
    # 过滤掉None值
    update_data = {k: v for k, v in group_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    try:
        updated_group = GroupService.update_group(db, group_id, update_data)
        if not updated_group:
            raise HTTPException(status_code=404, detail="分组不存在")
        
        return GroupResponse(**updated_group.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{group_id}")
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    """删除分组"""
    success = GroupService.delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    return {"message": "分组删除成功"}

@router.get("/{group_id}/members")
async def get_group_members(group_id: int, db: Session = Depends(get_db)):
    """获取组内成员"""
    members = GroupService.get_group_members(db, group_id)
    
    # 检查分组是否存在
    group = GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    return {
        "group_id": group_id,
        "group_name": group.name,
        "member_count": len(members),
        "members": [member.to_dict() for member in members]
    }

@router.post("/{group_id}/assign/{participant_id}")
async def assign_participant_to_group(
    group_id: int, 
    participant_id: int, 
    db: Session = Depends(get_db)
):
    """将参赛者分配到指定组"""
    success = GroupService.assign_participant_to_group(db, participant_id, group_id)
    if not success:
        raise HTTPException(status_code=400, detail="分配失败，请检查参赛者和分组是否存在")
    
    return {"message": "参赛者分配成功"}

@router.delete("/remove/{participant_id}")
async def remove_participant_from_group(participant_id: int, db: Session = Depends(get_db)):
    """将参赛者从组中移除"""
    success = GroupService.remove_participant_from_group(db, participant_id)
    if not success:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    return {"message": "参赛者已从组中移除"}

@router.get("/ungrouped/participants")
async def get_ungrouped_participants(db: Session = Depends(get_db)):
    """获取未分组的参赛者"""
    participants = GroupService.get_ungrouped_participants(db)
    return {
        "count": len(participants),
        "participants": [p.to_dict() for p in participants]
    }

@router.post("/auto-group/by-organization")
async def auto_group_by_organization(
    request: AutoGroupRequest, 
    db: Session = Depends(get_db)
):
    """按单位自动分组"""
    try:
        created_groups = GroupService.auto_group_by_organization(db, request.max_group_size)
        
        return {
            "message": f"自动分组完成，创建了 {len(created_groups)} 个组",
            "groups": [GroupResponse(**group.to_dict()) for group in created_groups]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/merge-small-organizations")
async def merge_small_organizations(
    request: MergeGroupRequest, 
    db: Session = Depends(get_db)
):
    """合并小单位到同一组"""
    try:
        created_groups = GroupService.merge_small_organizations(
            db, request.min_group_size, request.max_group_size
        )
        
        return {
            "message": f"合并分组完成，创建了 {len(created_groups)} 个组",
            "groups": [GroupResponse(**group.to_dict()) for group in created_groups]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/draw-lots")
async def draw_lots_for_groups(db: Session = Depends(get_db)):
    """为所有组抽签确定出场顺序"""
    result = GroupService.draw_lots_for_groups(db)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/statistics/overview")
async def get_groups_statistics(db: Session = Depends(get_db)):
    """获取分组统计信息"""
    return GroupService.get_groups_statistics(db)

# 批量操作接口
@router.post("/batch/assign")
async def batch_assign_participants(
    assignments: List[dict], 
    db: Session = Depends(get_db)
):
    """批量分配参赛者到组
    
    assignments格式: [{"participant_id": 1, "group_id": 1}, ...]
    """
    success_count = 0
    errors = []
    
    for i, assignment in enumerate(assignments):
        try:
            participant_id = assignment.get("participant_id")
            group_id = assignment.get("group_id")
            
            if not participant_id or not group_id:
                errors.append({"index": i, "error": "缺少participant_id或group_id"})
                continue
            
            success = GroupService.assign_participant_to_group(db, participant_id, group_id)
            if success:
                success_count += 1
            else:
                errors.append({"index": i, "error": "分配失败"})
                
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    return {
        "success_count": success_count,
        "error_count": len(errors),
        "errors": errors
    }

@router.get("/draw-order/list")
async def get_groups_by_draw_order(db: Session = Depends(get_db)):
    """按抽签顺序获取分组列表"""
    groups = GroupService.get_all_groups(db)
    
    # 按抽签顺序排序
    sorted_groups = sorted(groups, key=lambda x: x.draw_order or 999)
    
    return [
        {
            "group_id": group.id,
            "group_name": group.name,
            "draw_order": group.draw_order,
            "member_count": group.member_count,
            "checkin_count": group.checkin_count,
            "organizations": group.organizations
        }
        for group in sorted_groups
    ]