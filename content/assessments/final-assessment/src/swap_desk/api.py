"""Task 3: the swap desk API, with an in-memory store."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """POST /swaps -> 201 and the stored swap (ids from 1); GET /swaps[?team=...] -> list;
    GET /swaps/{id} -> the swap, or 404. Each app has its own, empty store."""
    # TODO Task 3
    raise NotImplementedError
