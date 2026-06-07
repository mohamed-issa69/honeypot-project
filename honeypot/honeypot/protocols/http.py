import http.server
import socketserver
from urllib.parse import parse_qs
from honeypot.loggers.file_logger import FileLogger


class HTTPHoneypotHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.logger = FileLogger("logs/attacks.json")
        super().__init__(*args, **kwargs)

    def log_attack(self, service, data=None, payload=None):

        event_data = {
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
            "payload": payload or ""
        }

        if data:
            event_data.update(data)

        self.logger.log_event(
            service=service,
            src_ip=self.client_address[0],
            src_port=self.client_address[1],
            data=event_data
        )

    def do_GET(self):
        self.log_attack("http")

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        fake_login = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Login</title>

            <!-- نفس CSS الحقيقي -->
            <link rel="stylesheet" href="http://127.0.0.1/real_site2/css/style.css">

        </head>

        <body id="login">

            <div class="login-container">
                <img src="http://127.0.0.1/real_site2/css/img/login.png">

                <form method="POST">
                    <div class="login-input">
                        <input type="text" name="username" placeholder="Enter Username">
                    </div>

                    <div class="login-input">
                        <input type="password" name="password" placeholder="Enter Password">
                    </div>

                    <input type="submit" value="LOGIN" class="btn-login">
                </form>

            </div>

        </body>
        </html>
        """

        self.wfile.write(fake_login.encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode(errors='ignore')

        creds = parse_qs(data)

        self.log_attack("http", {
            "username": creds.get("username", [""])[0],
            "password": creds.get("password", [""])[0],
        }, payload=data)

        self.do_GET()

    def log_message(self, format, *args):
        return


class HTTPHoneypot:
    def __init__(self, host="0.0.0.0", port=8081):
        self.host = host
        self.port = port

    def run(self):
        print(f"[+] HTTP Honeypot running on {self.host}:{self.port}")
        with socketserver.TCPServer((self.host, self.port), HTTPHoneypotHandler) as httpd:
            httpd.serve_forever()