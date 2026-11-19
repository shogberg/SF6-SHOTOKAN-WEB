from fastapi import APIRouter
from ..util import wrap, not_found
from ..queries import sets as Q

router = APIRouter(tags=["sets"])


@router.get("/sets/{set_key}")
def detail(set_key: str):
    d = Q.detail(set_key)
    return wrap(d) if d else not_found("set")
