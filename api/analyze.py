from _shared import JsonHandler
from service_core import analyze_dataset, resolve_dataset_from_payload


class handler(JsonHandler):
    def do_POST(self):
        payload = self.read_json()
        dataset = resolve_dataset_from_payload(payload)
        prompt_version = payload.get("prompt_version", "v2")
        self.send_json(analyze_dataset(dataset, prompt_version))
