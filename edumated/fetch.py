import re
from os import path
from concurrent import futures
from datetime import datetime, timedelta

import bs4
import requests
import urllib3
from tqdm import tqdm

from .util import extract_teacher

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
    EDUMTE_RE = r"^\S+ (.*) (\d+|\w+|\d+\w+) \((\w\d{3}|.*).*\).*"
    EDUMATE_FMT = "%Y-%m-%d %H:%M:%S.000000"

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
                    self.colours[key.strip()] = value.strip().lower()

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
        formatted_data = []
        skip = []  # due to double periods
        for day in self.get_dates(dates):
            day_data = []
            for index, event in enumerate(day["events"]):
                if event in skip:
                    continue
                if event["eventType"] == "class":
                    match = re.match(self.EDUMTE_RE, event["activityName"])
                    subject = match.group(1) if match else event["activityName"]
                    room = match.group(3) if match else None
                    start = self.time_to_datetime(event["startDateTime"]["date"])
                    end = self.time_to_datetime(event["endDateTime"]["date"])
                    teacher = extract_teacher(event["links"])

                    if event["period"].isdigit() and int(event["period"]) % 2:
                        next_event = day["events"][index + 1]
                        match = re.match(self.EDUMTE_RE, next_event["activityName"])
                        next_subject = match.group(1) if match else event["activityName"]
                        if subject == next_subject:
                            skip.append(next_event)
                            next_room = match.group(3) if match else None
                            next_teacher = extract_teacher(event["links"])
                            end = self.time_to_datetime(next_event["endDateTime"]["date"])
                            if next_room != room:
                                room += f", {next_room}"
                            if next_teacher != teacher:
                                teacher += f", {next_teacher}"

                    # Edumate says extension classes start at 8:13
                    if event["period"] == "BS2":
                        start = start.replace(hour=7, minute=30)

                    event_data = {
                        "name": subject,
                        "colour": self.get_colour(subject),
                        "room": room,
                        "start_time": start,
                        "end_time": end,
                        "description": teacher,
                        "timezone": event["startDateTime"]["timezone"].title(),
                    }

                elif event["eventType"] == "event":
                    match = re.match(self.EDUMTE_RE, event["activityName"])
                    if match is None:
                        name = match.group(1) + " " + match.group(2) if match else event["activityName"]
                    event_data = {
                        "name": match.group(1) + " " + match.group(2),
                        "colour": self.get_colour(event["activityName"].split(" ")[1]),
                        "start_time": self.time_to_datetime(
                            event["startDateTime"]["date"]
                        ),
                        "description": None,
                        "end_time": self.time_to_datetime(event["endDateTime"]["date"]),
                        "timezone": event["startDateTime"]["timezone"].title(),
                        "room": None,
                        "colour": self.get_colour("event"),
                    }
                else:
                    event_data = {}

                day_data.append(event_data)

            formatted_data.append(day_data)

        return formatted_data

    def get_week(self, date):
        monday = date - timedelta(days=date.weekday())
        week = [monday + timedelta(days=day_int) for day_int in range(-1, 4)]
        week_data = self.get_simple_dates(week)
        return week_data

    def time_to_datetime(self, time):
        # "2019-02-01 08:42:00.000000"
        return datetime.strptime(time, self.EDUMATE_FMT)

    def __repr__(self):
        return f"<Fetcher username={self.credentials['username']} password=...>"
