"""Settings from ASSISTANT_* environment variables and .env.

The LLM's own settings (LLM_MODEL, OPENAI_API_KEY ...) use the course's variable names,
without the prefix: see generation.LLMSettings.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# A similarity threshold belongs to one embedding model (Session 11). 0.6 is Session 11's
# value for bge-small; the hashing embedder matches words, so its scores are much lower.
# Tune with `knowledge-assistant evaluate`, and override with ASSISTANT_MIN_SCORE.
DEFAULT_MIN_SCORE = {"fastembed": 0.6, "hashing": 0.2}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ASSISTANT_", env_file=".env", extra="ignore", frozen=True
    )

    documents: Path = Path("data/docs")
    index: Path = Path("index")
    embedder: Literal["fastembed", "hashing"] = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"  # used by the fastembed embedder
    chunk_size: PositiveInt = 800
    chunk_overlap: int = Field(default=100, ge=0)
    generator: Literal["openai", "extractive"] = "openai"
    top_k: PositiveInt = 4
    min_score: float | None = Field(default=None, ge=-1.0, le=1.0)  # None: the default above

    @model_validator(mode="after")
    def overlap_smaller_than_size(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self

    @property
    def effective_min_score(self) -> float:
        return self.min_score if self.min_score is not None else DEFAULT_MIN_SCORE[self.embedder]
