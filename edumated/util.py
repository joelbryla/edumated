import argparse
import datetime
from os import path, mkdir
from shutil import rmtree


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf-folder",
        default=path.join(path.expanduser("~"), ".edumated"),
        help="Config folder containg calender id, username, etc. (Default: ~/.edumated/",
    )
    parser.add_argument(
        "--start-date",
        default=datetime.datetime.now().date(),
        type=datetime.date.fromisoformat,
        help="Start date in ISO format, YYYY-MM-DD (Default: today)",
    )
    parser.add_argument(
        "--end-date",
        type=datetime.date.fromisoformat,
        help="End date in ISO format, YYYY-MM-DD",
    )
    parser.add_argument("--weeks", type=int, help="Weeks including start date to fetch")
    parser.add_argument(
        "--days",
        default=1,
        type=int,
        help="Days including start date to fetch (Default: 1)",
    )
    parser.add_argument("--reset", action="store_true", help="Deletes config files")

    args = parser.parse_args()

    if not args.end_date:
        args.end_date = (
            args.start_date
            + datetime.timedelta(days=args.days)
            - datetime.timedelta(days=1)
        )

        if args.weeks:
            args.end_date = (
                args.start_date
                + datetime.timedelta(weeks=args.weeks)
                - datetime.timedelta(days=1)
            )

    if args.reset:
        rmtree(args.conf_folder)

    if not path.isdir(args.conf_folder):
        mkdir(args.conf_folder)

    return args


def daterange(start_date, end_date):
    dates = []
    for n in range(int((end_date - start_date).days) + 1):
        dates.append(start_date + datetime.timedelta(n))
    return dates
