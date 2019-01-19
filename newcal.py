import requests


class Calender:
    api_key = open("apikey").read()
    base_url = "https://www.googleapis.com/calendar/v3/"

    def get(self, url, headers=None):
        data = {"Authorization": "Bearer " + self.api_key}
        if headers is not None:
            data = {**data, **headers}
        return requests.get(self.base_url + url, headers=data)

    def get_calendars(self):
        response = requests.get(
            url="https://www.googleapis.com/calendar/v3/users/me/calendarList",
            headers={"Authorization": "Bearer ACCESS_TOKEN"},
        )
        response.raise_for_status()
        calendars = response.json().get("items")

        return calendars  # self.get("users/me/calendarList")


if __name__ == "__main__":
    cal = Calender()
    print(cal.get_calendars().text)
