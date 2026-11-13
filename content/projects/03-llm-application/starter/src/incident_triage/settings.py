"""Settings from environment variables and .env, using the course's variable names.

Workbook Milestone 2: add the fields in the workbook's table. With no prefix,
a field named llm_model is read from LLM_MODEL (matching is case-insensitive).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)
