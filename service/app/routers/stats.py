from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
import numpy as np

from ..deps import require_admin
from ..db import get_db
from ..models import RequestLog

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    dependencies=[Depends(require_admin)],
)

def qpack(values):
    """
    Returns mean / p50 / p95 / p99 for an array-like of numbers.
    If there are no values, returns None.
    """
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return None
    return {
        "mean": float(arr.mean()),
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
    }

@router.get("")
def stats(db: Session = Depends(get_db)):
    # last 100 requests for stability
    rows = db.execute(
        select(RequestLog).order_by(desc(RequestLog.id)).limit(100)
    ).scalars().all()

    ok_rows = [r for r in rows if r.status_code == 200]

    return {
        "count_total": len(rows),
        "count_ok": len(ok_rows),

        "latency_ms": qpack(r.duration_ms for r in ok_rows),

        # text characteristics
        "prompt_len_chars": qpack(r.prompt_len for r in rows),
        "token_count": qpack(r.token_count for r in rows),

        # image characteristics (only where present)
        "image_w": qpack(r.image_w for r in rows if r.image_w is not None),
        "image_h": qpack(r.image_h for r in rows if r.image_h is not None),
    }
