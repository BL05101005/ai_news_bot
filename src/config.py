import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BotSettings:
    tickers: List[str]
    headline_limit: int = 5
    news_source: str = "Yahoo Finance RSS"


def load_settings(config_path: Optional[Path] = None) -> BotSettings:
    """Load bot settings from a JSON configuration file."""
    path = config_path or Path("config") / "settings.json"
    logger.debug("Loading configuration from %s", path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {path}")

    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    tickers = config.get("tickers", [])
    if not tickers:
        raise ValueError("No tickers provided in configuration.")

    headline_limit = int(config.get("headline_limit", 5))
    news_source = config.get("news_source", "Yahoo Finance RSS")

    logger.debug(
        "Configuration loaded: %s tickers, headline_limit=%s, news_source=%s",
        len(tickers),
        headline_limit,
        news_source,
    )
    return BotSettings(tickers=tickers, headline_limit=headline_limit, news_source=news_source)
