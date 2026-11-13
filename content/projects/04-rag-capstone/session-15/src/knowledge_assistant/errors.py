"""Exceptions raised by the knowledge_assistant package."""


class AssistantError(Exception):
    """Base class for the assistant's own errors."""


class DocumentError(AssistantError):
    """A document or folder can't be read, or has no text to index."""


class IndexMismatchError(AssistantError):
    """The index was built with a different configuration: rebuild it to change that."""


class GenerationError(AssistantError):
    """No usable answer came back from the generator."""


class GeneratorConfigurationError(GenerationError):
    """No API key, a rejected key, an unknown model, or a request the provider refuses.

    Retrying won't help: the configuration has to change.
    """


class GeneratorUnavailable(GenerationError):
    """The provider timed out, was unreachable, rate-limited us or failed (5xx), even
    after the SDK's retries. Asking again later may work."""


class InvalidAnswerError(GenerationError):
    """The model answered, but not usably: invalid or truncated output, a refusal, or
    citations that don't match the sources it was given."""
