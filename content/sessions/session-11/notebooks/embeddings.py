"""Embeddings for the Session 11 notebooks: recorded by default, computed live on request.

The notebooks embed the handbook's chunks and a set of example questions. So that they
run without a download, a key or a network, the vectors for exactly those texts are
recorded in `recorded-embeddings.npz`. They were made with fastembed's
BAAI/bge-small-en-v1.5 model, the free local model from Session 01 Part 9.

Any other text (your own question, a different chunk size) needs the model itself:
create the embedder with `live=True`. The first live use downloads about 67 MB, once.
"""

import hashlib
import os
from pathlib import Path

import numpy as np

MODEL_ID = "BAAI/bge-small-en-v1.5"
RECORDED = Path(__file__).parent / "recorded-embeddings.npz"


def text_key(text: str) -> str:
    """A short, stable identifier for a text: the start of its SHA-256 hash."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


class Embedder:
    """Turns texts into unit-length vectors, one row per text, in input order."""

    def __init__(self, *, live: bool = False) -> None:
        self.model_id = MODEL_ID
        # Course authors set COURSE_RECORD_EMBEDDINGS=1 to add missing vectors to the file
        self.recording = os.environ.get("COURSE_RECORD_EMBEDDINGS") == "1"
        self.live = live or self.recording
        self._model = None
        self._recorded: dict[str, np.ndarray] = {}
        if RECORDED.exists():
            with np.load(RECORDED) as data:
                self._recorded = {key: data[key] for key in data.files}

    def embed(self, texts: list[str]) -> np.ndarray:
        missing = [
            text
            for text in dict.fromkeys(texts)
            if text_key(text) not in self._recorded
        ]
        if missing and not self.live:
            raise LookupError(
                f"{len(missing)} text(s) have no recorded vector, for example {missing[0][:60]!r}. "
                "Create the embedder with live=True to compute them (free and local; the first "
                "use downloads about 67 MB)."
            )
        if missing:
            vectors = np.array(
                list(self._load_model().embed(missing)), dtype=np.float32
            )
            for text, vector in zip(missing, vectors, strict=True):
                self._recorded[text_key(text)] = vector
            if self.recording:
                np.savez_compressed(RECORDED, **self._recorded)
        return np.array(
            [self._recorded[text_key(text)] for text in texts], dtype=np.float32
        )

    def _load_model(self):
        if self._model is None:
            from fastembed import TextEmbedding  # imported only when needed

            cache = (
                os.environ.get("FASTEMBED_CACHE_PATH")
                or Path.home() / ".cache" / "fastembed"
            )
            self._model = TextEmbedding(model_name=MODEL_ID, cache_dir=str(cache))
        return self._model
