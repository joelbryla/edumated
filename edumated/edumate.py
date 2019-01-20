#!/usr/bin/env python3
import argparse
import datetime
import getpass
from os import path, mkdir
import pandas as pd

from .fetch import Fetcher
from .googcal import CalendarTool


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_date",
        type=datetime.date.fromisoformat,
        default=datetime.datetime.now().date(),
        help="Start date in ISO format, YYYY-MM-DD (Defaults to today)",
    )
    parser.add_argument(
        "--end_date",
        type=datetime.date.fromisoformat,
        default=None,
        help="End date in ISO format, YYYY-MM-DD",
    )

    parser.add_argument(
        "--days", default=1, type=int, help="Days including start date to fetch"
    )
    parser.add_argument("--weeks", type=int, help="Weeks including start date to fetch")

    parser.add_argument(
        "--conf_folder",
        default=path.join(path.expanduser("~"), "/.edumated/"),
        type=str,
        help="Config file containg calender id (default is ~/.edumated/",
    )

    args = parser.parse_args()

    if args.weeks is not None:
        args.days = args.weeks * 7

    one_day_offset = datetime.timedelta(days=1)

    if args.end_date is not None:
        args.days = (args.end_date - args.start_date + one_day_offset).days

    if not path.isdir(args.conf_folder):
        mkdir(args.conf_folder)

    pass_file = args.conf_folder + "pass"
    cal_file = args.conf_folder + "cal"

    if not path.isfile(pass_file):
        username = input("Username: ")
        password = getpass.getpass(prompt="Password: ")
        with open(pass_file, "w+") as file:
            file.write(username + "\n")
            file.write(password)

    with open(pass_file) as pass_f:
        username = pass_f.readline().strip()
        password = pass_f.readline().strip()

    if not path.isfile(cal_file):
        cal_id = input("Google Calendar ID: ")
        with open(cal_file, "w+") as file:
            file.write(cal_id)

    with open(cal_file) as conf:
        calendar_id = conf.readline().strip()

    cal = CalendarTool(calendar_id, args.conf_folder)
    fetcher = Fetcher(username, password)

    args.start_date = args.start_date - one_day_offset
    dates = pd.date_range(args.start_date, periods=args.days)

    print(
        f"Fetching Events: {dates[0].date()+one_day_offset} to {dates[-1].date()+one_day_offset}"
    )
    edumate_day_data = fetcher.get_simple_dates(dates)

    print("Adding to Google Calendar")
    cal.make_all_events(edumate_day_data)
