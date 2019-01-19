import fetch
from googcal import CalendarTool
from datetime import datetime
from pprint import pprint
import pandas as pd

cal = CalendarTool()
dates = pd.date_range(pd.datetime(2019, 1, 31), periods=200)
week_data = fetch.get_simple_dates(dates)

[cal.make_events(day) for day in week_data]
