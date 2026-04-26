from _shared import JsonHandler
from service_core import list_datasets


class handler(JsonHandler):
    def do_GET(self):
        self.send_json({"datasets": list_datasets()})
