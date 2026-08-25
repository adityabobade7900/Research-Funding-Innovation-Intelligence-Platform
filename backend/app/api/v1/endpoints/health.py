from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.core.config import settings
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check verifying API operational status and database connectivity."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return ApiResponse(
        success=(db_status == "healthy"),
        data={
            "status": "online",
            "project_name": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "database": db_status,
            "version": "1.0.0"
        },
        message="System health status retrieved successfully"
    )
