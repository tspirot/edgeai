from govor.asr.base import AsrBackend, Segment, Transkript


def build_asr(cfg) -> AsrBackend:
    if cfg.backend == "dummy":
        from govor.asr.dummy_backend import DummyAsr

        return DummyAsr(cfg)
    if cfg.backend == "faster-whisper":
        from govor.asr.whisper_backend import WhisperAsr

        return WhisperAsr(cfg)
    raise ValueError(
        f"Непознат ASR: '{cfg.backend}' (има: faster-whisper, dummy)"
    )


__all__ = ["AsrBackend", "Segment", "Transkript", "build_asr"]
