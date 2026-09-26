"""
Manually maintained model catalog.

Add models here as needed. Each model defines its capabilities,
API type, and any special handling (e.g., vision fallback model).
"""
# TODO: should use something like https://github.com/anomalyco/models.dev in future

from dataclasses import dataclass
from enum import Enum

DEFAULT_MAX_TOKENS = 16384


class ApiType(Enum):
    OPENAI_COMPLETIONS = "openai-completions"
    OPENAI_RESPONSES = "openai-responses"
    GITHUB_COPILOT = "github-copilot"
    GITHUB_COPILOT_RESPONSES = "github-copilot-responses"


@dataclass
class Model:
    id: str  # Model ID (e.g., "glm-5.3", "deepseek-flash")
    provider: str  # "openai", "zhipu", "github-copilot"
    api: ApiType  # Which API format to use
    base_url: str  # API endpoint
    max_tokens: int  # Max output tokens
    supports_images: bool  # Native vision support
    supports_thinking: bool  # Reasoning/thinking support
    context_window: int | None = None  # Max context (None = use config default)
    vision_model: str | None = None  # Fallback vision model if no native support


MODELS: dict[str, Model] = {
    # ZhiPu models
    "glm-5.3": Model(
        id="glm-5.3",
        provider="zhipu",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.z.ai/api/coding/paas/v4",
        max_tokens=131072,
        supports_images=False,
        supports_thinking=True,
        context_window=1000000,
    ),
    "glm-5.3-flash": Model(
        id="glm-5.3-flash",
        provider="zhipu",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.z.ai/api/coding/paas/v4",
        max_tokens=131072,
        supports_images=True,
        supports_thinking=True,
        context_window=1000000,
    ),
    # DeepSeek models (OpenAI-compatible Chat Completions API)
    "deepseek-flash": Model(
        id="deepseek-flash",
        provider="deepseek",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.deepseek.com",
        max_tokens=384000,
        supports_images=True,
        supports_thinking=True,
        context_window=1000000,
    ),
    "deepseek-v4-pro": Model(
        id="deepseek-v4-pro",
        provider="deepseek",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.deepseek.com",
        max_tokens=384000,
        supports_images=False,
        supports_thinking=True,
        context_window=1000000,
    ),
    # GitHub Copilot models - GPT (uses Copilot Responses API)
    "gpt-5.6-sol-copilot": Model(
        id="gpt-5.6-sol",
        provider="github-copilot",
        api=ApiType.GITHUB_COPILOT_RESPONSES,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
        context_window=372000,
    ),
    "gpt-5.6-terra-copilot": Model(
        id="gpt-5.6-terra",
        provider="github-copilot",
        api=ApiType.GITHUB_COPILOT_RESPONSES,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
        context_window=372000,
    ),
    "gpt-5.6-luna-copilot": Model(
        id="gpt-5.6-luna",
        provider="github-copilot",
        api=ApiType.GITHUB_COPILOT_RESPONSES,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
        context_window=372000,
    ),
    "gpt-5.5-copilot": Model(
        id="gpt-5.5",
        provider="github-copilot",
        api=ApiType.GITHUB_COPILOT_RESPONSES,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
}


def get_model(model_id: str, provider: str | None = None) -> Model | None:
    if provider:
        for model in MODELS.values():
            if model.id == model_id and model.provider == provider:
                return model

    direct = MODELS.get(model_id)
    if direct:
        return direct

    for model in MODELS.values():
        if model.id == model_id:
            return model

    return None


def get_all_models() -> list[Model]:
    return list(MODELS.values())


def get_models_by_provider(provider: str) -> list[Model]:
    return [m for m in MODELS.values() if m.provider == provider]


def get_max_tokens(model_id: str) -> int:
    model = MODELS.get(model_id)
    return model.max_tokens if model else DEFAULT_MAX_TOKENS
