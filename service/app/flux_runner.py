import os
import time
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


def _is_true_env(name: str) -> bool:
    v = os.environ.get(name)
    if v is None:
        return False
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


def _choose_device(requested: str) -> str:
    """
    requested: 'cpu' | 'mps' | 'cuda' | 'auto'
    """
    requested = (requested or "auto").strip().lower()
    if requested in ("cpu", "mps", "cuda"):
        return requested

    # auto
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def _dummy_image(w: int, h: int, title: str, subtitle: str) -> Image.Image:
    img = Image.new("RGB", (w, h), (240, 240, 240))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, w, 64], fill=(30, 30, 30))
    d.text((12, 18), title, fill=(255, 255, 255))

    d.text((12, 84), subtitle[:200], fill=(10, 10, 10))

    d.rectangle([12, h - 52, w - 12, h - 12], outline=(255, 0, 0), width=3)
    d.text((22, h - 44), "DUMMY MODE (no HF / no diffusers)", fill=(255, 0, 0))
    return img


class FluxRunner:
    """
    Ленивая загрузка: ничего тяжелого не делаем в __init__.
    """

    def __init__(self) -> None:
        self._pipe = None
        self._device = None
        self._loaded_model_id = None

    def _ensure_pipe(self, device: str = "auto") -> None:
        if _is_true_env("DUMMY"):
            return

        if self._pipe is not None:
            return

        import torch
        from diffusers import FluxPipeline

        self._device = _choose_device(device)

        model_id = os.environ.get("FLUX_MODEL_ID", "black-forest-labs/FLUX.1-schnell")

        dtype = torch.float16 if self._device in ("cuda", "mps") else torch.float32

        pipe = FluxPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
        )

        pipe.to(self._device)
        self._pipe = pipe
        self._loaded_model_id = model_id

    def text2image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        seed: Optional[int] = None,
        device: str = "auto",
    ) -> Image.Image:
        if _is_true_env("DUMMY"):
            return _dummy_image(width, height, "t2i", prompt)

        self._ensure_pipe(device=device)

        import torch

        gen = None
        if seed is not None:
            gen = torch.Generator(device=self._device).manual_seed(int(seed))

        with torch.inference_mode():
            out = self._pipe(
                prompt=prompt,
                height=int(height),
                width=int(width),
                num_inference_steps=int(steps),
                generator=gen,
            )

        img = out.images[0]
        if not isinstance(img, Image.Image):
            img = Image.fromarray(img)
        return img

    def image2image(
        self,
        image: Image.Image,
        prompt: str,
        steps: int = 20,
        strength: float = 0.6,
        seed: Optional[int] = None,
        device: str = "auto",
    ) -> Image.Image:
        if _is_true_env("DUMMY"):
            w, h = image.size
            return _dummy_image(w, h, "i2i", prompt)

        self._ensure_pipe(device=device)

        import torch

        gen = None
        if seed is not None:
            gen = torch.Generator(device=self._device).manual_seed(int(seed))

        try:
            with torch.inference_mode():
                out = self._pipe(
                    prompt=prompt,
                    image=image,
                    strength=float(strength),
                    num_inference_steps=int(steps),
                    generator=gen,
                )
            img = out.images[0]
            if not isinstance(img, Image.Image):
                img = Image.fromarray(img)
            return img
        except TypeError:
            img = image.convert("RGB").copy()
            d = ImageDraw.Draw(img)
            d.rectangle([0, 0, img.size[0], 54], fill=(0, 0, 0))
            d.text((12, 16), f"i2i fallback: {prompt[:80]}", fill=(255, 255, 255))
            return img


flux_runner = FluxRunner()
