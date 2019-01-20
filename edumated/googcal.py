from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from rfc3339 import rfc3339


class CalendarTool:

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    CRED_FILE = "credentials.json"

    def __init__(self, calendar_id):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.CAL_ID = calendar_id
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CRED_FILE, self.SCOPES
                )
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("calendar", "v3", credentials=creds)

        self.cal_events = (
            self.service.events()
            .list(calendarId=self.CAL_ID, pageToken=None)
            .execute()["items"]
        )

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
            event_date = datetime.strptime(
                event["start"]["dateTime"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
            ).date()

            if event_date == date.date():
                self.service.events().delete(
                    calendarId=self.CAL_ID, eventId=event["id"]
                ).execute()

    def get_cals(self):
        return self.service.calendarList().list(pageToken=None).execute()

    def make_event(self, event_data):
        event = {
            "summary": event_data["period"] + ". " + event_data["name"],
            "location": event_data["room"],
            "description": event_data["teacher"],
            "colorId": event_data["colour"],
            "start": {
                "dateTime": rfc3339(event_data["start_time"]),
                "timeZone": "Australia/Sydney",
            },
            "end": {
                "dateTime": rfc3339(event_data["end_time"]),
                "timeZone": "Australia/Sydney",
            },
        }

        event = (
            self.service.events().insert(calendarId=self.CAL_ID, body=event).execute()
        )
