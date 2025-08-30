from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from ..database import get_db
from ..services.score_service import ScoreService

router = APIRouter()

class ScoreSubmit(BaseModel):
    participant_id: int
    judge_id: int
    score: float
    round_number: int = 1
    
    @validator('score')
    def validate_score(cls, v):
        if not (0 <= v <= 10):
            raise ValueError('评分必须在0-10之间')
        return v

class ScoreResponse(BaseModel):
    id: int
    participant_id: int
    participant_name: Optional[str] = None
    judge_id: int
    judge_name: Optional[str] = None
    score: float
    round_number: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class RankingItem(BaseModel):
    rank: int
    participant: dict
    average_score: float
    score_count: int
    total_judges: int

@router.post("/submit")
async def submit_score(score_data: ScoreSubmit, db: Session = Depends(get_db)):
    """提交评分"""
    result = ScoreService.submit_score(
        db=db,
        participant_id=score_data.participant_id,
        judge_id=score_data.judge_id,
        score=score_data.score,
        round_number=score_data.round_number
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/participant/{participant_id}", response_model=List[ScoreResponse])
async def get_participant_scores(
    participant_id: int, 
    round_number: int = 1, 
    db: Session = Depends(get_db)
):
    """获取参赛者的所有评分"""
    scores = ScoreService.get_participant_scores(db, participant_id, round_number)
    return [ScoreResponse(**score.to_dict()) for score in scores]

@router.get("/judge/{judge_id}", response_model=List[ScoreResponse])
async def get_judge_scores(
    judge_id: int, 
    round_number: int = 1, 
    db: Session = Depends(get_db)
):
    """获取评委的所有评分"""
    scores = ScoreService.get_judge_scores(db, judge_id, round_number)
    return [ScoreResponse(**score.to_dict()) for score in scores]

@router.get("/participant/{participant_id}/average")
async def get_participant_average(
    participant_id: int, 
    round_number: int = 1, 
    db: Session = Depends(get_db)
):
    """获取参赛者平均分"""
    average = ScoreService.calculate_participant_average(db, participant_id, round_number)
    
    if average is None:
        return {"participant_id": participant_id, "average_score": None, "message": "暂无评分"}
    
    return {"participant_id": participant_id, "average_score": average}

@router.get("/ranking", response_model=List[RankingItem])
async def get_ranking(round_number: int = 1, db: Session = Depends(get_db)):
    """获取排行榜"""
    ranking = ScoreService.get_ranking(db, round_number)
    return [RankingItem(**item) for item in ranking]

@router.get("/progress")
async def get_scoring_progress(round_number: int = 1, db: Session = Depends(get_db)):
    """获取评分进度"""
    return ScoreService.get_scoring_progress(db, round_number)

@router.delete("/{score_id}")
async def delete_score(score_id: int, db: Session = Depends(get_db)):
    """删除评分"""
    success = ScoreService.delete_score(db, score_id)
    if not success:
        raise HTTPException(status_code=404, detail="评分记录不存在")
    
    return {"message": "评分删除成功"}

@router.get("/participant/{participant_id}/detailed")
async def get_participant_detailed_scores(
    participant_id: int, 
    round_number: int = 1, 
    db: Session = Depends(get_db)
):
    """获取参赛者详细评分信息"""
    details = ScoreService.get_participant_detailed_scores(db, participant_id, round_number)
    
    if not details:
        raise HTTPException(status_code=404, detail="参赛者不存在")
    
    return details

@router.get("/export")
async def export_scores(round_number: int = 1, db: Session = Depends(get_db)):
    """导出评分数据"""
    return ScoreService.export_scores(db, round_number)

@router.get("/statistics")
async def get_score_statistics(round_number: int = 1, db: Session = Depends(get_db)):
    """获取评分统计信息"""
    return ScoreService.get_score_statistics(db, round_number)

# 批量评分接口
@router.post("/batch")
async def batch_submit_scores(scores_data: List[ScoreSubmit], db: Session = Depends(get_db)):
    """批量提交评分"""
    results = []
    errors = []
    
    for i, score_data in enumerate(scores_data):
        try:
            result = ScoreService.submit_score(
                db=db,
                participant_id=score_data.participant_id,
                judge_id=score_data.judge_id,
                score=score_data.score,
                round_number=score_data.round_number
            )
            
            if result["success"]:
                results.append(result)
            else:
                errors.append({"index": i, "error": result["message"]})
                
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors
    }

# 评委评分界面专用接口
@router.get("/judge/{judge_id}/next-participant")
async def get_next_participant_to_score(
    judge_id: int, 
    round_number: int = 1, 
    db: Session = Depends(get_db)
):
    """获取评委下一个需要评分的参赛者"""
    # 获取所有参赛者
    from ..services.participant_service import ParticipantService
    all_participants = ParticipantService.get_all_participants(db)
    
    # 获取该评委已评分的参赛者
    judge_scores = ScoreService.get_judge_scores(db, judge_id, round_number)
    scored_participant_ids = {score.participant_id for score in judge_scores}
    
    # 找到下一个未评分的参赛者
    for participant in all_participants:
        if participant.id not in scored_participant_ids:
            return {
                "participant": participant.to_dict(),
                "has_next": True
            }
    
    return {
        "participant": None,
        "has_next": False,
        "message": "所有参赛者已评分完成"
    }

@router.get("/judge/{judge_id}/progress")
async def get_judge_scoring_progress(
    judge_id: int, 
    round_number: int = 1, 
    db: Session = Depends(get_db)
):
    """获取评委评分进度"""
    from ..services.participant_service import ParticipantService
    
    total_participants = len(ParticipantService.get_all_participants(db))
    judge_scores = ScoreService.get_judge_scores(db, judge_id, round_number)
    scored_count = len(judge_scores)
    
    return {
        "judge_id": judge_id,
        "total_participants": total_participants,
        "scored_participants": scored_count,
        "remaining_participants": total_participants - scored_count,
        "completion_rate": round(scored_count / total_participants * 100, 2) if total_participants > 0 else 0
    }