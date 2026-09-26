from kon.llm.models import ApiType, get_model


def test_get_model_resolves_provider_scoped_lookup():
    copilot = get_model("gpt-5.5", "github-copilot")
    zhipu = get_model("glm-5.3", "zhipu")

    assert copilot is not None
    assert zhipu is not None
    assert copilot.provider == "github-copilot"
    assert zhipu.provider == "zhipu"


def test_get_model_falls_back_to_id_lookup():
    model = get_model("glm-5.3")

    assert model is not None
    assert model.provider == "zhipu"
    assert model.context_window == 1000000
    assert model.max_tokens == 131072


def test_get_model_resolves_glm_5_3_flash():
    model = get_model("glm-5.3-flash", "zhipu")

    assert model is not None
    assert model.provider == "zhipu"
    assert model.supports_images is True
    assert model.context_window == 1000000


def test_get_model_resolves_deepseek_models():
    model = get_model("deepseek-flash", "deepseek")

    assert model is not None
    assert model.provider == "deepseek"
    assert model.context_window == 1000000
    assert model.max_tokens == 384000
    assert model.supports_images is True


def test_get_model_resolves_gpt_5_6_copilot_models():
    for model_id in ("gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"):
        model = get_model(model_id, "github-copilot")

        assert model is not None
        assert model.provider == "github-copilot"
        assert model.api == ApiType.GITHUB_COPILOT_RESPONSES
        assert model.context_window == 372000
        assert model.supports_images is True
        assert model.supports_thinking is True
