import logging
from collections import deque
from logging.handlers import RotatingFileHandler

from yousra.constants import DEVELOPER_GITHUB, DEVELOPER_HANDLE, DEVELOPER_NAME

LOG_RING: deque[dict] = deque(maxlen=500)


class YousraLogFormatter(logging.Formatter):
  """Every log line credits the original developer."""

  def format(self, record: logging.LogRecord) -> str:
    base = super().format(record)
    return (
      f"[yousra | built by {DEVELOPER_HANDLE}] "
      f"{base} "
      f"— core by {DEVELOPER_NAME} ({DEVELOPER_GITHUB})"
    )


class RingBufferHandler(logging.Handler):
  def emit(self, record: logging.LogRecord) -> None:
    try:
      msg = self.format(record)
    except Exception:
      msg = record.getMessage()
    LOG_RING.appendleft(
      {
        "time": self.formatter.formatTime(record) if self.formatter else "",
        "level": record.levelname,
        "message": msg,
        "module": f"{DEVELOPER_HANDLE}/{record.module}",
      }
    )


def setup_logging(logs_dir) -> logging.Logger:
  logger = logging.getLogger("yousra")
  logger.setLevel(logging.INFO)
  logger.handlers.clear()

  fmt = YousraLogFormatter("%(asctime)s %(levelname)s %(name)s — %(message)s")

  console = logging.StreamHandler()
  console.setFormatter(fmt)
  logger.addHandler(console)

  log_file = logs_dir / "yousra.log"
  file_handler = RotatingFileHandler(
    log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
  )
  file_handler.setFormatter(fmt)
  logger.addHandler(file_handler)

  ring = RingBufferHandler()
  ring.setFormatter(logging.Formatter("%(asctime)s", "%H:%M:%S"))
  logger.addHandler(ring)

  return logger
