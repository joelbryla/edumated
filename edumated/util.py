import argparse
import datetime
import os
from shutil import rmtree

TEACHERS = {}


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf-folder",
        default=os.path.join(os.path.expanduser("~"), ".edumated"),
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

    parser.add_argument(
        "--colour-help",
        action="store_true",
        help="Returns help for colour config and quits",
    )

    parser.add_argument("--reset", action="store_true", help="Deletes config files")

    args = parser.parse_args()

    colour_conf_file = os.path.join(args.conf_folder, "colour_config.txt")
    teachers = os.path.join(args.conf_folder, "teachers.txt")

    if os.path.isfile(teachers):
        for line in open(teachers).readlines():
            split = line.strip().split(":")
            if len(split) <= 1:
                continue
            TEACHERS[split[0]] = split[1]

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

    if not os.path.isdir(args.conf_folder):
        os.mkdir(args.conf_folder)

    if not os.path.isfile(colour_conf_file):
        with open(colour_conf_file, "w+") as file:
            for line in default_colours.items():
                file.write(f"{line[0]}: {line[1]}\n")

    if args.colour_help:
        print(
            f"""To add custom colours edit colour_config.txt in config folder ({args.conf_folder})
run edumated to generate folder and file

    Format is:
        SUBJECT: COLOUR

    SUBJECT: the first word of a subject (eg. English Advanced : English, Food Technology : Food, ect.)
            also includes "default" and "event" options
    
    COLOUR: google calendar colour names

            Google Colour options include:
                tomato, flamingo, tangerine, banana, sage, basil, peacock, blueberry, lavender, grape, graphite"""
        )
        if os.name == "nt":
            os.startfile(colour_conf_file)
        quit()

    return args


def daterange(start_date, end_date):
    dates = []
    for n in range(int((end_date - start_date).days) + 1):
        dates.append(start_date + datetime.timedelta(n))
    return dates


def extract_teacher(links):
    if "href" in links[0].keys():
        *_, email = links[0]["href"].split("=")
        abreviated, *_ = email.split("@")
        return TEACHERS.get(abreviated, abreviated)
    else:
        return None
