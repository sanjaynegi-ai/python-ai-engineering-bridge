"""Settings from HANDBOOK_* environment variables and .env."""

from pathlib import Path
from typing import Literal

from pydantic import Field, PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HANDBOOK_", env_file=".env", extra="ignore", frozen=True
    )

    documents: Path = Path("data/handbook")
    index: Path = Path("index")
    embedder: Literal["fastembed", "hashing"] = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"  # used by the fastembed embedder
    chunk_size: PositiveInt = 500
    chunk_overlap: int = Field(default=100, ge=0)
    top_k: PositiveInt = 3
    min_score: float = Field(default=0.6, ge=-1.0, le=1.0)

    @model_validator(mode="after")
    def overlap_smaller_than_size(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self
