from znak.vote import Vote


def test_needs_min_count():
    v = Vote(window=6, min_count=4, min_confidence=0.5)
    assert v.push("A", 0.9) is None
    assert v.push("A", 0.9) is None
    assert v.push("A", 0.9) is None
    assert v.push("A", 0.9) == "A"


def test_low_confidence_ignored():
    v = Vote(window=5, min_count=2, min_confidence=0.6)
    for _ in range(4):
        v.push("A", 0.3)
    assert v.current is None


def test_switches_letter():
    v = Vote(window=4, min_count=3, min_confidence=0.5)
    for _ in range(4):
        v.push("A", 0.9)
    assert v.current == "A"
    for _ in range(4):
        v.push("B", 0.9)
    assert v.current == "B"


def test_noise_does_not_flip():
    v = Vote(window=6, min_count=4, min_confidence=0.5)
    for _ in range(6):
        v.push("A", 0.9)
    assert v.current == "A"
    v.push("B", 0.9)          # један промашај
    assert v.current == "A"
