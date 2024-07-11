import re
import time

import requests
from bs4 import BeautifulSoup


class EconomicTable:
    def __init__(self, url: str = "https://www.investing.com/economic-calendar/"):
        self.url = url
        self.table = self.refresh()

    def fetch_content(self) -> bytes:
        """
        Fetches the content of the webpage using a GET request with custom headers.

        Returns:
            bytes: The content of the webpage as bytes if the status code of the response is 200, otherwise an empty bytes object.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
        }

        response = requests.get(self.url, headers=headers)
        return response.content if response.status_code == 200 else bytes()

    def extract_time(self, element):
        """
        Extracts the time information from the given element.

        Parameters:
            element (BeautifulSoup Tag): The element from which to extract the time information.

        Returns:
            str: The time information extracted from the element.
        """
        return element.find("td", class_="first left time js-time").string

    def extract_value(self, id, element):
        """
        Extracts the actual, forecast, and previous values from the given element based on the provided id.

        Parameters:
            id (str): The unique identifier used to locate the specific values within the element.
            element (BeautifulSoup Tag): The element containing the actual, forecast, and previous values.

        Returns:
            tuple: A tuple containing the actual, forecast, and previous values extracted from the element.
        """
        actual = element.find("td", id=f"eventActual_{id}").text
        forecast = element.find("td", id=f"eventForecast_{id}").text
        previous = element.find("td", id=f"eventPrevious_{id}").text
        return actual, forecast, previous

    def extract_nubmer_star(self, element):
        """
        Extracts the number of stars representing the importance of an economic event from the given element.

        Parameters:
            element (BeautifulSoup Tag): The element from which to extract the star information.

        Returns:
            str: A string representing the importance of the economic event using stars.
        """
        imp = element.find("td", class_="left textNum sentiment noWrap").attrs[
            "data-img_key"
        ]
        pattern = re.compile("bull([0-3])")
        len_star = pattern.findall(imp)
        imp_list = ["*" for _ in range(int(len_star[0]))]
        return "".join(imp_list)

    def extract_flag(self, element):
        return element.find("td", class_="left flagCur noWrap").text.strip()

    def extract_event(self, element):
        return element.find("a", href=True).text.strip()

    def __replace_star_with_enum(self, star: str) -> int:
        """
        Replaces the star representation of the importance of an economic event with an integer value.

        Parameters:
            star (str): A string representing the importance of the economic event using stars.

        Returns:
            int: An integer value representing the importance of the economic event, where an empty string is converted to 0 and the length of the star string is returned otherwise.
        """
        return 0 if not star else len(star)

    def extract_table(self):  # sourcery skip: avoid-builtin-shadow
        """
        Extracts the relevant information from the HTML table of economic events.

        Returns:
            list: A list of dictionaries, where each dictionary represents a single economic event with the following keys:
                - "Time": The time of the economic event.
                - "Flag": The flag representing the country of the economic event.
                - "Importance": The importance of the economic event represented as an integer.
                - "Event": The description of the economic event.
                - "Actual": The actual value of the economic event.
                - "Forecast": The forecasted value of the economic event.
                - "Previous": The previous value of the economic event.
        """
        soup = BeautifulSoup(self.data, "html.parser")
        table = soup.find("table", id="economicCalendarData")
        results = []
        for element in table.find_all("tr", class_="js-event-item"):
            element_dict = element.attrs
            _id = element_dict["id"].split("_")[1]
            time_ = self.extract_time(element)
            flag = self.extract_flag(element)
            imp_star = self.extract_nubmer_star(element)
            event = self.extract_event(element)
            actual, forecast, previous = self.extract_value(id=_id, element=element)
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
        """
        Refreshes the data and table of economic events by fetching the content, extracting the table, and updating the class attributes accordingly.

        If the data is successfully fetched, the table is extracted and updated. If the data fetching fails, the method retries after a 20-second delay.

        Returns:
            list: A list of dictionaries representing the economic events with updated information after the refresh operation.
        """
        self.data = self.fetch_content()
        if self.data:
            self.table = self.extract_table()
        else:
            time.sleep(20)
            self.refresh()
        return self.table
