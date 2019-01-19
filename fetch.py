from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import json
from pprint import pprint
from tqdm import tqdm
import requests


# class Fetcher:

#     LOGIN_URL = "https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php?"

#     def __init__(self, username, password):
#         self.session = requests.Session()

#         self.login(username, password)

#     def login(self, username, password):
#         data = {"username": username, "password": password}
#         self.session.post(self.LOGIN_URL, data=data)


def get_dates(dates):
    driver = webdriver.Safari()
    wait = WebDriverWait(driver, 30)

    driver.get(
        "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/admin/get-day-calendar/2019-01-01/next?_dc=1547718083391"
    )

    wait.until(EC.title_contains("Enter your username and password"))
    time.sleep(2)
    password_input = driver.find_element_by_name("password")
    # password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(8)

    data = []
    for date in tqdm(dates):
        date_str = date.strftime("%Y-%m-%d")

        url = f"https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/admin/get-day-calendar/{date_str}/next?_dc=1547718083391"

        driver.get(url)

        time.sleep(2)
        day_data = driver.find_element_by_xpath("/html/body/pre").text
        data.append(json.loads(day_data))

    driver.quit()
    return data


def get_colour(name):
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

    try:
        return class_colour[name]
    except:
        return 8


def get_simple_dates(dates):
    dates_data = get_dates(dates)

    formatted_data = []
    for day in dates_data:
        events = day["events"]

        formatted_data.append(
            [
                {
                    "name": "".join(event["activityName"].split("(")[:-1])
                    .replace(")", "")
                    .strip(),
                    "colour": get_colour(event["activityName"].split(" ")[1]),
                    "room": event["activityName"].split(" (")[-1].rstrip(")"),
                    "period": event["period"],
                    "start_time": time_to_datetime(event["startDateTime"]["date"]),
                    "end_time": time_to_datetime(event["endDateTime"]["date"]),
                    "teacher": event["links"][0]["href"].split("bcc=")[1].split("@")[0],
                }
                for event in events
                if event["eventType"] == "class"
            ]
        )

    return formatted_data


def get_week(date):
    monday = date - timedelta(days=date.weekday())
    week = [monday + timedelta(days=day_int) for day_int in range(-1, 4)]
    week_data = get_simple_dates(week)
    return week_data


def time_to_datetime(time):
    # "2019-02-01 08:42:00.000000"
    return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.000000")


if __name__ == "__main__":
    # with open("pass") as file:
    #     username = file.readline().strip()
    #     password = file.readline().strip()
    # Fetcher(username, password)

    pprint(get_week(datetime(2019, 2, 10)))
