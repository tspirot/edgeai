"""Изградња RAG индекса из фолдера са материјалима (.txt / .md)."""

from __future__ import annotations

import logging
from pathlib import Path

from asistent.rag.store import Index, build_embedder, chunk_text

log = logging.getLogger(__name__)

_EKSTENZIJE = (".txt", ".md", ".markdown")


def build_index(folder: "str | Path", rag_cfg) -> Index:
    root = Path(folder)
    if not root.exists():
        raise FileNotFoundError(f"Фолдер са материјалима не постоји: {root}")

    embedder = build_embedder(rag_cfg)
    idx = Index(embedder.name, getattr(embedder, "dim", rag_cfg.dim))

    files = sorted(p for p in root.rglob("*") if p.suffix.lower() in _EKSTENZIJE)
    if not files:
        raise ValueError(f"Нема .txt ни .md фајлова у {root}")

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        chunks = chunk_text(text, rag_cfg.chunk_chars, rag_cfg.chunk_overlap)
        idx.add(str(path.relative_to(root)), chunks, embedder)
        log.info("%s → %d исечака", path.name, len(chunks))

    return idx
