# AI News Bot

A minimal Python bot that fetches the latest news headlines for configured stock tickers using a free Yahoo Finance RSS feed.

## Features
- Config-driven tickers, keyword filters, and settings (`config/settings.json`)
- Fetches top headlines per ticker (default 5)
- Keyword-based filtering (include/exclude) and cross-run de-duplication via `data/seen.json`
- Console output grouped by ticker with titles, links, and published time
- Optional Telegram alerts with per-ticker or combined delivery modes
- Basic logging and error handling

## Setup
1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies (none required, but keep this step for future additions):
   ```bash
   pip install -r requirements.txt
   ```
3. Configure tickers and filters in `config/settings.json`. A sample configuration is provided:
   ```json
   {
     "tickers": ["TSM", "HOOD", "CRCL", "NVDA", "QQQ", "XLK", "BTC-USD", "ETH-USD"],
     "headline_limit": 5,
     "news_source": "Yahoo Finance RSS",
     "include_keywords": ["earnings", "guidance", "downgrade", "upgrade", "SEC", "lawsuit", "acquisition", "M&A", "tariff", "China", "Taiwan", "AI", "semiconductor", "NVIDIA"],
     "exclude_keywords": ["paid partner", "sponsored"]
   }
   ```
4. Set up environment variables for Telegram (optional):
   - Copy `.env.example` to `.env` and fill in the values:
     ```bash
     cp .env.example .env
     ```
   - `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are required when using Telegram alerts. Leave them blank if you only want console output.

## Telegram setup
1. Create a bot with BotFather:
   - Open Telegram and start a chat with `@BotFather`.
   - Send `/newbot` and follow the prompts to name your bot and set a username.
   - BotFather will reply with an HTTP API token. Save this as `TELEGRAM_BOT_TOKEN` in your `.env` file.
2. Find your `chat_id`:
   - Start a chat with your new bot and send any message (e.g., "hi").
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser (replace `<YOUR_TOKEN>` with your bot token).
   - Look for `"chat":{"id":...}` in the response; that numeric value is your `TELEGRAM_CHAT_ID`.

## Run
Execute the bot with:
```bash
python -m src.main
```

To override the configuration file:
```bash
python -m src.main --config path/to/your_config.json
```

To override tickers from the command line (ignores those in the config for this run):
```bash
python -m src.main --tickers NVDA TSLA
```

Telegram options:
- `--telegram`: enable Telegram delivery (requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`).
- `--telegram-mode`: choose `per_ticker` (default; one message per ticker) or `combined` (all tickers in one message, split automatically if needed).
- `--dry-run`: print the messages that would be sent without calling the Telegram API.

Notes on filtering and de-duplication:
- Headlines must match at least one `include_keyword` (case-insensitive) unless the list is empty.
- Headlines containing any `exclude_keyword` are removed.
- Seen headlines are tracked in `data/seen.json` (normalized, case-insensitive, punctuation removed) to avoid repeats across runs.

## Notes
- The bot uses free Yahoo Finance RSS feeds; no API key is required.
- Network access is required to retrieve headlines (and to send Telegram messages when enabled).
