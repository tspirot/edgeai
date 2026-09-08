import numpy as np

from titlovi.asr.vad import EnergyVad, rms


def test_rms_helper():
    assert rms([]) == 0.0
    assert abs(rms([1.0, -1.0, 1.0, -1.0]) - 1.0) < 1e-9


def test_endpoint_after_silence():
    sr = 16000
    vad = EnergyVad(samplerate=sr, silence_seconds=0.3, threshold=0.02)
    speech = np.full(sr // 10, 0.2, dtype=np.float32)   # 100 ms гласно
    silence = np.zeros(sr // 10, dtype=np.float32)       # 100 ms тишина

    assert vad.update(speech)["speech"] is True
    assert vad.update(silence)["endpoint"] is False      # 100 ms тишине
    assert vad.update(silence)["endpoint"] is False      # 200 ms
    assert vad.update(silence)["endpoint"] is True       # 300 ms → крај целине


def test_no_endpoint_without_prior_speech():
    vad = EnergyVad(samplerate=16000, silence_seconds=0.1, threshold=0.02)
    silence = np.zeros(16000, dtype=np.float32)
    assert vad.update(silence)["endpoint"] is False
