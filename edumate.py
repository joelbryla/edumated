from googcal import CalendarTool
import pandas as pd
from tqdm import tqdm
import argparse
import datetime
from fetch import Fetcher

parser = argparse.ArgumentParser()
parser.add_argument(
    "--start_date",
    type=datetime.date.fromisoformat,
    default=datetime.datetime.now().date(),
    help="Start date in ISO format, YYYY-MM-DD (Defaults to today)",
)

parser.add_argument(
    "--days", default=1, type=int, help="Days including start date to fetch"
)
parser.add_argument("--weeks", type=int, help="Weeks including start date to fetch")

parser.add_argument(
    "--file",
    default="pass",
    type=open,
    help="File containg username, password and calender id",
)

args = parser.parse_args()

if args.weeks is not None:
    args.days = args.weeks * 7

with args.file as conf:
    username = conf.readline().strip()
    password = conf.readline().strip()
    calendar_id = conf.readline().strip()

cal = CalendarTool(calendar_id)
fetcher = Fetcher(username, password)

one_day_offset = datetime.timedelta(days=1)

args.start_date = args.start_date - one_day_offset
dates = pd.date_range(args.start_date, periods=args.days)


print(
    f"Fetching Events: {dates[0].date()+one_day_offset} to {dates[-1].date()+one_day_offset}"
)
edumate_day_data = fetcher.get_simple_dates(dates)

print("Adding to Google Calendar")
[cal.make_events(day) for day in tqdm(edumate_day_data)]
