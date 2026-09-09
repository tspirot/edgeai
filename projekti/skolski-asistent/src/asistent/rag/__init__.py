"""RAG над школским материјалима."""

from __future__ import annotations

from asistent.rag.index import build_index
from asistent.rag.store import Index, build_embedder, chunk_text

__all__ = ["Index", "build_embedder", "build_index", "chunk_text", "load_index"]


def load_index(path) -> Index:
    return Index.load(path)
