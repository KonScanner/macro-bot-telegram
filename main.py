import logging
import time

from src.economic_calendar import EconomicTable
from src.telegram_bot import send_massage

TIMEOUT_SLEEP = 30
INITIALIZE_SLEEP = 2
GENERAL_SLEEP = 5
logging.basicConfig(level=logging.DEBUG)


def compute(e: EconomicTable, check_list: list, condition: bool = False):
    for _, i in enumerate(e.table):
        event = i.get("Event")
        importance = i.get("Importance")
        timestamp = i.get("Time")
        flag = i.get("Flag")
        previous = i.get("Previous")
        forecast = i.get("Forecast")
        actual = i.get("Actual")
        if condition:
            if actual != "" and actual not in check_list:
                hash_massage = send_massage(
                    event,
                    importance,
                    timestamp,
                    flag,
                    previous,
                    forecast,
                    actual,
                )
                check_list.append(hash_massage)
        else:
            hash_massage = send_massage(
                event,
                importance,
                timestamp,
                flag,
                previous,
                forecast,
                actual,
            )
            check_list.append(hash_massage)
            time.sleep(INITIALIZE_SLEEP)
    return check_list


def main(e: EconomicTable):
    check_list = []
    while True:
        e.refresh()
        if check_list == []:
            try:
                check_list = compute(e, check_list)
            except Exception:
                logging.exception(
                    f"{time.ctime()} - Error in sending message to telegram bot: {e}"
                )
                time.sleep(TIMEOUT_SLEEP)
        else:
            try:
                compute(e, check_list, condition=True)
            except Exception:
                logging.exception(
                    f"{time.ctime()} - Error in sending message to telegram bot: {e}"
                )
                time.sleep(TIMEOUT_SLEEP)
        time.sleep(GENERAL_SLEEP)


if __name__ == "__main__":
    url = "https://www.investing.com/economic-calendar/"
    e = EconomicTable()
    time.sleep(GENERAL_SLEEP)
    main(e)
