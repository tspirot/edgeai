"""RAG над школским материјалима — дељење на исечке, уградња, претрага.

Подразумевани `hashing` уграђивач нема ниједну зависност (bag-of-words hashing
+ косинусна сличност) — довољан за демо и тестове. За озбиљну употребу
пребацити на `sentence-transformers` у конфигурацији.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_WORD = re.compile(r"\w+", re.UNICODE)


def _stable_bucket(word: str, dim: int) -> int:
    """Стабилан хеш (не зависи од PYTHONHASHSEED) → индекс кофе."""
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % dim


def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list:
    """Подели текст на исечке ~`size` знакова, са преклапањем `overlap`.

    Реже на границама пасуса кад може, да исечак остане смислен.
    """
    text = text.strip()
    if not text:
        return []
    if overlap >= size:
        raise ValueError("overlap мора бити мањи од size")

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list = []
    buf = ""
    for para in paragraphs:
        if buf and len(buf) + len(para) + 2 > size:
            chunks.append(buf)
            buf = buf[-overlap:] + "\n\n" + para if overlap else para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
        while len(buf) > size:
            chunks.append(buf[:size])
            buf = buf[size - overlap:]
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


class HashingEmbedder:
    """Bag-of-words hashing уградња. Детерминистична, без модела."""

    name = "hashing"

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim

    def embed(self, texts: list) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for word in _WORD.findall(text.lower()):
                out[i, _stable_bucket(word, self.dim)] += 1.0
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return out / norms


class SentenceTransformerEmbedder:
    name = "sentence-transformers"

    def __init__(self, model: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model)
        self.dim = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: list) -> np.ndarray:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float32)


def build_embedder(rag_cfg):
    backend = (rag_cfg.embed_backend or "hashing").lower()
    if backend == "hashing":
        return HashingEmbedder(rag_cfg.dim)
    if backend in ("sentence-transformers", "st"):
        return SentenceTransformerEmbedder(rag_cfg.embed_model)
    raise ValueError(f"Непознат уграђивач: '{rag_cfg.embed_backend}'")


@dataclass
class Entry:
    source: str
    text: str
    vector: np.ndarray


class Index:
    """Списак исечака са векторима + косинусна претрага."""

    def __init__(self, embedder_name: str = "hashing", dim: int = 512) -> None:
        self.embedder_name = embedder_name
        self.dim = dim
        self.entries: list = []

    def add(self, source: str, chunks: list, embedder) -> None:
        if not chunks:
            return
        vectors = embedder.embed(chunks)
        for text, vec in zip(chunks, vectors):
            self.entries.append(Entry(source=source, text=text, vector=np.asarray(vec)))

    def search(self, query: str, embedder, top_k: int = 3, min_score: float = 0.0) -> list:
        if not self.entries:
            return []
        q = embedder.embed([query])[0]
        matrix = np.vstack([e.vector for e in self.entries])
        scores = matrix @ q
        order = np.argsort(scores)[::-1][:top_k]
        return [(float(scores[i]), self.entries[i]) for i in order if scores[i] >= min_score]

    def save(self, path: "str | Path") -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "embedder": self.embedder_name,
            "dim": self.dim,
            "entries": [
                {"source": e.source, "text": e.text, "vector": e.vector.tolist()}
                for e in self.entries
            ],
        }
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: "str | Path") -> "Index":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"RAG индекс не постоји: {p}. Направи га са `asistent index build <фолдер>`."
            )
        data = json.loads(p.read_text(encoding="utf-8"))
        idx = cls(data.get("embedder", "hashing"), data.get("dim", 512))
        for e in data.get("entries", []):
            idx.entries.append(
                Entry(e["source"], e["text"], np.asarray(e["vector"], dtype=np.float32))
            )
        return idx
