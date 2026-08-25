from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    health,
    profile,
    publications,
    patents,
    funding,
    research_intelligence,
    patent_intelligence,
    technology_intelligence,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["Research Profile"])
api_router.include_router(publications.router, prefix="/publications", tags=["Publications"])
api_router.include_router(patents.router, prefix="/patents", tags=["Patents"])
api_router.include_router(funding.router, prefix="/funding", tags=["Funding Opportunities"])
api_router.include_router(research_intelligence.router, prefix="/research-intelligence", tags=["Research Intelligence"])
api_router.include_router(patent_intelligence.router, prefix="/patent-intelligence", tags=["Patent Intelligence"])
api_router.include_router(technology_intelligence.router, prefix="/technology-intelligence", tags=["Technology Intelligence & Whitespace"])

