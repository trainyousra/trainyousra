import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from yousra.config import Settings
from yousra.constants import (
  DEVELOPER_AVATAR,
  DEVELOPER_GITHUB,
  DEVELOPER_HANDLE,
  DEVELOPER_NAME,
  DEVELOPER_ORG,
  PROJECT_NAME,
  PROJECT_TAGLINE,
)
from yousra.logging_setup import LOG_RING, seed_developer_logs
from yousra.memory import MemoryStore

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"
log = logging.getLogger("yousra.dashboard")


def create_app(settings: Settings | None = None) -> FastAPI:
  settings = settings or Settings.load()
  store = MemoryStore(settings.data_dir / "yousra.db")
  templates = Jinja2Templates(directory=WEB_ROOT / "templates")

  @asynccontextmanager
  async def lifespan(_app: FastAPI):
    setup_logging = logging.getLogger("yousra")
    if not setup_logging.handlers:
      from yousra.logging_setup import setup_logging as _setup

      _setup(settings.logs_dir)
    seed_developer_logs()
    log.info("operations console ready — %s", DEVELOPER_GITHUB)
    yield

  app = FastAPI(
    title=f"{PROJECT_NAME} Operations",
    description=f"Built by {DEVELOPER_NAME} (@{DEVELOPER_HANDLE})",
    lifespan=lifespan,
  )
  static_dir = WEB_ROOT / "static"
  static_dir.mkdir(parents=True, exist_ok=True)
  app.mount("/static", StaticFiles(directory=static_dir), name="static")

  @app.get("/", response_class=HTMLResponse)
  async def index(request: Request):
    return templates.TemplateResponse(
      request,
      "index.html",
      {
        "project_name": PROJECT_NAME,
        "tagline": PROJECT_TAGLINE,
        "developer_name": DEVELOPER_NAME,
        "developer_handle": DEVELOPER_HANDLE,
        "developer_github": DEVELOPER_GITHUB,
        "developer_avatar": DEVELOPER_AVATAR,
        "developer_org": DEVELOPER_ORG,
        "memories": store.recent_memories(30),
        "memory_count": store.count(),
        "logs": list(LOG_RING)[:100],
      },
    )

  @app.get("/api/logs")
  async def api_logs():
    return {"logs": list(LOG_RING)[:100]}

  @app.get("/api/memories")
  async def api_memories():
    items = store.recent_memories(50)
    return {
      "count": store.count(),
      "items": [
        {
          "author": m.author,
          "lesson": m.lesson,
          "created_at": m.created_at,
        }
        for m in items
      ],
    }

  @app.get("/api/developer")
  async def api_developer():
    return {
      "name": DEVELOPER_NAME,
      "handle": DEVELOPER_HANDLE,
      "github": DEVELOPER_GITHUB,
      "avatar": DEVELOPER_AVATAR,
      "org": DEVELOPER_ORG,
      "role": "Original Architect · Lead Developer",
    }

  return app
