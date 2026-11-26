from fastapi import APIRouter
from ..util import wrap, planned
from ..queries import characters as C

router = APIRouter(tags=["character matchups"])


@router.get("/matchups")
def matchups(band: str | None = None):
    """Stats by character: game win rates of every character against every other, optionally for one MR band
    (the band of the player using the character). `bands` lists the filter values, "all" first."""
    return wrap(C.character_stats(band), bands=C.bands(), band=band or "all")


@router.get("/matchups/{char_a}/{char_b}")
def matchup_detail(char_a: str, char_b: str):
    planned(4, "character matchup detail (damage, starters, punishes)")
