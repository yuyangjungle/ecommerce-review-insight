import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib import error, request

from mock_pipeline import (
    PROMPT_CONFIGS,
    analyze_dataset as analyze_dataset_mock,
    apply_prompt_version,
    build_base_result,
    normalize_dataset,
)


DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"


@dataclass
class LLMConfig:
    enabled: bool
    provider_name: Optional[str]
    mode_setting: str
    api_key: Optional[str]
    base_url: str
    model_name: Optional[str]
    timeout_seconds: int


def _read_mode_setting() -> str:
    return (os.getenv("REVIEW_INSIGHT_USE_LLM") or "auto").strip().lower()


def load_llm_config() -> LLMConfig:
    mode_setting = _read_mode_setting()
    timeout_seconds = int(os.getenv("OPENAI_TIMEOUT_SECONDS") or "45")

    deepseek_api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip() or None
    openai_api_key = (os.getenv("OPENAI_API_KEY") or "").strip() or None

    if deepseek_api_key:
        provider_name = "DeepSeek"
        api_key = deepseek_api_key
        base_url = (
            os.getenv("DEEPSEEK_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or DEFAULT_DEEPSEEK_BASE_URL
        ).strip().rstrip("/")
        model_name = (
            os.getenv("DEEPSEEK_MODEL")
            or os.getenv("OPENAI_MODEL")
            or DEFAULT_DEEPSEEK_MODEL
        ).strip() or None
    else:
        provider_name = "OpenAI-compatible" if openai_api_key else None
        api_key = openai_api_key
        base_url = (os.getenv("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE_URL).strip().rstrip("/")
        model_name = (os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL).strip() or None

    enabled = bool(
        api_key
        and model_name
        and mode_setting not in {"0", "false", "off", "no", "disabled"}
    )

    return LLMConfig(
        enabled=enabled,
        provider_name=provider_name,
        mode_setting=mode_setting,
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        timeout_seconds=timeout_seconds,
    )


def get_runtime_status() -> Dict:
    config = load_llm_config()
    return {
        "llm_enabled": config.enabled,
        "analysis_mode": "hybrid_llm" if config.enabled else "mock",
        "mode_setting": config.mode_setting,
        "provider_name": config.provider_name if config.enabled else None,
        "model_name": config.model_name if config.enabled else None,
    }


def _extract_json_object(text: str) -> Dict:
    start = text.find("{")
    if start == -1:
        raise ValueError("模型输出中没有找到 JSON 对象。")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : index + 1])

    raise ValueError("模型输出中的 JSON 对象不完整。")


def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    chunks.append(item.get("text", ""))
                elif "text" in item:
                    chunks.append(str(item["text"]))
            else:
                chunks.append(str(item))
        return "".join(chunks)
    return str(content)


def _post_chat_completions(payload: Dict, config: LLMConfig) -> Dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=f"{config.base_url}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=config.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"网络请求失败：{exc.reason}") from exc


def _call_llm_for_refinement(prompt_messages: List[Dict], config: LLMConfig) -> Dict:
    base_payload = {
        "model": config.model_name,
        "messages": prompt_messages,
        "temperature": 0.3,
        "max_tokens": 1600,
    }
    if config.provider_name == "DeepSeek":
        base_payload["thinking"] = {"type": "disabled"}

    for include_response_format in (True, False):
        payload = dict(base_payload)
        if include_response_format:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = _post_chat_completions(payload, config)
            content = _content_to_text(response["choices"][0]["message"]["content"])
            return _extract_json_object(content)
        except RuntimeError as exc:
            if include_response_format and "response_format" in str(exc):
                continue
            raise

    raise RuntimeError("模型调用失败。")


def _truncate_error_message(message: str) -> str:
    clean = " ".join(message.split())
    return clean[:180]


def _build_refinement_messages(result: Dict, prompt_version: str) -> List[Dict]:
    evidence = {
        "product_name": result["product_name"],
        "prompt_version": prompt_version,
        "workflow_label": PROMPT_CONFIGS[prompt_version]["label"],
        "workflow_description": PROMPT_CONFIGS[prompt_version]["description"],
        "positive_themes": result["summary"]["top_positive_themes"],
        "negative_themes": result["summary"]["top_negative_themes"],
        "key_questions": result["summary"]["key_questions"],
        "selling_points": result["assets"]["selling_points"],
        "copy_suggestions": result["assets"]["copy_suggestions"],
        "faqs": result["assets"]["faqs"],
        "optimization_suggestions": result["assets"]["optimization_suggestions"],
        "reviews": result["source_reviews"][:6],
    }

    schema = {
        "overview": {
            "headline": "string",
            "executive_summary": "string",
            "highlighted_selling_point": "string",
        },
        "selling_point_contents": ["string"],
        "copy_suggestion_contents": ["string"],
        "faq_answers": ["string"],
        "optimization_contents": ["string"],
    }

    system_prompt = (
        "你是电商评论洞察产品中的内容生成助手。"
        "你的任务是基于已经抽取好的主题、问题与引用证据，生成更自然、更像正式产品输出的中文文案。"
        "不要凭空补充没有证据支持的信息，不要发散成营销口号堆砌。"
        "只输出 JSON，不要输出解释文字。"
    )

    user_prompt = (
        "请根据下面的结构化证据，润色并重写内容层输出。\n"
        "要求：\n"
        "1. 保持中文、简洁、专业，适合电商运营阅读。\n"
        "2. overview 要能直接放在摘要区。\n"
        "3. selling_point_contents、copy_suggestion_contents、faq_answers、optimization_contents 的元素数量必须与输入对应数组完全一致。\n"
        "4. 不要新增字段，不要改动标题，不要改动引用 id。\n"
        "5. 如果某一项信息不足，就在已有方向上保守表达，不要编造。\n\n"
        f"输出 JSON Schema：\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        f"输入证据：\n{json.dumps(evidence, ensure_ascii=False, indent=2)}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _merge_refinement(result: Dict, refinement: Dict) -> None:
    overview = refinement.get("overview") or {}
    result["overview"]["headline"] = overview.get("headline") or result["overview"]["headline"]
    result["overview"]["executive_summary"] = (
        overview.get("executive_summary") or result["overview"]["executive_summary"]
    )
    result["overview"]["highlighted_selling_point"] = (
        overview.get("highlighted_selling_point") or result["overview"]["highlighted_selling_point"]
    )

    for index, value in enumerate(refinement.get("selling_point_contents") or []):
        if index < len(result["assets"]["selling_points"]) and value:
            result["assets"]["selling_points"][index]["content"] = value

    for index, value in enumerate(refinement.get("copy_suggestion_contents") or []):
        if index < len(result["assets"]["copy_suggestions"]) and value:
            result["assets"]["copy_suggestions"][index]["content"] = value

    for index, value in enumerate(refinement.get("faq_answers") or []):
        if index < len(result["assets"]["faqs"]) and value:
            result["assets"]["faqs"][index]["answer"] = value

    for index, value in enumerate(refinement.get("optimization_contents") or []):
        if index < len(result["assets"]["optimization_suggestions"]) and value:
            result["assets"]["optimization_suggestions"][index]["content"] = value


def analyze_dataset(dataset: Dict, prompt_version: str = "v2") -> Dict:
    config = load_llm_config()
    dataset = normalize_dataset(dataset)

    if not config.enabled:
        return analyze_dataset_mock(dataset, prompt_version, analysis_mode="mock")

    base_result = build_base_result(dataset)
    result = apply_prompt_version(
        base_result,
        prompt_version,
        analysis_mode="hybrid_llm",
        provider_name=config.provider_name,
        model_name=config.model_name,
    )

    try:
        refinement = _call_llm_for_refinement(_build_refinement_messages(result, prompt_version), config)
        _merge_refinement(result, refinement)
        return result
    except Exception as exc:
        warning = f"LLM 调用失败，已自动回退为 mock 输出：{_truncate_error_message(str(exc))}"
        return analyze_dataset_mock(
            dataset,
            prompt_version,
            analysis_mode="mock_fallback",
            provider_name=config.provider_name,
            model_name=config.model_name,
            warnings=[warning],
        )
