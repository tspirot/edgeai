import numpy as np

from asistent.config import Config
from asistent.pipeline import Assistant
from asistent.rag.store import HashingEmbedder, Index


class RecordingTts:
    def __init__(self):
        self.spoken = []

    def say(self, text):
        self.spoken.append(text)

    def close(self):
        pass


def _cfg_dummy():
    cfg = Config()
    cfg.asr.backend = "dummy"
    cfg.vlm.backend = "dummy"
    cfg.tts.backend = "console"
    return cfg


def _slika():
    return np.full((32, 32, 3), 120, dtype=np.uint8)


def test_end_to_end_dummy():
    cfg = _cfg_dummy()
    tts = RecordingTts()
    assistant = Assistant(cfg, tts=tts)
    try:
        answer = assistant.ask(_slika(), "Шта је ово?")
    finally:
        assistant.close()

    assert "Шта је ово?" in answer.text
    assert tts.spoken == [answer.text]


def test_empty_question_is_handled():
    assistant = Assistant(_cfg_dummy(), tts=RecordingTts())
    answer = assistant.ask(_slika(), "   ")
    assert "Понови" in answer.text


def test_no_speak_skips_tts():
    cfg = _cfg_dummy()
    cfg.tts.speak = False
    tts = RecordingTts()
    Assistant(cfg, tts=tts).ask(_slika(), "питање")
    assert tts.spoken == []


def test_transcribe_uses_asr_backend():
    assistant = Assistant(_cfg_dummy(), tts=RecordingTts())
    assert assistant.transcribe(np.zeros(1600, dtype=np.float32)) == assistant.cfg.asr.dummy_text


def test_rag_context_reaches_answer(tmp_path):
    emb = HashingEmbedder(dim=512)
    idx = Index(emb.name, emb.dim)
    idx.add("elektro.md", ["Ом-ов закон: напон је производ струје и отпора, U = I * R."], emb)
    index_path = tmp_path / "index.json"
    idx.save(index_path)

    cfg = _cfg_dummy()
    cfg.rag.enabled = True
    cfg.rag.index_path = str(index_path)
    cfg.rag.min_score = 0.0

    assistant = Assistant(cfg, tts=RecordingTts())
    answer = assistant.ask(_slika(), "шта каже Омов закон")
    assert answer.used_context
    assert "Ом-ов закон" in answer.used_context[0]
