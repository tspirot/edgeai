"""Командна линија: `mapa sim | map | navigate | plan | show | devices`."""

from __future__ import annotations

import argparse
import logging
import sys
import time

from mapa import __version__
from mapa.config import load_config

log = logging.getLogger("mapa")


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc is not None:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mapa", description="Ходник у глави — 2D SLAM и навигација")
    p.add_argument("--version", action="version", version=f"mapa {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sim = sub.add_parser("sim", help="Синтетичка просторија: мапирање + навигација до циља")
    sim.add_argument("-c", "--config")
    sim.add_argument("--goal", nargs=2, type=float, metavar=("X", "Y"), default=[2.0, 1.2])
    sim.add_argument("--steps", type=int, default=200)
    sim.add_argument("--out", default="out/mapa.png")
    sim.add_argument("-v", "--verbose", action="store_true")

    mp = sub.add_parser("map", help="Право возило: сакупи скенове (гурање/вожња) → мапа")
    mp.add_argument("-c", "--config")
    mp.add_argument("--seconds", type=float, default=60.0)
    mp.add_argument("--replay", help=".npz снимак скенова уместо RPLIDAR-а")
    mp.add_argument("--out", default="out/mapa.npz")
    mp.add_argument("-v", "--verbose", action="store_true")

    nav = sub.add_parser("navigate", help="SLAM + навигација до тачке (право возило)")
    nav.add_argument("-c", "--config")
    nav.add_argument("--goal", nargs=2, type=float, metavar=("X", "Y"), required=True)
    nav.add_argument("--replay", help=".npz снимак скенова (без кретања — за пробу)")
    nav.add_argument("-v", "--verbose", action="store_true")

    pl = sub.add_parser("plan", help="Учитај мапу, испланирај пут до циља, сними слику")
    pl.add_argument("map", help=".npz мапа")
    pl.add_argument("--start", nargs=2, type=float, metavar=("X", "Y"), default=[0.0, 0.0])
    pl.add_argument("--goal", nargs=2, type=float, metavar=("X", "Y"), required=True)
    pl.add_argument("-c", "--config")
    pl.add_argument("--out", default="out/plan.png")

    sh = sub.add_parser("show", help="Прикажи сачувану мапу као слику")
    sh.add_argument("map")
    sh.add_argument("--out", default="out/mapa.png")

    sub.add_parser("devices", help="Прикажи серијске портове")
    return p


def _sim_setup(cfg, start_theta=0.0):
    from mapa.pose import Pose
    from mapa.robot import SimRobot
    from mapa.world import SimLidar, room

    lidar = SimLidar(room(), max_m=cfg.lidar.max_mm / 1000.0)
    robot = SimRobot(lidar, Pose(-1.5, -0.8, start_theta), cfg.pursuit.wheelbase_m, speed_scale=1.0)
    return robot


def cmd_sim(args) -> int:
    cfg = load_config(args.config)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else "INFO")
    from mapa.mapio import save_png
    from mapa.navigator import Navigator

    robot = _sim_setup(cfg)
    nav = Navigator(cfg, robot, start=robot.true_pose)
    res = nav.drive_to(tuple(args.goal), max_steps=args.steps)
    tp, ep = robot.true_pose, nav.slam.pose
    drift = ((tp.x - ep.x) ** 2 + (tp.y - ep.y) ** 2) ** 0.5
    print(
        f"Циљ {tuple(args.goal)}: {'СТИГАО' if res['reached'] else 'није стигао'} "
        f"за {res['steps']} корака.\n"
        f"  стварно ({tp.x:+.2f}, {tp.y:+.2f})  процена ({ep.x:+.2f}, {ep.y:+.2f})  "
        f"грешка SLAM-а {drift:.2f} m"
    )
    save_png(nav.slam.grid, args.out, path_world=nav.path, pose=nav.slam.pose)
    print(f"Мапа → {args.out}")
    return 0 if res["reached"] else 1


def cmd_map(args) -> int:
    cfg = load_config(args.config)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)
    from mapa.mapio import save_npz, save_png
    from mapa.scan import build_scan_source
    from mapa.slam import Slam

    src = build_scan_source(cfg.lidar, replay=args.replay)
    slam = Slam(cfg)
    print(f"Мапирам {args.seconds:.0f} s — гурај/вози возило споро…")
    t_end = time.monotonic() + args.seconds
    n = 0
    try:
        while time.monotonic() < t_end:
            try:
                angles, ranges = src.read()
            except StopIteration:
                break
            slam.update(angles, ranges)
            n += 1
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        src.close()
    save_npz(slam.grid, args.out)
    save_png(slam.grid, str(args.out).replace(".npz", ".png"), pose=slam.pose)
    print(f"{n} скенова → {args.out}. Положај на крају: {slam.pose}")
    return 0


def cmd_navigate(args) -> int:
    cfg = load_config(args.config)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)
    from mapa.actuators import build_actuator
    from mapa.navigator import Navigator
    from mapa.robot import RealRobot
    from mapa.scan import build_scan_source

    src = build_scan_source(cfg.lidar, replay=args.replay)
    robot = RealRobot(src, build_actuator("dummy" if args.replay else "auto"))
    nav = Navigator(cfg, robot)
    try:
        res = nav.drive_to(tuple(args.goal))
    finally:
        robot.close()
    print(f"{'СТИГАО' if res['reached'] else 'није стигао'} за {res['steps']} корака")
    return 0 if res["reached"] else 1


def cmd_plan(args) -> int:
    cfg = load_config(args.config)
    from mapa.mapio import load_npz, save_png
    from mapa.planner import plan

    grid = load_npz(args.map)
    path = plan(grid, tuple(args.start), tuple(args.goal), cfg.planner)
    if not path:
        print("Нема пута до циља (препрека или непознат простор).")
        save_png(grid, args.out)
        return 1
    length = sum(
        ((path[i][0] - path[i - 1][0]) ** 2 + (path[i][1] - path[i - 1][1]) ** 2) ** 0.5
        for i in range(1, len(path))
    )
    save_png(grid, args.out, path_world=path)
    print(f"Пут: {len(path)} тачака, ~{length:.2f} m → {args.out}")
    return 0


def cmd_show(args) -> int:
    from mapa.mapio import load_npz, save_png

    grid = load_npz(args.map)
    save_png(grid, args.out)
    print(f"{args.out}")
    return 0


def cmd_devices(_args) -> int:
    import glob

    print("Серијски портови:", sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")) or "нема")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    handlers = {
        "sim": cmd_sim, "map": cmd_map, "navigate": cmd_navigate,
        "plan": cmd_plan, "show": cmd_show, "devices": cmd_devices,
    }
    return handlers[args.cmd](args)
