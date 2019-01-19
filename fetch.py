from datetime import datetime, timedelta
from pprint import pprint
import time

import bs4
from tqdm import tqdm
import requests


def param(data: dict):
    return "&".join([key + "=" + value for key, value in data.items()])


class Fetcher:

    URLS = {
        "base": "https://edumate.rosebank.nsw.edu.au",
        "index": "https://edumate.rosebank.nsw.edu.au/rosebank/index.php",
        "sso-login": "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/sso-login/?return_path=dashboard/my-edumate/",
        "login": "https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php?",
        "accounts": "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/saml/acs",
        "day": "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/admin/get-day-calendar/{}/next",
    }

    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.session.verify = False
        self.credentials = {"username": username, "password": password}
        self.login()

    def login(self):
        e = self.session.get(self.URLS["base"])
        n = self.session.get(self.URLS["index"])
        o = self.session.get(self.URLS["sso-login"])
        soup = bs4.BeautifulSoup(o.history[1].content, "lxml")
        auth = {"AuthState": soup.a.attrs["href"][soup.a.attrs["href"].find("=") + 1 :]}
        l = self.session.post(
            self.URLS["login"] + param(auth) + "&" + param(self.credentials)
        )
        soup = bs4.BeautifulSoup(l.content, "lxml")
        saml_response = {"SAMLResponse": soup.find_all("input")[1].attrs["value"]}
        ol = self.session.post(
            self.URLS["accounts"],
            data={
                **saml_response,
                "RelayState": "%7B%22return_path%22%3A%22dashboard%5C%2Fmy-edumate%5C%2F%22%7D",
            },
        )
        d = self.session.get(self.URLS["day"].format("2019-02-01"))
        if d.status_code == 200:
            print("Login Successful")

    def get_dates(self, dates):
        data = []
        for date in tqdm(dates):
            date_str = date.strftime("%Y-%m-%d")
            r = self.session.get(self.URLS["day"].format(date_str))
            # print(r)
            # print(r.text)
            data.append(r.json())

        return data

    def get_colour(self, name):
        class_colour = {
            "Home": 8,  # yellow
            "Physics": 2,
            "Mathematics": 9,  # dark blue
            "Pastoral": 8,  # yellow
            "Engineering": 5,
            "Studies": 10,  # religon
            "English": 6,
            "Chemistry": 3,
        }
        class_colour.get(name, 8)

    def get_simple_dates(self, dates):
        dates_data = self.get_dates(dates)

        formatted_data = []
        for day in dates_data:
            events = day["events"]

            formatted_data.append(
                [
                    {
                        "name": "".join(event["activityName"].split("(")[:-1])
                        .replace(")", "")
                        .strip(),
                        "colour": self.get_colour(event["activityName"].split(" ")[1]),
                        "room": event["activityName"].split(" (")[-1].rstrip(")"),
                        "period": event["period"],
                        "start_time": self.time_to_datetime(event["startDateTime"]["date"]),
                        "end_time": self.time_to_datetime(event["endDateTime"]["date"]),
                        "teacher": event["links"][0]["href"]
                        .split("bcc=")[1]
                        .split("@")[0],
                    }
                    for event in events
                    if event["eventType"] == "class"
                ]
            )

        return formatted_data

    def get_week(self, date):
        monday = date - timedelta(days=date.weekday())
        week = [monday + timedelta(days=day_int) for day_int in range(-1, 4)]
        week_data = self.get_simple_dates(week)
        return week_data

    def time_to_datetime(self, time):
        # "2019-02-01 08:42:00.000000"
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.000000")


if __name__ == "__main__":
    with open("pass") as file:
        username = file.readline().strip()
        password = file.readline().strip()
    a = Fetcher(username, password)
    # pprint(a.get_week(datetime(2019,2,4)))
