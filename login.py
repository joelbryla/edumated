import bs4
import requests

def param(data: dict):
    return "".join([key + "=" + value for key, value in data.items()])

payload = {"username": "doconnell", "password": open("pass").read().strip()}
edumate = "https://edumate.rosebank.nsw.edu.au"

with requests.Session() as s:
    e = s.get(edumate, verify=False)
    # php_session_id = {"PHPSESSID": e.history[1].cookies["PHPSESSID"]}
    n = s.get("https://edumate.rosebank.nsw.edu.au/rosebank/index.php", verify=False)
    o = s.get(
        "https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/sso-login/?return_path=dashboard/my-edumate/",
        verify=False,
    )
    simplesamlid = {"SimpleSAMLSessionID": o.history[1].cookies["SimpleSAMLSessionID"]}
    soup = bs4.BeautifulSoup(o.history[1].content, "lxml")
    auth = {"AuthState": soup.a.attrs["href"][soup.a.attrs["href"].find("=")+1:]}
    l = s.post("https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php?" + param(auth) + "&" + param(payload), cookies=simplesamlid)
    d = s.get("https://edumate.rosebank.nsw.edu.au/rosebank/web/app.php/admin/get-day-calendar/2019-01-19/next?_dc=1547853340085&page=1&start=0&limit=25", verify=False)
