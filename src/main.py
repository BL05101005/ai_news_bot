import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Iterable, List, Set, Tuple

from src.config import BotSettings, load_settings
from src.news_fetcher import NewsItem, fetch_headlines


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def display_headlines(ticker: str, headlines: Iterable[NewsItem]) -> None:
    print(f"\n=== {ticker} ===")
    if not headlines:
        print("No headlines available.")
        return

    for item in headlines:
        print(f"- {item.title}")
        print(f"  Published: {item.published}")
        print(f"  Link: {item.link}")


def normalize_title(title: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def keyword_matches(title: str, include_keywords: List[str], exclude_keywords: List[str]) -> bool:
    lower_title = title.lower()
    if any(keyword.lower() in lower_title for keyword in exclude_keywords):
        return False
    if include_keywords:
        return any(keyword.lower() in lower_title for keyword in include_keywords)
    return True


def filter_headlines_by_keywords(
    headlines: List[NewsItem], include_keywords: List[str], exclude_keywords: List[str]
) -> Tuple[List[NewsItem], int]:
    filtered: List[NewsItem] = []
    filtered_out = 0
    for item in headlines:
        if keyword_matches(item.title, include_keywords, exclude_keywords):
            filtered.append(item)
        else:
            filtered_out += 1
    return filtered, filtered_out


def remove_seen_headlines(headlines: List[NewsItem], seen_titles: Set[str]) -> Tuple[List[NewsItem], int]:
    fresh_items: List[NewsItem] = []
    filtered_out = 0
    for item in headlines:
        normalized = normalize_title(item.title)
        if normalized in seen_titles:
            filtered_out += 1
            continue
        seen_titles.add(normalized)
        fresh_items.append(item)
    return fresh_items, filtered_out


def load_seen_titles(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return {str(item) for item in data}
        return set()
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Could not read seen titles file: %s", exc)
        return set()


def save_seen_titles(path: Path, seen_titles: Set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(sorted(seen_titles), file, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch latest stock news headlines.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config") / "settings.json",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Override tickers defined in the configuration file.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    logger = logging.getLogger(__name__)

    try:
        settings: BotSettings = load_settings(args.config)
    except Exception as exc:  # noqa: BLE001
        logger.error("Could not load configuration: %s", exc)
        return 1

    if args.tickers:
        settings.tickers = args.tickers

    logger.info("Using news source: %s", settings.news_source)

    seen_file = Path("data") / "seen.json"
    seen_titles = load_seen_titles(seen_file)
    total_new_items = 0
    total_filtered_out = 0

    for ticker in settings.tickers:
        try:
            headlines = fetch_headlines(ticker, limit=settings.headline_limit)
            filtered_headlines, keyword_filtered = filter_headlines_by_keywords(
                headlines, settings.include_keywords, settings.exclude_keywords
            )
            deduped_headlines, duplicate_filtered = remove_seen_headlines(filtered_headlines, seen_titles)

            total_filtered_out += keyword_filtered + duplicate_filtered
            total_new_items += len(deduped_headlines)

            display_headlines(ticker, deduped_headlines)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to fetch headlines for %s: %s", ticker, exc)

    save_seen_titles(seen_file, seen_titles)

    print("\nTotal new items:", total_new_items)
    print("Total filtered out:", total_filtered_out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
