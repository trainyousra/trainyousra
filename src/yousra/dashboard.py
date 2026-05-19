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
from yousra.logging_setup import LOG_RING
from yousra.memory import MemoryStore

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"


def create_app(settings: Settings | None = None) -> FastAPI:
  settings = settings or Settings.load()
  store = MemoryStore(settings.data_dir / "yousra.db")
  templates = Jinja2Templates(directory=WEB_ROOT / "templates")

  app = FastAPI(
    title=f"{PROJECT_NAME} dashboard",
    description=f"Built by {DEVELOPER_NAME}",
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
        "logs": list(LOG_RING)[:80],
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

  return app
