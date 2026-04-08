import io
import time
from typing import Optional

from PIL import Image
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy import insert

from ..db import SessionLocal
from ..models import RequestLog
from ..utils import pil_to_b64

router = APIRouter(tags=["inference"])


def bad_request():
    return PlainTextResponse("bad request", status_code=400)


def model_failed():
    return PlainTextResponse("модель не смогла обработать данные", status_code=403)


def _h_int(headers, key: str, default: int) -> int:
    try:
        v = headers.get(key)
        return default if v is None else int(v)
    except Exception:
        return default


def _h_float(headers, key: str, default: float) -> float:
    try:
        v = headers.get(key)
        return default if v is None else float(v)
    except Exception:
        return default


def _h_opt_int(headers, key: str) -> Optional[int]:
    v = headers.get(key)
    if v is None or str(v).strip() == "":
        return None
    try:
        return int(v)
    except Exception:
        return None


@router.post("/forward")
async def forward(request: Request):
    ct = (request.headers.get("content-type", "") or "").lower()
    t0 = time.perf_counter()

    log = {
        "endpoint": "/forward",
        "mode": "unknown",        # t2i / i2i / unknown
        "input_type": "unknown",  # json / multipart / unknown
        "prompt_len": 0,
        "token_count": 0,
        "image_w": None,
        "image_h": None,
        "duration_ms": 0.0,
        "status_code": 200,
        "error": None,
    }

    resp = None

    try:
        # ---------- JSON: text2image ----------
        if ct.startswith("application/json"):
            log["input_type"] = "json"
            log["mode"] = "t2i"

            try:
                data = await request.json()
            except Exception:
                log["status_code"] = 400
                resp = bad_request()
                return resp

            prompt = data.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                log["status_code"] = 400
                resp = bad_request()
                return resp

            width = int(data.get("width", 512))
            height = int(data.get("height", 512))
            steps = int(data.get("steps", 20))
            seed = data.get("seed", None)
            seed = int(seed) if seed is not None else None

            device = request.headers.get("x-device", "auto")

            log["prompt_len"] = len(prompt)
            log["token_count"] = len(prompt.split())
            log["image_w"] = width
            log["image_h"] = height

            try:
                from ..flux_runner import flux_runner

                img: Image.Image = flux_runner.text2image(
                    prompt=prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    seed=seed,
                    device=device,
                )
            except Exception as e:
                log["status_code"] = 403
                log["error"] = str(e)[:1000]
                resp = model_failed()
                return resp

            resp = JSONResponse({"ok": True, "image_b64": pil_to_b64(img)})
            return resp

        # ---------- multipart: image2image ----------
        if ct.startswith("multipart/form-data"):
            log["input_type"] = "multipart"
            log["mode"] = "i2i"

            form = await request.form()
            file = form.get("image", None)
            if file is None:
                log["status_code"] = 400
                resp = bad_request()
                return resp

            prompt = (request.headers.get("x-prompt") or "").strip()
            if not prompt:
                log["status_code"] = 400
                resp = bad_request()
                return resp

            steps = _h_int(request.headers, "x-steps", 20)
            seed = _h_opt_int(request.headers, "x-seed")
            strength = _h_float(request.headers, "x-strength", 0.6)
            device = request.headers.get("x-device", "auto")

            raw = await file.read()
            try:
                img_in = Image.open(io.BytesIO(raw)).convert("RGB")
            except Exception:
                log["status_code"] = 400
                resp = bad_request()
                return resp

            w, h = img_in.size
            log["prompt_len"] = len(prompt)
            log["token_count"] = len(prompt.split())
            log["image_w"] = w
            log["image_h"] = h

            try:
                from ..flux_runner import flux_runner

                img_out: Image.Image = flux_runner.image2image(
                    image=img_in,
                    prompt=prompt,
                    steps=steps,
                    strength=strength,
                    seed=seed,
                    device=device,
                )
            except Exception as e:
                log["status_code"] = 403
                log["error"] = str(e)[:1000]
                resp = model_failed()
                return resp

            resp = JSONResponse({"ok": True, "image_b64": pil_to_b64(img_out)})
            return resp

        log["status_code"] = 400
        resp = bad_request()
        return resp

    finally:
        log["duration_ms"] = (time.perf_counter() - t0) * 1000.0
        if resp is not None:
            log["status_code"] = getattr(resp, "status_code", log["status_code"])

        try:
            with SessionLocal() as db:
                db.execute(insert(RequestLog).values(**log))
                db.commit()
        except Exception:
            pass
