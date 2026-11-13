"""The assembled assistant: one object that the CLI, the API and the UI all share."""

from dataclasses import dataclass

import httpx2

from knowledge_assistant.answering import answer_question
from knowledge_assistant.embedding import Embedder, make_embedder
from knowledge_assistant.generation import Generator, make_generator
from knowledge_assistant.models import IndexConfig
from knowledge_assistant.schemas import Answer
from knowledge_assistant.settings import Settings
from knowledge_assistant.store import ChunkStore


def open_store(settings: Settings, embedder: Embedder, *, rebuild: bool = False) -> ChunkStore:
    config = IndexConfig(
        embedding_model=embedder.model_id,
        dimensions=embedder.dimensions,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return ChunkStore(settings.index, config, rebuild=rebuild)


@dataclass
class Assistant:
    store: ChunkStore
    embedder: Embedder
    generator: Generator
    top_k: int
    min_score: float

    def ask(self, question: str) -> Answer:
        return answer_question(
            question,
            store=self.store,
            embedder=self.embedder,
            generator=self.generator,
            top_k=self.top_k,
            min_score=self.min_score,
        )


def build_assistant(
    settings: Settings | None = None, *, http_client: httpx2.Client | None = None
) -> Assistant:
    """The assistant described by the settings (by default, from the environment and .env).

    Raises AssistantError subclasses for a missing key or an index built with other
    settings, so a misconfigured service fails at startup rather than on the first question.
    """
    settings = settings or Settings()
    embedder = make_embedder(settings)
    return Assistant(
        store=open_store(settings, embedder),
        embedder=embedder,
        generator=make_generator(settings, http_client=http_client),
        top_k=settings.top_k,
        min_score=settings.effective_min_score,
    )
