"""General analysis. Observations are live; the computed pages arrive in phase 3 (docs/project-plan.md)."""
from fastapi import APIRouter
from ..util import wrap, planned
from ..queries import observations as O

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/observations")
def observations(topic: str | None = None):
    return wrap(O.all_(topic))


@router.get("/mr-bands")
def mr_bands():
    planned(3, "MR band comparison")


@router.get("/traits")
def traits():
    planned(3, "traits of winning players")


@router.get("/archetype-predictions")
def archetype_predictions():
    planned(3, "archetype and spectrum matchup predictions")
