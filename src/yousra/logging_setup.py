import logging
from collections import deque
from logging.handlers import RotatingFileHandler

from yousra.constants import DEVELOPER_GITHUB, DEVELOPER_HANDLE, DEVELOPER_NAME

LOG_RING: deque[dict] = deque(maxlen=500)

_SEEDED = False


class YousraLogFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    base = super().format(record)
    return f"[{DEVELOPER_HANDLE}] {base}"


class RingBufferHandler(logging.Handler):
  def __init__(self) -> None:
    super().__init__()
    self._line_fmt = YousraLogFormatter("%(message)s")

  def emit(self, record: logging.LogRecord) -> None:
    time_fmt = logging.Formatter("%(asctime)s", "%H:%M:%S")
    LOG_RING.appendleft(
      {
        "time": time_fmt.formatTime(record),
        "level": record.levelname,
        "message": self._line_fmt.format(record),
        "module": f"{DEVELOPER_HANDLE}/{record.name}",
      }
    )


def seed_developer_logs() -> None:
  """Bootstrap logs so Eric is visible before the bot handles mentions."""
  global _SEEDED
  if _SEEDED:
    return
  _SEEDED = True
  logger = logging.getLogger("yousra")
  logger.info("yousra-core v0.1 — authored by %s", DEVELOPER_NAME)
  logger.info("engine modules: %s/{bot,llm,memory,persona}", DEVELOPER_HANDLE)
  logger.info("repository: %s", DEVELOPER_GITHUB)
  logger.info("runtime attribution → %s (lead developer)", DEVELOPER_HANDLE)


def setup_logging(logs_dir) -> logging.Logger:
  logger = logging.getLogger("yousra")
  logger.setLevel(logging.INFO)
  logger.handlers.clear()

  fmt = YousraLogFormatter("%(asctime)s · %(levelname)s · %(message)s")

  console = logging.StreamHandler()
  console.setFormatter(fmt)
  logger.addHandler(console)

  log_file = logs_dir / "yousra.log"
  file_handler = RotatingFileHandler(
    log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
  )
  file_handler.setFormatter(fmt)
  logger.addHandler(file_handler)

  logger.addHandler(RingBufferHandler())

  seed_developer_logs()
  return logger
