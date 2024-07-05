# macro-bot-telegram
Gib me macro stats

## Requirements
Create venv using your favourite tool + install requirements.
- My preferred tool is `pip install uv` then `uv pip sync`

Then create a `.env` file and add the following things:
```
API_KEY='YOUR_TELEGRAM_API_KEY'
TG_CHAT_ID='YOUR_TELEGRAM_CHAT_ID'
DB_URI=postgresql://jerome:jpgotyourback@localhost:4242/postgres
```

Ready to go!