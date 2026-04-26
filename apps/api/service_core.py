from pathlib import Path
from typing import Dict

from llm_pipeline import analyze_dataset, get_runtime_status
from mock_pipeline import load_dataset, normalize_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
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
