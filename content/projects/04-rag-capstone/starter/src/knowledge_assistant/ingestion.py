"""Bringing the index up to date with the documents folder, one file at a time."""

import logging
from pathlib import Path

from knowledge_assistant.embedding import Embedder
from knowledge_assistant.models import IngestReport
from knowledge_assistant.store import ChunkStore

logger = logging.getLogger(__name__)


def ingest(folder: Path, store: ChunkStore, embedder: Embedder) -> IngestReport:
    """Make the index match `folder`, doing only the work that changed.

    - A file whose content hash matches the index is unchanged: it's not read again,
      and nothing is embedded for it.
    - A new or changed file is loaded, chunked and embedded, then replaces whatever the
      index held for it.
    - A file that fails (DocumentError, or no chunks) is reported, and the index keeps
      whatever it held for it before. The other files carry on.
    - A source in the index that is no longer in the folder is removed.

    Any other exception (an embedder failure, say) stops the run. Files finished before
    it stay indexed, and the file being processed keeps its previous chunks, so running
    again carries on where this run stopped.

    Logs each added, updated and removed file at INFO and each failed file at WARNING,
    by its source, never by its contents or full path. Raises IndexMismatchError if the
    embedder isn't the one the index was built with.
    """
    # TODO Milestone 5
    raise NotImplementedError
