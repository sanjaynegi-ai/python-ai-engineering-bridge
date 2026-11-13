"""Exceptions raised by the knowledge_assistant package."""


class AssistantError(Exception):
    """Base class for the assistant's own errors."""


class DocumentError(AssistantError):
    """A document or folder can't be read, or has no text to index."""


class IndexMismatchError(AssistantError):
    """The index was built with a different configuration: rebuild it to change that."""
