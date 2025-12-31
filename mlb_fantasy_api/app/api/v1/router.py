from fastapi import APIRouter

from app.api.v1.endpoints import health, players, scouting, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(players.router)
api_router.include_router(scouting.router)
api_router.include_router(users.router)
