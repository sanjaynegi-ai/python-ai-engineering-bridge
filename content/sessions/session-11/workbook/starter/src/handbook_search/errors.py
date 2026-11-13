"""Exceptions raised by the handbook_search package."""


class DocumentError(Exception):
    """A document or folder can't be read."""


class SearchIndexError(Exception):
    """The search index is missing, damaged, or built with a different embedding model."""
