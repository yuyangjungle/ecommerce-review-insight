from _shared import JsonHandler
from service_core import evaluate_prompt_versions, resolve_dataset_from_payload


class handler(JsonHandler):
    def do_POST(self):
        try:
            payload = self.read_json()
            dataset = resolve_dataset_from_payload(payload)
            left_prompt_version = payload.get("left_prompt_version", "v1")
            right_prompt_version = payload.get("right_prompt_version", "v2")
            self.send_json(evaluate_prompt_versions(dataset, left_prompt_version, right_prompt_version))
        except Exception as exc:
            self.send_error_json(exc)
