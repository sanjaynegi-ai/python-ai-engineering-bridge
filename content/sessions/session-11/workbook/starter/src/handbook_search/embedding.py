"""Embedders: turn texts into vectors, one row per text, in input order."""

import hashlib
import os
import re
from pathlib import Path
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    model_id: str
    dimensions: int

    def embed(self, texts: list[str]) -> np.ndarray: ...


class HashingEmbedder:
    """A deterministic bag-of-words embedder: no model, no download, no cost.

    Each word is hashed into one of `dimensions` slots, so texts that share words get
    similar vectors. It matches words, not meaning, so it's a baseline and a test double,
    not a substitute for a real embedding model.
    """

    def __init__(self, dimensions: int = 512) -> None:
        self.dimensions = dimensions
        self.model_id = f"hashing-{dimensions}"

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dimensions), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                slot = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % self.dimensions
                vectors[row, slot] += 1.0
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.where(norms == 0, 1, norms)


class FastEmbedEmbedder:
    """A real embedding model, run locally with fastembed (Session 01, Part 9).

    The first use downloads the model (about 67 MB for the default) into `cache_dir`: by
    default FASTEMBED_CACHE_PATH, or ~/.cache/fastembed, as in Session 01.
    """

    def __init__(
        self, model_id: str = "BAAI/bge-small-en-v1.5", cache_dir: Path | None = None
    ) -> None:
        from fastembed import TextEmbedding  # imported here: loading it takes a second

        cache = (
            cache_dir
            or os.environ.get("FASTEMBED_CACHE_PATH")
            or Path.home() / ".cache" / "fastembed"
        )
        self._model = TextEmbedding(model_name=model_id, cache_dir=str(cache))
        self.model_id = model_id
        self.dimensions = self._model.embedding_size

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimensions), dtype=np.float32)
        return np.array(list(self._model.embed(texts)), dtype=np.float32)
