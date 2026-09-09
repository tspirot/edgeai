from drzanje.config import PostureConfig
from drzanje.posture import PostureMonitor, Reference


def _mon(**kw):
    cfg = PostureConfig(
        neck_threshold_deg=12.0, trunk_threshold_deg=10.0, clear_margin_deg=4.0,
        bad_after_s=2.0, alert_after_s=6.0, alert_cooldown_s=20.0,
    )
    for k, v in kw.items():
        setattr(cfg, k, v)
    return PostureMonitor(cfg, Reference(neck_deg=5.0, trunk_deg=3.0))


def _drive(mon, neck, trunk, seconds, dt=1.0, t0=0.0):
    last = None
    t = t0
    for _ in range(int(seconds / dt)):
        last = mon.update(neck, trunk, t)
        t += dt
    return last, t


def test_good_posture_never_bad():
    mon = _mon()
    st, _ = _drive(mon, neck=6.0, trunk=4.0, seconds=30)
    assert not st.bad
    assert st.total_bad_s == 0.0
    assert st.events == 0


def test_slouch_becomes_bad_and_counts_after_delay():
    mon = _mon()
    # врат 25° → одступање 20° > праг 12
    st, t = _drive(mon, neck=25.0, trunk=4.0, seconds=5)
    assert st.bad
    assert st.events == 1               # ушло у бројач после bad_after_s
    assert st.total_bad_s > 0


def test_alert_fires_after_sustained_slouch_once():
    mon = _mon()
    alerts = 0
    t = 0.0
    for _ in range(15):                 # 15 s погрбљено
        s = mon.update(25.0, 4.0, t)
        alerts += int(s.alert)
        t += 1.0
    assert alerts == 1                  # једном (cooldown 20 s)


def test_hysteresis_clears_only_below_margin():
    mon = _mon()
    _drive(mon, 25.0, 4.0, seconds=5)   # уђи у лоше
    # угао одступања = 13 (још увек > праг−маргина = 8) → и даље лоше
    s, _ = _drive(mon, neck=18.0, trunk=4.0, seconds=3, t0=5.0)
    assert s.bad
    # одступање 2 (< 8) → чисти се
    s, _ = _drive(mon, neck=7.0, trunk=4.0, seconds=3, t0=8.0)
    assert not s.bad


def test_second_episode_increments_events():
    mon = _mon()
    _drive(mon, 25.0, 4.0, 5, t0=0.0)          # епизода 1
    _drive(mon, 6.0, 4.0, 5, t0=5.0)           # опоравак
    st, _ = _drive(mon, 25.0, 4.0, 5, t0=10.0)  # епизода 2
    assert st.events == 2


def test_reference_shifts_baseline():
    # без референце: угао 10 је добар (< 12). са референцом 5: одступање 5, и даље добро
    mon = PostureMonitor(PostureConfig(bad_after_s=1.0), Reference(0.0, 0.0))
    st = mon.update(10.0, 5.0, 0.0)
    assert not st.bad
