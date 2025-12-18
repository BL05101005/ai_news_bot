import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import List
from urllib import request

logger = logging.getLogger(__name__)

RSS_URL_TEMPLATE = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"


@dataclass
class NewsItem:
    title: str
    link: str
    published: str


def _parse_published(published_raw: str) -> str:
    """Convert raw published string to ISO format when possible."""
    if not published_raw:
        return "Unknown time"

    try:
        dt = parsedate_to_datetime(published_raw)
        if not dt:
            raise ValueError("parsedate_to_datetime returned None")
        return dt.isoformat()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to parse published date '%s': %s", published_raw, exc)
        return published_raw


def _fetch_feed_xml(url: str) -> bytes:
    req = request.Request(url, headers={"User-Agent": "ai-news-bot/1.0"})
    with request.urlopen(req, timeout=10) as response:
        if response.status >= 400:
            raise ConnectionError(f"HTTP {response.status}")
        return response.read()


def fetch_headlines(ticker: str, limit: int = 5) -> List[NewsItem]:
    """Fetch the latest headlines for the given ticker from Yahoo Finance RSS."""
    url = RSS_URL_TEMPLATE.format(ticker=ticker)
    logger.info("Fetching news for %s from %s", ticker, url)

    try:
        xml_bytes = _fetch_feed_xml(url)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to retrieve feed for %s: %s", ticker, exc)
        return []

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        logger.error("Could not parse feed for %s: %s", ticker, exc)
        return []

    news_items: List[NewsItem] = []
    channel = root.find("channel")
    if channel is None:
        logger.warning("No channel found in feed for %s", ticker)
        return news_items

    for item in channel.findall("item")[:limit]:
        title_elem = item.find("title")
        link_elem = item.find("link")
        pub_date_elem = item.find("pubDate")

        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No title"
        link = link_elem.text.strip() if link_elem is not None and link_elem.text else "No link available"
        published_raw = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""
        published = _parse_published(published_raw)

        news_items.append(NewsItem(title=title, link=link, published=published))

    logger.debug("Fetched %s items for %s", len(news_items), ticker)
    return news_items
