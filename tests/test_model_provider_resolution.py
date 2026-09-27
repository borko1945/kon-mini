from kon.llm.models import ApiType, get_model


def test_get_model_resolves_provider_scoped_lookup():
    deepseek = get_model("deepseek-v4-pro", "deepseek")
    zhipu = get_model("glm-5.3", "zhipu")

    assert deepseek is not None
    assert zhipu is not None
    assert deepseek.provider == "deepseek"
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
    assert model.api == ApiType.OPENAI_COMPLETIONS
    assert model.context_window == 1000000
    assert model.max_tokens == 384000
    assert model.supports_images is True
