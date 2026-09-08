from titlovi.asr.streaming import LocalAgreement


def test_confirms_on_second_agreement():
    la = LocalAgreement()

    newly, partial = la.insert(["ово", "је", "тест"])
    assert newly == []
    assert partial == ["ово", "је", "тест"]

    newly, partial = la.insert(["ово", "је", "проба"])
    assert newly == ["ово", "је"]
    assert partial == ["проба"]

    newly, partial = la.insert(["ово", "је", "проба", "звука"])
    assert newly == ["проба"]
    assert partial == ["звука"]


def test_flush_confirms_remainder():
    la = LocalAgreement()
    la.insert(["крај", "реченице"])
    la.insert(["крај", "реченице"])
    assert la.flush() == []
    la.reset()
    la.insert(["нова", "реч"])
    assert la.flush() == ["нова", "реч"]


def test_shrinking_hypothesis_keeps_committed():
    la = LocalAgreement()
    la.insert(["а", "б", "в"])
    la.insert(["а", "б", "в"])  # потврђено 3
    newly, partial = la.insert(["а"])  # хипотеза се смањила
    assert newly == []
    assert partial == []
