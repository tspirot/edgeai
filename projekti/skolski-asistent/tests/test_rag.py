import numpy as np

from asistent.config import RagConfig
from asistent.rag.store import HashingEmbedder, Index, build_embedder, chunk_text


def test_chunk_text_splits_with_overlap():
    text = "\n\n".join(f"Пасус број {i}. " + "реч " * 60 for i in range(6))
    chunks = chunk_text(text, size=400, overlap=80)
    assert len(chunks) > 1
    assert all(len(c) <= 400 for c in chunks)


def test_chunk_text_empty():
    assert chunk_text("   ") == []


def test_hashing_embedder_deterministic_and_normalized():
    emb = HashingEmbedder(dim=256)
    a = emb.embed(["отпорник у колу", "отпорник у колу"])
    assert np.allclose(a[0], a[1])
    assert np.isclose(np.linalg.norm(a[0]), 1.0)


def test_index_search_finds_relevant_chunk():
    emb = HashingEmbedder(dim=512)
    idx = Index(emb.name, emb.dim)
    idx.add("elektro.md", [
        "Ом-ов закон повезује напон, струју и отпор: U = I * R.",
        "Транзистор као прекидач у засићењу проводи струју колектор-емитор.",
    ], emb)
    idx.add("mehanika.md", ["Полуга множи силу на рачун пута."], emb)

    hits = idx.search("како гласи Омов закон", emb, top_k=1, min_score=0.0)
    assert hits
    assert "Ом-ов закон" in hits[0][1].text


def test_index_save_load_roundtrip(tmp_path):
    emb = HashingEmbedder(dim=128)
    idx = Index(emb.name, emb.dim)
    idx.add("a.md", ["први исечак", "други исечак"], emb)
    path = tmp_path / "index.json"
    idx.save(path)

    back = Index.load(path)
    assert len(back.entries) == 2
    assert back.entries[0].source == "a.md"
    assert np.allclose(back.entries[0].vector, idx.entries[0].vector)


def test_build_embedder_hashing_from_config():
    emb = build_embedder(RagConfig(embed_backend="hashing", dim=64))
    assert emb.dim == 64
