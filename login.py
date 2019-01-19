import bs4
import requests


def save(words):
    with open("test.html", "wb") as w:
        w.write(words)


def param(data: dict):
    return "&".join([key + "=" + value for key, value in data.items()])


logins = {"username": "doconnell", "password": open("pass").read().strip()}
edumate = "https://edumate.rosebank.nsw.edu.au"

with requests.Session() as s:
    e = s.get(edumate, verify=False)
    n = s.get("https://edumate.rosebank.nsw.edu.au/rosebank/index.php", verify=False)
    o = s.get(
        "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/sso-login/?return_path=dashboard/my-edumate/",
        verify=False,
    )
    simplesamlid = {"SimpleSAMLSessionID": o.history[1].cookies["SimpleSAMLSessionID"]}
    soup = bs4.BeautifulSoup(o.history[1].content, "lxml")
    auth = {"AuthState": soup.a.attrs["href"][soup.a.attrs["href"].find("=") + 1 :]}
    l = s.post(
        "https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php?"
        + param(auth)
        + "&"
        + param(logins),
        cookies=simplesamlid,
    )
    soup = bs4.BeautifulSoup(l.content, "lxml")
    saml_response = {"SAMLResponse": soup.find_all("input")[1].attrs["value"]}
    ol = s.post(
        "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/saml/acs",
        data={
            **saml_response,
            "RelayState": "%7B%22return_path%22%3A%22dashboard%5C%2Fmy-edumate%5C%2F%22%7D",
        },
        cookies={"device_view": "full", "PHPSESSID": s.cookies["PHPSESSID"]},
    )
    d = s.get(
        "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/admin/get-day-calendar/2019-01-19/next?_dc=1547853340085&page=1&start=0&limit=25",
        verify=False,
    )
