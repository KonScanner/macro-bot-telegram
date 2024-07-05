import hashlib
import logging
import os
import re
import time
from datetime import datetime
from typing import Tuple

import requests
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(text):
    """
    Sends a message to a Telegram chat using the Telegram API.

    Parameters:
    - text: The message text to send.
    - chat_id: The ID of the chat to send the message to.
    - api_key: The API key of your Telegram bot.
    """
    tg_chat_id = os.getenv("TG_CHAT_ID")
    api_key = os.getenv("API_KEY")
    if tg_chat_id is None or api_key is None:
        logging.warning("Please set the environment variables TG_CHAT_ID and TG_TOKEN")
        return
    base_url = "https://api.telegram.org"
    url = f"{base_url}/bot{api_key}/sendMessage"
    params = {"chat_id": tg_chat_id, "text": text}
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


def surprise(actual, forecast) -> Tuple[bool, float]:
    def clean_string_to_float(value: str) -> str:
        return re.sub(r"[^\d.]+", "", value)

    is_surprise = False
    actual = clean_string_to_float(actual)
    forecast = clean_string_to_float(forecast)
    if actual == "" or forecast == "":
        return is_surprise, 0
    diff = round(float(actual) - float(forecast), 3)
    is_surprise = True if diff != 0 else False
    return is_surprise, diff


def increase_from_previous(actual, previous) -> Tuple[bool, float]:
    def clean_string_to_float(value: str) -> str:
        return re.sub(r"[^\d.]+", "", value)

    is_surprise = False
    actual = clean_string_to_float(actual)
    previous = clean_string_to_float(previous)
    if actual == "" or previous == "":
        return is_surprise, 0
    diff = round(float(actual) - float(previous), 3)
    is_surprise = True if diff != 0 else False
    return is_surprise, diff


def build_message(event, importance, timestamp, flag, previous, forecast, actual):
    date_of_event = datetime.now().strftime("%Y-%m-%d") + " " + timestamp
    core = f"""
📅 {event}
❗ {importance}
💱 {flag}
⌚ {date_of_event}"""
    secondary = f"""

✅ Actual ----> {actual}
✅ Forecast ----> {forecast}
✅ Previous ----> {previous}
    """
    if not actual and not previous and not forecast:
        return core
    else:
        surprise_, diff = surprise(actual, forecast)
        surprise_previous, diff_previous = increase_from_previous(actual, previous)
        if surprise_ and surprise_previous:
            return (
                core
                + secondary
                + f"\n🎉 Surprise ----> {diff}"
                + f"\n🎉 Surprise from previous ----> {diff_previous}"
            )
        elif surprise_:
            return core + secondary + f"\n🎉 Surprise ----> {diff}"
        elif surprise_previous:
            return (
                core + secondary + f"\n🎉 Surprise from previous ----> {diff_previous}"
            )
        else:
            return core + secondary


def compute_massage(
    event, importance, timestamp, flag, previous, forecast, actual
) -> Tuple[str, str]:
    parameters = {
        "text": build_message(
            event, importance, timestamp, flag, previous, forecast, actual
        ),
    }
    hash_massage = hashlib.sha256(parameters["text"].encode("utf-8")).hexdigest()
    return hash_massage, parameters["text"]
