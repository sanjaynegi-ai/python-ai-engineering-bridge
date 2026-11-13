"""The persistent index: chunks, their metadata and their vectors, in a local Chroma database."""

from pathlib import Path

import chromadb  # noqa: F401  (you'll need these in ChunkStore)
import numpy as np
from chromadb.config import Settings as ChromaSettings  # noqa: F401

from knowledge_assistant.errors import IndexMismatchError  # noqa: F401
from knowledge_assistant.models import Chunk, Hit, IndexConfig


class ChunkStore:
    """Chunks and vectors for every indexed source, kept on disk in `folder`.

    The index remembers the IndexConfig it was built with. Opening it with a different
    one raises IndexMismatchError, naming the settings that differ, unless `rebuild` is
    True, which deletes everything and starts an empty index with the new configuration.
    """

    def __init__(self, folder: Path, config: IndexConfig, *, rebuild: bool = False) -> None:
        self.config = config
        # TODO Milestone 4: open (or create) the Chroma collection, and check the config

    def count(self) -> int:
        """The number of chunks in the index."""
        # TODO Milestone 4
        raise NotImplementedError

    def sources(self) -> dict[str, str]:
        """Every indexed source, with the content hash its chunks were made from."""
        # TODO Milestone 4
        raise NotImplementedError

    def chunks(self, source: str) -> list[Chunk]:
        """The source's chunks, in index order, exactly as they were stored.

        Empty if the source isn't indexed.
        """
        # TODO Milestone 4
        raise NotImplementedError

    def replace(self, source: str, chunks: list[Chunk], vectors: np.ndarray) -> None:
        """Make `chunks` the source's only chunks, with one vector (row) each.

        Raises ValueError, before changing anything, if a chunk belongs to another
        source, the counts differ, or the vectors have the wrong dimensions. An empty
        list removes the source.
        """
        # TODO Milestone 4
        raise NotImplementedError

    def remove(self, source: str) -> int:
        """Delete every chunk of `source`; returns how many there were."""
        # TODO Milestone 4
        raise NotImplementedError

    def search(self, vector: np.ndarray, *, k: int) -> list[Hit]:
        """The k chunks most similar to `vector`, best first; scores are cosine similarities.

        Raises ValueError if the vector has the wrong dimensions.
        """
        # TODO Milestone 4
        raise NotImplementedError
