from volan.actuators import DummyActuator
from volan.camera import DummyCamera
from volan.config import Config
from volan.lidar import DummyLidar
from volan.pipeline import DriveLoop
from volan.policy.dummy_policy import DummyPolicy


def _loop(cfg=None, **kw):
    cfg = cfg or Config()
    return DriveLoop(
        cfg,
        camera=kw.get("camera", DummyCamera(cfg.camera)),
        policy=kw.get("policy", DummyPolicy(throttle=0.4)),
        lidar=kw.get("lidar", DummyLidar()),
        actuator=kw.get("actuator", DummyActuator()),
    )


def test_free_road_drives():
    act = DummyActuator()
    loop = _loop(actuator=act)
    d = loop.step()
    assert not d.braking
    assert act.commands[-1][1] > 0     # има гаса


def test_obstacle_stops_car():
    lidar = DummyLidar(obstacle_mm=4000)
    act = DummyActuator()
    loop = _loop(lidar=lidar, actuator=act)
    loop.step()
    lidar.set_obstacle(350.0)
    d = loop.step()
    assert d.braking
    assert act.commands[-1][1] == 0.0


def test_run_respects_max_steps():
    loop = _loop()
    assert loop.run(max_steps=15) == 15


def test_steer_shaping_trim_and_invert():
    cfg = Config()
    cfg.drive.steer_trim = 0.1
    cfg.drive.invert_steer = True
    loop = _loop(cfg=cfg, policy=DummyPolicy(steer=0.5, throttle=0.2))
    d = loop.step()
    # invert(0.5 * gain 1.0 + trim 0.1) = -0.6
    assert abs(d.steer - (-0.6)) < 1e-6


def test_max_throttle_enforced_end_to_end():
    cfg = Config()
    cfg.drive.max_throttle = 0.25
    loop = _loop(cfg=cfg, policy=DummyPolicy(throttle=0.9))
    d = loop.step()
    assert d.throttle == 0.25
