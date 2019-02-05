import re
from os import path
from concurrent import futures
from datetime import datetime, timedelta

import bs4
import requests
import urllib3
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def param(data: dict):
    return "&".join([key + "=" + value for key, value in data.items()])


class Fetcher:

    URLS = {
        "sso-login": "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/sso-login/",
        "login": "https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php?",
        "accounts": "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/saml/acs",
        "day": "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/admin/get-day-calendar/{}/next",
    }
    MAX_WORKERS = 20

    colour_to_code = {
        "tomato": 11,
        "flamingo": 4,
        "tangerine": 6,
        "banana": 5,
        "sage": 2,
        "basil": 10,
        "peacock": 7,
        "blueberry": 9,
        "lavender": 1,
        "grape": 3,
        "graphite": 8,
    }

    colours = {}

    def __init__(self, username: str, password: str, conf_folder):
        self.colour_conf = path.join(conf_folder, "colour_config.txt")

        if path.isfile(self.colour_conf):
            self.colours = {}
            with open(self.colour_conf) as file:
                for line in file.readlines():
                    split = line.split(":")
                    if len(split) <= 1:
                        continue
                    key, value = split
                    self.colours[key.strip()] = value.strip()

                if "default" not in self.colours.keys():
                    self.colours["default"] = "graphite"
        else:
            with open(self.colour_conf, "w+") as file:
                for line in self.colours.items():
                    file.write(f"{line[0]}: {line[1]}\n")

        self.session = requests.Session()
        self.session.verify = False
        self.credentials = {"username": username, "password": password}
        self.login()
        if self.successful_login():
            print("Successful login")
        else:
            print("Login failed")
            quit()

    def login(self):
        sso_login = self.session.get(self.URLS["sso-login"])
        soup = bs4.BeautifulSoup(sso_login.history[1].content, "html.parser")
        auth = {"AuthState": soup.a.attrs["href"][soup.a.attrs["href"].find("=") + 1 :]}
        login = self.session.post(
            self.URLS["login"] + param({**auth, **self.credentials})
        )
        soup = bs4.BeautifulSoup(login.content, "html.parser")
        saml_response = {"SAMLResponse": soup.find_all("input")[1].attrs["value"]}
        self.session.post(self.URLS["accounts"], data=saml_response)

    def successful_login(self):
        test = self.session.get(self.URLS["day"].format("2019-02-01"))
        return test.status_code == 200 and test.json()

    def get_dates(self, dates: iter):
        data = []
        with futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            to_do = []
            for date in dates:
                date = date - timedelta(days=1)
                date_str = date.strftime("%Y-%m-%d")
                future = executor.submit(
                    self.session.get, self.URLS["day"].format(date_str)
                )
                to_do.append(future)

            for future in tqdm(futures.as_completed(to_do), total=len(dates)):
                data.append(future.result().json())

        return data

    def get_colour(self, name):
        return self.colour_to_code.get(
            self.colours.get(name, self.colours["default"]),
            self.colour_to_code[self.colours["default"]],
        )

    def get_simple_dates(self, dates):
        dates_data = self.get_dates(dates)

        formatted_data = []
        for day in dates_data:
            events = day["events"]

            day_data = []

            day_data += [
                {
                    "name": event["period"]
                    + ". "
                    + re.sub(
                        "^([1-10])\w+",
                        "",
                        "".join(event["activityName"].split("(")[:-1]).replace(")", ""),
                    ).strip(),
                    "colour": self.get_colour(event["activityName"].split(" ")[1]),
                    "room": event["activityName"].split(" (")[-1].rstrip(")"),
                    "start_time": self.time_to_datetime(event["startDateTime"]["date"]),
                    "end_time": self.time_to_datetime(event["endDateTime"]["date"]),
                    "description": event["links"][0]["href"]
                    .split("bcc=")[1]
                    .split("@")[0],
                    "timezone": event["startDateTime"]["timezone"].title(),
                }
                for event in events
                if event["eventType"] == "class"
            ]

            day_data += [
                {
                    "name": (event["activityName"]).lstrip("Event: ").strip(),
                    "colour": self.get_colour(event["activityName"].split(" ")[1]),
                    "start_time": self.time_to_datetime(event["startDateTime"]["date"]),
                    "description": "",
                    "end_time": self.time_to_datetime(event["endDateTime"]["date"]),
                    "timezone": event["startDateTime"]["timezone"].title(),
                    "room": "",
                    "colour": self.get_colour("event"),
                }
                for event in events
                if event["eventType"] == "event"
            ]
            formatted_data.append(day_data)

        return formatted_data

    def get_week(self, date):
        monday = date - timedelta(days=date.weekday())
        week = [monday + timedelta(days=day_int) for day_int in range(-1, 4)]
        week_data = self.get_simple_dates(week)
        return week_data

    def time_to_datetime(self, time):
        # "2019-02-01 08:42:00.000000"
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.000000")

    def __repr__(self):
        return f"<Fetcher username={self.credentials['username']} password=...>"
