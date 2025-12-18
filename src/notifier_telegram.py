import json
import logging
from datetime import datetime
from typing import Dict, Iterable, List
from urllib import error, parse, request

from src.news_fetcher import NewsItem

logger = logging.getLogger(__name__)

TELEGRAM_TEXT_LIMIT = 4096
SAFE_TEXT_LIMIT = 3800


def _chunk_long_line(line: str, max_length: int) -> List[str]:
    return [line[i : i + max_length] for i in range(0, len(line), max_length)]


def split_message_into_chunks(text: str, max_length: int = SAFE_TEXT_LIMIT) -> List[str]:
    """Split text into chunks that respect Telegram's message length limits."""
    if max_length <= 0:
        raise ValueError("max_length must be positive")

    if len(text) <= max_length:
        return [text]

    chunks: List[str] = []
    current_lines: List[str] = []

    for line in text.splitlines():
        segments: Iterable[str]
        if len(line) > max_length:
            segments = _chunk_long_line(line, max_length)
        else:
            segments = [line]

        for segment in segments:
            candidate_lines = current_lines + [segment]
            candidate = "\n".join(candidate_lines)
            if candidate_lines and len(candidate) > max_length:
                chunks.append("\n".join(current_lines))
                current_lines = [segment]
            else:
                current_lines.append(segment)

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks


def _build_ticker_lines(ticker: str, headlines: List[NewsItem], headline_limit: int) -> List[str]:
    lines: List[str] = [ticker]
    if not headlines:
        lines.append("No new headlines.")
        return lines

    for item in headlines[:headline_limit]:
        lines.append(f"• {item.title}")
        lines.append(f"{item.published} | {item.link}")
    return lines


def _format_messages(
    ticker_headlines: Dict[str, List[NewsItem]],
    timestamp: datetime,
    mode: str,
    headline_limit: int,
) -> List[str]:
    if mode not in {"per_ticker", "combined"}:
        raise ValueError("mode must be 'per_ticker' or 'combined'")

    header = f"Stock News Bot — {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    if not ticker_headlines:
        return [header + "\nNo new headlines."]

    if mode == "combined":
        lines: List[str] = [header]
        for ticker, headlines in ticker_headlines.items():
            lines.append("")
            lines.extend(_build_ticker_lines(ticker, headlines, headline_limit))
        return split_message_into_chunks("\n".join(lines), SAFE_TEXT_LIMIT)

    messages: List[str] = []
    for ticker, headlines in ticker_headlines.items():
        lines = [header, ""]
        lines.extend(_build_ticker_lines(ticker, headlines, headline_limit))
        messages.extend(split_message_into_chunks("\n".join(lines), SAFE_TEXT_LIMIT))
    return messages


def _post_message(token: str, chat_id: str, message: str, timeout: int = 10) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    data = parse.urlencode(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            if response.status >= 400:
                body = response.read().decode("utf-8", errors="replace")
                logger.error("Telegram API responded with %s: %s", response.status, body)
            else:
                logger.debug("Telegram message sent, status %s", response.status)
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logger.error("Telegram API error (status %s): %s", exc.code, body)
    except error.URLError as exc:
        logger.error("Network error while sending Telegram message: %s", exc.reason)
    except TimeoutError:
        logger.error("Telegram request timed out after %s seconds", timeout)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error while sending Telegram message: %s", exc)


def send_telegram_messages(
    token: str,
    chat_id: str,
    ticker_headlines: Dict[str, List[NewsItem]],
    *,
    mode: str = "per_ticker",
    headline_limit: int = 5,
    dry_run: bool = False,
) -> None:
    """Format and send Telegram messages for the provided tickers."""
    timestamp = datetime.now()
    messages = _format_messages(ticker_headlines, timestamp, mode, headline_limit)

    if dry_run:
        for message in messages:
            logger.info("[DRY RUN] Would send Telegram message to %s:\n%s", chat_id, message)
        return

    for message in messages:
        if len(message) > TELEGRAM_TEXT_LIMIT:
            logger.warning(
                "Message exceeds Telegram limit (%s > %s); it may be truncated.",
                len(message),
                TELEGRAM_TEXT_LIMIT,
            )
        _post_message(token, chat_id, message)
