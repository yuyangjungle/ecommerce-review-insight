import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from llm_pipeline import analyze_dataset, get_runtime_status
from mock_pipeline import load_dataset, normalize_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "apps" / "web"
DATA_ROOT = PROJECT_ROOT / "data" / "sample"


def list_datasets():
    datasets = []
    for path in sorted(DATA_ROOT.glob("*-demo.json")):
        dataset = load_dataset(path)
        datasets.append(
            {
                "id": dataset["dataset_id"],
                "name": dataset.get("product_name", dataset["dataset_id"]),
                "review_count": len(dataset.get("reviews", [])),
            }
        )
    return datasets


def get_dataset_by_id(dataset_id: str):
    for path in DATA_ROOT.glob("*-demo.json"):
        dataset = load_dataset(path)
        if dataset["dataset_id"] == dataset_id:
            return dataset
    raise FileNotFoundError(f"Dataset not found: {dataset_id}")


def resolve_dataset_from_payload(payload):
    if "dataset" in payload and payload["dataset"]:
        return normalize_dataset(payload["dataset"])
    if payload.get("dataset_id"):
        return get_dataset_by_id(payload["dataset_id"])
    raise FileNotFoundError("Dataset payload is missing dataset_id or dataset")


def evaluate_prompt_versions(dataset: Dict, left_prompt_version: str, right_prompt_version: str) -> Dict:
    left_result = analyze_dataset(dataset, left_prompt_version)
    right_result = analyze_dataset(dataset, right_prompt_version)

    left_score = left_result["evaluation"]["human_usable_score"] + left_result["evaluation"]["trust_score"]
    right_score = right_result["evaluation"]["human_usable_score"] + right_result["evaluation"]["trust_score"]

    if left_score == right_score:
        winner = "tie"
    else:
        winner = left_prompt_version if left_score > right_score else right_prompt_version

    return {
        "dataset_id": dataset["dataset_id"],
        "winner": winner,
        "left": {
            "prompt_version": left_prompt_version,
            "result": left_result,
            "scores": left_result["evaluation"],
        },
        "right": {
            "prompt_version": right_prompt_version,
            "result": right_result,
            "scores": right_result["evaluation"],
        },
        "runtime": get_runtime_status(),
    }


class DemoRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.send_json({"status": "ok", "runtime": get_runtime_status()})
            return
        if parsed.path == "/api/datasets":
            self.send_json({"datasets": list_datasets()})
            return
        self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/analyze":
            payload = self.read_json()
            dataset = resolve_dataset_from_payload(payload)
            prompt_version = payload.get("prompt_version", "v2")
            self.send_json(analyze_dataset(dataset, prompt_version))
            return
        if parsed.path == "/api/evaluate":
            payload = self.read_json()
            dataset = resolve_dataset_from_payload(payload)
            left_prompt_version = payload.get("left_prompt_version", "v1")
            right_prompt_version = payload.get("right_prompt_version", "v2")
            self.send_json(evaluate_prompt_versions(dataset, left_prompt_version, right_prompt_version))
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
            raise

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_static(self, request_path: str):
        relative_path = "index.html" if request_path in ("", "/") else request_path.lstrip("/")
        target = (WEB_ROOT / relative_path).resolve()

        if WEB_ROOT not in target.parents and target != WEB_ROOT:
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return
        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type, _ = mimetypes.guess_type(str(target))
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Serve the Taotian AI Product Assistant demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
    print(f"本地演示服务已启动：http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
