import argparse
import logging
import sys
from pathlib import Path

from src.config import load_settings
from src.news_fetcher import fetch_headlines


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def display_headlines(ticker: str, headlines) -> None:
    print(f"\n=== {ticker} ===")
    if not headlines:
        print("No headlines available.")
        return

    for idx, item in enumerate(headlines, start=1):
        print(f"{idx}. {item.title}")
        print(f"   Link: {item.link}")
        print(f"   Published: {item.published}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch latest stock news headlines.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config") / "settings.json",
        help="Path to the JSON configuration file.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    logger = logging.getLogger(__name__)

    try:
        settings = load_settings(args.config)
    except Exception as exc:  # noqa: BLE001
        logger.error("Could not load configuration: %s", exc)
        return 1

    logger.info("Using news source: %s", settings.news_source)

    for ticker in settings.tickers:
        try:
            headlines = fetch_headlines(ticker, limit=settings.headline_limit)
            display_headlines(ticker, headlines)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to fetch headlines for %s: %s", ticker, exc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
