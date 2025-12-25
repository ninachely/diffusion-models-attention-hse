from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from ..deps import require_admin
from ..db import get_db
from ..models import RequestLog
from ..config import settings

router = APIRouter(prefix="/history", tags=["history"])

@router.get("", dependencies=[Depends(require_admin)])
def get_history(db: Session = Depends(get_db)):
    rows = db.execute(select(RequestLog).order_by(RequestLog.id.desc())).scalars().all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "mode": r.mode,
            "input_type": r.input_type,
            "prompt_len": r.prompt_len,
            "token_count": r.token_count,
            "image_w": r.image_w,
            "image_h": r.image_h,
            "duration_ms": r.duration_ms,
            "status_code": r.status_code,
            "error": r.error,
        } for r in rows
    ]

@router.delete("", dependencies=[Depends(require_admin)])
def clear_history(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("x-confirm-token")
    if token != settings.HISTORY_DELETE_TOKEN:
        return PlainTextResponse("forbidden", status_code=403)
    db.execute(delete(RequestLog))
    db.commit()
    return {"ok": True}
