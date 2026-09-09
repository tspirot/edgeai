import numpy as np

from mapa.config import Config
from mapa.navigator import Navigator
from mapa.pose import Pose
from mapa.robot import SimRobot
from mapa.slam import Slam
from mapa.world import SimLidar, room


def _cfg():
    cfg = Config()
    cfg.grid.size_m = 10.0
    cfg.grid.res_m = 0.1
    cfg.planner.inflate_m = 0.2
    return cfg


def test_slam_tracks_pose_while_driving_straight():
    cfg = _cfg()
    start = Pose(-2.0, 0.0, 0.0)
    lidar = SimLidar(room(obstacles=False), n_beams=240, noise_m=0.005, seed=1)
    robot = SimRobot(lidar, start, cfg.pursuit.wheelbase_m, speed_scale=0.6)

    slam = Slam(cfg, start=start)
    for _ in range(20):
        slam.update(*robot.sense())
        robot.move(0.0, 0.5, 0.15)

    err = np.hypot(slam.pose.x - robot.true_pose.x, slam.pose.y - robot.true_pose.y)
    assert err < 0.25          # процена прати стварни положај


def test_navigator_reaches_goal_in_sim():
    cfg = _cfg()
    start = Pose(-2.0, -1.0, 0.0)
    lidar = SimLidar(room(obstacles=False), n_beams=240, noise_m=0.004, seed=2)
    robot = SimRobot(lidar, start, cfg.pursuit.wheelbase_m, speed_scale=0.7)
    nav = Navigator(cfg, robot, start=start)

    goal = (0.6, 0.2)
    res = nav.drive_to(goal, dt=0.15, max_steps=140, replan_every=8)
    assert res["reached"]
    final = np.hypot(robot.true_pose.x - goal[0], robot.true_pose.y - goal[1])
    assert final < 0.5


def test_map_has_walls_after_scan():
    cfg = _cfg()
    start = Pose(0.0, 0.0, 0.0)
    lidar = SimLidar(room(width=6, height=4, obstacles=False), n_beams=240, noise_m=0.003, seed=3)
    robot = SimRobot(lidar, start, cfg.pursuit.wheelbase_m)

    slam = Slam(cfg, start=start)
    for _ in range(6):
        slam.update(*robot.sense())
        robot.move(0.15, 0.3, 0.15)

    assert slam.grid.occupied_mask().sum() > 20
    cx, cy = slam.grid.world_to_cell([3.0, 0.0])
    assert slam.grid.occupied_mask()[max(0, cy - 3):cy + 3, max(0, cx - 3):cx + 3].any()
