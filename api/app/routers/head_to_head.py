from fastapi import APIRouter
from ..util import wrap, not_found
from ..queries import head_to_head as Q

router = APIRouter(tags=["head to head"])


@router.get("/h2h/{a}/{b}")
def h2h(a: int, b: int):
    d = Q.h2h(a, b)
    return wrap(d) if d else not_found("player")
