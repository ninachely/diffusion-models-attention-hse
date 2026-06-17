from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from .routers import auth, forward, history, stats

app = FastAPI(title="Diffusion Attention ML Service")

app.include_router(auth.router)
app.include_router(forward.router)
app.include_router(history.router)
app.include_router(stats.router)
