"""General analysis. Observations and traits are live; the other computed pages arrive in phase 3 (docs/project-plan.md)."""
from fastapi import APIRouter
from ..util import wrap, planned
from ..queries import observations as O, traits as T, mr_bands as B, archetypes as A, characters as C

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/observations")
def observations(topic: str | None = None):
    return wrap(O.all_(topic))


@router.get("/mr-bands")
def mr_bands(view: str = "all"):
    """view=all | others (without the configured player, whose sets are most of the data)"""
    return wrap(B.mr_bands("others" if view == "others" else "all"))


@router.get("/traits")
def traits(view: str = "all"):
    """view=all | others (sets without the configured player) | me (the configured player's wins against losses)"""
    if view not in ("all", "others", "me"):
        view = "all"
    return wrap(T.traits(view))


@router.get("/archetypes")
def archetypes(band: str | None = None):
    """Archetype mix, set win rates, typical characters / leans / spectra per archetype, and archetype vs archetype
    set results; `band` filters to one MR band (the band of the player whose archetype it is). `bands` = filter values."""
    return wrap(A.archetypes(band), bands=C.bands())


@router.get("/archetype-predictions")
def archetype_predictions():
    planned(3, "archetype and spectrum matchup predictions")
