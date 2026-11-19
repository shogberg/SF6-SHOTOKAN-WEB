from ..db import rows
from ..util import loads


def all_(topic=None):
    r = rows("select * from observations" + (" where topic=:t" if topic else "") + " order by written_at desc, obs_id desc", t=topic)
    for o in r:
        o["evidence"] = loads(o.pop("evidence_json"), [])
    return r
