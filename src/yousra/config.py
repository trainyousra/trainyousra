import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    x_api_key: str
    x_api_secret: str
    x_access_token: str
    x_access_token_secret: str
    x_bearer_token: str
    x_bot_username: str
    openai_api_key: str
    openai_model: str
    poll_interval_seconds: int
    max_tweet_length: int
    max_memories_in_prompt: int
    dashboard_host: str
    dashboard_port: int
    data_dir: Path
    logs_dir: Path

    @classmethod
    def load(cls) -> "Settings":
        data_dir = ROOT / "data"
        logs_dir = ROOT / "logs"
        data_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        return cls(
            x_api_key=os.getenv("X_API_KEY", ""),
            x_api_secret=os.getenv("X_API_SECRET", ""),
            x_access_token=os.getenv("X_ACCESS_TOKEN", ""),
            x_access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET", ""),
            x_bearer_token=os.getenv("X_BEARER_TOKEN", ""),
            x_bot_username=os.getenv("X_BOT_USERNAME", "yousra").lstrip("@"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "45")),
            max_tweet_length=int(os.getenv("MAX_TWEET_LENGTH", "280")),
            max_memories_in_prompt=int(os.getenv("MAX_MEMORIES_IN_PROMPT", "24")),
            dashboard_host=os.getenv("DASHBOARD_HOST", "127.0.0.1"),
            dashboard_port=int(os.getenv("DASHBOARD_PORT", "8787")),
            data_dir=data_dir,
            logs_dir=logs_dir,
        )

    def validate_x(self) -> None:
        missing = [
            k
            for k, v in {
                "X_API_KEY": self.x_api_key,
                "X_API_SECRET": self.x_api_secret,
                "X_ACCESS_TOKEN": self.x_access_token,
                "X_ACCESS_TOKEN_SECRET": self.x_access_token_secret,
                "X_BEARER_TOKEN": self.x_bearer_token,
            }.items()
            if not v
        ]
        if missing:
            raise ValueError(f"Missing X credentials: {', '.join(missing)}")

    def validate_openai(self) -> None:
        if not self.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")
