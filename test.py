import requests

with open("pass") as file:
    username = file.readline().strip()
    password = file.readline().strip()
session = requests.Session()

r = session.get(
    "https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php"
)

SAML_session_id = r.headers["Set-Cookie"].lstrip("SimpleSAMLSessionID=").split("; ")[0]
print(r.headers)

r = session.get(
    "https://rosebank-login.cloudworkengine.net/module.php/core/loginuserpass.php?",
    data={"username": username, "password": password, "AuthState": AuthState},
)

print(r.text)
