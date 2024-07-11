import logging
import time

from src.economic_calendar import EconomicTable
from src.store.macro_events import MacroEventsStore
from src.telegram_bot import compute_massage, send_telegram_message
from src.utils.db import get_session_factory, get_unique_hashes

TIMEOUT_SLEEP = 30
INITIALIZE_SLEEP = 2
GENERAL_SLEEP = 3
logging.basicConfig(level=logging.DEBUG)


class Bot(object):
    def __init__(self):
        self.session_factory = get_session_factory()
        self.session = self.session_factory()
        self.check_list = get_unique_hashes(self.session)

    def compute(self, e: EconomicTable, flags: list[str], actual_val: str = ""):
        if not flags:
            flags = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY"]
        for i in e.table:
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
                hash_massage = f"0x{hash_massage}"
                if hash_massage not in self.check_list and not actual_val:
                    if not actual:
                        continue
                    payload = {
                        "hash": hash_massage,
                        "event": event,
                        "importance": importance,
                        "timestamp": timestamp,
                        "flag": flag,
                        "previous": previous,
                        "forecast": forecast,
                        "actual": actual,
                    }
                    send_telegram_message(text=text)
                    MacroEventsStore().write_all(
                        self.session,
                        json_data_list=[payload],
                        merge=True,
                        commit=True,
                    )
                    time.sleep(INITIALIZE_SLEEP)
                self.check_list.add(hash_massage)

    def core(self, e: EconomicTable, **kwargs):
        should_terminate = False
        while not should_terminate:
            try:
                self.compute(e, **kwargs)
            except Exception:
                logging.exception(
                    f"{time.ctime()} - Error in sending message to telegram bot: {e}"
                )
                should_terminate = True
            logging.info(
                f"{time.ctime()} - Sleeping for {GENERAL_SLEEP} seconds, Checklist length: {len(self.check_list)}"
            )
            time.sleep(GENERAL_SLEEP)
            e.refresh()


if __name__ == "__main__":
    e = EconomicTable()
    b = Bot()
    b.core(e, flags=["USD", "EUR", "GBP"], actual_val="")
