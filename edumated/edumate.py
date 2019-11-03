#!/usr/bin/env python3
from getpass import getpass
from os import path, mkdir

from .fetch import Fetcher
from .googcal import CalendarTool
from .util import daterange, parseargs


def main():
    args = parseargs()

    conf_file = path.join(args.conf_folder, "conf")

    if not path.isdir(args.conf_folder):
        mkdir(args.conf_folder)

    if not path.isfile(conf_file):
        username = input("Username: ")
        password = getpass(prompt="Password: ").replace("%", "%25")
        calendar_id = input("Google Calendar ID: ")
        with open(conf_file, "w") as f:
            f.write("\n".join([username, password, calendar_id]))
    else:
        with open(conf_file) as f:
            username, password, calendar_id = map(lambda l: l.strip(), f.readlines())

    calendar = CalendarTool(calendar_id, args.conf_folder)
    fetcher = Fetcher(username, password, args.conf_folder)
    dates = daterange(args.start_date, args.end_date)

    print(f"Fetching Events: {dates[0]} to {dates[-1]}")
    classes = fetcher.get_simple_dates(dates)

    print("Adding to Google Calendar")
    calendar.make_all_events(classes)
