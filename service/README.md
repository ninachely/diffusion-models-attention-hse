# Diffusion Models Service (FastAPI)

Сервис инференса: `POST /forward` (t2i/i2i), логирование в SQLite, `history/stats` под JWT. Есть режим **DUMMY=1** (без модели) и режим **FLUX** (через diffusers + HF токен).

---

## Быстрый старт

Из корня репозитория:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

# зависимости сервиса
python -m pip install -r service/requirements.txt -r service/requirements-torch-cpu.txt
```

> Для CUDA (Linux/Windows):  
> `python -m pip install -r service/requirements.txt -r service/requirements-torch-cu121.txt`

---

## Конфиг (.env)

Создай **service/.env** (и добавь `service/.env` в `.gitignore`):

```env
JWT_SECRET=change-me
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
CONFIRM_TOKEN=change-me-too

# нужно только для FLUX
HUGGINGFACE_HUB_TOKEN=hf_xxx
```

---

## Запуск

### Dummy (без FLUX)
```bash
export DUMMY=1
./service/scripts/run_server.sh
```

### FLUX (реальный инференс)
```bash
unset DUMMY
./service/scripts/run_server.sh
```

Сервер: http://127.0.0.1:8000

---

## Тесты (из корня)

### t2i (JSON)
```bash
PY=./.venv/bin/python
rm -f out_t2i.png /tmp/t2i.json /tmp/t2i.hdr

curl -sS -D /tmp/t2i.hdr -o /tmp/t2i.json -X POST http://127.0.0.1:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"prompt":"hello","width":256,"height":256}'

tail -n 1 /tmp/t2i.hdr
head -c 120 /tmp/t2i.json; echo

$PY - <<'PY'
import json, base64
d=json.load(open("/tmp/t2i.json"))
open("out_t2i.png","wb").write(base64.b64decode(d["image_b64"]))
print("saved out_t2i.png")
PY

open out_t2i.png
```

### i2i (multipart)
```bash
PY=./.venv/bin/python
IMG="/ABS/PATH/TO/service/input.png"
rm -f out_i2i.png /tmp/i2i.json /tmp/i2i.hdr

curl -sS -D /tmp/i2i.hdr -o /tmp/i2i.json -X POST http://127.0.0.1:8000/forward \
  -H "x-prompt: paint it red" \
  -F "image=@$IMG"

tail -n 1 /tmp/i2i.hdr
head -c 120 /tmp/i2i.json; echo

$PY - <<'PY'
import json, base64
d=json.load(open("/tmp/i2i.json"))
open("out_i2i.png","wb").write(base64.b64decode(d["image_b64"]))
print("saved out_i2i.png")
PY

open out_i2i.png
```

---

## Auth / history / stats

```bash
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" \
| ./\.venv/bin/python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s http://127.0.0.1:8000/history -H "Authorization: Bearer $TOKEN" | head -c 800; echo
curl -s http://127.0.0.1:8000/stats   -H "Authorization: Bearer $TOKEN"; echo

curl -s -X DELETE http://127.0.0.1:8000/history \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-confirm-token: change-me-too"
echo
```

---

## Частые проблемы

- `JSONDecodeError` в тесте → сервер вернул не JSON (например текст ошибки). Используй тесты с `-D ... -o ...` и смотри `tail -n 1 /tmp/*.hdr`.
- `401 / gated repo` (FLUX) → нет доступа к модели на HF. Нужен токен с `read` + “request/agree access” на странице модели + `HUGGINGFACE_HUB_TOKEN` в `service/.env`.
