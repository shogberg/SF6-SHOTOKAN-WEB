from fastapi import APIRouter
from ..util import planned

router = APIRouter(tags=["character matchups"])


@router.get("/matchups")
@router.get("/matchups/{char_a}/{char_b}")
def matchups(char_a: str | None = None, char_b: str | None = None):
    planned(4, "character matchup stats")
