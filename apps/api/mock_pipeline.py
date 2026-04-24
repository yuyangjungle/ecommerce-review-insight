import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Dict, List


POSITIVE_RULES = {
    "battery_life": {
        "label": "续航表现",
        "priority": 1,
        "keywords": ["续航", "通勤", "一天"],
        "summary": "用户反复提到日常通勤和整天使用场景下的续航表现稳定。",
        "selling_point": "突出全天续航能力，覆盖通勤和轻运动场景。",
        "copy": "全天通勤不断电，日常出门更省心。",
        "faq": {
            "question": "一天一充够吗？",
            "answer": "从评论来看，多数用户认为日常通勤场景基本可以满足一天使用。"
        }
    },
    "comfort": {
        "label": "佩戴舒适度",
        "priority": 2,
        "keywords": ["舒服", "舒适", "不疼", "运动", "不容易掉"],
        "summary": "佩戴体验稳定，长时间使用和运动场景下都有正向反馈。",
        "selling_point": "强调长时间佩戴舒适和运动时稳固不易脱落。",
        "copy": "久戴不压耳，运动通勤都稳稳贴合。",
        "faq": {
            "question": "运动时容易掉吗？",
            "answer": "现有评论显示，大多数用户认为佩戴较稳，运动时不易脱落。"
        }
    },
    "portability": {
        "label": "便携与外观",
        "priority": 3,
        "keywords": ["小巧", "很小", "方便", "口袋", "好看", "外观", "便携"],
        "summary": "评论对充电盒便携性和外观设计认可度较高。",
        "selling_point": "突出小巧便携和外观设计感，适合日常携带。",
        "copy": "小巧充电盒随手装进口袋，轻装出门更方便。",
        "faq": {
            "question": "充电盒便携吗？",
            "answer": "不少用户提到充电盒体积小，放入口袋或随身包里都很方便。"
        }
    },
    "fast_connection": {
        "label": "连接速度",
        "priority": 4,
        "keywords": ["秒连", "连接速度", "连接快", "拿出来"],
        "summary": "用户对耳机拿出即连的连接速度反馈较好。",
        "selling_point": "强调开盖即连和日常切换设备时的效率体验。",
        "copy": "拿起即连，碎片化使用也不用等。",
        "faq": {
            "question": "连接速度快吗？",
            "answer": "从样本评论看，连接速度是明显的正向体验点。"
        }
    }
}

NEGATIVE_RULES = {
    "connection_stability": {
        "label": "连接稳定性",
        "priority": 1,
        "keywords": ["断连", "地铁"],
        "summary": "复杂环境下存在偶发断连问题，影响连续使用体验。",
        "optimization": "优先优化复杂通勤环境下的蓝牙连接稳定性。",
        "question": "地铁等复杂环境会不会断连？"
    },
    "noise_cancellation": {
        "label": "降噪落差",
        "priority": 3,
        "keywords": ["降噪", "宣传比", "差一些"],
        "summary": "用户认可有一定降噪效果，但对宣传预期与实际体验存在落差。",
        "optimization": "优化降噪能力表达，减少宣传与实际体验之间的心理落差。",
        "question": "降噪效果和宣传一致吗？"
    },
    "microphone": {
        "label": "通话收音稳定性",
        "priority": 2,
        "keywords": ["麦克风", "收音", "开会", "声音忽大忽小"],
        "summary": "通话场景中收音稳定性不足，影响远程会议体验。",
        "optimization": "提升麦克风收音的一致性与会议场景适配能力。",
        "question": "开会通话时收音稳定吗？"
    },
    "sound_quality": {
        "label": "音质期待管理",
        "priority": 4,
        "keywords": ["音质一般"],
        "summary": "部分评论认为音质表现中规中矩，未形成明显惊喜。",
        "optimization": "在内容表达上避免对音质做过度承诺，聚焦更强势卖点。",
        "question": "音质是不是核心卖点？"
    }
}

PROMPT_CONFIGS = {
    "v1": {
        "label": "v1 直接总结工作流",
        "description": "直接总结评论内容，结构较轻，引用覆盖不稳定。",
    },
    "v2": {
        "label": "v2 主题优先工作流",
        "description": "先抽取主题再生成内容，并显式保留引用依据。",
    },
}


