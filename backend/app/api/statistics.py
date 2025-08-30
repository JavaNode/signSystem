from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.statistics_service import StatisticsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_statistics(db: Session = Depends(get_db)):
    """获取仪表板统计数据"""
    return StatisticsService.get_dashboard_statistics(db)

@router.get("/checkin/timeline")
async def get_checkin_timeline(db: Session = Depends(get_db)):
    """获取签到时间线统计"""
    return StatisticsService.get_checkin_timeline(db)

@router.get("/organizations")
async def get_organization_statistics(db: Session = Depends(get_db)):
    """获取单位统计信息"""
    return StatisticsService.get_organization_statistics(db)

@router.get("/groups")
async def get_group_statistics(db: Session = Depends(get_db)):
    """获取分组统计信息"""
    return StatisticsService.get_group_statistics(db)

@router.get("/scoring/heatmap")
async def get_scoring_heatmap(db: Session = Depends(get_db)):
    """获取评分热力图数据"""
    return StatisticsService.get_scoring_heatmap(db)

@router.get("/performance/trends")
async def get_performance_trends(db: Session = Depends(get_db)):
    """获取性能趋势数据"""
    return StatisticsService.get_performance_trends(db)

@router.get("/competition/summary")
async def get_competition_summary(db: Session = Depends(get_db)):
    """获取比赛总结统计"""
    return StatisticsService.get_competition_summary(db)

@router.get("/export/full-report")
async def export_full_report(db: Session = Depends(get_db)):
    """导出完整报告"""
    return StatisticsService.export_full_report(db)