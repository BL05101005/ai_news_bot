# AI News Bot

A minimal Python bot that fetches the latest news headlines for configured stock tickers using a free Yahoo Finance RSS feed.

## Features
- Config-driven tickers and settings (`config/settings.json`)
- Fetches top headlines per ticker (default 5)
- Console output with titles, links, and published time
- Basic logging and error handling

## Setup
1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```
2. Install dependencies (none required, but keep this step for future additions):
   ```bash
   pip install -r requirements.txt
   ```
3. Configure tickers in `config/settings.json`. A sample configuration is provided:
   ```json
   {
     "tickers": ["NVDA", "AAPL", "TSLA", "TSM", "MU"],
     "headline_limit": 5,
     "news_source": "Yahoo Finance RSS"
   }
   ```
4. (Optional) Copy `.env.example` to `.env` for future API keys or secrets.

## Run
Execute the bot with:
```bash
python -m src.main
```

To use a different configuration file:
```bash
python -m src.main --config path/to/your_config.json
```

## Notes
- The bot uses free Yahoo Finance RSS feeds; no API key is required.
- Network access is required to retrieve headlines.
