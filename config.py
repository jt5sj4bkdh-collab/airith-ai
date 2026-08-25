import os
from dataclasses import dataclass


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str
    channel_id: str
    owner_id: int
    auto_post_enabled: bool


settings = Settings(
    telegram_bot_token=required("TELEGRAM_BOT_TOKEN"),
    openai_api_key=required("OPENAI_API_KEY"),
    channel_id=required("CHANNEL_ID"),
    owner_id=int(required("OWNER_ID")),
    auto_post_enabled=os.getenv("AUTO_POST_ENABLED", "false").lower() == "true",
)
