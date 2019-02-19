from concurrent import futures
import datetime
from os import path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from rfc3339 import rfc3339
from tqdm import tqdm


class CalendarTool:

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, calendar_id, conf_folder):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.CAL_ID = calendar_id
        self.CRED_FILE = {
            "installed": {
                "client_id": "260443697659-7fqv4qks7t7536sacm81ujk7n4bjfssf.apps.googleusercontent.com",
                "project_id": "edumated-1547966773995",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "GgYorkYBYUqfMBcp81HbFYpB",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            }
        }

        self.pickle = path.join(conf_folder, "token.pickle")
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if path.exists(self.pickle):
            with open(self.pickle, "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(self.CRED_FILE, self.SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(self.pickle, "wb") as token:
                pickle.dump(creds, token)

        self.service = build("calendar", "v3", credentials=creds)

        self.cal_events = []
        page_token = None
        while True:
            events = (
                self.service.events()
                .list(calendarId=self.CAL_ID, pageToken=page_token)
                .execute()
            )
            self.cal_events += events["items"]
            page_token = events.get("nextPageToken")
            if not page_token:
                break

    def make_events(self, events_data):
        try:
            date = events_data[0]["end_time"]
        except:
            return
        self.del_day(date)
        for event in events_data:
            self.make_event(event)

    def del_day(self, date):
        for event in self.cal_events:
            time_dict = event["start"]
            if "dateTime" in time_dict.keys():
                event_date = datetime.datetime.strptime(
                    event["start"]["dateTime"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
                ).date()
            elif "data" in time_dict.keys():
                event_date = datetime.datetime.strptime(
                    event["start"]["date"].split("+")[0], "%Y-%m-%d"
                ).date()

            if event_date == date.date():
                self.service.events().delete(
                    calendarId=self.CAL_ID, eventId=event["id"]
                ).execute()

    def make_event(self, event_data):
        timezone = event_data["timezone"]

        event = {
            "summary": event_data["name"],
            "location": event_data["room"],
            "description": event_data["description"],
            "colorId": event_data["colour"],
            "start": {
                "dateTime": rfc3339(event_data["start_time"]),
                "timeZone": timezone,
            },
            "end": {"dateTime": rfc3339(event_data["end_time"]), "timeZone": timezone},
        }
        event = (
            self.service.events().insert(calendarId=self.CAL_ID, body=event).execute()
        )

    def make_all_events(self, dates):
        # with futures.ThreadPoolExecutor(max_workers=10) as executor:
        #     to_do = []
        #     for date in dates:
        #         future = executor.submit(
        #             self.make_events, date
        #         )
        #         to_do.append(future)

        #     for future in tqdm(
        #         futures.as_completed(to_do), unit="day", total=len(dates)
        #     ):
        #         pass
        for date in tqdm(dates):
            self.make_events(date)
