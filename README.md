# AI News Bot

A minimal Python bot that fetches the latest news headlines for configured stock tickers using a free Yahoo Finance RSS feed.

## Features
- Config-driven tickers, keyword filters, and settings (`config/settings.json`)
- Fetches top headlines per ticker (default 5)
- Keyword-based filtering (include/exclude) and cross-run de-duplication via `data/seen.json`
- Console output grouped by ticker with titles, links, and published time
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
4. (Optional) Copy `.env.example` to `.env` for future API keys or secrets.

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

Notes on filtering and de-duplication:
- Headlines must match at least one `include_keyword` (case-insensitive) unless the list is empty.
- Headlines containing any `exclude_keyword` are removed.
- Seen headlines are tracked in `data/seen.json` (normalized, case-insensitive, punctuation removed) to avoid repeats across runs.

## Notes
- The bot uses free Yahoo Finance RSS feeds; no API key is required.
- Network access is required to retrieve headlines.
