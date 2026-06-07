from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import urllib.parse

REAL_SITE = "http://127.0.0.1/real_site2"
HONEYPOT = "http://127.0.0.1:8081"

# Session للحفاظ على الـ cookies والـ PHP session
session = requests.Session()

PATTERNS = [
    # SQL Injection
    "union", "select", "or 1=1", "--",
    "' or '1'='1", "' or 1=1",
    "drop", "insert", "update", "delete",

    # XSS
    "<script", "javascript:", "onerror", "alert(",

    # Command Injection
    "whoami", "ls", "cat ",

    # Path Traversal
    "../", "..\\", "/etc/passwd"
]


def is_attack(data: str):

    if not data:
        return False

    decoded = urllib.parse.unquote(data.lower())

    return any(p in decoded for p in PATTERNS)


class Gateway(BaseHTTPRequestHandler):

    def forward(self, target, body=None):

        url = target.rstrip("/") + self.path

        headers = dict(self.headers)

        # مهم عشان الـ Host ما يبوظش الـ session
        headers.pop("Host", None)

        try:

            if self.command == "POST":

                r = session.post(
                    url,
                    headers=headers,
                    data=body,
                    allow_redirects=False
                )

            else:

                r = session.get(
                    url,
                    headers=headers,
                    allow_redirects=False
                )

            self.send_response(r.status_code)

            for k, v in r.headers.items():

                # تجاهل transfer encoding
                if k.lower() == "transfer-encoding":
                    continue

                # تعديل أي redirects عشان تفضل جوة البروكسي
                if k.lower() == "location":

                    if v.startswith("/"):

                        v = "http://127.0.0.1:8000" + v

                    else:

                        v = v.replace(
                            "http://127.0.0.1",
                            "http://127.0.0.1:8000"
                        )

                self.send_header(k, v)

            self.end_headers()

            self.wfile.write(r.content)

        except Exception as e:
            print("Error:", e)

    def extract_payload(self):

        parsed = urllib.parse.urlparse(self.path)

        query = urllib.parse.parse_qs(parsed.query)

        data = ""

        # GET params
        for key in query:
            for value in query[key]:
                data += value + " "

        body = None

        # POST body
        length = int(self.headers.get("Content-Length", 0))

        if length > 0:

            raw_body = self.rfile.read(length)

            try:
                body = raw_body.decode(errors="ignore")
                data += body

            except:
                body = raw_body

        return data.strip(), body

    def handle_request(self):

        data, body = self.extract_payload()

        decoded_data = urllib.parse.unquote(data.lower())

        print("[DEBUG PAYLOAD]", decoded_data)

        # كشف الهجمات
        if is_attack(decoded_data):

            print("[HONEYPOT] Attack detected")

            target = HONEYPOT

        # أي admin page تتحول للهانيبوت
        elif "admin" in self.path.lower():

            print("[HONEYPOT] Admin path detected")

            target = HONEYPOT

        else:

            target = REAL_SITE

        print("[TARGET]", target)

        self.forward(target, body)

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def log_message(self, format, *args):
        return


print("[+] Smart Gateway running on http://127.0.0.1:8000")

HTTPServer(("", 8000), Gateway).serve_forever()