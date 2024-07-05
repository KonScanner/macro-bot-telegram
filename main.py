import logging
import time

from src.economic_calendar import EconomicTable
from src.telegram_bot import compute_massage, send_telegram_message

TIMEOUT_SLEEP = 30
INITIALIZE_SLEEP = 2
GENERAL_SLEEP = 5
logging.basicConfig(level=logging.DEBUG)


class Bot(object):
    def __init__(self):
        self.check_list = set()

    def compute(
        self,
        e: EconomicTable,
        flags: list[str] = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY"],
        actual_val: str = "",
    ):
        for _, i in enumerate(e.table):
            event: str = i.get("Event")
            importance: int = i.get("Importance")
            timestamp: str = i.get("Time")
            flag: str = i.get("Flag")
            previous: str = i.get("Previous")
            forecast: str = i.get("Forecast")
            actual: str = i.get("Actual")
            if flag in flags:
                hash_massage, text = compute_massage(
                    event,
                    importance,
                    timestamp,
                    flag,
                    previous,
                    forecast,
                    actual,
                )
                if hash_massage not in self.check_list:
                    if actual_val == "":
                        if actual == "":
                            continue
                        send_telegram_message(text=text)
                        time.sleep(INITIALIZE_SLEEP)
                self.check_list.add(hash_massage)
            else:
                continue

    def core(self, e: EconomicTable, **kwargs):
        while True:
            e.refresh()
            try:
                self.compute(e, **kwargs)
            except Exception:
                logging.exception(
                    f"{time.ctime()} - Error in sending message to telegram bot: {e}"
                )
                time.sleep(TIMEOUT_SLEEP)
            logging.info(
                f"{time.ctime()} - Sleeping for {GENERAL_SLEEP} seconds, Checklist length: {len(self.check_list)}"
            )
            time.sleep(GENERAL_SLEEP)


if __name__ == "__main__":
    url = "https://www.investing.com/economic-calendar/"
    e = EconomicTable()
    time.sleep(GENERAL_SLEEP)
    b = Bot()
    b.core(e, flags=["USD", "EUR", "GBP"], actual_val="")
