from fastapi import APIRouter

from app.api import catalog, match_events, matches, players, teams

router = APIRouter()
router.include_router(catalog.router)
router.include_router(match_events.router)
router.include_router(matches.router)
router.include_router(players.router)
router.include_router(teams.router)


@router.get("/")
def root():
    return {
        "module": "sport-basketball",
        "message": "API del módulo basketball",
        "endpoints": [
            "/suite-events",
            "/matches",
            "/regulations",
            "/result-types",
            "/players",
            "/teams",
            "/matches/{id}/events",
        ],
    }