"""A small vector store: vectors, chunks and the embedding model's ID, kept together."""

from pathlib import Path

import numpy as np

from handbook_search.errors import SearchIndexError  # noqa: F401  (you'll need it in load)
from handbook_search.models import Chunk, Hit


def normalise(vectors: np.ndarray) -> np.ndarray:
    """Scale each row (or a single vector) to length 1; all-zero rows stay zero."""
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    return (vectors / np.where(norms == 0, 1, norms)).astype(np.float32)


class VectorStore:
    def __init__(self, model_id: str, dimensions: int) -> None:
        self.model_id = model_id
        self.dimensions = dimensions
        # TODO Milestone 4: somewhere to keep the vectors and the chunks

    def __len__(self) -> int:
        # TODO Milestone 4
        raise NotImplementedError

    @property
    def chunks(self) -> list[Chunk]:
        """The stored chunks, in the order they were added (a copy)."""
        # TODO Milestone 4
        raise NotImplementedError

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        """Store chunks with their vectors (one row each), normalised.

        Raises ValueError if the counts differ or the vectors have the wrong dimensions.
        """
        # TODO Milestone 4
        raise NotImplementedError

    def search(
        self, query: np.ndarray, *, k: int = 3, min_score: float = -1.0, source: str | None = None
    ) -> list[Hit]:
        """The k chunks most similar to `query`, best first, scoring at least `min_score`.

        With `source`, only chunks from that file are considered (filtered before ranking).
        Raises ValueError if the query has the wrong dimensions.
        """
        # TODO Milestone 4
        raise NotImplementedError

    def save(self, folder: Path) -> None:
        """Write `vectors.npy` and `store.json` (model ID, dimensions, chunks) to `folder`."""
        # TODO Milestone 4
        raise NotImplementedError

    @classmethod
    def load(cls, folder: Path, *, model_id: str) -> "VectorStore":
        """The store saved in `folder`.

        Raises SearchIndexError if there is no index, if it is damaged, or if it was built
        with a different embedding model than `model_id`.
        """
        # TODO Milestone 4
        raise NotImplementedError
