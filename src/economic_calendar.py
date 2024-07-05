import re
import time

import requests
from bs4 import BeautifulSoup


class EconomicTable:
    def __init__(self, url: str = "https://www.investing.com/economic-calendar/"):
        self.url = url
        self.table = self.refresh()

    def fetch_content(self) -> bytes:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
        }

        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return bytes()

    def extract_time(self, element):
        time_ = element.find("td", class_="first left time js-time").string
        return time_

    def extract_value(self, id, element):
        """find the value of each rows of Actual Forecast and Previous"""
        actual = element.find("td", id=f"eventActual_{id}").text
        forecast = element.find("td", id=f"eventForecast_{id}").text
        previous = element.find("td", id=f"eventPrevious_{id}").text
        return actual, forecast, previous

    def extract_nubmer_star(self, element):
        imp = element.find("td", class_="left textNum sentiment noWrap").attrs[
            "data-img_key"
        ]
        imp_list = []
        pattern = re.compile("bull([0-3])")
        len_star = pattern.findall(imp)
        for _ in range(int(len_star[0])):
            imp_list.append("*")
        imp_star = "".join(imp_list)
        return imp_star

    def extract_flag(self, element):
        """find the flag of each id"""
        return element.find("td", class_="left flagCur noWrap").text.strip()

    def extract_event(self, element):
        """the name of event find with this function"""
        return element.find("a", href=True).text.strip()

    def __replace_star_with_enum(self, star: str) -> int:
        if star == "":
            return 0
        return len(star)

    def extract_table(self):
        soup = BeautifulSoup(self.data, "html.parser")
        table = soup.find("table", id="economicCalendarData")
        results = []
        for element in table.find_all("tr", class_="js-event-item"):
            element_dict = element.attrs
            id = element_dict["id"].split("_")[1]
            time_ = self.extract_time(element)
            flag = self.extract_flag(element)
            imp_star = self.extract_nubmer_star(element)
            event = self.extract_event(element)
            actual, forecast, previous = self.extract_value(id=id, element=element)
            results.append(
                {
                    "Time": time_,
                    "Flag": flag,
                    "Importance": self.__replace_star_with_enum(imp_star),
                    "Event": event,
                    "Actual": str(actual).replace("\xa0", ""),
                    "Forecast": str(forecast).replace("\xa0", ""),
                    "Previous": str(previous).replace("\xa0", ""),
                }
            )
        return results

    def refresh(self):
        self.data = self.fetch_content()
        if self.data:
            self.table = self.extract_table()
        else:
            time.sleep(20)
            self.refresh()
        return self.table
