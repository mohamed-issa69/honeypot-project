import json
import time
import os
import urllib.parse
from dotenv import load_dotenv


class FileLogger:

    def __init__(self, log_file):
        self.log_file = log_file

        load_dotenv(
            os.path.join(
                os.path.dirname(__file__),
                '../../.env'
            )
        )

    def extract_features(self, text):

        raw_text = text.lower()
        decoded_text = urllib.parse.unquote(raw_text)

        sql_keywords = [
            "select", "union", "or 1=1", "drop",
            "insert", "update", "delete", "--"
        ]

        xss_keywords = [
            "<script", "javascript:", "onerror", "alert("
        ]

        cmd_keywords = [
            "whoami", "ls", "cat ", ";", "|", "&&"
        ]

        path_keywords = [
            "../", "..\\", "/etc/passwd"
        ]

        return {
            "length": len(decoded_text),

            "num_quotes":
                decoded_text.count("'") +
                decoded_text.count('"'),

            "num_dashes":
                decoded_text.count("-"),

            "num_angles":
                decoded_text.count("<") +
                decoded_text.count(">"),

            "num_special_chars":
                sum(not c.isalnum() for c in decoded_text),

            "num_digits":
                sum(c.isdigit() for c in decoded_text),

            "num_spaces":
                decoded_text.count(" "),

            "encoded_chars":
                raw_text.count("%"),

            "has_encoded_payload":
                int("%" in raw_text),

            "has_sql_keywords":
                int(any(k in decoded_text for k in sql_keywords)),

            "has_xss_keywords":
                int(any(k in decoded_text for k in xss_keywords)),

            "has_cmd_keywords":
                int(any(k in decoded_text for k in cmd_keywords)),

            "has_path_keywords":
                int(any(k in decoded_text for k in path_keywords)),

            "num_equal_signs":
                decoded_text.count("="),

            "num_ampersands":
                decoded_text.count("&"),

            "payload_entropy":
                len(set(decoded_text))
        }

    def detect_attack_type(self, features):

        if features["has_sql_keywords"]:
            return "sql_injection"

        elif features["has_xss_keywords"]:
            return "xss"

        elif features["has_cmd_keywords"]:
            return "command_injection"

        elif features["has_path_keywords"]:
            return "path_traversal"

        return None   # ❌ مهم: مفيش normal خالص

    def log_event(self, service, src_ip, src_port, data):

        path = data.get("path", "")
        payload = data.get("payload", "")

        # GET fallback
        if payload == "" and "?" in path:
            payload = path.split("?", 1)[1]

        full_text = (path + " " + payload).lower()

        features = self.extract_features(full_text)

        attack_type = self.detect_attack_type(features)

        # ❌ أهم سطر: تجاهل أي حاجة مش attack
        if attack_type is None:
            return

        event = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "service": service,
            "src_ip": src_ip,
            "src_port": src_port,
            "path": path,
            "payload": payload,
            "attack_type": attack_type,
            "features": features
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
