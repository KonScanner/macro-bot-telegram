import hashlib
import logging
import os
import time
from datetime import datetime
from typing import Union

import requests
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(text, chat_id, api_key):
    """
    Sends a message to a Telegram chat using the Telegram API.

    Parameters:
    - text: The message text to send.
    - chat_id: The ID of the chat to send the message to.
    - api_key: The API key of your Telegram bot.
    """
    base_url = "https://api.telegram.org"
    url = f"{base_url}/bot{api_key}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        if response.status_code == 429:
            res = response.json()
            _retry = res["parameters"].get("retry_after")
            if _retry:
                time.sleep(_retry + 0.05)
        else:
            raise KeyboardInterrupt(
                f"Failed to send message: {response.content}, {response.status_code}"
            )
    else:
        print("Message sent successfully.")


def build_message(event, importance, timestamp, flag, previous, forecast, actual):
    date_of_event = datetime.now().strftime("%Y-%m-%d") + " " + timestamp
    return f"""
📅 {event}
❗ {importance}
💱 {flag}
⌚ {date_of_event}

✅ Actual ----> {actual}
✅ Forecast ----> {forecast}
✅ Previous ----> {previous}
"""


def send_massage(
    event, importance, timestamp, flag, previous, forecast, actual
) -> Union[str, None]:
    tg_chat_id = os.getenv("TG_CHAT_ID")
    api_key = os.getenv("API_KEY")
    if tg_chat_id is None or api_key is None:
        logging.warning("Please set the environment variables TG_CHAT_ID and TG_TOKEN")
        return
    parameters = {
        "chat_id": f"@'{tg_chat_id}'",
        "text": build_message(
            event, importance, timestamp, flag, previous, forecast, actual
        ),
    }
    hash_massage = hashlib.sha256(parameters["text"].encode("utf-8")).hexdigest()
    try:
        send_telegram_message(
            text=parameters["text"], chat_id=tg_chat_id, api_key=api_key
        )
        return hash_massage
    except Exception as e:
        logging.exception(f"Error in sending message to telegram bot: {e}")
        return None
