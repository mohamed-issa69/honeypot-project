from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import urllib.parse

REAL_SITE = "http://127.0.0.1:80/real_site"
HONEYPOT = "http://127.0.0.1:8081"

PATTERNS = [
    # SQL Injection
    "union", "select", "or 1=1", "--",
    "' or '1'='1", "' or 1=1",
    "drop", "insert", "update", "delete",

    # XSS
    "<script", "javascript:", "onerror", "alert(",

    # Command Injection
    "whoami", "ls", "cat ", ";", "|", "&&",

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
        url = target + self.path
        headers = dict(self.headers)

        try:
            if self.command == "POST":
                r = requests.post(url, headers=headers, data=body)

            else:
                r = requests.get(url, headers=headers)

            self.send_response(r.status_code)

            for k, v in r.headers.items():
                if k.lower() != "transfer-encoding":
                    self.send_header(k, v)

            self.end_headers()
            self.wfile.write(r.content)

        except Exception as e:
            print("Error:", e)

    def extract_payload(self):

        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        data = ""

        # GET parameters
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

        # مهم جداً
        decoded_data = urllib.parse.unquote(data.lower())

        print("[DEBUG PAYLOAD]", decoded_data)

        if is_attack(decoded_data):
            print("[HONEYPOT] Attack detected")
            target = HONEYPOT

        elif "admin" in self.path.lower():
            print("[HONEYPOT] Admin path detected")
            target = HONEYPOT

        else:
            target = REAL_SITE

        self.forward(target, body)

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def log_message(self, format, *args):
        return


print("[+] Smart Gateway running on http://127.0.0.1:8000")
HTTPServer(("", 8000), Gateway).serve_forever()
