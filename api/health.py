from _shared import JsonHandler
from service_core import get_runtime_status


class handler(JsonHandler):
    def do_GET(self):
        self.send_json({"status": "ok", "runtime": get_runtime_status()})
