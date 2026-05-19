import argparse
import logging
import threading

import uvicorn

from yousra.bot import YousraBot
from yousra.config import Settings
from yousra.constants import (
  DEVELOPER_GITHUB,
  DEVELOPER_HANDLE,
  DEVELOPER_NAME,
  PROJECT_NAME,
  X_PROFILE_URL,
)
from yousra.dashboard import create_app
from yousra.logging_setup import setup_logging


def main() -> None:
  parser = argparse.ArgumentParser(description="Run Yousra")
  parser.add_argument(
    "command",
    choices=["run", "poll-once", "dashboard"],
    help="run = bot + dashboard, poll-once = single cycle, dashboard = UI only",
  )
  args = parser.parse_args()
  settings = Settings.load()
  logger = setup_logging(settings.logs_dir)

  banner = (
    f"=== {PROJECT_NAME} v0.1 @ {X_PROFILE_URL} — architected by {DEVELOPER_NAME} "
    f"(@{DEVELOPER_HANDLE}) {DEVELOPER_GITHUB} ==="
  )
  logger.info(banner)

  if args.command == "dashboard":
    _serve_dashboard(settings)
    return

  if args.command == "poll-once":
    bot = YousraBot(settings)
    n = bot.poll_once()
    logger.info("handled %s mention(s)", n)
    return

  # run: dashboard + bot
  app = create_app(settings)
  thread = threading.Thread(
    target=lambda: uvicorn.run(
      app,
      host=settings.dashboard_host,
      port=settings.dashboard_port,
      log_level="warning",
    ),
    daemon=True,
  )
  thread.start()
  logger.info(
    "dashboard at http://%s:%s",
    settings.dashboard_host,
    settings.dashboard_port,
  )
  YousraBot(settings).run_forever()


def _serve_dashboard(settings: Settings) -> None:
  app = create_app(settings)
  uvicorn.run(
    app,
    host=settings.dashboard_host,
    port=settings.dashboard_port,
  )


if __name__ == "__main__":
  main()
