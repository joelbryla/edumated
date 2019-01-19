from googcal import CalendarTool
import pandas as pd
from tqdm import tqdm

from fetch import Fetcher

with open("pass") as conf:
    username = conf.readline().strip()
    password = conf.readline().strip()
    calendar_id = conf.readline().strip()

cal = CalendarTool(calendar_id)
fetcher = Fetcher(username, password)

print("Fetching Events")
dates = pd.date_range(pd.datetime(2019, 1, 31), periods=200)
week_data = fetcher.get_simple_dates(dates)

print("Insert to calendar")
[cal.make_events(day) for day in tqdm(week_data)]