def load_dataset(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_dataset(dataset: Dict) -> Dict:
    normalized = deepcopy(dataset)
    normalized.setdefault("dataset_id", "uploaded-dataset")
    normalized.setdefault("product_name", "上传商品")
    normalized.setdefault("reviews", [])
    return normalized


def dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def collect_themes(reviews: List[Dict], rules: Dict, theme_type: str) -> List[Dict]:
    bucket = {}
    for review in reviews:
        text = review["content"]
        for theme_id, rule in rules.items():
            if any(keyword in text for keyword in rule["keywords"]):
                entry = bucket.setdefault(
                    theme_id,
                    {
                        "theme_id": theme_id,
                        "title": rule["label"],
                        "priority": rule["priority"],
                        "type": theme_type,
                        "summary": rule["summary"],
                        "count": 0,
                        "citations": [],
                        "snippets": [],
                    },
                )
                entry["count"] += 1
                entry["citations"].append(review["review_id"])
                entry["snippets"].append(review["content"])

    themes = []
    for item in bucket.values():
        item["citations"] = dedupe(item["citations"])[:3]
        item["snippets"] = item["snippets"][:2]
        themes.append(item)

    themes.sort(key=lambda item: (-item["count"], item["priority"], item["title"]))
    for item in themes:
        item.pop("priority", None)
    return themes


def build_key_questions(positive_themes: List[Dict], negative_themes: List[Dict]) -> List[Dict]:
    questions = []
    for theme in negative_themes:
        rule = NEGATIVE_RULES[theme["theme_id"]]
        questions.append(
            {
                "question": rule["question"],
                "summary": theme["summary"],
                "citations": theme["citations"],
            }
        )

    for theme in positive_themes:
        rule = POSITIVE_RULES[theme["theme_id"]]
        questions.append(
            {
                "question": rule["faq"]["question"],
                "summary": theme["summary"],
                "citations": theme["citations"],
            }
        )

    return questions[:3]


def build_assets(positive_themes: List[Dict], negative_themes: List[Dict]) -> Dict:
    selling_points = []
    copy_suggestions = []
    faqs = []
    optimization_suggestions = []

    for theme in positive_themes[:3]:
        rule = POSITIVE_RULES[theme["theme_id"]]
        selling_points.append(
            {
                "title": theme["title"],
                "content": rule["selling_point"],
                "citations": theme["citations"],
            }
        )
        copy_suggestions.append(
            {
                "title": f"{theme['title']}文案建议",
                "content": rule["copy"],
                "citations": theme["citations"],
            }
        )
        faqs.append(
            {
                "question": rule["faq"]["question"],
                "answer": rule["faq"]["answer"],
                "citations": theme["citations"],
            }
        )

    for theme in negative_themes[:3]:
        rule = NEGATIVE_RULES[theme["theme_id"]]
        optimization_suggestions.append(
            {
                "title": theme["title"],
                "content": rule["optimization"],
                "citations": theme["citations"],
            }
        )

    return {
        "selling_points": selling_points,
        "copy_suggestions": copy_suggestions,
        "faqs": faqs,
        "optimization_suggestions": optimization_suggestions,
    }


def calculate_evaluation(positive_themes: List[Dict], negative_themes: List[Dict], assets: Dict) -> Dict:
    sections = [
        positive_themes,
        negative_themes,
        assets["selling_points"],
        assets["copy_suggestions"],
        assets["faqs"],
        assets["optimization_suggestions"],
    ]
    structure_completeness = round(sum(bool(section) for section in sections) / len(sections), 2)

    cited_items = 0
    total_items = 0
    for section in sections:
        for item in section:
            total_items += 1
            if item.get("citations"):
                cited_items += 1

    citation_coverage = round(cited_items / total_items, 2) if total_items else 0.0
    human_usable_score = round(3.2 + structure_completeness * 0.8 + citation_coverage * 0.5, 2)
    trust_score = round(3.0 + citation_coverage, 2)

    return {
        "structure_completeness": structure_completeness,
        "citation_coverage": citation_coverage,
        "human_usable_score": human_usable_score,
        "trust_score": trust_score,
    }


def build_review_lookup(reviews: List[Dict]) -> Dict:
    lookup = {}
    for review in reviews:
        lookup[review["review_id"]] = {
            "review_id": review["review_id"],
            "content": review["content"],
            "rating": review.get("rating"),
            "created_at": review.get("created_at"),
        }
    return lookup


def build_overview(
    product_name: str,
    positive_themes: List[Dict],
    negative_themes: List[Dict],
    assets: Dict,
    review_count: int,
) -> Dict:
    top_positive = positive_themes[0]["title"] if positive_themes else "暂无明显正向主题"
    top_negative = negative_themes[0]["title"] if negative_themes else "暂无明显负向主题"
    key_copy = assets["selling_points"][0]["content"] if assets["selling_points"] else "暂无推荐卖点"

    return {
        "headline": f"{product_name} 的核心机会在 {top_positive}，主要风险集中在 {top_negative}。",
        "executive_summary": (
            f"系统基于 {review_count} 条评论完成主题抽取与内容生成，"
            f"当前建议优先放大“{top_positive}”相关卖点，同时关注“{top_negative}”带来的体验落差。"
        ),
        "highlighted_selling_point": key_copy,
        "top_positive_label": top_positive,
        "top_negative_label": top_negative,
        "review_count": review_count,
    }


def apply_prompt_version(base_result: Dict, prompt_version: str) -> Dict:
    if prompt_version not in PROMPT_CONFIGS:
        raise ValueError(f"Unsupported prompt version: {prompt_version}")

    result = deepcopy(base_result)
    result["metadata"] = {
        "prompt_version": prompt_version,
        "workflow_label": PROMPT_CONFIGS[prompt_version]["label"],
        "workflow_description": PROMPT_CONFIGS[prompt_version]["description"],
    }

    if prompt_version == "v1":
        result["summary"]["top_positive_themes"] = result["summary"]["top_positive_themes"][:3]
        result["summary"]["top_negative_themes"] = result["summary"]["top_negative_themes"][:2]
        result["summary"]["key_questions"] = result["summary"]["key_questions"][:2]
        result["assets"]["copy_suggestions"] = result["assets"]["copy_suggestions"][:2]
        result["assets"]["optimization_suggestions"] = []

        if len(result["assets"]["selling_points"]) > 1:
            result["assets"]["selling_points"][1]["citations"] = []
        if len(result["assets"]["faqs"]) > 1:
            result["assets"]["faqs"][1]["citations"] = []
        if result["summary"]["key_questions"]:
            result["summary"]["key_questions"][-1]["citations"] = []

    result["evaluation"] = calculate_evaluation(
        result["summary"]["top_positive_themes"],
        result["summary"]["top_negative_themes"],
        result["assets"],
    )
    return result


def analyze_dataset(dataset: Dict, prompt_version: str = "v2") -> Dict:
    dataset = normalize_dataset(dataset)
    reviews = dataset["reviews"]
    positive_themes = collect_themes(reviews, POSITIVE_RULES, "positive_theme")
    negative_themes = collect_themes(reviews, NEGATIVE_RULES, "negative_theme")
    key_questions = build_key_questions(positive_themes, negative_themes)
    assets = build_assets(positive_themes, negative_themes)
    review_lookup = build_review_lookup(reviews)
    overview = build_overview(dataset["product_name"], positive_themes, negative_themes, assets, len(reviews))
    base_result = {
        "dataset_id": dataset["dataset_id"],
        "product_name": dataset["product_name"],
        "overview": overview,
        "review_lookup": review_lookup,
        "source_reviews": reviews[:8],
        "summary": {
            "top_positive_themes": positive_themes,
            "top_negative_themes": negative_themes,
            "key_questions": key_questions,
        },
        "assets": assets,
    }
    return apply_prompt_version(base_result, prompt_version)


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
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight review insight analysis.")
    parser.add_argument("--dataset", required=True, help="Path to the dataset JSON file.")
    parser.add_argument("--output", required=True, help="Path to write the analysis JSON output.")
    parser.add_argument("--prompt-version", default="v2", choices=sorted(PROMPT_CONFIGS.keys()))
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    output_path = Path(args.output)

    dataset = load_dataset(dataset_path)
    result = analyze_dataset(dataset, args.prompt_version)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(f"Analysis written to {output_path}")


if __name__ == "__main__":
    main()
