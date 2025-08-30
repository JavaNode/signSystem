from fastapi import APIRouter
from .participants import router as participants_router
from .groups import router as groups_router
from .judges import router as judges_router
from .scores import router as scores_router
from .checkin import router as checkin_router
from .statistics import router as statistics_router
from .admin import router as admin_router

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(participants_router, prefix="/participants", tags=["participants"])
api_router.include_router(groups_router, prefix="/groups", tags=["groups"])
api_router.include_router(judges_router, prefix="/judges", tags=["judges"])
api_router.include_router(scores_router, prefix="/scores", tags=["scores"])
api_router.include_router(checkin_router, prefix="/checkin", tags=["checkin"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["statistics"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

__all__ = ["api_router"]