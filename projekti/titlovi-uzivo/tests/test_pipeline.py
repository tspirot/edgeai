import numpy as np

from titlovi.config import Config
from titlovi.pipeline import Pipeline


class RecordingDisplay:
    def __init__(self):
        self.updates = []
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def render(self, committed, partial):
        self.updates.append((committed, partial))

    def should_quit(self):
        return False

    def stop(self):
        self.stopped = True


def _silence_frames(seconds, sr=16000, block=1600):
    for _ in range(int(seconds * sr / block)):
        yield np.zeros(block, dtype=np.float32)


def test_dummy_pipeline_end_to_end():
    cfg = Config()
    cfg.asr.backend = "dummy"
    cfg.text.script = "as-is"

    display = RecordingDisplay()
    final = Pipeline(cfg, frames=_silence_frames(6), display=display).run()

    assert display.started and display.stopped
    assert "demonstracija" in final
    assert "oblak" in final
    assert display.updates


def test_script_transliteration_applied():
    cfg = Config()
    cfg.asr.backend = "dummy"
    cfg.text.script = "cyrillic"

    display = RecordingDisplay()
    Pipeline(cfg, frames=_silence_frames(6), display=display).run()

    last_committed = display.updates[-1][0]
    assert "демонстрација" in last_committed
