"""Acceptance tests for Settings (workbook Milestone 2). Do not edit."""

import pytest
from pydantic import SecretStr, ValidationError

from incident_triage.settings import Settings


def test_defaults(clean_env):
    settings = Settings()

    assert settings.llm_model == "gpt-5.6-terra"
    assert settings.openai_api_key is None
    assert settings.openai_base_url is None
    assert settings.llm_timeout_seconds == 30.0
    assert settings.llm_max_retries == 2
    assert settings.llm_max_output_tokens == 2000
    assert settings.llm_input_usd_per_million is None
    assert settings.llm_output_usd_per_million is None


def test_reads_the_course_variable_names(clean_env):
    clean_env.setenv("LLM_MODEL", "gpt-test")
    clean_env.setenv("OPENAI_API_KEY", "not-a-real-key")
    clean_env.setenv("LLM_TIMEOUT_SECONDS", "12.5")
    clean_env.setenv("LLM_MAX_RETRIES", "0")
    clean_env.setenv("LLM_INPUT_USD_PER_MILLION", "0.25")

    settings = Settings()

    assert settings.llm_model == "gpt-test"
    assert isinstance(settings.openai_api_key, SecretStr)
    assert settings.openai_api_key.get_secret_value() == "not-a-real-key"
    assert settings.llm_timeout_seconds == 12.5
    assert settings.llm_max_retries == 0
    assert settings.llm_input_usd_per_million == 0.25


def test_dotenv_file(clean_env, tmp_path):
    (tmp_path / ".env").write_text("LLM_MODEL=from-dotenv\n", encoding="utf-8")

    assert Settings().llm_model == "from-dotenv"


def test_key_is_never_shown(clean_env):
    clean_env.setenv("OPENAI_API_KEY", "not-a-real-key")

    assert "not-a-real-key" not in repr(Settings())
    assert "not-a-real-key" not in str(Settings().model_dump())


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("LLM_TIMEOUT_SECONDS", "0"),
        ("LLM_MAX_OUTPUT_TOKENS", "-5"),
        ("LLM_TIMEOUT_SECONDS", "soon"),
    ],
)
def test_invalid_numbers_are_rejected(clean_env, name, value):
    clean_env.setenv(name, value)

    with pytest.raises(ValidationError):
        Settings()
